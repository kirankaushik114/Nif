"""
Bank Nifty AI Analyzer
======================

Phase 1 local AI analyzer.

Ollama performs a small classification task.
Python validates and structures the result.

AI does NOT:
- place trades
- modify SIC
- override paper trading
- invent missing data
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Any

from .config import (
    AI_ENABLED,
    AI_TEMPERATURE,
    OLLAMA_ENABLED,
)

from .ollama_client import OllamaClient


logger = logging.getLogger(__name__)


class BankNiftyAIAnalyzer:

    VALID_BIASES = {
        "BULLISH",
        "BEARISH",
        "NEUTRAL",
        "UNCLEAR",
    }

    def __init__(
        self,
        client: OllamaClient | None = None,
    ) -> None:

        self.client = (
            client
            or OllamaClient()
        )

    # ==========================================================
    # ANALYZE
    # ==========================================================

    def analyze(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:

        timestamp = datetime.now().isoformat()

        if not AI_ENABLED:

            return self._disabled(
                "AI disabled.",
                timestamp,
            )

        if not OLLAMA_ENABLED:

            return self._disabled(
                "Ollama disabled.",
                timestamp,
            )

        if not isinstance(
            context,
            dict,
        ):

            return self._error(
                "Invalid AI context.",
                timestamp,
            )

        status = self.client.status()

        if status.get("status") != "ready":

            return self._error(
                (
                    "Ollama not ready: "
                    f"{status.get('status')}"
                ),
                timestamp,
            )

        # ------------------------------------------------------
        # MARKET DATA
        # ------------------------------------------------------

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

        bank_nifty = market.get(
            "bank_nifty"
        )

        gift_nifty = market.get(
            "gift_nifty"
        )

        rsi_1m = indicators.get(
            "rsi_1m"
        )

        rsi_15m = indicators.get(
            "rsi_15m"
        )

        sic_signal = sic.get(
            "signal",
            "NEUTRAL",
        )

        conditions = sic.get(
            "conditions",
            [],
        )

        # ------------------------------------------------------
        # PROMPT
        # ------------------------------------------------------

        prompt = self._build_prompt(
            bank_nifty=bank_nifty,
            gift_nifty=gift_nifty,
            rsi_1m=rsi_1m,
            rsi_15m=rsi_15m,
            sic_signal=sic_signal,
            conditions=conditions,
        )

        # ------------------------------------------------------
        # OLLAMA
        # ------------------------------------------------------

        try:

            response = self.client.generate(

                prompt,

                temperature=AI_TEMPERATURE,

                num_predict=80,

                num_ctx=512,
            )

        except Exception as exc:

            logger.exception(
                "Bank Nifty AI analysis failed."
            )

            return self._error(
                str(exc),
                timestamp,
            )

        if not response:

            return self._error(
                "Ollama returned no response.",
                timestamp,
            )

        # ------------------------------------------------------
        # PARSE
        # ------------------------------------------------------

        ai_result = self._parse_ai_response(
            response
        )

        bias = ai_result.get(
            "bias",
            "UNCLEAR",
        )

        confidence = self._safe_confidence(
            ai_result.get(
                "confidence",
                0,
            )
        )

        # ------------------------------------------------------
        # VALIDATE BIAS
        # ------------------------------------------------------

        if bias not in self.VALID_BIASES:

            bias = "UNCLEAR"
            confidence = 0

        # ------------------------------------------------------
        # PYTHON FACTORS
        # ------------------------------------------------------

        factors = self._build_factors(
            rsi_1m=rsi_1m,
            rsi_15m=rsi_15m,
            sic_signal=sic_signal,
            conditions=conditions,
        )

        # ------------------------------------------------------
        # PYTHON RISKS
        # ------------------------------------------------------

        risks = self._build_risks(
            gift_nifty=gift_nifty,
            rsi_1m=rsi_1m,
            rsi_15m=rsi_15m,
            sic_signal=sic_signal,
        )

        # ------------------------------------------------------
        # SUMMARY
        # ------------------------------------------------------

        summary = self._build_summary(
            bias=bias,
            confidence=confidence,
        )

        structured = {
            "bias": bias,
            "confidence": confidence,
            "factors": factors,
            "risks": risks,
            "summary": summary,
        }

        return {
            "success": True,
            "status": "completed",
            "timestamp": timestamp,
            "model": self.client.model,
            "analysis": json.dumps(
                structured,
                separators=(",", ":"),
            ),
            "structured": structured,
            "context": context,
        }

    # ==========================================================
    # PROMPT
    # ==========================================================

    @staticmethod
    def _build_prompt(
        *,
        bank_nifty: Any,
        gift_nifty: Any,
        rsi_1m: Any,
        rsi_15m: Any,
        sic_signal: Any,
        conditions: Any,
    ) -> str:

        return (
            "Classify Bank Nifty.\n"
            f"BankNifty={bank_nifty}\n"
            f"GiftNifty={gift_nifty}\n"
            f"RSI1M={rsi_1m}\n"
            f"RSI15M={rsi_15m}\n"
            f"SIC={sic_signal}\n"
            f"Conditions={conditions}\n\n"
            "Return ONLY JSON with exactly these keys:\n"
            '{"bias":"NEUTRAL","confidence":50}'
        )

    # ==========================================================
    # PARSE AI RESPONSE
    # ==========================================================

    @classmethod
    def _parse_ai_response(
        cls,
        response: str,
    ) -> dict[str, Any]:

        text = response.strip()

        # ------------------------------------------------------
        # JSON
        # ------------------------------------------------------

        try:

            data = json.loads(
                text
            )

            if isinstance(
                data,
                dict,
            ):

                return cls._extract_fields(
                    data
                )

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):

            pass

        # ------------------------------------------------------
        # EXTRACT JSON OBJECT
        # ------------------------------------------------------

        start = text.find("{")
        end = text.rfind("}")

        if (
            start >= 0
            and end > start
        ):

            candidate = text[
                start:end + 1
            ]

            try:

                data = json.loads(
                    candidate
                )

                if isinstance(
                    data,
                    dict,
                ):

                    return cls._extract_fields(
                        data
                    )

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ):

                pass

        # ------------------------------------------------------
        # TEXT FALLBACK
        # ------------------------------------------------------

        bias_match = re.search(
            r"\b(BULLISH|BEARISH|NEUTRAL|UNCLEAR)\b",
            text.upper(),
        )

        confidence_match = re.search(
            r"confidence\s*[:=]\s*[\"']?"
            r"(\d+(?:\.\d+)?)",
            text,
            re.IGNORECASE,
        )

        return {
            "bias": (
                bias_match.group(1)
                if bias_match
                else "UNCLEAR"
            ),
            "confidence": (
                confidence_match.group(1)
                if confidence_match
                else 0
            ),
        }

    # ==========================================================
    # EXTRACT JSON FIELDS
    # ==========================================================

    @staticmethod
    def _extract_fields(
        data: dict[str, Any],
    ) -> dict[str, Any]:

        # ------------------------------------------------------
        # Qwen sometimes returns "BIA" instead of "bias".
        # Support both.
        # ------------------------------------------------------

        bias = data.get(
            "bias"
        )

        if bias is None:

            bias = data.get(
                "BIA"
            )

        if bias is None:

            bias = data.get(
                "BIAS"
            )

        # ------------------------------------------------------
        # Confidence may be uppercase.
        # ------------------------------------------------------

        confidence = data.get(
            "confidence"
        )

        if confidence is None:

            confidence = data.get(
                "CONFIDENCE"
            )

        return {
            "bias": str(
                bias
                if bias is not None
                else "UNCLEAR"
            ).upper().strip(),

            "confidence": (
                confidence
                if confidence is not None
                else 0
            ),
        }

    # ==========================================================
    # CONFIDENCE
    # ==========================================================

    @staticmethod
    def _safe_confidence(
        value: Any,
    ) -> int:

        try:

            value = float(
                value
            )

            value = max(
                0,
                min(
                    100,
                    value,
                ),
            )

            return int(
                round(value)
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0

    # ==========================================================
    # FACTORS
    # ==========================================================

    @staticmethod
    def _build_factors(
        *,
        rsi_1m: Any,
        rsi_15m: Any,
        sic_signal: Any,
        conditions: Any,
    ) -> list[str]:

        factors: list[str] = []

        if sic_signal:

            factors.append(
                f"SIC: {sic_signal}"
            )

        try:

            rsi = float(
                rsi_1m
            )

            if rsi >= 70:

                factors.append(
                    "1M RSI overbought"
                )

            elif rsi <= 30:

                factors.append(
                    "1M RSI oversold"
                )

            elif rsi > 50:

                factors.append(
                    "1M RSI above 50"
                )

            else:

                factors.append(
                    "1M RSI below 50"
                )

        except (
            TypeError,
            ValueError,
        ):

            pass

        if len(factors) < 2:

            try:

                rsi = float(
                    rsi_15m
                )

                if rsi >= 70:

                    factors.append(
                        "15M RSI overbought"
                    )

                elif rsi <= 30:

                    factors.append(
                        "15M RSI oversold"
                    )

                elif rsi > 50:

                    factors.append(
                        "15M RSI above 50"
                    )

                else:

                    factors.append(
                        "15M RSI below 50"
                    )

            except (
                TypeError,
                ValueError,
            ):

                pass

        return factors[:2]

    # ==========================================================
    # RISKS
    # ==========================================================

    @staticmethod
    def _build_risks(
        *,
        gift_nifty: Any,
        rsi_1m: Any,
        rsi_15m: Any,
        sic_signal: Any,
    ) -> list[str]:

        risks: list[str] = []

        if gift_nifty is None:

            risks.append(
                "Gift Nifty data unavailable"
            )

        if (
            str(
                sic_signal
            ).upper()
            == "NEUTRAL"
            and not risks
        ):

            risks.append(
                "SIC is neutral"
            )

        try:

            rsi1 = float(
                rsi_1m
            )

            rsi15 = float(
                rsi_15m
            )

            if (
                rsi1 > 50
                and rsi15 < 50
            ) or (
                rsi1 < 50
                and rsi15 > 50
            ):

                risks = [
                    "1M and 15M RSI disagree"
                ]

        except (
            TypeError,
            ValueError,
        ):

            pass

        return risks[:1]

    # ==========================================================
    # SUMMARY
    # ==========================================================

    @staticmethod
    def _build_summary(
        *,
        bias: str,
        confidence: int,
    ) -> str:

        if bias == "UNCLEAR":

            return (
                "Insufficient information "
                "for a clear AI bias."
            )

        if bias == "BULLISH":

            return (
                f"AI sees a bullish bias "
                f"with {confidence}% confidence."
            )

        if bias == "BEARISH":

            return (
                f"AI sees a bearish bias "
                f"with {confidence}% confidence."
            )

        return (
            f"AI sees a neutral bias "
            f"with {confidence}% confidence."
        )

    # ==========================================================
    # HEALTH
    # ==========================================================

    def health(
        self,
    ) -> dict[str, Any]:

        return self.client.status()

    # ==========================================================
    # DISABLED
    # ==========================================================

    @staticmethod
    def _disabled(
        reason: str,
        timestamp: str,
    ) -> dict[str, Any]:

        return {
            "success": False,
            "status": "disabled",
            "timestamp": timestamp,
            "model": None,
            "analysis": None,
            "structured": None,
            "reason": reason,
        }

    # ==========================================================
    # ERROR
    # ==========================================================

    @staticmethod
    def _error(
        reason: str,
        timestamp: str,
    ) -> dict[str, Any]:

        return {
            "success": False,
            "status": "unavailable",
            "timestamp": timestamp,
            "model": None,
            "analysis": None,
            "structured": None,
            "reason": reason,
        }