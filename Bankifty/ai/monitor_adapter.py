"""
Bank Nifty AI Monitor Adapter
=============================

Connects the existing ContinuousBankNiftyMonitor data to the
Phase 1 AI Controller.

This adapter does NOT:
- calculate RSI
- calculate SIC
- create trades
- modify paper trading
- execute orders

It only prepares already-existing monitor values for AI.
"""

from __future__ import annotations

import logging
from typing import Any

from .controller import AIController


logger = logging.getLogger(__name__)


class AIMonitorAdapter:
    """
    Lightweight adapter between the existing Bank Nifty monitor
    and the AI Controller.
    """

    def __init__(
        self,
        controller: AIController | None = None,
    ) -> None:

        self.controller = (
            controller
            or AIController()
        )

    # ==========================================================
    # PROCESS MONITOR DATA
    # ==========================================================

    def process(
        self,
        *,
        bank_nifty: float | None = None,
        gift_nifty: float | None = None,
        rsi_1m: float | None = None,
        rsi_15m: float | None = None,
        sic_signal: str | None = None,
        sic_conditions: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
        trades: dict[str, Any] | None = None,
        macro: dict[str, Any] | None = None,
        banks: dict[str, Any] | None = None,
        market_timestamp: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Send existing monitor information to the AI controller.

        AI will only run when its configured interval is due.
        """

        try:

            return self.controller.run_if_due(

                market={
                    "bank_nifty": bank_nifty,
                    "gift_nifty": gift_nifty,
                    "timestamp": market_timestamp,
                },

                indicators={
                    "rsi_1m": rsi_1m,
                    "rsi_15m": rsi_15m,
                },

                sic={
                    "signal": sic_signal,
                    "conditions": sic_conditions or {},
                },

                options=options or {},

                trades=trades or {},

                macro=macro or {},

                banks=banks or {},

                system={
                    "source": "ContinuousBankNiftyMonitor",
                },
            )

        except Exception:

            logger.exception(
                "AI monitor adapter failed. "
                "Existing monitor continues."
            )

            return None

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        Return adapter/AI status.
        """

        return self.controller.status()

    # ==========================================================
    # LAST RESULT
    # ==========================================================

    def last_result(
        self,
    ) -> dict[str, Any] | None:
        """
        Return the latest AI result.
        """

        return self.controller.get_last_result()