"""
Bank Nifty AI - Structured Context Builder
===========================================

Phase 1:

Converts the EXISTING Bank Nifty system data into a structured
context for AI analysis.

Important:
- This file does NOT calculate RSI.
- This file does NOT calculate SIC.
- This file does NOT create trades.
- This file does NOT modify paper trading.
- It only organizes already-calculated information.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


class MarketContextBuilder:
    """
    Build structured market context for the Bank Nifty AI.

    The existing Bank Nifty system remains the source of truth.
    """

    # ==========================================================
    # COMPLETE CONTEXT
    # ==========================================================

    def build(
        self,
        *,
        market: dict[str, Any] | None = None,
        indicators: dict[str, Any] | None = None,
        sic: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
        trades: dict[str, Any] | None = None,
        macro: dict[str, Any] | None = None,
        banks: dict[str, Any] | None = None,
        system: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build the complete structured context.

        All sections are optional because individual data sources
        may temporarily be unavailable.
        """

        return {
            "context_timestamp": datetime.now().isoformat(),

            "market": self._clean(market),

            "indicators": self._clean(indicators),

            "sic": self._clean(sic),

            "options": self._clean(options),

            "paper_trading": self._clean(trades),

            "macro": self._clean(macro),

            "bank_constituents": self._clean(banks),

            "system": self._clean(system),
        }

    # ==========================================================
    # MARKET DATA
    # ==========================================================

    def build_market(
        self,
        *,
        bank_nifty: float | None = None,
        nifty: float | None = None,
        gift_nifty: float | None = None,
        timestamp: str | None = None,
    ) -> dict[str, Any]:
        """
        Build the main Indian market section.
        """

        return self._clean(
            {
                "timestamp": timestamp,
                "bank_nifty": bank_nifty,
                "nifty": nifty,
                "gift_nifty": gift_nifty,
            }
        )

    # ==========================================================
    # GLOBAL / MACRO MARKET
    # ==========================================================

    def build_macro(
        self,
        *,
        crude: float | None = None,
        usd_inr: float | None = None,
        vix: float | None = None,
        us_markets: dict[str, Any] | None = None,
        asian_markets: dict[str, Any] | None = None,
        other: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build macro/global market information.

        These fields will become more important when the
        news and geopolitical collectors are added.
        """

        data: dict[str, Any] = {
            "crude": crude,
            "usd_inr": usd_inr,
            "vix": vix,
            "us_markets": us_markets or {},
            "asian_markets": asian_markets or {},
            "other": other or {},
        }

        return self._clean(data)

    # ==========================================================
    # TECHNICAL INDICATORS
    # ==========================================================

    def build_indicators(
        self,
        *,
        rsi_1m: float | None = None,
        rsi_15m: float | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build technical indicator information.

        RSI values come from the existing indicator engine.
        """

        data: dict[str, Any] = {
            "rsi_1m": rsi_1m,
            "rsi_15m": rsi_15m,
        }

        if extra:
            data.update(extra)

        return self._clean(data)

    # ==========================================================
    # SIC
    # ==========================================================

    def build_sic(
        self,
        *,
        signal: str | None = None,
        conditions: dict[str, Any] | None = None,
        strategy: str | None = None,
    ) -> dict[str, Any]:
        """
        Build SIC information.

        IMPORTANT:
        The AI receives SIC results.
        The AI does NOT calculate or modify SIC.
        """

        return self._clean(
            {
                "signal": signal,
                "strategy": strategy,
                "conditions": conditions or {},
            }
        )

    # ==========================================================
    # OPTIONS
    # ==========================================================

    def build_options(
        self,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build options market information.

        Future fields may include:
        - CE LTP
        - PE LTP
        - OI
        - volume
        - IV
        - PCR
        - strike
        """

        return self._clean(data)

    # ==========================================================
    # PAPER TRADING
    # ==========================================================

    def build_trades(
        self,
        *,
        open_trades: list[dict[str, Any]] | None = None,
        recent_trades: list[dict[str, Any]] | None = None,
        pnl: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build paper-trading information.
        """

        return self._clean(
            {
                "open_trades": open_trades or [],
                "recent_trades": recent_trades or [],
                "pnl": pnl or {},
            }
        )

    # ==========================================================
    # BANK CONSTITUENTS
    # ==========================================================

    def build_banks(
        self,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build Bank Nifty constituent information.

        Later this will contain intelligence for banks such as:
        HDFC Bank
        ICICI Bank
        SBI
        Axis Bank
        Kotak Bank
        IndusInd Bank
        and other current constituents.
        """

        return self._clean(data)

    # ==========================================================
    # SYSTEM STATUS
    # ==========================================================

    def build_system(
        self,
        *,
        market_session: str | None = None,
        data_status: str | None = None,
        ai_status: str | None = None,
        data_timestamp: str | None = None,
    ) -> dict[str, Any]:
        """
        Build system/runtime information.
        """

        return self._clean(
            {
                "market_session": market_session,
                "data_status": data_status,
                "ai_status": ai_status,
                "data_timestamp": data_timestamp,
            }
        )

    # ==========================================================
    # CLEAN DATA
    # ==========================================================

    @staticmethod
    def _clean(
        data: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Remove None values while preserving valid values such as:
        0
        False
        empty lists
        empty dictionaries
        """

        if not data:
            return {}

        return {
            key: value
            for key, value in data.items()
            if value is not None
        }