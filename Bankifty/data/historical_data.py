"""
Bank Nifty Historical Data

Purpose
-------
Fetch Bank Nifty historical candles for RSI calculation.

Date selection
--------------
Before 09:00 IST:
    Use previous trading day.

From 09:00 IST onward:
    Use today's data.

RSI warm-up
------------
For the current trading day, previous trading-day candles
are automatically added when required to provide enough
history for RSI(14).

Current candle
--------------
The latest candle from TODAY remains the latest/current candle.

Example at 10:51:

1-minute:
    Previous-day warm-up
    +
    Today 09:15 -> 10:51

15-minute:
    Previous-day warm-up
    +
    Today 09:15 -> 10:45

The latest 15-minute candle remains 10:45.
"""

from datetime import (
    datetime,
    timedelta,
)

import calendar

import contextlib
import io

from growwapi import GrowwAPI

from config.settings import (
    GROWW_API_KEY,
    GROWW_API_SECRET,

    DATA_SELECTION_TIME,

    HISTORICAL_START_TIME,
    HISTORICAL_END_TIME,

    HISTORICAL_LOOKBACK_DAYS,

    RSI_PERIOD,
)


class GrowwHistoricalData:

    def __init__(self):

        self.groww = None

        # Actual trading date being monitored.
        self.data_date = None

    # ========================================================
    # CONNECT
    # ========================================================

    def connect(self):

        with contextlib.redirect_stdout(
            io.StringIO()
        ):

            access_token = (
                GrowwAPI.get_access_token(
                    api_key=GROWW_API_KEY,
                    secret=GROWW_API_SECRET,
                )
            )

            self.groww = GrowwAPI(
                access_token
            )

    # ========================================================
    # CURRENT DATE
    # ========================================================

    @staticmethod
    def get_selected_date():

        now = datetime.now()

        selection_time = (
            datetime.strptime(
                DATA_SELECTION_TIME,
                "%H:%M",
            ).time()
        )

        today = now.date()

        # ----------------------------------------------------
        # Before 09:00
        # ----------------------------------------------------

        if now.time() < selection_time:

            return (
                today
                -
                timedelta(days=1)
            )

        # ----------------------------------------------------
        # 09:00 onward
        # ----------------------------------------------------

        return today

    # ========================================================
    # MARKET TIMES
    # ========================================================

    @staticmethod
    def get_market_times(
        selected_date=None,
    ):

        if selected_date is None:

            selected_date = (
                GrowwHistoricalData
                .get_selected_date()
            )

        start_clock = (
            datetime.strptime(
                HISTORICAL_START_TIME,
                "%H:%M",
            ).time()
        )

        end_clock = (
            datetime.strptime(
                HISTORICAL_END_TIME,
                "%H:%M",
            ).time()
        )

        start_time = datetime.combine(
            selected_date,
            start_clock,
        )

        end_time = datetime.combine(
            selected_date,
            end_clock,
        )

        return (
            start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            end_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )

    # ========================================================
    # REQUEST 1-MINUTE DATA
    # ========================================================

    def _request_1_minute(
        self,
        selected_date,
    ):

        start_time, end_time = (
            self.get_market_times(
                selected_date
            )
        )

        return (
            self.groww
            .get_historical_candles(

                exchange=(
                    self.groww.EXCHANGE_NSE
                ),

                segment=(
                    self.groww.SEGMENT_CASH
                ),

                groww_symbol=(
                    "NSE-BANKNIFTY"
                ),

                start_time=start_time,

                end_time=end_time,

                candle_interval=(
                    self.groww
                    .CANDLE_INTERVAL_MIN_1
                ),
            )
        )

    # ========================================================
    # REQUEST 15-MINUTE DATA
    # ========================================================

    def _request_15_minute(
        self,
        selected_date,
    ):

        start_time, end_time = (
            self.get_market_times(
                selected_date
            )
        )

        return (
            self.groww
            .get_historical_candles(

                exchange=(
                    self.groww.EXCHANGE_NSE
                ),

                segment=(
                    self.groww.SEGMENT_CASH
                ),

                groww_symbol=(
                    "NSE-BANKNIFTY"
                ),

                start_time=start_time,

                end_time=end_time,

                candle_interval=(
                    self.groww
                    .CANDLE_INTERVAL_MIN_15
                ),
            )
        )

    # ========================================================
    # CHECK CANDLES
    # ========================================================

    @staticmethod
    def _get_candles(
        data,
    ):

        if not data:

            return []

        return data.get(
            "candles",
            []
        )

    # ========================================================
    # CANDLE TIMESTAMP
    # ========================================================

    @staticmethod
    def _candle_timestamp(
        candle,
    ):

        if not candle:

            return None

        return candle[0]

    # ========================================================
    # COMBINE CANDLES
    # ========================================================

    @staticmethod
    def _combine_candles(
        previous_candles,
        current_candles,
    ):

        combined = []

        seen = set()

        for candle in (
            previous_candles
            +
            current_candles
        ):

            timestamp = (
                GrowwHistoricalData
                ._candle_timestamp(
                    candle
                )
            )

            if timestamp is None:

                continue

            if timestamp in seen:

                continue

            seen.add(
                timestamp
            )

            combined.append(
                candle
            )

        # ----------------------------------------------------
        # Chronological order
        # ----------------------------------------------------

        combined.sort(
            key=lambda x: x[0]
        )

        return combined

    # ========================================================
    # FIND PREVIOUS TRADING DAY
    # ========================================================

    def _get_previous_trading_day(
        self,
        current_date,
    ):

        for offset in range(
            1,
            HISTORICAL_LOOKBACK_DAYS + 1,
        ):

            candidate_date = (
                current_date
                -
                timedelta(days=offset)
            )

            data_15m = (
                self._request_15_minute(
                    candidate_date
                )
            )

            candles = (
                self._get_candles(
                    data_15m
                )
            )

            if candles:

                return candidate_date

        return None

    # ========================================================
    # GET PREVIOUS DAY WARM-UP
    # ========================================================

    def _get_warmup_data(
        self,
        current_date,
    ):

        previous_date = (
            self._get_previous_trading_day(
                current_date
            )
        )

        if previous_date is None:

            return (
                [],
                [],
                None,
            )

        previous_1m = (
            self._request_1_minute(
                previous_date
            )
        )

        previous_15m = (
            self._request_15_minute(
                previous_date
            )
        )

        return (
            self._get_candles(
                previous_1m
            ),
            self._get_candles(
                previous_15m
            ),
            previous_date,
        )

    # ========================================================
    # FIND DATA DATE BEFORE 09:00
    # ========================================================

    def _find_previous_data_date(
        self,
    ):

        selected_date = (
            self.get_selected_date()
        )

        for offset in range(
            HISTORICAL_LOOKBACK_DAYS
        ):

            candidate = (
                selected_date
                -
                timedelta(days=offset)
            )

            data = (
                self._request_1_minute(
                    candidate
                )
            )

            candles = (
                self._get_candles(
                    data
                )
            )

            if candles:

                return candidate

        raise ValueError(
            "No Bank Nifty historical data "
            "found within configured lookback."
        )

    # ========================================================
    # 1-MINUTE DATA
    # ========================================================

    def get_1_minute_candles(
        self,
    ):

        if self.groww is None:

            self.connect()

        selected_date = (
            self.get_selected_date()
        )

        # ----------------------------------------------------
        # Before 09:00
        # ----------------------------------------------------

        now = datetime.now()

        selection_time = (
            datetime.strptime(
                DATA_SELECTION_TIME,
                "%H:%M",
            ).time()
        )

        if now.time() < selection_time:

            self.data_date = (
                self._find_previous_data_date()
            )

            return (
                self._request_1_minute(
                    self.data_date
                )
            )

        # ----------------------------------------------------
        # 09:00 onward
        # ----------------------------------------------------

        self.data_date = (
            selected_date
        )

        current_data = (
            self._request_1_minute(
                selected_date
            )
        )

        current_candles = (
            self._get_candles(
                current_data
            )
        )

        # ----------------------------------------------------
        # No current data
        # ----------------------------------------------------

        if not current_candles:

            self.data_date = (
                self._find_previous_data_date()
            )

            return (
                self._request_1_minute(
                    self.data_date
                )
            )

        # ----------------------------------------------------
        # Warm-up only needed if insufficient candles
        # ----------------------------------------------------

        minimum_candles = (
            RSI_PERIOD + 1
        )

        if len(current_candles) >= (
            minimum_candles
        ):

            return {
                "candles":
                    current_candles
            }

        # ----------------------------------------------------
        # Previous trading day
        # ----------------------------------------------------

        (
            previous_1m,
            _,
            previous_date,
        ) = self._get_warmup_data(
            selected_date
        )

        combined = (
            self._combine_candles(
                previous_1m,
                current_candles,
            )
        )

        print()
        print(
            "1M RSI warm-up:"
        )

        print(
            "  Previous date :",
            previous_date
        )

        print(
            "  Previous      :",
            len(previous_1m)
        )

        print(
            "  Today         :",
            len(current_candles)
        )

        print(
            "  Total         :",
            len(combined)
        )

        return {
            "candles":
                combined
        }

    # ========================================================
    # 15-MINUTE DATA
    # ========================================================

    def get_15_minute_candles(
        self,
    ):

        if self.groww is None:

            self.connect()

        selected_date = (
            self.get_selected_date()
        )

        # ----------------------------------------------------
        # Before 09:00
        # ----------------------------------------------------

        now = datetime.now()

        selection_time = (
            datetime.strptime(
                DATA_SELECTION_TIME,
                "%H:%M",
            ).time()
        )

        if now.time() < selection_time:

            self.data_date = (
                self._find_previous_data_date()
            )

            return (
                self._request_15_minute(
                    self.data_date
                )
            )

        # ----------------------------------------------------
        # Today's data
        # ----------------------------------------------------

        self.data_date = (
            selected_date
        )

        current_data = (
            self._request_15_minute(
                selected_date
            )
        )

        current_candles = (
            self._get_candles(
                current_data
            )
        )

        # ----------------------------------------------------
        # No current data
        # ----------------------------------------------------

        if not current_candles:

            self.data_date = (
                self._find_previous_data_date()
            )

            return (
                self._request_15_minute(
                    self.data_date
                )
            )

        # ----------------------------------------------------
        # RSI(14) requires at least 15 prices.
        #
        # At 10:51 today we only have:
        #
        # 09:15
        # 09:30
        # 09:45
        # 10:00
        # 10:15
        # 10:30
        # 10:45
        #
        # Therefore previous-day warm-up is required.
        # ----------------------------------------------------

        minimum_candles = (
            RSI_PERIOD + 1
        )

        if len(current_candles) >= (
            minimum_candles
        ):

            return {
                "candles":
                    current_candles
            }

        # ----------------------------------------------------
        # Get previous trading day
        # ----------------------------------------------------

        (
            _,
            previous_15m,
            previous_date,
        ) = self._get_warmup_data(
            selected_date
        )

        # ----------------------------------------------------
        # Combine
        # ----------------------------------------------------

        combined = (
            self._combine_candles(
                previous_15m,
                current_candles,
            )
        )

        print()
        print(
            "15M RSI warm-up:"
        )

        print(
            "  Previous date :",
            previous_date
        )

        print(
            "  Previous      :",
            len(previous_15m)
        )

        print(
            "  Today         :",
            len(current_candles)
        )

        print(
            "  Total         :",
            len(combined)
        )

        return {
            "candles":
                combined
        }

    # ========================================================
    # NEXT AVAILABLE BANK NIFTY EXPIRY
    # ========================================================

    def _get_next_bank_nifty_expiry(self):

        if self.groww is None:

            self.connect()

        today = datetime.now().date()

        expiries = []

        year = today.year
        month = today.month

        for offset in range(3):

            month_index = month - 1 + offset
            request_year = year + (month_index // 12)
            request_month = (month_index % 12) + 1

            try:

                response = self.groww.get_expiries(
                    exchange=self.groww.EXCHANGE_NSE,
                    underlying_symbol="BANKNIFTY",
                    year=request_year,
                    month=request_month,
                )

                values = response.get("expiries", []) if response else []

                expiries.extend(values)

            except Exception:

                continue

        valid = []

        for expiry in expiries:

            try:
                expiry_date = datetime.strptime(
                    expiry,
                    "%Y-%m-%d",
                ).date()

                if expiry_date >= today:
                    valid.append((expiry_date, expiry))

            except (TypeError, ValueError):

                continue

        if not valid:

            raise RuntimeError(
                "No future BANKNIFTY expiry found."
            )

        valid.sort(key=lambda item: item[0])

        return valid[0][1]

    # ========================================================
    # OPTION LTP BY STRIKE
    # ========================================================

    def get_option_ltp(
        self,
        option_type,
        strike,
    ):

        if self.groww is None:

            self.connect()

        expiry = self._get_next_bank_nifty_expiry()

        response = self.get_bank_nifty_option_chain(
            expiry
        )

        if not response:
            return None

        # SDK responses are normally already flattened, but
        # support a payload wrapper as well.
        payload = response.get("payload", response)

        strikes = payload.get("strikes", {}) if isinstance(payload, dict) else {}

        if not strikes:
            return None

        requested = float(strike)
        selected_key = None

        for key in strikes.keys():

            try:
                numeric_key = float(key)
            except (TypeError, ValueError):
                continue

            if numeric_key == requested:
                selected_key = key
                break

        if selected_key is None:
            return None

        contract = strikes.get(selected_key, {})

        if option_type not in contract:
            return None

        option = contract[option_type]

        if not isinstance(option, dict):
            return None

        ltp = option.get("ltp")
        trading_symbol = option.get("trading_symbol")

        if ltp is None or not trading_symbol:
            return None

        return {
            "trading_symbol": trading_symbol,
            "ltp": float(ltp),
            "expiry": expiry,
        }

    # ========================================================
    # OPTION LTP BY TRADING SYMBOL
    # ========================================================

    def get_option_ltp_by_symbol(
        self,
        trading_symbol,
    ):

        if self.groww is None:

            self.connect()

        if not trading_symbol:
            return None

        exchange_symbol = (
            f"NSE_{trading_symbol}"
        )

        response = self.groww.get_ltp(
            segment=self.groww.SEGMENT_FNO,
            exchange_trading_symbols=(
                exchange_symbol,
            ),
        )

        if not response:
            return None

        payload = response.get(
            "payload",
            response,
        )

        if not isinstance(payload, dict):
            return None

        value = payload.get(
            exchange_symbol
        )

        if value is None:
            # Some SDK versions may return the bare trading symbol.
            value = payload.get(
                trading_symbol
            )

        if value is None:
            return None

        if isinstance(value, dict):
            value = value.get("ltp")

        if value is None:
            return None

        return float(value)

    # ========================================================
    # OPTION CHAIN
    # ========================================================

    def get_bank_nifty_option_chain(
        self,
        expiry_date,
    ):

        if self.groww is None:

            self.connect()

        return (
            self.groww
            .get_option_chain(

                exchange=(
                    self.groww.EXCHANGE_NSE
                ),

                underlying="BANKNIFTY",

                expiry_date=expiry_date,
            )
        )

    # ========================================================
    # DISPLAY 1M
    # ========================================================

    @staticmethod
    def display_1_minute(
        data,
    ):

        candles = (
            data.get(
                "candles",
                []
            )
        )

        print()
        print("=" * 70)
        print("1-MINUTE DATA")
        print("=" * 70)

        print(
            "Number of candles:",
            len(candles)
        )

        if not candles:

            print(
                "No 1-minute candles found."
            )

            return

        print()
        print("First candle:")

        print(
            candles[0]
        )

        print()
        print("Last candle:")

        print(
            candles[-1]
        )

    # ========================================================
    # DISPLAY 15M
    # ========================================================

    @staticmethod
    def display_15_minute(
        data,
    ):

        candles = (
            data.get(
                "candles",
                []
            )
        )

        print()
        print("=" * 70)
        print("15-MINUTE DATA")
        print("=" * 70)

        print(
            "Number of candles:",
            len(candles)
        )

        if not candles:

            print(
                "No 15-minute candles found."
            )

            return

        print()
        print("First candle:")

        print(
            candles[0]
        )

        print()
        print("Last candle:")

        print(
            candles[-1]
        )

    # ========================================================
    # TEST
    # ========================================================

    def test(self):

        print()
        print("=" * 70)
        print(
            "BANK NIFTY HISTORICAL DATA TEST"
        )
        print("=" * 70)

        print()
        print(
            "Current Time:",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        print(
            "Selected Date:",
            self.get_selected_date()
        )

        one_minute = (
            self.get_1_minute_candles()
        )

        fifteen_minute = (
            self.get_15_minute_candles()
        )

        self.display_1_minute(
            one_minute
        )

        self.display_15_minute(
            fifteen_minute
        )

        print()
        print(
            "Selected Data Date:",
            self.data_date
        )

        return (
            one_minute,
            fifteen_minute,
        )


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        historical = (
            GrowwHistoricalData()
        )

        historical.test()

        print()
        print("=" * 70)
        print(
            "HISTORICAL DATA TEST : SUCCESS"
        )
        print("=" * 70)

    except Exception as error:

        print()
        print("=" * 70)
        print(
            "HISTORICAL DATA TEST : FAILED"
        )
        print("=" * 70)

        print(
            "Error type:",
            type(error).__name__
        )

        print(
            "Error:",
            error
        )

        print("=" * 70)


if __name__ == "__main__":

    main()