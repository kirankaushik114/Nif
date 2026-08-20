"""
Bank Nifty Continuous RSI Monitor

REAL MARKET DATA
PAPER / VIRTUAL TRADING ONLY

SIX INDEPENDENT PAPER-TRADING TRIGGERS

1. 1M <= 30
       CE
       Target = Entry + 15

2. 1M >= 70
       PE
       Target = Entry + 15

3. 15M < 30
       CE
       Target = Entry + 45

4. 15M > 70
       PE
       Target = Entry + 45

5. 1M < 20
   AND
   15M < 25
       CE
       Target = Entry + 75

6. 1M > 80
   AND
   15M > 75
       PE
       Target = Entry + 75


SIX INDEPENDENT STRATEGY LOCKS

1M_CE
1M_PE
15M_CE
15M_PE
COMBINED_CE
COMBINED_PE

A strategy cannot BUY again while its own trade is OPEN.

After that trade is SOLD, that strategy becomes available again.

NEW PAPER BUYs:
10:00 AM to 3:00 PM IST only.

NO REAL ORDERS ARE PLACED.
"""

import time

from datetime import datetime
from datetime import time as dt_time

from zoneinfo import ZoneInfo


from data.historical_data import (
    GrowwHistoricalData
)

from indicators.rsi import (
    candle_closes_to_series,
    calculate_latest_rsi,
)

from notifications.email import (
    EmailNotifier
)

from paper_trading.trade_manager import (
    PaperTradeManager
)

from config.settings import (

    # ========================================================
    # MARKET
    # ========================================================

    TIME_ZONE,

    PRE_MARKET_TIME,
    MARKET_OPEN_TIME,
    MARKET_CLOSE_TIME,
    MONITOR_CLOSE_TIME,

    # ========================================================
    # RSI
    # ========================================================

    RSI_PERIOD,

    RSI_15_EXTREME_OVERSOLD,
    RSI_15_EXTREME_OVERBOUGHT,

    RSI_15_BULLISH,
    RSI_15_BEARISH,

    RSI_1_BULLISH,
    RSI_1_BEARISH,

    # ========================================================
    # MONITORING
    # ========================================================

    CHECK_INTERVAL_SECONDS,

    # ========================================================
    # EMAIL
    # ========================================================

    EMAIL_ENABLED,

    EMAIL_ON_PAPER_PURCHASE,
    EMAIL_ON_PAPER_SELL,

    # ========================================================
    # PAPER TRADING
    # ========================================================

    PAPER_TRADING_ENABLED,
    REAL_ORDERS_ENABLED,

    PAPER_1M_TARGET_POINTS,
    PAPER_15M_TARGET_POINTS,
    PAPER_COMBINED_TARGET_POINTS,

    PAPER_STRIKE_STEP,
    PAPER_LOTS,
    PAPER_DATABASE_FILE,
)


# ============================================================
# TIMEZONE
# ============================================================

IST = ZoneInfo(
    TIME_ZONE
)


