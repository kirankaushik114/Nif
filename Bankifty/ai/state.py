"""
Bank Nifty AI - Persistent State
=================================

Stores the last known AI processing state.

Purpose:
- Remember where AI stopped.
- Restore state after application restart.
- Support future time-aware catch-up.
- Keep AI state separate from paper-trading state.

Important:
This database does NOT control trades.
The existing paper-trading database remains authoritative
for trading information.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# DATABASE LOCATION
# ============================================================

AI_DATA_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "ai"
)

AI_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

STATE_DB = AI_DATA_DIR / "ai_state.db"


class AIState:
    """
    Persistent AI state manager.

    Uses SQLite because the Bank Nifty project already uses
    SQLite and this keeps the Phase 1 implementation lightweight.
    """

    def __init__(
        self,
        database_path: str | Path | None = None,
    ) -> None:

        self.database_path = Path(
            database_path
            if database_path
            else STATE_DB
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    # ==========================================================
    # DATABASE INITIALIZATION
    # ==========================================================

    def _initialize(self) -> None:
        """
        Create the AI state table if it does not exist.
        """

        with sqlite3.connect(
            self.database_path
        ) as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),

                    updated_at TEXT,

                    last_analysis_time TEXT,

                    last_market_timestamp TEXT,

                    last_bank_nifty REAL,

                    last_gift_nifty REAL,

                    last_rsi_1m REAL,

                    last_rsi_15m REAL,

                    last_sic_signal TEXT,

                    last_ai_bias TEXT,

                    last_ai_confidence REAL,

                    last_analysis TEXT,

                    last_context_json TEXT
                )
                """
            )

            connection.commit()

    # ==========================================================
    # SAVE STATE
    # ==========================================================

    def save(
        self,
        *,
        market_timestamp: str | None = None,
        bank_nifty: float | None = None,
        gift_nifty: float | None = None,
        rsi_1m: float | None = None,
        rsi_15m: float | None = None,
        sic_signal: str | None = None,
        ai_bias: str | None = None,
        ai_confidence: float | None = None,
        analysis: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """
        Save the latest AI processing state.

        Existing state is replaced because only the latest
        checkpoint is required at this stage.
        """

        updated_at = datetime.now(
            timezone.utc
        ).isoformat()

        analysis_time = updated_at

        context_json = (
            json.dumps(
                context,
                default=str,
            )
            if context is not None
            else None
        )

        with sqlite3.connect(
            self.database_path
        ) as connection:

            connection.execute(
                """
                INSERT INTO ai_state (
                    id,
                    updated_at,
                    last_analysis_time,
                    last_market_timestamp,
                    last_bank_nifty,
                    last_gift_nifty,
                    last_rsi_1m,
                    last_rsi_15m,
                    last_sic_signal,
                    last_ai_bias,
                    last_ai_confidence,
                    last_analysis,
                    last_context_json
                )
                VALUES (
                    1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                ON CONFLICT(id)
                DO UPDATE SET
                    updated_at = excluded.updated_at,
                    last_analysis_time =
                        excluded.last_analysis_time,
                    last_market_timestamp =
                        excluded.last_market_timestamp,
                    last_bank_nifty =
                        excluded.last_bank_nifty,
                    last_gift_nifty =
                        excluded.last_gift_nifty,
                    last_rsi_1m =
                        excluded.last_rsi_1m,
                    last_rsi_15m =
                        excluded.last_rsi_15m,
                    last_sic_signal =
                        excluded.last_sic_signal,
                    last_ai_bias =
                        excluded.last_ai_bias,
                    last_ai_confidence =
                        excluded.last_ai_confidence,
                    last_analysis =
                        excluded.last_analysis,
                    last_context_json =
                        excluded.last_context_json
                """,
                (
                    updated_at,
                    analysis_time,
                    market_timestamp,
                    bank_nifty,
                    gift_nifty,
                    rsi_1m,
                    rsi_15m,
                    sic_signal,
                    ai_bias,
                    ai_confidence,
                    analysis,
                    context_json,
                ),
            )

            connection.commit()

    # ==========================================================
    # LOAD STATE
    # ==========================================================

    def load(self) -> dict[str, Any] | None:
        """
        Load the last saved AI state.

        Returns:
            Dictionary containing the state,
            or None if no state exists.
        """

        with sqlite3.connect(
            self.database_path
        ) as connection:

            connection.row_factory = sqlite3.Row

            row = connection.execute(
                """
                SELECT
                    updated_at,
                    last_analysis_time,
                    last_market_timestamp,
                    last_bank_nifty,
                    last_gift_nifty,
                    last_rsi_1m,
                    last_rsi_15m,
                    last_sic_signal,
                    last_ai_bias,
                    last_ai_confidence,
                    last_analysis,
                    last_context_json
                FROM ai_state
                WHERE id = 1
                """
            ).fetchone()

        if row is None:
            return None

        state = dict(row)

        # ------------------------------------------------------
        # Restore structured context
        # ------------------------------------------------------

        context_json = state.pop(
            "last_context_json",
            None,
        )

        if context_json:

            try:

                state["last_context"] = json.loads(
                    context_json
                )

            except json.JSONDecodeError:

                state["last_context"] = {}

        else:

            state["last_context"] = {}

        return state

    # ==========================================================
    # CLEAR
    # ==========================================================

    def clear(self) -> None:
        """
        Clear stored AI state.

        Useful during development/testing.
        """

        with sqlite3.connect(
            self.database_path
        ) as connection:

            connection.execute(
                "DELETE FROM ai_state WHERE id = 1"
            )

            connection.commit()

    # ==========================================================
    # EXISTS
    # ==========================================================

    def exists(self) -> bool:
        """
        Return True if an AI checkpoint exists.
        """

        return self.load() is not None