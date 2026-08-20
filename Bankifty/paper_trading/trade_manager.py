"""
Bank Nifty Paper Trading Manager

REAL MARKET DATA
ZERO REAL ORDERS

Six independent paper-trading strategies:

1. 1M_CE
       1M <= 30
       CE
       Target +15

2. 1M_PE
       1M >= 70
       PE
       Target +15

3. 15M_CE
       15M < 30
       CE
       Target +45

4. 15M_PE
       15M > 70
       PE
       Target +45

5. COMBINED_CE
       1M < 20 AND 15M < 25
       CE
       Target +75

6. COMBINED_PE
       1M > 80 AND 15M > 75
       PE
       Target +75

IMPORTANT:

Each strategy has its own independent lock.

Example:

    1M_CE OPEN
        -> another 1M_CE BUY is blocked

    1M_PE
        -> still allowed

    15M_CE
        -> still allowed

    COMBINED_CE
        -> still allowed

A strategy becomes available again only after
its own trade is CLOSED.

MANUAL EXIT:

    Manual SELL price can be ANY valid price.

    Example:

        BUY    = 250
        TARGET = 265
        CURRENT = 235

        Manual SELL = 280

    The paper trade is closed at 280.

    P&L = 280 - 250 = +30 points.

    Manual SELL can be:
        below BUY
        equal to BUY
        above BUY
        below TARGET
        equal to TARGET
        above TARGET

    The manual price overwrites the CURRENT price
    for the paper-trade exit calculation.

REAL ORDERS ARE NEVER PLACED.
"""

import sqlite3

from datetime import datetime

from pathlib import Path

from zoneinfo import ZoneInfo


