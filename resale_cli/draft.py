"""Draft marketplace listings from a product record."""

from typing import List

from .models import ProductRecord, ListingDraft
from .llm import LLMEnhancer


PLATFORMS = ["ebay", "amazon"]


def draft_listings(
    product: ProductRecord,
    enhancer: LLMEnhancer,
    platforms: List[str] = None,
) -> List[ListingDraft]:
    """Create a listing draft for each platform from one product record."""
    if platforms is None:
        platforms = PLATFORMS

    drafts: List[ListingDraft] = []
    for platform in platforms:
        title, description = enhancer.enhance_for_platform(
            platform,
            product.title,
            product.description,
            product.condition_notes,
            product.pricing_hints,
        )
        drafts.append(
            ListingDraft(
                product_id=product.id,
                platform=platform,
                title=title,
                description=description,
                price=product.pricing_hints,
                condition=product.condition_notes,
            )
        )
    return drafts
