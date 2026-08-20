"""
News Collector.

Normalizes, fingerprints and persistently stores news.
"""

from __future__ import annotations

import logging
from typing import Any

from .deduplicator import NewsDeduplicator
from .news_item import NewsItem
from .news_store import NewsStore


logger = logging.getLogger(__name__)


class NewsCollector:

    def __init__(
        self,
        store: NewsStore | None = None,
        deduplicator: NewsDeduplicator | None = None,
    ) -> None:

        self.store = (
            store
            or NewsStore()
        )

        self.deduplicator = (
            deduplicator
            or NewsDeduplicator()
        )

    # ==========================================================
    # COLLECT
    # ==========================================================

    def collect(
        self,
        item: NewsItem,
    ) -> bool:

        if not item.title:

            logger.warning(
                "Ignoring news item without title."
            )

            return False

        fingerprint = (
            self.deduplicator.fingerprint(
                title=item.title,
                source=item.source,
            )
        )

        # ------------------------------------------------------
        # DUPLICATE
        # ------------------------------------------------------

        if self.store.exists(
            fingerprint
        ):

            logger.debug(
                "Duplicate news ignored: %s",
                item.title,
            )

            return False

        # ------------------------------------------------------
        # STORE
        # ------------------------------------------------------

        saved = self.store.save(
            item,
            fingerprint=fingerprint,
        )

        if saved:

            logger.info(
                "News stored: %s",
                item.title,
            )

        return saved

    # ==========================================================
    # ADD
    # ==========================================================

    def add(
        self,
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
    ) -> bool:

        item = NewsItem.create(

            title=title,

            summary=summary,

            source=source,

            url=url,

            category=category,

            importance=importance,

            country=country,

            company=company,

            symbols=symbols,

            event_type=event_type,

            sentiment=sentiment,

            timestamp=timestamp,

            external_id=external_id,
        )

        return self.collect(
            item
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self) -> dict[str, Any]:

        return {
            "collector": "ready",
            "stored_news": self.store.count(),
        }

    # ==========================================================
    # LATEST
    # ==========================================================

    def latest(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:

        return self.store.latest(
            limit
        )

    # ==========================================================
    # SINCE
    # ==========================================================

    def since(
        self,
        timestamp: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        return self.store.since(
            timestamp,
            limit,
        )