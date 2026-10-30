"""Local JSON storage for products and listing drafts."""

import json
import os
from typing import List, Optional

from .models import ProductRecord, ListingDraft


class Storage:
    """Simple local-first JSON storage."""

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir
        self.products_path = os.path.join(data_dir, "products.json")
        self.drafts_path = os.path.join(data_dir, "listings.json")
        os.makedirs(data_dir, exist_ok=True)

    # -- products -----------------------------------------------------
    def load_products(self) -> List[ProductRecord]:
        if not os.path.exists(self.products_path):
            return []
        try:
            with open(self.products_path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return []
        return [ProductRecord.from_dict(item) for item in raw]

    def save_products(self, products: List[ProductRecord]) -> None:
        with open(self.products_path, "w", encoding="utf-8") as fh:
            json.dump([p.to_dict() for p in products], fh, indent=2)

    def add_product(self, product: ProductRecord) -> ProductRecord:
        products = self.load_products()
        products.append(product)
        self.save_products(products)
        return product

    def update_product(self, product: ProductRecord) -> bool:
        products = self.load_products()
        for i, p in enumerate(products):
            if p.id == product.id:
                products[i] = product
                self.save_products(products)
                return True
        return False

    def delete_product(self, product_id: str) -> bool:
        products = self.load_products()
        filtered = [p for p in products if p.id != product_id]
        if len(filtered) == len(products):
            return False
        self.save_products(filtered)
        # remove drafts tied to this product
        self.delete_drafts_for_product(product_id)
        return True

    def get_product(self, product_id: str) -> Optional[ProductRecord]:
        for p in self.load_products():
            if p.id == product_id:
                return p
        return None

    # -- drafts -------------------------------------------------------
    def load_drafts(self) -> List[ListingDraft]:
        if not os.path.exists(self.drafts_path):
            return []
        try:
            with open(self.drafts_path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return []
        return [ListingDraft.from_dict(item) for item in raw]

    def save_drafts(self, drafts: List[ListingDraft]) -> None:
        with open(self.drafts_path, "w", encoding="utf-8") as fh:
            json.dump([d.to_dict() for d in drafts], fh, indent=2)

    def add_draft(self, draft: ListingDraft) -> ListingDraft:
        drafts = self.load_drafts()
        drafts.append(draft)
        self.save_drafts(drafts)
        return draft

    def delete_drafts_for_product(self, product_id: str) -> None:
        drafts = self.load_drafts()
        drafts = [d for d in drafts if d.product_id != product_id]
        self.save_drafts(drafts)
