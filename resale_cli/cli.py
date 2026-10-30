"""Command-line interface for the resale cross-lister."""

import argparse
import sys
from typing import List, Optional

from .models import ProductRecord
from .storage import Storage
from .llm import LLMEnhancer
from .draft import draft_listings, PLATFORMS
from .export import export_csv


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resale-cli",
        description="Draft eBay and Amazon resale listings from one product record.",
    )
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new product record.")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--description", required=True)
    p_add.add_argument("--condition", required=True)
    p_add.add_argument("--pricing", required=True, dest="pricing")
    p_add.set_defaults(func=_cmd_add)

    # list
    p_list = sub.add_parser("list", help="List stored products.")
    p_list.set_defaults(func=_cmd_list)

    # draft
    p_draft = sub.add_parser("draft", help="Draft listings for a product.")
    p_draft.add_argument("--id", required=True, help="Product id.")
    p_draft.add_argument(
        "--platform",
        choices=PLATFORMS,
        action="append",
        help="Platform to draft (repeatable). Defaults to both.",
    )
    p_draft.add_argument("--no-llm", action="store_true", help="Skip LLM enhancement.")
    p_draft.add_argument("--llm-url", default=None, help="LLM endpoint base URL.")
    p_draft.add_argument("--llm-model", default=None, help="LLM model name.")
    p_draft.set_defaults(func=_cmd_draft)

    # show
    p_show = sub.add_parser("show", help="Show a product and its drafts.")
    p_show.add_argument("--id", required=True)
    p_show.set_defaults(func=_cmd_show)

    # export
    p_export = sub.add_parser("export", help="Export drafts to CSV.")
    p_export.add_argument("--out", required=True, help="Output CSV path.")
    p_export.set_defaults(func=_cmd_export)

    # delete
    p_delete = sub.add_parser("delete", help="Delete a product and its drafts.")
    p_delete.add_argument("--id", required=True)
    p_delete.set_defaults(func=_cmd_delete)

    return parser


def _cmd_add(args) -> int:
    storage = Storage()
    product = ProductRecord(
        title=args.title,
        description=args.description,
        condition_notes=args.condition,
        pricing_hints=args.pricing,
    )
    storage.add_product(product)
    print(f"Added product {product.id}: {product.title}")
    return 0


def _cmd_list(args) -> int:
    storage = Storage()
    products = storage.load_products()
    if not products:
        print("No products stored yet.")
        return 0
    for p in products:
        print(f"{p.id} | {p.title} | {p.condition_notes} | {p.pricing_hints}")
    return 0


def _cmd_draft(args) -> int:
    storage = Storage()
    product = storage.get_product(args.id)
    if product is None:
        print(f"Product {args.id} not found.")
        return 1
    enhancer = LLMEnhancer(
        base_url=args.llm_url,
        model=args.llm_model,
        enabled=not args.no_llm,
    )
    platforms = args.platform or PLATFORMS
    drafts = draft_listings(product, enhancer, platforms)
    for d in drafts:
        storage.add_draft(d)
        print(f"Drafted {d.platform} listing {d.id}: {d.title}")
    return 0


def _cmd_show(args) -> int:
    storage = Storage()
    product = storage.get_product(args.id)
    if product is None:
        print(f"Product {args.id} not found.")
        return 1
    print(f"Product {product.id}")
    print(f"  Title:        {product.title}")
    print(f"  Description:  {product.description}")
    print(f"  Condition:    {product.condition_notes}")
    print(f"  Pricing:      {product.pricing_hints}")
    print(f"  Created:      {product.created_at}")
    drafts = [d for d in storage.load_drafts() if d.product_id == product.id]
    if drafts:
        print("Drafts:")
        for d in drafts:
            print(f"  [{d.platform}] {d.id}: {d.title} | {d.price} | {d.condition}")
    else:
        print("Drafts: none yet. Run `resale-cli draft --id <id>`.")
    return 0


def _cmd_export(args) -> int:
    storage = Storage()
    drafts = storage.load_drafts()
    if not drafts:
        print("No drafts to export.")
        return 0
    path = export_csv(drafts, args.out)
    print(f"Exported {len(drafts)} drafts to {path}")
    return 0


def _cmd_delete(args) -> int:
    storage = Storage()
    if storage.delete_product(args.id):
        print(f"Deleted product {args.id} and its drafts.")
        return 0
    print(f"Product {args.id} not found.")
    return 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
