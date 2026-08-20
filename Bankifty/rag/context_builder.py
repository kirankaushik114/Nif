"""
Bank Nifty RAG Context Builder
==============================

Builds a compact, time-aware context from stored news.

The builder does NOT call Ollama.

Its job is only:

    News database
        ↓
    Retrieve relevant events
        ↓
    Rank events
        ↓
    Build compact AI context
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from news.news_retriever import NewsRetriever


class RAGContextBuilder:

    def __init__(
        self,
        retriever: NewsRetriever | None = None,
    ) -> None:

        self.retriever = (
            retriever
            or NewsRetriever()
        )

    # ==========================================================
    # BUILD MARKET CONTEXT
    # ==========================================================

    def build(
        self,
        *,
        bank_nifty: float | None = None,
        gift_nifty: float | None = None,
        rsi_1m: float | None = None,
        rsi_15m: float | None = None,
        sic_signal: str = "NEUTRAL",
        minutes: int = 15,
        max_news: int = 10,
    ) -> dict[str, Any]:

        # ------------------------------------------------------
        # RETRIEVE RECENT NEWS
        # ------------------------------------------------------

        news = self.retriever.last_minutes(
            minutes,
            limit=max_news * 3,
        )

        # ------------------------------------------------------
        # RANK
        # ------------------------------------------------------

        ranked_news = self._rank_news(
            news
        )

        ranked_news = ranked_news[
            :max_news
        ]

        # ------------------------------------------------------
        # BUILD NEWS CONTEXT
        # ------------------------------------------------------

        news_context = []

        for item in ranked_news:

            news_context.append(
                self._normalize_news(
                    item
                )
            )

        # ------------------------------------------------------
        # FINAL CONTEXT
        # ------------------------------------------------------

        return {

            "generated_at": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),

            "window_minutes": minutes,

            "market": {

                "bank_nifty":
                    bank_nifty,

                "gift_nifty":
                    gift_nifty,
            },

            "indicators": {

                "rsi_1m":
                    rsi_1m,

                "rsi_15m":
                    rsi_15m,
            },

            "sic": {

                "signal":
                    sic_signal,
            },

            "news": news_context,

            "news_count":
                len(news_context),
        }

    # ==========================================================
    # RANK NEWS
    # ==========================================================

    @staticmethod
    def _rank_news(
        news: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        def score(
            item: dict[str, Any],
        ) -> tuple[float, str]:

            importance = float(
                item.get(
                    "importance",
                    0.0,
                )
                or 0.0
            )

            timestamp = str(
                item.get(
                    "timestamp",
                    "",
                )
            )

            return (
                importance,
                timestamp,
            )

        return sorted(
            news,
            key=score,
            reverse=True,
        )

    # ==========================================================
    # NORMALIZE NEWS
    # ==========================================================

    @staticmethod
    def _normalize_news(
        item: dict[str, Any],
    ) -> dict[str, Any]:

        return {

            "timestamp":
                item.get(
                    "timestamp"
                ),

            "collected_at":
                item.get(
                    "collected_at"
                ),

            "title":
                item.get(
                    "title",
                    "",
                ),

            "summary":
                item.get(
                    "summary",
                    "",
                ),

            "source":
                item.get(
                    "source",
                    "",
                ),

            "category":
                item.get(
                    "category",
                    "general",
                ),

            "importance":
                item.get(
                    "importance",
                    0.0,
                ),

            "country":
                item.get(
                    "country",
                    "",
                ),

            "company":
                item.get(
                    "company",
                    "",
                ),

            "symbols":
                item.get(
                    "symbols",
                    [],
                ),

            "event_type":
                item.get(
                    "event_type",
                    "",
                ),

            "sentiment":
                item.get(
                    "sentiment",
                    "UNKNOWN",
                ),
        }

    # ==========================================================
    # TEXT FORMAT
    # ==========================================================

    def build_text(
        self,
        context: dict[str, Any],
    ) -> str:
        """
        Convert structured RAG context into a compact text
        representation for an AI model.
        """

        lines = []

        market = context.get(
            "market",
            {},
        )

        indicators = context.get(
            "indicators",
            {},
        )

        sic = context.get(
            "sic",
            {},
        )

        lines.append(
            "BANK NIFTY MARKET CONTEXT"
        )

        lines.append(
            f"Bank Nifty: "
            f"{market.get('bank_nifty')}"
        )

        lines.append(
            f"Gift Nifty: "
            f"{market.get('gift_nifty')}"
        )

        lines.append(
            f"RSI 1M: "
            f"{indicators.get('rsi_1m')}"
        )

        lines.append(
            f"RSI 15M: "
            f"{indicators.get('rsi_15m')}"
        )

        lines.append(
            f"SIC: "
            f"{sic.get('signal')}"
        )

        lines.append("")

        lines.append(
            "RECENT NEWS"
        )

        news = context.get(
            "news",
            [],
        )

        if not news:

            lines.append(
                "No relevant news in "
                f"the last "
                f"{context.get('window_minutes')} "
                "minutes."
            )

        else:

            for index, item in enumerate(
                news,
                start=1,
            ):

                lines.append(
                    f"{index}. "
                    f"{item.get('title', '')}"
                )

                if item.get(
                    "summary"
                ):

                    lines.append(
                        "   "
                        + str(
                            item.get(
                                "summary"
                            )
                        )
                    )

                lines.append(
                    "   Category: "
                    f"{item.get('category')}"
                )

                lines.append(
                    "   Importance: "
                    f"{item.get('importance')}"
                )

                lines.append(
                    "   Sentiment: "
                    f"{item.get('sentiment')}"
                )

        return "\n".join(
            lines
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "rag": "ready",

            "retriever":
                self.retriever.status(),
        }