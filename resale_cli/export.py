"""CSV export for listing drafts."""

import csv
import os
from typing import List

from .models import ListingDraft


FIELDS = ["id", "product_id", "platform", "title", "description", "price", "condition", "created_at"]


def export_csv(drafts: List[ListingDraft], path: str) -> str:
    """Write listing drafts to a CSV file. Returns the path written."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for draft in drafts:
            writer.writerow(draft.to_dict())
    return path
