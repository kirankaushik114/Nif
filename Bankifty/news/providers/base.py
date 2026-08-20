"""
Base News Provider
==================

Provider-neutral interface.

Every real news provider should return normalized
NewsItem objects to the existing collector.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from ..news_item import NewsItem


class NewsProvider(ABC):
    """
    Base interface for all news providers.
    """

    name = "unknown"

    @abstractmethod
    def fetch(
        self,
        since: str | None = None,
    ) -> Iterable[NewsItem]:
        """
        Fetch news after the supplied timestamp.

        Parameters
        ----------
        since:
            ISO timestamp of the last successful collection.

        Returns
        -------
        Iterable[NewsItem]
        """

        raise NotImplementedError

    def status(self) -> dict:
        return {
            "provider": self.name,
            "status": "ready",
        }