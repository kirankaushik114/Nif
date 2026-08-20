"""
News Collection State
=====================

Maintains two independent checkpoints:

last_poll_time
    When the provider was last successfully contacted.

last_event_timestamp
    Timestamp of the newest actual news event processed.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class NewsCollectionState:

    def __init__(
        self,
        path: str | Path = "data/news_collection_state.json",
    ) -> None:

        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # DEFAULT
    # ==========================================================

    @staticmethod
    def _default() -> dict[str, Any]:

        return {
            "last_poll_time": None,
            "last_event_timestamp": None,
            "updated_at": None,
        }

    # ==========================================================
    # LOAD
    # ==========================================================

    def load(self) -> dict[str, Any]:

        if not self.path.exists():
            return self._default()

        try:

            with self.path.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if not isinstance(data, dict):
                return self._default()

            # Backward compatibility
            old_timestamp = data.get(
                "last_collection_time"
            )

            if (
                data.get("last_poll_time") is None
                and old_timestamp
            ):
                data["last_poll_time"] = (
                    old_timestamp
                )

            if (
                data.get("last_event_timestamp") is None
                and old_timestamp
            ):
                data["last_event_timestamp"] = (
                    old_timestamp
                )

            data.setdefault(
                "last_poll_time",
                None,
            )

            data.setdefault(
                "last_event_timestamp",
                None,
            )

            data.setdefault(
                "updated_at",
                None,
            )

            return data

        except (
            OSError,
            json.JSONDecodeError,
        ):

            return self._default()

    # ==========================================================
    # SAVE
    # ==========================================================

    def save(
        self,
        *,
        last_poll_time: str | None = None,
        last_event_timestamp: str | None = None,
    ) -> None:

        current = self.load()

        if last_poll_time is not None:

            current["last_poll_time"] = (
                last_poll_time
            )

        if last_event_timestamp is not None:

            current["last_event_timestamp"] = (
                last_event_timestamp
            )

        current["updated_at"] = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        self._write(current)

    # ==========================================================
    # WRITE
    # ==========================================================

    def _write(
        self,
        data: dict[str, Any],
    ) -> None:

        temporary = self.path.with_suffix(
            ".tmp"
        )

        with temporary.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
            )

        temporary.replace(
            self.path
        )

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(self) -> None:

        self._write(
            self._default()
        )

    # ==========================================================
    # LAST POLL
    # ==========================================================

    def last_poll_time(self) -> str | None:

        return self.load().get(
            "last_poll_time"
        )

    # ==========================================================
    # LAST EVENT
    # ==========================================================

    def last_event_timestamp(self) -> str | None:

        return self.load().get(
            "last_event_timestamp"
        )

    # ==========================================================
    # MARK POLL
    # ==========================================================

    def mark_poll(
        self,
        poll_time: str | None = None,
    ) -> None:

        if poll_time is None:

            poll_time = datetime.now(
                timezone.utc
            ).isoformat()

        self.save(
            last_poll_time=poll_time
        )

    # ==========================================================
    # MARK EVENT
    # ==========================================================

    def mark_event(
        self,
        event_timestamp: str,
    ) -> None:

        self.save(
            last_event_timestamp=(
                event_timestamp
            )
        )