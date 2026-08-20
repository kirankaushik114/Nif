"""
Bank Nifty AI Controller
========================

Controls when AI analysis is executed.

Market data may refresh every second, while AI runs at its
own configurable interval.

This prevents Ollama from becoming a bottleneck.

Important:
- Does not control trades.
- Does not modify SIC.
- Does not stop the market monitor.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from .config import (
    AI_ANALYSIS_INTERVAL_SECONDS,
    AI_ENABLED,
    OLLAMA_ENABLED,
)
from .service import BankNiftyAIService


logger = logging.getLogger(__name__)


class AIController:
    """
    Controls periodic AI analysis.

    Example:

        market refresh = 1 second
        AI analysis    = 60 seconds
    """

    def __init__(
        self,
        service: BankNiftyAIService | None = None,
    ) -> None:

        self.service = (
            service
            or BankNiftyAIService()
        )

        self.interval = max(
            1,
            AI_ANALYSIS_INTERVAL_SECONDS,
        )

        self.last_run_monotonic: float | None = None

        self.last_result: dict[str, Any] | None = None

    # ==========================================================
    # SHOULD RUN
    # ==========================================================

    def should_run(self) -> bool:
        """
        Determine whether enough time has passed for another
        AI analysis.
        """

        if not AI_ENABLED:
            return False

        if not OLLAMA_ENABLED:
            return False

        now = time.monotonic()

        if self.last_run_monotonic is None:
            return True

        elapsed = (
            now
            - self.last_run_monotonic
        )

        return elapsed >= self.interval

    # ==========================================================
    # RUN
    # ==========================================================

    def run_if_due(
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
    ) -> dict[str, Any] | None:
        """
        Run AI only when the configured interval has elapsed.

        Returns:
            AI result if executed.
            None if not due.
        """

        if not self.should_run():
            return None

        self.last_run_monotonic = time.monotonic()

        logger.info(
            "Running Bank Nifty AI analysis."
        )

        try:

            result = self.service.analyze_market(

                market=market,

                indicators=indicators,

                sic=sic,

                options=options,

                trades=trades,

                macro=macro,

                banks=banks,

                system=system,
            )

            self.last_result = result

            return result

        except Exception:

            logger.exception(
                "AI analysis failed. "
                "Main market system continues."
            )

            return None

    # ==========================================================
    # LAST RESULT
    # ==========================================================

    def get_last_result(
        self,
    ) -> dict[str, Any] | None:
        """
        Return the latest AI result held in memory.
        """

        return self.last_result

    # ==========================================================
    # RESET TIMER
    # ==========================================================

    def reset_timer(self) -> None:
        """
        Force the next call to run AI immediately.
        """

        self.last_run_monotonic = None

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self) -> dict[str, Any]:

        return {
            "ai_enabled": AI_ENABLED,

            "ollama_enabled": OLLAMA_ENABLED,

            "interval_seconds": self.interval,

            "last_run": (
                self.last_run_monotonic
                is not None
            ),

            "has_result": (
                self.last_result
                is not None
            ),
        }