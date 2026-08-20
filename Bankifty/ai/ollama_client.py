"""
Bank Nifty AI - Ollama Client
==============================

Safe interface between the Bank Nifty AI layer and Ollama.

Features:
- Enable / disable Ollama
- Health check
- Model availability
- JSON output support
- Qwen3 thinking disabled
- Timeout handling
- Safe failure handling
- Never crashes the Bank Nifty monitor
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from .config import (
    AI_CONTEXT_SIZE,
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    OLLAMA_BASE_URL,
    OLLAMA_ENABLED,
    OLLAMA_MODEL,
)


logger = logging.getLogger(__name__)


class OllamaClient:
    """Safe client for the local Ollama server."""

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
    ) -> None:

        self.base_url = base_url.rstrip("/")
        self.model = model

    # ==========================================================
    # ENABLED
    # ==========================================================

    @property
    def enabled(self) -> bool:
        return OLLAMA_ENABLED

    # ==========================================================
    # HEALTH
    # ==========================================================

    def health(self) -> bool:

        if not self.enabled:
            return False

        try:

            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            return response.ok

        except requests.RequestException as exc:

            logger.warning(
                "Ollama health check failed: %s",
                exc,
            )

            return False

    # ==========================================================
    # MODEL AVAILABLE
    # ==========================================================

    def model_available(self) -> bool:

        if not self.enabled:
            return False

        try:

            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            response.raise_for_status()

            data = response.json()

            for model in data.get("models", []):

                name = model.get(
                    "name",
                    "",
                )

                if (
                    name == self.model
                    or name.startswith(
                        f"{self.model}:"
                    )
                ):

                    return True

            return False

        except (
            requests.RequestException,
            ValueError,
            TypeError,
        ) as exc:

            logger.warning(
                "Unable to check Ollama model: %s",
                exc,
            )

            return False

    # ==========================================================
    # GENERATE
    # ==========================================================

    def generate(
        self,
        prompt: str,
        **options: Any,
    ) -> str | None:
        """
        Generate a final response from Ollama.

        Qwen3 thinking is disabled for routine Bank Nifty
        analysis so the generation budget is used for the
        actual answer.
        """

        if not self.enabled:

            logger.info(
                "Ollama is disabled."
            )

            return None

        if not prompt or not prompt.strip():

            logger.warning(
                "Ollama prompt is empty."
            )

            return None

        # ------------------------------------------------------
        # DEFAULT OPTIONS
        # ------------------------------------------------------

        ollama_options = {

            "temperature": AI_TEMPERATURE,

            "num_predict": AI_MAX_TOKENS,

            "num_ctx": AI_CONTEXT_SIZE,
        }

        # Caller options override defaults.
        ollama_options.update(options)

        # ------------------------------------------------------
        # PAYLOAD
        # ------------------------------------------------------

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,

            # Disable Qwen3 thinking.
            "think": False,

            # Request structured JSON.
            "format": "json",

            "options": ollama_options,
        }

        # ------------------------------------------------------
        # REQUEST
        # ------------------------------------------------------

        try:

            logger.info(
                "Sending request to Ollama model=%s",
                self.model,
            )

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=180,
            )

            response.raise_for_status()

            data = response.json()

            # --------------------------------------------------
            # FINAL RESPONSE
            # --------------------------------------------------

            result = data.get(
                "response",
                "",
            )

            if isinstance(
                result,
                str,
            ):

                result = result.strip()

            if result:

                return result

            # --------------------------------------------------
            # THINKING ONLY
            # --------------------------------------------------

            thinking = data.get(
                "thinking",
                "",
            )

            if thinking:

                logger.warning(
                    "Ollama returned no response text "
                    "but returned thinking content."
                )

            else:

                logger.warning(
                    "Ollama returned an empty response."
                )

            return None

        # ------------------------------------------------------
        # TIMEOUT
        # ------------------------------------------------------

        except requests.Timeout:

            logger.warning(
                "Ollama generation timed out."
            )

            return None

        # ------------------------------------------------------
        # CONNECTION
        # ------------------------------------------------------

        except requests.ConnectionError:

            logger.warning(
                "Cannot connect to Ollama at %s",
                self.base_url,
            )

            return None

        # ------------------------------------------------------
        # HTTP
        # ------------------------------------------------------

        except requests.HTTPError as exc:

            logger.warning(
                "Ollama HTTP error: %s",
                exc,
            )

            return None

        # ------------------------------------------------------
        # REQUEST
        # ------------------------------------------------------

        except requests.RequestException as exc:

            logger.warning(
                "Ollama request failed: %s",
                exc,
            )

            return None

        # ------------------------------------------------------
        # RESPONSE PARSING
        # ------------------------------------------------------

        except (
            ValueError,
            TypeError,
        ) as exc:

            logger.warning(
                "Invalid Ollama response: %s",
                exc,
            )

            return None

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self) -> dict[str, Any]:

        if not self.enabled:

            return {
                "enabled": False,
                "running": False,
                "model": self.model,
                "model_available": False,
                "status": "disabled",
            }

        running = self.health()

        if not running:

            return {
                "enabled": True,
                "running": False,
                "model": self.model,
                "model_available": False,
                "status": "offline",
            }

        available = self.model_available()

        return {
            "enabled": True,
            "running": True,
            "model": self.model,
            "model_available": available,
            "status": (
                "ready"
                if available
                else "model_missing"
            ),
        }