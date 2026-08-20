"""
Persistent SQLite news store.

Stores both:
- original event/publication timestamp
- collection timestamp
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .news_item import NewsItem


class NewsStore:

    def __init__(
        self,
        db_path: str | Path = "data/news.db",
    ) -> None:

        self.db_path = Path(
            db_path
        )

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    # ==========================================================
    # INITIALIZE
    # ==========================================================

    def _initialize(self) -> None:

        with sqlite3.connect(
            self.db_path
        ) as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    timestamp TEXT NOT NULL,

                    collected_at TEXT NOT NULL,

                    title TEXT NOT NULL,

                    summary TEXT,

                    source TEXT,

                    url TEXT,

                    external_id TEXT,

                    fingerprint TEXT UNIQUE,

                    category TEXT,

                    importance REAL,

                    country TEXT,

                    company TEXT,

                    symbols TEXT,

                    event_type TEXT,

                    sentiment TEXT
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_news_timestamp
                ON news(timestamp)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_news_collected_at
                ON news(collected_at)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_news_category
                ON news(category)
                """
            )

            connection.commit()

    # ==========================================================
    # SAVE
    # ==========================================================

    def save(
        self,
        item: NewsItem,
        fingerprint: str | None = None,
    ) -> bool:

        symbols = json.dumps(
            item.symbols or []
        )

        with sqlite3.connect(
            self.db_path
        ) as connection:

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO news (
                    timestamp,
                    collected_at,
                    title,
                    summary,
                    source,
                    url,
                    external_id,
                    fingerprint,
                    category,
                    importance,
                    country,
                    company,
                    symbols,
                    event_type,
                    sentiment
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?
                )
                """,
                (
                    item.timestamp,
                    item.collected_at,
                    item.title,
                    item.summary,
                    item.source,
                    item.url,
                    item.external_id,
                    fingerprint,
                    item.category,
                    item.importance,
                    item.country,
                    item.company,
                    symbols,
                    item.event_type,
                    item.sentiment,
                ),
            )

            connection.commit()

            return cursor.rowcount > 0

    # ==========================================================
    # LATEST
    # ==========================================================

    def latest(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:

        with sqlite3.connect(
            self.db_path
        ) as connection:

            connection.row_factory = (
                sqlite3.Row
            )

            rows = connection.execute(
                """
                SELECT *
                FROM news
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            self._row_to_dict(row)
            for row in rows
        ]

    # ==========================================================
    # TIME WINDOW
    # ==========================================================

    def since(
        self,
        timestamp: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        with sqlite3.connect(
            self.db_path
        ) as connection:

            connection.row_factory = (
                sqlite3.Row
            )

            rows = connection.execute(
                """
                SELECT *
                FROM news
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
                LIMIT ?
                """,
                (
                    timestamp,
                    limit,
                ),
            ).fetchall()

        return [
            self._row_to_dict(row)
            for row in rows
        ]

    # ==========================================================
    # FINGERPRINT CHECK
    # ==========================================================

    def exists(
        self,
        fingerprint: str,
    ) -> bool:

        with sqlite3.connect(
            self.db_path
        ) as connection:

            row = connection.execute(
                """
                SELECT 1
                FROM news
                WHERE fingerprint = ?
                LIMIT 1
                """,
                (fingerprint,),
            ).fetchone()

        return row is not None

    # ==========================================================
    # COUNT
    # ==========================================================

    def count(self) -> int:

        with sqlite3.connect(
            self.db_path
        ) as connection:

            row = connection.execute(
                "SELECT COUNT(*) FROM news"
            ).fetchone()

        return int(row[0])

    # ==========================================================
    # ROW CONVERSION
    # ==========================================================

    @staticmethod
    def _row_to_dict(
        row: sqlite3.Row,
    ) -> dict[str, Any]:

        item = dict(row)

        try:

            item["symbols"] = json.loads(
                item.get(
                    "symbols"
                ) or "[]"
            )

        except json.JSONDecodeError:

            item["symbols"] = []

        return item

    # ==========================================================
    # CLEAR
    # ==========================================================

    def clear(self) -> None:

        with sqlite3.connect(
            self.db_path
        ) as connection:

            connection.execute(
                "DELETE FROM news"
            )

            connection.commit()