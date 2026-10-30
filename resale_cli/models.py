"""Data models for products and listing drafts."""

from dataclasses import dataclass, field, asdict
from typing import Optional
import uuid
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return uuid.uuid4().hex


@dataclass
class ProductRecord:
    """A single product record shared across eBay and Amazon listings."""

    id: str = field(default_factory=_new_id)
    title: str = ""
    description: str = ""
    condition_notes: str = ""
    pricing_hints: str = ""
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def touch(self) -> None:
        self.updated_at = _now_iso()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ProductRecord":
        return cls(**{k: data.get(k, "") for k in cls._fields()})

    @classmethod
    def _fields(cls):
        return [f.name for f in __import__("dataclasses").fields(cls)]


@dataclass
class ListingDraft:
    """A drafted listing for a single marketplace."""

    id: str = field(default_factory=_new_id)
    product_id: str = ""
    platform: str = ""  # "ebay" or "amazon"
    title: str = ""
    description: str = ""
    price: str = ""
    condition: str = ""
    created_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ListingDraft":
        return cls(**{k: data.get(k, "") for k in cls._fields()})

    @classmethod
    def _fields(cls):
        return [f.name for f in __import__("dataclasses").fields(cls)]
