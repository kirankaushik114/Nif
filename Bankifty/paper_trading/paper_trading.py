"""
Bank Nifty Paper Trading Manager

REAL MARKET DATA
ZERO REAL ORDERS

Six independent strategies:

1M:
    <= 30 -> CE -> +15
    >= 70 -> PE -> +15

15M:
    < 20 -> CE -> +100
    > 80 -> PE -> +100

1M + 15M:
    <=30 and <=40 -> CE -> +50
    >=70 and >=60 -> PE -> +50
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


class PaperTradeManager:

    def __init__(
        self,
        database_file,
        timezone="Asia/Kolkata",
        lot_quantity=1,
    ):

        self.database_file = Path(
            database_file
        )

        self.database_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.timezone = ZoneInfo(
            timezone
        )

        self.lot_quantity = lot_quantity

        self._create_database()

    # ========================================================
    # DATABASE
    # ========================================================

    def _connect(self):

        return sqlite3.connect(
            self.database_file
        )

    def _create_database(self):

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS paper_trades (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    strategy TEXT NOT NULL,

                    signal TEXT NOT NULL,

                    option_type TEXT NOT NULL,

                    strike REAL NOT NULL,

                    trading_symbol TEXT,

                    entry_time TEXT NOT NULL,

                    entry_price REAL NOT NULL,

                    target_price REAL NOT NULL,

                    exit_time TEXT,

                    exit_price REAL,

                    target_points REAL NOT NULL,

                    quantity INTEGER NOT NULL,

                    pnl_points REAL,

                    pnl_value REAL,

                    status TEXT NOT NULL,

                    entry_rsi_1m REAL,

                    entry_rsi_15m REAL,

                    entry_bank_nifty REAL,

                    exit_reason TEXT,

                    created_at TEXT NOT NULL
                )
                """
            )

            connection.commit()

    # ========================================================
    # CURRENT IST TIME
    # ========================================================

    def now(self):

        return datetime.now(
            self.timezone
        )

    # ========================================================
    # FIND OPEN TRADE
    # ========================================================

    def get_open_trade(
        self,
        strategy,
    ):

        with self._connect() as connection:

            cursor = connection.execute(
                """
                SELECT *
                FROM paper_trades
                WHERE strategy = ?
                AND status = 'OPEN'
                ORDER BY id DESC
                LIMIT 1
                """,
                (strategy,)
            )

            return cursor.fetchone()

    # ========================================================
    # OPEN TRADE
    # ========================================================

    def open_trade(
        self,
        strategy,
        signal,
        option_type,
        strike,
        trading_symbol,
        entry_price,
        target_points,
        rsi_1m,
        rsi_15m,
        bank_nifty,
    ):

        # ----------------------------------------------------
        # NEVER CREATE DUPLICATE OPEN TRADE
        # ----------------------------------------------------

        existing = self.get_open_trade(
            strategy
        )

        if existing is not None:

            return False

        entry_price = float(
            entry_price
        )

        target_price = (
            entry_price
            +
            float(target_points)
        )

        current_time = (
            self.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO paper_trades (

                    strategy,
                    signal,
                    option_type,
                    strike,
                    trading_symbol,
                    entry_time,
                    entry_price,
                    target_price,
                    target_points,
                    quantity,
                    status,
                    entry_rsi_1m,
                    entry_rsi_15m,
                    entry_bank_nifty,
                    created_at

                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    strategy,
                    signal,
                    option_type,
                    float(strike),
                    trading_symbol,
                    current_time,
                    entry_price,
                    target_price,
                    float(target_points),
                    self.lot_quantity,
                    "OPEN",
                    float(rsi_1m),
                    float(rsi_15m),
                    float(bank_nifty),
                    current_time,
                )
            )

            connection.commit()

        print()
        print("=" * 70)
        print("PAPER TRADE : VIRTUAL BUY")
        print("=" * 70)
        print(
            f"Strategy      : {strategy}"
        )
        print(
            f"Signal        : {signal}"
        )
        print(
            f"Option        : {option_type}"
        )
        print(
            f"Strike        : {strike}"
        )
        print(
            f"Trading Symbol: {trading_symbol}"
        )
        print(
            f"Entry LTP     : {entry_price:.2f}"
        )
        print(
            f"Target        : {target_price:.2f}"
        )
        print(
            f"Target Points : +{target_points:.2f}"
        )
        print(
            f"RSI 1M        : {rsi_1m:.2f}"
        )
        print(
            f"RSI 15M       : {rsi_15m:.2f}"
        )
        print(
            f"Bank Nifty    : {bank_nifty:,.2f}"
        )
        print(
            f"Time          : {current_time}"
        )
        print(
            "REAL ORDER    : NO"
        )
        print("=" * 70)

        return True

    # ========================================================
    # CLOSE TRADE
    # ========================================================

    def close_trade(
        self,
        trade_id,
        exit_price,
        exit_reason="TARGET",
    ):

        exit_price = float(
            exit_price
        )

        current_time = (
            self.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        with self._connect() as connection:

            cursor = connection.execute(
                """
                SELECT
                    entry_price,
                    quantity
                FROM paper_trades
                WHERE id = ?
                AND status = 'OPEN'
                """,
                (trade_id,)
            )

            row = cursor.fetchone()

            if row is None:
                return False

            entry_price = float(
                row[0]
            )

            quantity = int(
                row[1]
            )

            pnl_points = (
                exit_price
                -
                entry_price
            )

            pnl_value = (
                pnl_points
                *
                quantity
            )

            connection.execute(
                """
                UPDATE paper_trades

                SET
                    exit_time = ?,
                    exit_price = ?,
                    pnl_points = ?,
                    pnl_value = ?,
                    status = 'CLOSED',
                    exit_reason = ?

                WHERE id = ?
                """,
                (
                    current_time,
                    exit_price,
                    pnl_points,
                    pnl_value,
                    exit_reason,
                    trade_id,
                )
            )

            connection.commit()

        print()
        print("=" * 70)
        print("PAPER TRADE : VIRTUAL SELL")
        print("=" * 70)
        print(
            f"Trade ID      : {trade_id}"
        )
        print(
            f"Entry Price   : {entry_price:.2f}"
        )
        print(
            f"Exit Price    : {exit_price:.2f}"
        )
        print(
            f"P&L Points    : {pnl_points:+.2f}"
        )
        print(
            f"Virtual P&L   : {pnl_value:+.2f}"
        )
        print(
            f"Exit Reason   : {exit_reason}"
        )
        print(
            f"Time          : {current_time}"
        )
        print("=" * 70)

        return True

    # ========================================================
    # CHECK TARGET
    # ========================================================

    def check_targets(
        self,
        option_prices,
    ):

        """
        option_prices:

            {
                trading_symbol: current_ltp
            }
        """

        with self._connect() as connection:

            cursor = connection.execute(
                """
                SELECT
                    id,
                    trading_symbol,
                    target_price
                FROM paper_trades
                WHERE status = 'OPEN'
                """
            )

            open_trades = cursor.fetchall()

        closed = []

        for trade in open_trades:

            trade_id = trade[0]
            trading_symbol = trade[1]
            target_price = float(
                trade[2]
            )

            current_ltp = option_prices.get(
                trading_symbol
            )

            if current_ltp is None:
                continue

            current_ltp = float(
                current_ltp
            )

            if current_ltp >= target_price:

                self.close_trade(
                    trade_id=trade_id,
                    exit_price=target_price,
                    exit_reason="TARGET",
                )

                closed.append(
                    trade_id
                )

        return closed

    # ========================================================
    # GET OPEN TRADES
    # ========================================================

    def get_open_trades(self):

        with self._connect() as connection:

            cursor = connection.execute(
                """
                SELECT
                    id,
                    strategy,
                    signal,
                    option_type,
                    strike,
                    trading_symbol,
                    entry_time,
                    entry_price,
                    target_price,
                    target_points,
                    quantity
                FROM paper_trades
                WHERE status = 'OPEN'
                ORDER BY id
                """
            )

            return cursor.fetchall()

    # ========================================================
    # SUMMARY
    # ========================================================

    def get_summary(self):

        with self._connect() as connection:

            cursor = connection.execute(
                """
                SELECT
                    COUNT(*),
                    SUM(
                        CASE
                            WHEN status = 'CLOSED'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    SUM(
                        CASE
                            WHEN pnl_value > 0
                            THEN 1
                            ELSE 0
                        END
                    ),
                    SUM(
                        CASE
                            WHEN pnl_value < 0
                            THEN 1
                            ELSE 0
                        END
                    ),
                    COALESCE(
                        SUM(pnl_points),
                        0
                    ),
                    COALESCE(
                        SUM(pnl_value),
                        0
                    )
                FROM paper_trades
                """
            )

            return cursor.fetchone()