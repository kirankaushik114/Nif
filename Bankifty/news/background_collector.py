"""
Background News Collector
==========================

Runs the configured NewsProvider periodically.

Checkpoint model:

    last_poll_time
        =
    provider was successfully contacted

    last_event_timestamp
        =
    newest actual news event processed

The event checkpoint is NOT advanced when no news is returned.
"""

from __future__ import annotations

import logging
import threading

from datetime import (
    datetime,
    timezone,
)

from typing import Iterable

from .collection_state import (
    NewsCollectionState,
)

from .news_collector import (
    NewsCollector,
)

from .news_item import (
    NewsItem,
)

from .providers.base import (
    NewsProvider,
)


logger = logging.getLogger(
    __name__
)


class BackgroundNewsCollector:

    def __init__(
        self,
        provider: NewsProvider | None = None,
        collector: NewsCollector | None = None,
        state: NewsCollectionState | None = None,
        interval_seconds: int = 900,
    ) -> None:

        self.provider = provider

        self.collector = (
            collector
            or NewsCollector()
        )

        self.state = (
            state
            or NewsCollectionState()
        )

        self.interval_seconds = max(
            1,
            int(interval_seconds),
        )

        self._thread = None

        self._stop_event = (
            threading.Event()
        )

        self._running = False

        self.last_run = None

        self.last_fetched_count = 0

        self.last_saved_count = 0

        self.last_event_timestamp = None

        self.last_error = None

    # ==========================================================
    # COLLECT ONCE
    # ==========================================================

    def collect_once(self) -> int:

        if self.provider is None:

            self.last_error = (
                "No news provider configured."
            )

            logger.warning(
                self.last_error
            )

            return 0

        since = (
            self.state.last_event_timestamp()
        )

        poll_time = datetime.now(
            timezone.utc
        ).isoformat()

        logger.info(
            "Fetching news since: %s",
            since,
        )

        try:

            items: Iterable[NewsItem] = (
                self.provider.fetch(
                    since
                )
            )

            fetched = 0
            saved = 0

            newest_event = since

            for item in items:

                fetched += 1

                if self.collector.collect(
                    item
                ):

                    saved += 1

                if self._is_newer_timestamp(
                    item.timestamp,
                    newest_event,
                ):

                    newest_event = (
                        item.timestamp
                    )

            # --------------------------------------------------
            # Provider completed successfully.
            # --------------------------------------------------

            self.state.mark_poll(
                poll_time
            )

            # --------------------------------------------------
            # ONLY actual news events can advance the event
            # checkpoint.
            # --------------------------------------------------

            if (
                newest_event
                and newest_event != since
            ):

                self.state.mark_event(
                    newest_event
                )

            self.last_run = poll_time

            self.last_fetched_count = (
                fetched
            )

            self.last_saved_count = (
                saved
            )

            self.last_event_timestamp = (
                newest_event
            )

            self.last_error = None

            logger.info(
                "News collection complete: "
                "fetched=%s saved=%s event=%s",
                fetched,
                saved,
                newest_event,
            )

            return saved

        except Exception as exc:

            self.last_error = str(
                exc
            )

            logger.exception(
                "News collection failed."
            )

            # Do not advance either checkpoint.
            return 0

    # ==========================================================
    # START
    # ==========================================================

    def start(self) -> None:

        if self._running:
            return

        self._stop_event.clear()

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            name="BankNiftyNewsCollector",
            daemon=True,
        )

        self._thread.start()

        logger.info(
            "Background news collector started."
        )

    # ==========================================================
    # RUN
    # ==========================================================

    def _run(self) -> None:

        while not self._stop_event.is_set():

            self.collect_once()

            self._stop_event.wait(
                self.interval_seconds
            )

        self._running = False

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(
        self,
        timeout: float = 5.0,
    ) -> None:

        self._stop_event.set()

        if (
            self._thread is not None
            and self._thread.is_alive()
        ):

            self._thread.join(
                timeout=timeout
            )

        self._running = False

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self) -> dict:

        provider_status = None

        if self.provider is not None:

            provider_status = (
                self.provider.status()
            )

        state = self.state.load()

        return {

            "running":
                self._running,

            "interval_seconds":
                self.interval_seconds,

            "provider":
                provider_status,

            "last_poll_time":
                state.get(
                    "last_poll_time"
                ),

            "last_event_timestamp":
                state.get(
                    "last_event_timestamp"
                ),

            "last_run":
                self.last_run,

            "last_fetched_count":
                self.last_fetched_count,

            "last_saved_count":
                self.last_saved_count,

            "last_error":
                self.last_error,

            "stored_news":
                self.collector.store.count(),
        }

    # ==========================================================
    # TIMESTAMP COMPARISON
    # ==========================================================

    @staticmethod
    def _is_newer_timestamp(
        current: str | None,
        previous: str | None,
    ) -> bool:

        if not current:
            return False

        if not previous:
            return True

        try:

            current_dt = datetime.fromisoformat(
                current.replace(
                    "Z",
                    "+00:00",
                )
            )

            previous_dt = datetime.fromisoformat(
                previous.replace(
                    "Z",
                    "+00:00",
                )
            )

            if current_dt.tzinfo is None:

                current_dt = current_dt.replace(
                    tzinfo=timezone.utc
                )

            if previous_dt.tzinfo is None:

                previous_dt = previous_dt.replace(
                    tzinfo=timezone.utc
                )

            return current_dt > previous_dt

        except (
            TypeError,
            ValueError,
        ):

            return False