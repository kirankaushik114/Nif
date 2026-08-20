"""
Time-aware News Retriever
==========================

Retrieves stored news using event/publication time.

This is the first retrieval layer for Phase 2 RAG.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .news_store import NewsStore


class NewsRetriever:

    def __init__(
        self,
        store: NewsStore | None = None,
    ) -> None:

        self.store = (
            store
            or NewsStore()
        )

    # ==========================================================
    # SINCE TIMESTAMP
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

    # ==========================================================
    # LAST N MINUTES
    # ==========================================================

    def last_minutes(
        self,
        minutes: int,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        if minutes <= 0:
            return []

        cutoff = (
            datetime.now(
                timezone.utc
            )
            - timedelta(
                minutes=minutes
            )
        )

        return self.since(
            cutoff.isoformat(),
            limit,
        )

    # ==========================================================
    # LAST N HOURS
    # ==========================================================

    def last_hours(
        self,
        hours: int,
        limit: int = 500,
    ) -> list[dict[str, Any]]:

        if hours <= 0:
            return []

        cutoff = (
            datetime.now(
                timezone.utc
            )
            - timedelta(
                hours=hours
            )
        )

        return self.since(
            cutoff.isoformat(),
            limit,
        )

    # ==========================================================
    # RELEVANT SYMBOL
    # ==========================================================

    def for_symbol(
        self,
        symbol: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        symbol = symbol.strip().upper()

        if not symbol:
            return []

        items = self.store.latest(
            limit=500
        )

        results = []

        for item in items:

            symbols = [
                str(x).upper()
                for x in item.get(
                    "symbols",
                    [],
                )
            ]

            if symbol in symbols:

                results.append(item)

                if len(results) >= limit:
                    break

        return results

    # ==========================================================
    # CATEGORY
    # ==========================================================

    def for_category(
        self,
        category: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        category = (
            category
            .strip()
            .lower()
        )

        if not category:
            return []

        items = self.store.latest(
            limit=500
        )

        results = []

        for item in items:

            item_category = (
                str(
                    item.get(
                        "category",
                        "",
                    )
                )
                .strip()
                .lower()
            )

            if item_category == category:

                results.append(item)

                if len(results) >= limit:
                    break

        return results

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self) -> dict[str, Any]:

        return {
            "retriever": "ready",
            "stored_news": self.store.count(),
        }