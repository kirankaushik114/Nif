"""
Bank Nifty AI Service
=====================

Phase 1 AI orchestration layer.

Connects:

    Market Context
          ↓
    Context Builder
          ↓
    Ollama Analyzer
          ↓
    Persistent AI State

Important:
- Does NOT create trades.
- Does NOT modify SIC.
- Does NOT control PaperTradeManager.
- AI failure must not stop the main system.
"""

from __future__ import annotations

import logging
from typing import Any

from .analyzer import BankNiftyAIAnalyzer
from .context_builder import MarketContextBuilder
from .state import AIState


logger = logging.getLogger(__name__)


class BankNiftyAIService:
    """
    Main Phase 1 AI service.

    This class provides one simple interface for the existing
    Bank Nifty monitor to send market information to AI.
    """

    def __init__(
        self,
        analyzer: BankNiftyAIAnalyzer | None = None,
        context_builder: MarketContextBuilder | None = None,
        state: AIState | None = None,
    ) -> None:

        self.analyzer = (
            analyzer
            or BankNiftyAIAnalyzer()
        )

        self.context_builder = (
            context_builder
            or MarketContextBuilder()
        )

        self.state = (
            state
            or AIState()
        )

    # ==========================================================
    # ANALYZE MARKET
    # ==========================================================

    def analyze_market(
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
        Build context, run AI analysis, and save the result.

        This is the main method that will eventually be called
        by ContinuousBankNiftyMonitor.
        """

        # ------------------------------------------------------
        # BUILD CONTEXT
        # ------------------------------------------------------

        context = self.context_builder.build(
            market=market,
            indicators=indicators,
            sic=sic,
            options=options,
            trades=trades,
            macro=macro,
            banks=banks,
            system=system,
        )

        # ------------------------------------------------------
        # AI ANALYSIS
        # ------------------------------------------------------

        result = self.analyzer.analyze(
            context
        )

        # ------------------------------------------------------
        # SAVE STATE
        # ------------------------------------------------------

        self._save_result(
            context=context,
            result=result,
        )

        return result

    # ==========================================================
    # SAVE RESULT
    # ==========================================================

    def _save_result(
        self,
        *,
        context: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        """
        Persist the latest AI state.

        Saving failures are logged but never propagated to the
        trading system.
        """

        try:

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

            analysis = result.get(
                "analysis"
            )

            self.state.save(

                market_timestamp=market.get(
                    "timestamp"
                ),

                bank_nifty=market.get(
                    "bank_nifty"
                ),

                gift_nifty=market.get(
                    "gift_nifty"
                ),

                rsi_1m=indicators.get(
                    "rsi_1m"
                ),

                rsi_15m=indicators.get(
                    "rsi_15m"
                ),

                sic_signal=sic.get(
                    "signal"
                ),

                ai_bias=self._extract_bias(
                    analysis
                ),

                ai_confidence=self._extract_confidence(
                    analysis
                ),

                analysis=analysis,

                context=context,
            )

        except Exception:

            logger.exception(
                "Failed to save AI state."
            )

    # ==========================================================
    # EXTRACT MARKET BIAS
    # ==========================================================

    @staticmethod
    def _extract_bias(
        analysis: str | None,
    ) -> str | None:
        """
        Extract MARKET_BIAS from the AI response.

        This is intentionally simple in Phase 1.
        Later we can use structured JSON output.
        """

        if not analysis:
            return None

        for line in analysis.splitlines():

            line = line.strip()

            if line.upper().startswith(
                "MARKET_BIAS:"
            ):

                return line.split(
                    ":",
                    1,
                )[1].strip()

        return None

    # ==========================================================
    # EXTRACT CONFIDENCE
    # ==========================================================

    @staticmethod
    def _extract_confidence(
        analysis: str | None,
    ) -> float | None:
        """
        Extract CONFIDENCE from the AI response.
        """

        if not analysis:
            return None

        for line in analysis.splitlines():

            line = line.strip()

            if line.upper().startswith(
                "CONFIDENCE:"
            ):

                value = line.split(
                    ":",
                    1,
                )[1].strip()

                try:
                    return float(value)

                except ValueError:
                    return None

        return None

    # ==========================================================
    # LAST STATE
    # ==========================================================

    def get_last_state(
        self,
    ) -> dict[str, Any] | None:
        """
        Return the most recently saved AI state.
        """

        try:

            return self.state.load()

        except Exception:

            logger.exception(
                "Failed to load AI state."
            )

            return None

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        Return AI service status.
        """

        try:

            ai_status = self.analyzer.health()

            state_exists = self.state.exists()

            return {
                "ai": ai_status,
                "state_exists": state_exists,
            }

        except Exception as exc:

            logger.exception(
                "Failed to get AI service status."
            )

            return {
                "ai": {
                    "status": "error",
                    "error": str(exc),
                },
                "state_exists": False,
            }