class ContinuousBankNiftyMonitor:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        self.historical = (
            GrowwHistoricalData()
        )

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        self.email = None

        if EMAIL_ENABLED:

            self.email = (
                EmailNotifier()
            )

        # ----------------------------------------------------
        # PAPER TRADING
        # ----------------------------------------------------

        self.paper_trader = None

        if PAPER_TRADING_ENABLED:

            if REAL_ORDERS_ENABLED:

                raise RuntimeError(
                    "REAL_ORDERS_ENABLED "
                    "must remain False."
                )

            self.paper_trader = (
                PaperTradeManager(
                    database_file=(
                        PAPER_DATABASE_FILE
                    ),
                    timezone=TIME_ZONE,
                    lot_quantity=PAPER_LOTS,
                )
            )

        # ----------------------------------------------------
        # CURRENT DATA
        # ----------------------------------------------------

        self.last_rsi_1m = None

        self.last_rsi_15m = None

        self.last_bank_nifty = None

        self.last_candle_time = None

        self.data_date = None

    # ========================================================
    # CURRENT TIME
    # ========================================================

    def now(self):

        return datetime.now(
            IST
        )

    # ========================================================
    # PARSE HH:MM
    # ========================================================

    @staticmethod
    def parse_time(value):

        hour, minute = map(
            int,
            value.split(":")
        )

        return dt_time(
            hour,
            minute
        )

    # ========================================================
    # MARKET STATE
    # ========================================================

    def get_market_state(self):

        current_time = (
            self.now().time()
        )

        pre_market = (
            self.parse_time(
                PRE_MARKET_TIME
            )
        )

        market_open = (
            self.parse_time(
                MARKET_OPEN_TIME
            )
        )

        market_close = (
            self.parse_time(
                MARKET_CLOSE_TIME
            )
        )

        monitor_close = (
            self.parse_time(
                MONITOR_CLOSE_TIME
            )
        )

        if current_time < pre_market:

            return "CLOSED"

        if (
            pre_market
            <= current_time
            < market_open
        ):

            return "PRE-MARKET"

        if (
            market_open
            <= current_time
            < market_close
        ):

            return "RUNNING"

        if (
            market_close
            <= current_time
            <= monitor_close
        ):

            return "CLOSED"

        return "CLOSED"

    # ========================================================
    # PAPER TRADING SESSION
    # ========================================================
    #
    # NEW PAPER BUYs are allowed ONLY:
    #
    # 10:00 <= time < 15:00
    #
    # Existing OPEN trades can continue to be monitored.

    def is_paper_trading_session(self):

        current_time = (
            self.now().time()
        )

        paper_start = dt_time(
            10,
            0
        )

        paper_end = dt_time(
            15,
            0
        )

        return (
            paper_start
            <= current_time
            <
            paper_end
        )

    # ========================================================
    # READ MARKET DATA
    # ========================================================

    def read_data(self):

        data_1m = (
            self.historical
            .get_1_minute_candles()
        )

        data_15m = (
            self.historical
            .get_15_minute_candles()
        )

        candles_1m = (
            data_1m.get(
                "candles",
                []
            )
        )

        candles_15m = (
            data_15m.get(
                "candles",
                []
            )
        )

        if not candles_1m:

            raise RuntimeError(
                "No 1-minute candles received."
            )

        if not candles_15m:

            raise RuntimeError(
                "No 15-minute candles received."
            )

        closes_1m = (
            candle_closes_to_series(
                candles_1m
            )
        )

        closes_15m = (
            candle_closes_to_series(
                candles_15m
            )
        )

        self.last_rsi_1m = (
            calculate_latest_rsi(
                closes_1m,
                period=RSI_PERIOD,
            )
        )

        self.last_rsi_15m = (
            calculate_latest_rsi(
                closes_15m,
                period=RSI_PERIOD,
            )
        )

        self.last_bank_nifty = float(
            candles_1m[-1][4]
        )

        self.last_candle_time = (
            candles_1m[-1][0]
        )

        self.data_date = (
            self.historical.data_date
        )

    # ========================================================
    # SIX RSI CONDITIONS
    # ========================================================

    def get_conditions(self):

        rsi_1m = self.last_rsi_1m

        rsi_15m = self.last_rsi_15m

        conditions = set()

        # ----------------------------------------------------
        # CONDITION 1
        # 1M <= 30
        # ----------------------------------------------------

        if (
            rsi_1m
            <=
            RSI_1_BULLISH
        ):

            conditions.add(
                "1M_OVERSOLD"
            )

        # ----------------------------------------------------
        # CONDITION 2
        # 1M >= 70
        # ----------------------------------------------------

        if (
            rsi_1m
            >=
            RSI_1_BEARISH
        ):

            conditions.add(
                "1M_OVERBOUGHT"
            )

        # ----------------------------------------------------
        # CONDITION 3
        # 15M < 30
        # ----------------------------------------------------

        if (
            rsi_15m
            <
            RSI_15_EXTREME_OVERSOLD
        ):

            conditions.add(
                "15M_EXTREME_OVERSOLD"
            )

        # ----------------------------------------------------
        # CONDITION 4
        # 15M > 70
        # ----------------------------------------------------

        if (
            rsi_15m
            >
            RSI_15_EXTREME_OVERBOUGHT
        ):

            conditions.add(
                "15M_EXTREME_OVERBOUGHT"
            )

        # ----------------------------------------------------
        # CONDITION 5
        #
        # 1M < 20
        # AND
        # 15M < 25
        # ----------------------------------------------------

        if (
            rsi_1m < 20
            and
            rsi_15m < 25
        ):

            conditions.add(
                "BULLISH"
            )

        # ----------------------------------------------------
        # CONDITION 6
        #
        # 1M > 80
        # AND
        # 15M > 75
        # ----------------------------------------------------

        if (
            rsi_1m > 80
            and
            rsi_15m > 75
        ):

            conditions.add(
                "BEARISH"
            )

        return conditions

    # ========================================================
    # RESULT
    # ========================================================

    @staticmethod
    def result(condition):

        return (
            "MET"
            if condition
            else
            "NOT MET"
        )

    # ========================================================
    # FULL RSI REPORT
    # ========================================================

    def build_full_report(
        self,
        status
    ):

        rsi_1m = self.last_rsi_1m
        rsi_15m = self.last_rsi_15m

        c1 = (
            rsi_1m <= 30
        )

        c2 = (
            rsi_1m >= 70
        )

        c3 = (
            rsi_15m < 30
        )

        c4 = (
            rsi_15m > 70
        )

        c5_1m = (
            rsi_1m < 20
        )

        c5_15m = (
            rsi_15m < 25
        )

        c6_1m = (
            rsi_1m > 80
        )

        c6_15m = (
            rsi_15m > 75
        )

        generated_time = (
            self.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        return (

            "=" * 90
            + "\n"

            + "              BANK NIFTY RSI - "
            + f"{status}"

            + "\n"

            + "=" * 90
            + "\n\n"

            + "============================= 1 MIN ===============================\n"

            + f"1) 1M <= 30 → "
            + f"{self.result(c1)}\n"

            + f"2) 1M >= 70 → "
            + f"{self.result(c2)}\n\n"

            + "============================ 15 MIN ===============================\n"

            + f"3) 15M < 30 → "
            + f"{self.result(c3)}\n"

            + f"4) 15M > 70 → "
            + f"{self.result(c4)}\n\n"

            + "======================== 1 MIN + 15 MIN ===========================\n"

            + "5) BULLISH\n"

            + f"   1M < 20 → "
            + f"{self.result(c5_1m)}"

            + f" | 15M < 25 → "
            + f"{self.result(c5_15m)}\n\n"

            + "6) BEARISH\n"

            + f"   1M > 80 → "
            + f"{self.result(c6_1m)}"

            + f" | 15M > 75 → "
            + f"{self.result(c6_15m)}\n\n"

            + "========================== CURRENT VALUE ==========================\n"

            + f"   1M         : {rsi_1m:.2f}\n"

            + f"   15M        : {rsi_15m:.2f}\n"

            + f"   Bank Nifty : {self.last_bank_nifty:,.2f}\n"

            + f"   Candle     : {self.last_candle_time}\n"

            + f"   Data Date  : {self.data_date}\n"

            + f"   Current    : {generated_time}\n\n"

            + "=" * 90
        )

    # ========================================================
    # SEND EMAIL
    # ========================================================

    def send_email(
        self,
        subject,
        body
    ):

        if not EMAIL_ENABLED:
            return False

        if self.email is None:
            return False

        try:

            self.email.send(
                subject=subject,
                body=body
            )

            return True

        except Exception:

            return False

    # ========================================================
    # PAPER BUY EMAIL
    # ========================================================

    def send_paper_purchase_email(
        self,
        trade
    ):

        if not EMAIL_ENABLED:
            return

        if not EMAIL_ON_PAPER_PURCHASE:
            return

        current_time = (
            self.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        subject = (
            "BANK NIFTY PAPER BUY - "
            f"{trade['strategy']} - "
            f"{trade['option_type']} - "
            f"{current_time}"
        )

        body = (

            "=" * 70
            + "\n"

            + "       BANK NIFTY PAPER TRADE - VIRTUAL BUY\n"

            + "=" * 70
            + "\n\n"

            + f"Strategy       : {trade['strategy']}\n"
            + f"Signal         : {trade['signal']}\n"
            + f"Option         : {trade['option_type']}\n"
            + f"Strike         : {trade['strike']:.0f}\n"
            + f"Trading Symbol : {trade['trading_symbol']}\n\n"

            + f"Entry LTP      : {trade['entry_price']:.2f}\n"
            + f"Target         : {trade['target_price']:.2f}\n"
            + f"Target Points  : +{trade['target_points']:.2f}\n\n"

            + f"1M RSI         : {self.last_rsi_1m:.2f}\n"
            + f"15M RSI        : {self.last_rsi_15m:.2f}\n"
            + f"Bank Nifty     : {self.last_bank_nifty:,.2f}\n\n"

            + f"Quantity       : {PAPER_LOTS}\n"
            + f"Entry Time     : {current_time}\n\n"

            + "REAL ORDER     : NO\n"
            + "TRADE TYPE     : PAPER / VIRTUAL\n\n"

            + "=" * 70
        )

        self.send_email(
            subject,
            body
        )

    # ========================================================
    # PAPER SELL EMAIL
    # ========================================================

    def send_paper_sell_email(
        self,
        trade_id
    ):

        if not EMAIL_ENABLED:
            return

        if not EMAIL_ON_PAPER_SELL:
            return

        if self.paper_trader is None:
            return

        connection = (
            self.paper_trader._connect()
        )

        try:

            cursor = connection.execute(
                """
                SELECT
                    strategy,
                    signal,
                    option_type,
                    strike,
                    trading_symbol,
                    entry_time,
                    entry_price,
                    target_price,
                    target_points,
                    exit_time,
                    exit_price,
                    quantity,
                    pnl_points,
                    pnl_value,
                    exit_reason,
                    entry_rsi_1m,
                    entry_rsi_15m,
                    entry_bank_nifty

                FROM paper_trades

                WHERE id = ?

                AND status = 'CLOSED'
                """,
                (
                    trade_id,
                ),
            )

            trade = cursor.fetchone()

        finally:

            connection.close()

        if trade is None:
            return

        (
            strategy,
            signal,
            option_type,
            strike,
            symbol,
            entry_time,
            entry_price,
            target_price,
            target_points,
            exit_time,
            exit_price,
            quantity,
            pnl_points,
            pnl_value,
            exit_reason,
            entry_rsi_1m,
            entry_rsi_15m,
            entry_bank_nifty,
        ) = trade

        subject = (
            "BANK NIFTY PAPER SELL - "
            f"{strategy} - "
            f"{option_type} - "
            f"{exit_time}"
        )

        body = (

            "=" * 70
            + "\n"

            + "       BANK NIFTY PAPER TRADE - VIRTUAL SELL\n"

            + "=" * 70
            + "\n\n"

            + f"Trade ID       : {trade_id}\n"
            + f"Strategy       : {strategy}\n"
            + f"Signal         : {signal}\n"
            + f"Option         : {option_type}\n"
            + f"Strike         : {strike:.0f}\n"
            + f"Trading Symbol : {symbol}\n\n"

            + f"Entry Price    : {entry_price:.2f}\n"
            + f"Target Price   : {target_price:.2f}\n"
            + f"Target Points  : +{target_points:.2f}\n"
            + f"Exit Price     : {exit_price:.2f}\n\n"

            + f"P&L Points     : {pnl_points:+.2f}\n"
            + f"Virtual P&L    : {pnl_value:+.2f}\n\n"

            + f"Entry RSI 1M   : {entry_rsi_1m:.2f}\n"
            + f"Entry RSI 15M  : {entry_rsi_15m:.2f}\n"
            + f"Entry BankNifty: {entry_bank_nifty:,.2f}\n\n"

            + f"Quantity       : {quantity}\n"
            + f"Entry Time     : {entry_time}\n"
            + f"Exit Time      : {exit_time}\n"
            + f"Exit Reason    : {exit_reason}\n\n"

            + "REAL ORDER     : NO\n"
            + "TRADE TYPE     : PAPER / VIRTUAL\n\n"

            + "=" * 70
        )

        self.send_email(
            subject,
            body
        )

    # ========================================================
    # SIX PAPER TRADING SIGNALS
    # ========================================================

    def get_paper_signals(self):

        rsi_1m = self.last_rsi_1m
        rsi_15m = self.last_rsi_15m

        signals = []

        # ====================================================
        # CONDITION 1
        # 1M <= 30 -> CE +15
        # ====================================================

        if (
            rsi_1m
            <=
            RSI_1_BULLISH
        ):

            signals.append({

                "condition_number": 1,

                "condition_text":
                    "1M <= 30",

                "strategy":
                    "1M_CE",

                "signal":
                    "BULLISH",

                "option_type":
                    "CE",

                "target_points":
                    PAPER_1M_TARGET_POINTS,

            })

        # ====================================================
        # CONDITION 2
        # 1M >= 70 -> PE +15
        # ====================================================

        if (
            rsi_1m
            >=
            RSI_1_BEARISH
        ):

            signals.append({

                "condition_number": 2,

                "condition_text":
                    "1M >= 70",

                "strategy":
                    "1M_PE",

                "signal":
                    "BEARISH",

                "option_type":
                    "PE",

                "target_points":
                    PAPER_1M_TARGET_POINTS,

            })

        # ====================================================
        # CONDITION 3
        # 15M < 30 -> CE +45
        # ====================================================

        if (
            rsi_15m
            <
            RSI_15_EXTREME_OVERSOLD
        ):

            signals.append({

                "condition_number": 3,

                "condition_text":
                    "15M < 30",

                "strategy":
                    "15M_CE",

                "signal":
                    "BULLISH",

                "option_type":
                    "CE",

                "target_points":
                    PAPER_15M_TARGET_POINTS,

            })

        # ====================================================
        # CONDITION 4
        # 15M > 70 -> PE +45
        # ====================================================

        if (
            rsi_15m
            >
            RSI_15_EXTREME_OVERBOUGHT
        ):

            signals.append({

                "condition_number": 4,

                "condition_text":
                    "15M > 70",

                "strategy":
                    "15M_PE",

                "signal":
                    "BEARISH",

                "option_type":
                    "PE",

                "target_points":
                    PAPER_15M_TARGET_POINTS,

            })

        # ====================================================
        # CONDITION 5
        # 1M < 20 AND 15M < 25 -> CE +75
        # ====================================================

        if (
            rsi_1m < 20
            and
            rsi_15m < 25
        ):

            signals.append({

                "condition_number": 5,

                "condition_text":
                    "1M < 20 AND 15M < 25",

                "strategy":
                    "COMBINED_CE",

                "signal":
                    "BULLISH",

                "option_type":
                    "CE",

                "target_points":
                    PAPER_COMBINED_TARGET_POINTS,

            })

        # ====================================================
        # CONDITION 6
        # 1M > 80 AND 15M > 75 -> PE +75
        # ====================================================

        if (
            rsi_1m > 80
            and
            rsi_15m > 75
        ):

            signals.append({

                "condition_number": 6,

                "condition_text":
                    "1M > 80 AND 15M > 75",

                "strategy":
                    "COMBINED_PE",

                "signal":
                    "BEARISH",

                "option_type":
                    "PE",

                "target_points":
                    PAPER_COMBINED_TARGET_POINTS,

            })

        return signals

    # ========================================================
    # NEAREST STRIKE
    # ========================================================

    def get_nearest_strike(
        self,
        signal
    ):

        price = float(
            self.last_bank_nifty
        )

        step = (
            PAPER_STRIKE_STEP
        )

        return (
            round(
                price / step
            )
            * step
        )

    # ========================================================
    # OPTION LTP
    # ========================================================

    def get_option_ltp(
        self,
        option_type,
        strike
    ):

        method = getattr(
            self.historical,
            "get_option_ltp",
            None
        )

        if method is None:

            return None

        try:

            result = method(
                option_type=option_type,
                strike=strike,
            )

            if not result:
                return None

            if not isinstance(
                result,
                dict
            ):
                return None

            ltp = result.get(
                "ltp"
            )

            symbol = result.get(
                "trading_symbol"
            )

            if ltp is None:
                return None

            if symbol is None:
                return None

            return {

                "trading_symbol":
                    symbol,

                "ltp":
                    float(ltp),
            }

        except Exception:

            return None

    # ========================================================
    # DISPLAY PAPER SIGNAL
    # ========================================================

    def display_paper_signal(
        self,
        signal,
        strike,
        option=None
    ):

        # Kept for future use.
        # No normal RSI display.

        pass

    # ========================================================
    # PRINT CONDITION MET
    # ========================================================

    def print_condition_met(
        self,
        signal
    ):

        print()
        print("=" * 70)

        print(
            f"CONDITION {signal['condition_number']} MET"
        )

        print("=" * 70)

        print(
            f"Condition      : "
            f"{signal['condition_text']}"
        )

        print(
            f"Strategy       : "
            f"{signal['strategy']}"
        )

        print(
            f"Signal         : "
            f"{signal['signal']}"
        )

        print(
            f"Option         : "
            f"{signal['option_type']}"
        )

        print(
            f"Target Points  : "
            f"+{signal['target_points']}"
        )

        print(
            f"1M RSI         : "
            f"{self.last_rsi_1m:.2f}"
        )

        print(
            f"15M RSI        : "
            f"{self.last_rsi_15m:.2f}"
        )

        print(
            f"Bank Nifty     : "
            f"{self.last_bank_nifty:,.2f}"
        )

        print(
            f"Candle         : "
            f"{self.last_candle_time}"
        )

        print("=" * 70)

    # ========================================================
    # PAPER TRADING
    # ========================================================

    def process_paper_trading(self):

        if not PAPER_TRADING_ENABLED:
            return

        if self.paper_trader is None:
            return

        # ====================================================
        # EXISTING OPEN TRADES
        # ====================================================
        #
        # Existing trades continue to be monitored.
        # This happens even after 15:00.
        #
        # New BUYs are restricted separately below.

        open_trades = (
            self.paper_trader
            .get_open_trades()
        )

        option_prices = {}

        get_price = getattr(
            self.historical,
            "get_option_ltp_by_symbol",
            None
        )

        if get_price is not None:

            for trade in open_trades:

                trading_symbol = trade[5]

                if not trading_symbol:
                    continue

                try:

                    ltp = get_price(
                        trading_symbol
                    )

                    if ltp is not None:

                        option_prices[
                            trading_symbol
                        ] = float(ltp)

                except Exception:

                    continue

        closed_trade_ids = []

        if option_prices:

            closed_trade_ids = (
                self.paper_trader
                .check_targets(
                    option_prices
                )
            )

        # ====================================================
        # PAPER SELL
        # ====================================================

        for trade_id in closed_trade_ids:

            print()
            print("=" * 70)

            print(
                "PAPER SELL COMPLETED"
            )

            print(
                f"Trade ID      : {trade_id}"
            )

            print(
                f"1M RSI        : "
                f"{self.last_rsi_1m:.2f}"
            )

            print(
                f"15M RSI       : "
                f"{self.last_rsi_15m:.2f}"
            )

            print(
                f"Bank Nifty    : "
                f"{self.last_bank_nifty:,.2f}"
            )

            print(
                f"Candle        : "
                f"{self.last_candle_time}"
            )

            print(
                "REAL ORDER    : NO"
            )

            print("=" * 70)

            self.send_paper_sell_email(
                trade_id
            )

        # ====================================================
        # NEW PAPER BUY SESSION
        # ====================================================
        #
        # NO NEW BUY before 10:00
        # NO NEW BUY at/after 15:00
        #
        # Existing trades above are still monitored.

        if not self.is_paper_trading_session():

            return

        # ====================================================
        # CURRENT SIX CONDITIONS
        # ====================================================

        signals = (
            self.get_paper_signals()
        )

        if not signals:

            return

        # ====================================================
        # PROCESS SIGNALS
        # ====================================================

        for signal in signals:

            strategy = signal[
                "strategy"
            ]

            signal_name = signal[
                "signal"
            ]

            option_type = signal[
                "option_type"
            ]

            target_points = signal[
                "target_points"
            ]

            # ------------------------------------------------
            # STRATEGY LOCK
            # ------------------------------------------------
            #
            # If this strategy already has an OPEN trade,
            # do not BUY again.
            #
            # Once the trade is SOLD, this check becomes
            # available again automatically.

            existing_trade = (
                self.paper_trader
                .get_open_trade(
                    strategy
                )
            )

            if existing_trade is not None:

                continue

            # ------------------------------------------------
            # CONDITION MET
            # ------------------------------------------------

            self.print_condition_met(
                signal
            )

            # ------------------------------------------------
            # STRIKE
            # ------------------------------------------------

            strike = (
                self.get_nearest_strike(
                    signal_name
                )
            )

            # ------------------------------------------------
            # OPTION LTP
            # ------------------------------------------------

            option = (
                self.get_option_ltp(
                    option_type,
                    strike
                )
            )

            if option is None:

                continue

            trading_symbol = option[
                "trading_symbol"
            ]

            entry_price = float(
                option["ltp"]
            )

            target_price = (
                entry_price
                +
                target_points
            )

            # ------------------------------------------------
            # PAPER BUY
            # ------------------------------------------------

            opened = (
                self.paper_trader
                .open_trade(

                    strategy=strategy,
                    signal=signal_name,
                    option_type=option_type,
                    strike=strike,
                    trading_symbol=trading_symbol,
                    entry_price=entry_price,
                    target_points=target_points,
                    rsi_1m=self.last_rsi_1m,
                    rsi_15m=self.last_rsi_15m,
                    bank_nifty=self.last_bank_nifty,
                )
            )

            # ------------------------------------------------
            # CONFIRMED PAPER BUY
            # ------------------------------------------------

            if opened:

                print()
                print("=" * 70)

                print(
                    "PAPER BUY CREATED"
                )

                print(
                    f"Condition      : "
                    f"{signal['condition_number']} - "
                    f"{signal['condition_text']}"
                )

                print(
                    f"Strategy       : "
                    f"{strategy}"
                )

                print(
                    f"Signal         : "
                    f"{signal_name}"
                )

                print(
                    f"Option         : "
                    f"{option_type}"
                )

                print(
                    f"Strike         : "
                    f"{strike}"
                )

                print(
                    f"Trading Symbol : "
                    f"{trading_symbol}"
                )

                print(
                    f"Entry LTP      : "
                    f"{entry_price:.2f}"
                )

                print(
                    f"Target         : "
                    f"{target_price:.2f}"
                )

                print(
                    f"Target Points  : "
                    f"+{target_points}"
                )

                print(
                    f"1M RSI         : "
                    f"{self.last_rsi_1m:.2f}"
                )

                print(
                    f"15M RSI        : "
                    f"{self.last_rsi_15m:.2f}"
                )

                print(
                    f"Bank Nifty     : "
                    f"{self.last_bank_nifty:,.2f}"
                )

                print(
                    f"Candle         : "
                    f"{self.last_candle_time}"
                )

                print(
                    "REAL ORDER     : NO"
                )

                print("=" * 70)

                trade = {

                    "condition_number":
                        signal[
                            "condition_number"
                        ],

                    "condition_text":
                        signal[
                            "condition_text"
                        ],

                    "strategy":
                        strategy,

                    "signal":
                        signal_name,

                    "option_type":
                        option_type,

                    "strike":
                        strike,

                    "trading_symbol":
                        trading_symbol,

                    "entry_price":
                        entry_price,

                    "target_price":
                        target_price,

                    "target_points":
                        target_points,
                }

                self.send_paper_purchase_email(
                    trade
                )

    # ========================================================
    # NORMAL DISPLAY
    # ========================================================

    def display(self):

        # Normal RSI display remains disabled.
        #
        # Only PAPER BUY / PAPER SELL events are printed.

        pass

    # ========================================================
    # PROCESS
    # ========================================================

    def process(self):

        self.read_data()

        # ----------------------------------------------------
        # PAPER TRADING
        # ----------------------------------------------------

        self.process_paper_trading()

        # ----------------------------------------------------
        # NORMAL RSI DISPLAY DISABLED
        # ----------------------------------------------------

        # self.display()

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        try:

            while True:

                try:

                    self.process()

                    time.sleep(
                        CHECK_INTERVAL_SECONDS
                    )

                except Exception:

                    # All routine monitor errors are silent.
                    time.sleep(
                        CHECK_INTERVAL_SECONDS
                    )

        except KeyboardInterrupt:

            pass


# ============================================================
# MAIN
# ============================================================

def main():

    monitor = (
        ContinuousBankNiftyMonitor()
    )

    monitor.run()


if __name__ == "__main__":

    main()