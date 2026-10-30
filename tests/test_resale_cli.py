"""Tests for the resale cross-lister CLI."""

import csv
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Ensure the package is importable when tests run from the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resale_cli.models import ProductRecord, ListingDraft
from resale_cli.storage import Storage
from resale_cli.llm import LLMEnhancer
from resale_cli.draft import draft_listings, PLATFORMS
from resale_cli.export import export_csv
from resale_cli.cli import main


class TestModels(unittest.TestCase):
    def test_product_record_defaults(self):
        p = ProductRecord(title="Widget", description="A widget", condition_notes="Like new", pricing_hints="$10")
        self.assertTrue(p.id)
        self.assertEqual(p.title, "Widget")
        self.assertIsNotNone(p.created_at)
        self.assertEqual(p.created_at[:10], p.updated_at[:10])

    def test_product_roundtrip(self):
        p = ProductRecord(title="Widget", description="A widget", condition_notes="Like new", pricing_hints="$10")
        p2 = ProductRecord.from_dict(p.to_dict())
        self.assertEqual(p.id, p2.id)
        self.assertEqual(p.title, p2.title)

    def test_listing_draft_roundtrip(self):
        d = ListingDraft(product_id="abc", platform="ebay", title="T", description="D", price="$10", condition="New")
        d2 = ListingDraft.from_dict(d.to_dict())
        self.assertEqual(d.id, d2.id)
        self.assertEqual(d.platform, d2.platform)


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.storage = Storage(data_dir=self.tmp)

    def test_add_and_list_products(self):
        p = ProductRecord(title="Widget", description="d", condition_notes="c", pricing_hints="$1")
        self.storage.add_product(p)
        products = self.storage.load_products()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].title, "Widget")

    def test_get_and_update_product(self):
        p = self.storage.add_product(ProductRecord(title="Old", description="d", condition_notes="c", pricing_hints="$1"))
        p.title = "New"
        p.touch()
        self.assertTrue(self.storage.update_product(p))
        got = self.storage.get_product(p.id)
        self.assertEqual(got.title, "New")
        self.assertNotEqual(got.created_at, got.updated_at)

    def test_delete_product_removes_drafts(self):
        p = self.storage.add_product(ProductRecord(title="Widget", description="d", condition_notes="c", pricing_hints="$1"))
        self.storage.add_draft(ListingDraft(product_id=p.id, platform="ebay", title="T", description="D", price="$1", condition="c"))
        self.assertTrue(self.storage.delete_product(p.id))
        self.assertIsNone(self.storage.get_product(p.id))
        self.assertEqual(len(self.storage.load_drafts()), 0)


class TestLLMEnhancer(unittest.TestCase):
    def test_disabled_returns_originals(self):
        enhancer = LLMEnhancer(enabled=False)
        title, desc = enhancer.enhance_for_platform("ebay", "T", "D", "c", "$1")
        self.assertEqual(title, "T")
        self.assertEqual(desc, "D")

    def test_unreachable_endpoint_returns_originals(self):
        enhancer = LLMEnhancer(base_url="http://127.0.0.1:1", enabled=True)
        title, desc = enhancer.enhance_for_platform("ebay", "T", "D", "c", "$1")
        self.assertEqual(title, "T")
        self.assertEqual(desc, "D")

    def test_parse_labeled_output(self):
        enhancer = LLMEnhancer(enabled=False)
        title, desc = enhancer._parse("Title: New Title\nDescription: New Desc", "T", "D")
        self.assertEqual(title, "New Title")
        self.assertEqual(desc, "New Desc")

    def test_parse_title_only(self):
        enhancer = LLMEnhancer(enabled=False)
        title, desc = enhancer._parse("Title: Only Title", "T", "D")
        self.assertEqual(title, "Only Title")
        self.assertEqual(desc, "D")


class TestDraft(unittest.TestCase):
    def test_draft_creates_one_per_platform(self):
        product = ProductRecord(title="Widget", description="d", condition_notes="c", pricing_hints="$1")
        enhancer = LLMEnhancer(enabled=False)
        drafts = draft_listings(product, enhancer)
        self.assertEqual(len(drafts), len(PLATFORMS))
        platforms = {d.platform for d in drafts}
        self.assertEqual(platforms, set(PLATFORMS))
        for d in drafts:
            self.assertEqual(d.product_id, product.id)
            self.assertEqual(d.title, "Widget")
            self.assertEqual(d.description, "d")
            self.assertEqual(d.price, "$1")
            self.assertEqual(d.condition, "c")


class TestExport(unittest.TestCase):
    def test_export_csv_roundtrip(self):
        drafts = [
            ListingDraft(product_id="p1", platform="ebay", title="T1", description="D1", price="$1", condition="c"),
            ListingDraft(product_id="p1", platform="amazon", title="T2", description="D2", price="$2", condition="c"),
        ]
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "out.csv")
        export_csv(drafts, path)
        with open(path, newline="", encoding="utf-8") as fh:
            reader = list(csv.DictReader(fh))
        self.assertEqual(len(reader), 2)
        self.assertEqual(reader[0]["platform"], "ebay")
        self.assertEqual(reader[1]["platform"], "amazon")


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.env = dict(os.environ)
        self.env["RESALER_CLI_DATA_DIR"] = self.tmp

    def _run(self, *args):
        # Patch Storage to use a temp dir by monkeypatching the module attribute.
        import resale_cli.cli as climod
        orig = climod.Storage
        tmp = self.tmp

        class TempStorage(orig):
            def __init__(self, data_dir=None):
                super().__init__(data_dir=tmp)

        climod.Storage = TempStorage
        try:
            return main(list(args))
        finally:
            climod.Storage = orig

    def test_add_and_list(self):
        self.assertEqual(self._run("add", "--title", "Widget", "--description", "d", "--condition", "c", "--pricing", "$1"), 0)
        self.assertEqual(self._run("list"), 0)

    def test_draft_and_export(self):
        self._run("add", "--title", "Widget", "--description", "d", "--condition", "c", "--pricing", "$1")
        # Just exercise draft with a bogus id returns error code.
        self.assertEqual(self._run("draft", "--id", "nope"), 1)


if __name__ == "__main__":
    unittest.main()
