"""
Bank Nifty News Service
=======================

High-level controller for the Phase 2 news system.

Configuration is loaded from ai.config.

Responsibilities:

    configuration
        ↓
    RSS provider
        ↓
    BackgroundNewsCollector
        ↓
    NewsCollector
        ↓
    SQLite

The service does NOT:
- run Ollama
- perform AI analysis
- execute trades
- modify SIC
"""

from __future__ import annotations

from typing import Any

from ai import config

from .background_collector import (
    BackgroundNewsCollector,
)

from .collection_state import (
    NewsCollectionState,
)

from .news_collector import (
    NewsCollector,
)

from .providers.feed_config import (
    RSS_FEEDS,
)

from .providers.rss import (
    RSSNewsProvider,
)


class NewsService:

    def __init__(
        self,
        enabled: bool | None = None,
        interval_seconds: int | None = None,
        max_items_per_feed: int | None = None,
        timeout: int | None = None,
    ) -> None:

        # ------------------------------------------------------
        # Configuration
        #
        # Explicit constructor values override config.py.
        # If omitted, config.py is used.
        # ------------------------------------------------------

        self.enabled = (
            config.NEWS_ENABLED
            if enabled is None
            else bool(enabled)
        )

        self.interval_seconds = max(
            1,
            int(
                config.NEWS_COLLECTION_INTERVAL_SECONDS
                if interval_seconds is None
                else interval_seconds
            ),
        )

        self.max_items_per_feed = max(
            1,
            int(
                config.NEWS_MAX_ITEMS_PER_FEED
                if max_items_per_feed is None
                else max_items_per_feed
            ),
        )

        self.timeout = max(
            5,
            int(
                config.NEWS_REQUEST_TIMEOUT
                if timeout is None
                else timeout
            ),
        )

        # ------------------------------------------------------
        # RSS provider
        # ------------------------------------------------------

        self.provider = RSSNewsProvider(
            feeds=RSS_FEEDS,
            timeout=self.timeout,
            max_items_per_feed=(
                self.max_items_per_feed
            ),
        )

        # ------------------------------------------------------
        # Existing news collector
        # ------------------------------------------------------

        self.collector = NewsCollector()

        # ------------------------------------------------------
        # Persistent checkpoint
        # ------------------------------------------------------

        self.state = NewsCollectionState()

        # ------------------------------------------------------
        # Background collector
        # ------------------------------------------------------

        self.background = (
            BackgroundNewsCollector(
                provider=self.provider,
                collector=self.collector,
                state=self.state,
                interval_seconds=(
                    self.interval_seconds
                ),
            )
        )

    # ==========================================================
    # START
    # ==========================================================

    def start(self) -> bool:

        if not self.enabled:
            return False

        self.background.start()

        return True

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(self) -> None:

        self.background.stop()

    # ==========================================================
    # COLLECT ONCE
    # ==========================================================

    def collect_once(self) -> int:

        if not self.enabled:
            return 0

        return self.background.collect_once()

    # ==========================================================
    # ENABLE
    # ==========================================================

    def enable(self) -> None:

        self.enabled = True

    # ==========================================================
    # DISABLE
    # ==========================================================

    def disable(self) -> None:

        self.enabled = False

        self.background.stop()

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self) -> dict[str, Any]:

        background_status = (
            self.background.status()
        )

        return {

            "news_enabled":
                self.enabled,

            "interval_seconds":
                self.interval_seconds,

            "max_items_per_feed":
                self.max_items_per_feed,

            "timeout":
                self.timeout,

            "provider":
                self.provider.status(),

            "background":
                background_status,

            "stored_news":
                self.collector.store.count(),
        }