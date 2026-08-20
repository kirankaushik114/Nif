"""
RSS News Provider
=================

Reads RSS and Atom feeds and converts entries into NewsItem objects.

The provider is independent of:
- SQLite
- RAG
- Ollama
- Bank Nifty AI

Responsibilities:
    RSS/Atom
       ↓
    HTTP fetch
       ↓
    XML parsing
       ↓
    Timestamp normalization
       ↓
    NewsItem
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Iterable

import requests

from ..news_item import NewsItem
from .base import NewsProvider


logger = logging.getLogger(__name__)


class RSSNewsProvider(NewsProvider):

    name = "rss"

    def __init__(
        self,
        feeds: list[dict] | None = None,
        timeout: int = 15,
        max_items_per_feed: int = 25,
    ) -> None:

        self.feeds = feeds or []

        self.timeout = max(
            5,
            int(timeout),
        )

        # Safety limit.
        #
        # Prevents the first collection cycle from
        # importing hundreds of historical RSS entries.
        self.max_items_per_feed = max(
            1,
            int(max_items_per_feed),
        )

    # ==========================================================
    # FETCH ALL FEEDS
    # ==========================================================

    def fetch(
        self,
        since: str | None = None,
    ) -> Iterable[NewsItem]:

        results: list[NewsItem] = []

        for feed in self.feeds:

            try:

                items = self._fetch_feed(
                    feed,
                    since,
                )

                results.extend(
                    items
                )

            except Exception as exc:

                logger.warning(
                    "RSS feed failed: %s - %s",
                    feed.get(
                        "name",
                        "Unknown",
                    ),
                    exc,
                )

        return results

    # ==========================================================
    # FETCH SINGLE FEED
    # ==========================================================

    def _fetch_feed(
        self,
        feed: dict,
        since: str | None,
    ) -> list[NewsItem]:

        url = feed.get(
            "url",
            "",
        )

        if not url:
            return []

        response = requests.get(
            url,
            timeout=self.timeout,
            headers={
                "User-Agent":
                    "BankNiftyAI/1.0"
            },
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        results: list[NewsItem] = []

        # ======================================================
        # STANDARD RSS
        # ======================================================

        rss_elements = root.findall(
            ".//item"
        )

        # Safety limit per feed.
        rss_elements = rss_elements[
            :self.max_items_per_feed
        ]

        for element in rss_elements:

            item = self._parse_rss_item(
                element,
                feed,
            )

            if item is None:
                continue

            # --------------------------------------------------
            # Time-aware filtering.
            # --------------------------------------------------

            if not self._after_timestamp(
                item.timestamp,
                since,
            ):

                continue

            results.append(
                item
            )

        # ======================================================
        # ATOM FALLBACK
        # ======================================================

        if not results:

            atom_items = root.findall(
                ".//{http://www.w3.org/2005/Atom}entry"
            )

            atom_items = atom_items[
                :self.max_items_per_feed
            ]

            for element in atom_items:

                item = self._parse_atom_item(
                    element,
                    feed,
                )

                if item is None:
                    continue

                if not self._after_timestamp(
                    item.timestamp,
                    since,
                ):

                    continue

                results.append(
                    item
                )

        return results

    # ==========================================================
    # RSS PARSER
    # ==========================================================

    def _parse_rss_item(
        self,
        element: ET.Element,
        feed: dict,
    ) -> NewsItem | None:

        title = self._text(
            element,
            "title",
        )

        if not title:
            return None

        description = self._text(
            element,
            "description",
        )

        link = self._text(
            element,
            "link",
        )

        guid = self._text(
            element,
            "guid",
        )

        published = (
            self._text(
                element,
                "pubDate",
            )
            or self._text(
                element,
                "published",
            )
            or self._text(
                element,
                "updated",
            )
        )

        if published:

            timestamp = (
                self._parse_datetime(
                    published
                )
            )

        else:

            timestamp = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

        return NewsItem.create(

            title=title,

            summary=description or "",

            source=feed.get(
                "name",
                "RSS",
            ),

            url=link or "",

            category=feed.get(
                "category",
                "general",
            ),

            importance=float(
                feed.get(
                    "importance",
                    0.0,
                )
            ),

            country=feed.get(
                "country",
                "",
            ),

            company=feed.get(
                "company",
                "",
            ),

            symbols=feed.get(
                "symbols",
                [],
            ),

            event_type=feed.get(
                "event_type",
                "",
            ),

            sentiment=feed.get(
                "sentiment",
                "UNKNOWN",
            ),

            timestamp=timestamp,

            external_id=guid or "",
        )

    # ==========================================================
    # ATOM PARSER
    # ==========================================================

    def _parse_atom_item(
        self,
        element: ET.Element,
        feed: dict,
    ) -> NewsItem | None:

        namespace = {
            "atom":
                "http://www.w3.org/2005/Atom"
        }

        title_element = element.find(
            "atom:title",
            namespace,
        )

        if title_element is None:
            return None

        title = (
            title_element.text
            or ""
        ).strip()

        if not title:
            return None

        summary_element = element.find(
            "atom:summary",
            namespace,
        )

        if summary_element is None:

            summary_element = element.find(
                "atom:content",
                namespace,
            )

        summary = ""

        if summary_element is not None:

            summary = (
                summary_element.text
                or ""
            ).strip()

        published_element = element.find(
            "atom:published",
            namespace,
        )

        if published_element is None:

            published_element = element.find(
                "atom:updated",
                namespace,
            )

        published = None

        if published_element is not None:

            published = (
                published_element.text
            )

        if published:

            timestamp = (
                self._parse_datetime(
                    published
                )
            )

        else:

            timestamp = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

        link = ""

        # ------------------------------------------------------
        # Find alternate Atom link.
        # ------------------------------------------------------

        for link_element in element.findall(
            "atom:link",
            namespace,
        ):

            relation = link_element.attrib.get(
                "rel",
                "alternate",
            )

            if relation in (
                "",
                "alternate",
            ):

                link = link_element.attrib.get(
                    "href",
                    "",
                )

                if link:
                    break

        id_element = element.find(
            "atom:id",
            namespace,
        )

        external_id = ""

        if id_element is not None:

            external_id = (
                id_element.text
                or ""
            ).strip()

        return NewsItem.create(

            title=title,

            summary=summary,

            source=feed.get(
                "name",
                "RSS",
            ),

            url=link,

            category=feed.get(
                "category",
                "general",
            ),

            importance=float(
                feed.get(
                    "importance",
                    0.0,
                )
            ),

            country=feed.get(
                "country",
                "",
            ),

            company=feed.get(
                "company",
                "",
            ),

            symbols=feed.get(
                "symbols",
                [],
            ),

            event_type=feed.get(
                "event_type",
                "",
            ),

            sentiment=feed.get(
                "sentiment",
                "UNKNOWN",
            ),

            timestamp=timestamp,

            external_id=external_id,
        )

    # ==========================================================
    # GET XML TEXT
    # ==========================================================

    @staticmethod
    def _text(
        element: ET.Element,
        tag: str,
    ) -> str:

        child = element.find(
            tag
        )

        if child is None:
            return ""

        return (
            child.text
            or ""
        ).strip()

    # ==========================================================
    # PARSE DATETIME
    # ==========================================================

    @staticmethod
    def _parse_datetime(
        value: str,
    ) -> str:

        value = value.strip()

        if not value:

            return (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

        # ------------------------------------------------------
        # RFC 2822
        #
        # Common RSS format:
        #
        # Thu, 20 Aug 2026 11:43:39 GMT
        # ------------------------------------------------------

        try:

            dt = parsedate_to_datetime(
                value
            )

            if dt.tzinfo is None:

                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            return dt.astimezone(
                timezone.utc
            ).isoformat()

        except (
            TypeError,
            ValueError,
        ):

            pass

        # ------------------------------------------------------
        # ISO 8601
        # ------------------------------------------------------

        try:

            normalized = value

            if normalized.endswith(
                "Z"
            ):

                normalized = (
                    normalized[:-1]
                    + "+00:00"
                )

            dt = datetime.fromisoformat(
                normalized
            )

            if dt.tzinfo is None:

                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            return dt.astimezone(
                timezone.utc
            ).isoformat()

        except (
            TypeError,
            ValueError,
        ):

            logger.debug(
                "Could not parse RSS timestamp: %s",
                value,
            )

            return (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

    # ==========================================================
    # TIMESTAMP FILTER
    # ==========================================================

    @staticmethod
    def _after_timestamp(
        timestamp: str,
        since: str | None,
    ) -> bool:

        # No checkpoint means this is the initial fetch.
        if not since:
            return True

        try:

            current = (
                datetime.fromisoformat(
                    timestamp.replace(
                        "Z",
                        "+00:00",
                    )
                )
            )

            previous = (
                datetime.fromisoformat(
                    since.replace(
                        "Z",
                        "+00:00",
                    )
                )
            )

            if current.tzinfo is None:

                current = current.replace(
                    tzinfo=timezone.utc
                )

            if previous.tzinfo is None:

                previous = previous.replace(
                    tzinfo=timezone.utc
                )

            return current > previous

        except (
            TypeError,
            ValueError,
        ):

            # If the timestamp cannot be compared,
            # allow the item through rather than silently
            # dropping potentially important news.
            return True

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self) -> dict:

        return {

            "provider":
                self.name,

            "status":
                "ready",

            "feeds":
                len(self.feeds),

            "timeout":
                self.timeout,

            "max_items_per_feed":
                self.max_items_per_feed,
        }