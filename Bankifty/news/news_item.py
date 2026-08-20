"""
News item data model.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class NewsItem:

    # Original publication/event time.
    timestamp: str

    title: str

    summary: str = ""

    source: str = ""

    url: str = ""

    category: str = "general"

    importance: float = 0.0

    country: str = ""

    company: str = ""

    symbols: list[str] | None = None

    event_type: str = ""

    sentiment: str = "UNKNOWN"

    # Time when our system captured the item.
    collected_at: str = ""

    # Optional stable provider ID.
    external_id: str = ""

    def __post_init__(self) -> None:

        if self.symbols is None:
            self.symbols = []

        if not self.collected_at:

            self.collected_at = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

    @classmethod
    def create(
        cls,
        title: str,
        summary: str = "",
        source: str = "",
        url: str = "",
        category: str = "general",
        importance: float = 0.0,
        country: str = "",
        company: str = "",
        symbols: list[str] | None = None,
        event_type: str = "",
        sentiment: str = "UNKNOWN",
        timestamp: str | None = None,
        external_id: str = "",
    ) -> "NewsItem":

        now = datetime.now(
            timezone.utc
        ).isoformat()

        return cls(
            timestamp=timestamp or now,
            title=title.strip(),
            summary=summary.strip(),
            source=source.strip(),
            url=url.strip(),
            category=category.strip(),
            importance=float(
                importance
            ),
            country=country.strip(),
            company=company.strip(),
            symbols=symbols or [],
            event_type=event_type.strip(),
            sentiment=sentiment.strip().upper(),
            collected_at=now,
            external_id=external_id.strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)