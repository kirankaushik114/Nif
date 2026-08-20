"""
News deduplication.

Prevents the same news event from being stored repeatedly.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


class NewsDeduplicator:
    """Generate stable fingerprints for news items."""

    @staticmethod
    def normalize_text(value: Any) -> str:
        if value is None:
            return ""

        text = str(value).lower().strip()

        # Remove URLs.
        text = re.sub(
            r"https?://\S+",
            "",
            text,
        )

        # Keep words/numbers only.
        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text,
        )

        # Collapse whitespace.
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @classmethod
    def fingerprint(
        cls,
        title: str,
        source: str = "",
    ) -> str:

        normalized_title = cls.normalize_text(
            title
        )

        normalized_source = cls.normalize_text(
            source
        )

        raw = (
            f"{normalized_source}|"
            f"{normalized_title}"
        )

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()