class PaperTradeManager:
    # ========================================================
    # STRATEGY NAMES
    # ========================================================

    STRATEGY_1M_CE = "1M_CE"

    STRATEGY_1M_PE = "1M_PE"

    STRATEGY_15M_CE = "15M_CE"

    STRATEGY_15M_PE = "15M_PE"

    STRATEGY_COMBINED_CE = "COMBINED_CE"

    STRATEGY_COMBINED_PE = "COMBINED_PE"

    VALID_STRATEGIES = {
        STRATEGY_1M_CE,
        STRATEGY_1M_PE,
        STRATEGY_15M_CE,
        STRATEGY_15M_PE,
        STRATEGY_COMBINED_CE,
        STRATEGY_COMBINED_PE,
    }

    # ========================================================
    # INIT
    # ========================================================

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
            exist_ok=True,
        )

        self.timezone = ZoneInfo(
            timezone
        )

        self.lot_quantity = int(
            lot_quantity
        )

        self._create_database()

    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    def _connect(self):

        return sqlite3.connect(
            self.database_file
        )

    # ========================================================
    # CREATE DATABASE
    # ========================================================

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

                    target_points REAL NOT NULL,

                    exit_time TEXT,

                    exit_price REAL,

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
    # TIME
    # ========================================================

    def now(self):

        return datetime.now(
            self.timezone
        )

    # ========================================================
    # VALIDATE STRATEGY
    # ========================================================

    def validate_strategy(
            self,
            strategy,
    ):

        if strategy not in self.VALID_STRATEGIES:
            raise ValueError(
                f"Invalid paper-trading strategy: "
                f"{strategy}. "
                f"Expected one of: "
                f"{sorted(self.VALID_STRATEGIES)}"
            )

        return True

    # ========================================================
    # OPEN TRADE FOR ONE STRATEGY
    # ========================================================

    def get_open_trade(
            self,
            strategy,
    ):

        self.validate_strategy(
            strategy
        )

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
                (
                    strategy,
                ),
            )

            return cursor.fetchone()

    # ========================================================
    # CHECK WHETHER STRATEGY IS LOCKED
    # ========================================================

    def is_strategy_locked(
            self,
            strategy,
    ):

        return (
                self.get_open_trade(
                    strategy
                )
                is not None
        )

    # ========================================================
    # OPEN VIRTUAL TRADE
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

        self.validate_strategy(
            strategy
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Do not buy the same strategy again while OPEN.
        # ----------------------------------------------------

        existing_trade = (
            self.get_open_trade(
                strategy
            )
        )

        if existing_trade is not None:
            # PAPER TRADE BLOCKED PRINT DISABLED.
            # print(
            #     f"[PAPER TRADE BLOCKED] "
            #     f"{strategy} already has an OPEN trade."
            # )

            return False

        entry_price = float(
            entry_price
        )

        target_points = float(
            target_points
        )

        target_price = (
                entry_price
                +
                target_points
        )

        current_time = (
            self.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        # ----------------------------------------------------
        # INSERT PAPER TRADE
        # ----------------------------------------------------

        with self._connect() as connection:
            cursor = connection.execute(
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

                VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
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

                    target_points,

                    self.lot_quantity,

                    "OPEN",

                    float(rsi_1m),

                    float(rsi_15m),

                    float(bank_nifty),

                    current_time,
                ),
            )

            connection.commit()

            trade_id = (
                cursor.lastrowid
            )

        # ----------------------------------------------------
        # DISPLAY BUY - DISABLED HERE.
        # Continuous monitor prints the confirmed PAPER BUY.
        # Original print block intentionally retained below.
        # ----------------------------------------------------

        #         print()
        #
        #         print(
        #             "=" * 70
        #         )
        #
        #         print(
        #             "PAPER TRADE : VIRTUAL BUY"
        #         )
        #
        #         print(
        #             "=" * 70
        #         )
        #
        #         print(
        #             f"Trade ID       : {trade_id}"
        #         )
        #
        #         print(
        #             f"Strategy       : {strategy}"
        #         )
        #
        #         print(
        #             f"Signal         : {signal}"
        #         )
        #
        #         print(
        #             f"Option         : {option_type}"
        #         )
        #
        #         print(
        #             f"Strike         : {strike}"
        #         )
        #
        #         print(
        #             f"Trading Symbol : {trading_symbol}"
        #         )
        #
        #         print(
        #             f"Entry LTP      : {entry_price:.2f}"
        #         )
        #
        #         print(
        #             f"Target         : {target_price:.2f}"
        #         )
        #
        #         print(
        #             f"Target Points  : +{target_points:.2f}"
        #         )
        #
        #         print(
        #             f"RSI 1M         : {rsi_1m:.2f}"
        #         )
        #
        #         print(
        #             f"RSI 15M        : {rsi_15m:.2f}"
        #         )
        #
        #         print(
        #             f"Bank Nifty     : {bank_nifty:,.2f}"
        #         )
        #
        #         print(
        #             f"Time           : {current_time}"
        #         )
        #
        #         print(
        #             "REAL ORDER     : NO"
        #         )
        #
        #         print(
        #             "STATUS         : OPEN"
        #         )
        #
        #         print(
        #             "=" * 70
        #         )
        #

        return True

    # ========================================================
    # CLOSE VIRTUAL TRADE
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

        if exit_price <= 0:
            raise ValueError(
                "Exit price must be greater than 0."
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
                    strategy,
                    entry_price,
                    quantity

                FROM paper_trades

                WHERE id = ?

                AND status = 'OPEN'
                """,
                (
                    trade_id,
                ),
            )

            row = cursor.fetchone()

            if row is None:
                return False

            strategy = row[0]

            entry_price = float(
                row[1]
            )

            quantity = int(
                row[2]
            )

            # ------------------------------------------------
            # P&L
            #
            # SELL - BUY
            #
            # Example:
            # BUY  = 250
            # SELL = 280
            #
            # P&L = +30
            # ------------------------------------------------

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
                ),
            )

            connection.commit()

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Once status becomes CLOSED,
        # get_open_trade(strategy) returns None.
        #
        # Therefore this strategy is automatically UNLOCKED.
        # ----------------------------------------------------

        # DISPLAY SELL - DISABLED HERE.
        # Continuous monitor prints the confirmed PAPER SELL.
        # Original print block intentionally retained below.
        # ----------------------------------------------------

        #         print()
        #
        #         print(
        #             "=" * 70
        #         )
        #
        #         print(
        #             "PAPER TRADE : VIRTUAL SELL"
        #         )
        #
        #         print(
        #             "=" * 70
        #         )
        #
        #         print(
        #             f"Trade ID     : {trade_id}"
        #         )
        #
        #         print(
        #             f"Strategy     : {strategy}"
        #         )
        #
        #         print(
        #             f"Entry Price  : {entry_price:.2f}"
        #         )
        #
        #         print(
        #             f"Exit Price   : {exit_price:.2f}"
        #         )
        #
        #         print(
        #             f"P&L Points   : {pnl_points:+.2f}"
        #         )
        #
        #         print(
        #             f"Virtual P&L  : {pnl_value:+.2f}"
        #         )
        #
        #         print(
        #             f"Exit Reason  : {exit_reason}"
        #         )
        #
        #         print(
        #             f"Time         : {current_time}"
        #         )
        #
        #         print(
        #             "REAL ORDER   : NO"
        #         )
        #
        #         print(
        #             "STATUS       : CLOSED"
        #         )
        #
        #         print(
        #             "=" * 70
        #         )
        #

        return True

    # ========================================================
    # MANUAL EXIT
    # ========================================================
    #
    # Manual SELL price can be ANY valid price.
    #
    # It can be:
    #
    #   below BUY
    #   equal to BUY
    #   above BUY
    #   below TARGET
    #   equal to TARGET
    #   above TARGET
    #
    # The manually entered price becomes the actual
    # paper SELL price.
    #
    # The live CURRENT price is NOT used for the
    # manual exit calculation.
    #
    # Manual exit is allowed at ANY TIME.
    #
    # REAL ORDER = NO
    # ========================================================

    def manual_exit(
            self,
            trade_id,
            exit_price,
    ):

        try:

            exit_price = float(
                exit_price
            )

        except (
                TypeError,
                ValueError,
        ):

            raise ValueError(
                "Manual exit price must be a valid number."
            )

        if exit_price <= 0:
            raise ValueError(
                "Manual exit price must be greater than 0."
            )

        # ----------------------------------------------------
        # Use the normal close_trade() method.
        #
        # This guarantees:
        #
        # exit_price  = manual price
        # status      = CLOSED
        # pnl_points  = manual price - entry price
        # pnl_value   = pnl_points * quantity
        # exit_reason = MANUAL EXIT
        # ----------------------------------------------------

        return self.close_trade(
            trade_id=trade_id,

            exit_price=exit_price,

            exit_reason="MANUAL EXIT",
        )

    # ========================================================
    # CHECK TARGETS
    # ========================================================

    def check_targets(
            self,
            option_prices,
    ):

        with self._connect() as connection:

            cursor = connection.execute(
                """
                SELECT

                    id,

                    strategy,

                    trading_symbol,

                    target_price

                FROM paper_trades

                WHERE status = 'OPEN'
                """
            )

            trades = cursor.fetchall()

        closed = []

        for trade in trades:

            trade_id = trade[0]

            strategy = trade[1]

            symbol = trade[2]

            target_price = float(
                trade[3]
            )

            if not symbol:
                continue

            if symbol not in option_prices:
                continue

            current_ltp = float(
                option_prices[
                    symbol
                ]
            )

            if current_ltp >= target_price:

                closed_successfully = (
                    self.close_trade(

                        trade_id=trade_id,

                        exit_price=target_price,

                        exit_reason="TARGET",
                    )
                )

                if closed_successfully:
                    closed.append(
                        trade_id
                    )

        return closed

    # ========================================================
    # GET ALL OPEN TRADES
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
    # GET OPEN TRADE BY STRATEGY
    # ========================================================

    def get_open_trade_by_strategy(
            self,
            strategy,
    ):

        return self.get_open_trade(
            strategy
        )

    # ========================================================
    # GET STRATEGY STATUS
    # ========================================================

    def get_strategy_status(self):

        status = {}

        for strategy in sorted(
                self.VALID_STRATEGIES
        ):
            trade = (
                self.get_open_trade(
                    strategy
                )
            )

            status[strategy] = (

                "OPEN"

                if trade is not None

                else

                "AVAILABLE"
            )

        return status

    # ========================================================
    # PRINT STRATEGY STATUS
    # ========================================================

    def print_strategy_status(self):

        print()

        print(
            "=" * 70
        )

        print(
            "PAPER TRADING STRATEGY STATUS"
        )

        print(
            "=" * 70
        )

        status = (
            self.get_strategy_status()
        )

        for strategy in sorted(
                status
        ):
            print(
                f"{strategy:<15} : "
                f"{status[strategy]}"
            )

        print(
            "=" * 70
        )

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