"""
Bank Nifty RSI Monitor

Reads Bank Nifty historical candles from Groww
and calculates:

1-minute RSI(14)
15-minute RSI(14)

ALERT ONLY
No orders.
"""

from datetime import datetime

from data.historical_data import GrowwHistoricalData
from indicators.rsi import (
    candle_closes_to_series,
    calculate_latest_rsi,
)


# ============================================================
# RSI MONITOR
# ============================================================

class BankNiftyRSIMonitor:

    def __init__(self):

        self.market_data = (
            GrowwHistoricalData()
        )

    # ========================================================
    # CALCULATE RSI
    # ========================================================

    def calculate(self):

        print()
        print("=" * 70)
        print("BANK NIFTY RSI MONITOR")
        print("=" * 70)

        # ----------------------------------------------------
        # Get Groww candles
        # ----------------------------------------------------

        one_minute_data = (
            self.market_data
            .get_1_minute_candles()
        )

        fifteen_minute_data = (
            self.market_data
            .get_15_minute_candles()
        )

        # ----------------------------------------------------
        # Extract candles
        # ----------------------------------------------------

        candles_1m = (
            one_minute_data
            .get("candles", [])
        )

        candles_15m = (
            fifteen_minute_data
            .get("candles", [])
        )

        if not candles_1m:
            raise ValueError(
                "No 1-minute candles received."
            )

        if not candles_15m:
            raise ValueError(
                "No 15-minute candles received."
            )

        # ----------------------------------------------------
        # Convert closes
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Calculate RSI
        # ----------------------------------------------------

        rsi_1m = calculate_latest_rsi(
            closes_1m,
            period=14,
        )

        rsi_15m = calculate_latest_rsi(
            closes_15m,
            period=14,
        )

        # ----------------------------------------------------
        # Latest Bank Nifty price
        # ----------------------------------------------------

        bank_nifty = float(
            candles_1m[-1][4]
        )

        timestamp = candles_1m[-1][0]

        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        print()
        print(
            "Candle Time       :",
            timestamp
        )

        print(
            "Bank Nifty        :",
            f"{bank_nifty:,.2f}"
        )

        print(
            "1M RSI(14)        :",
            f"{rsi_1m:.2f}"
        )

        print(
            "15M RSI(14)       :",
            f"{rsi_15m:.2f}"
        )

        print()
        print(
            "Local Check Time  :",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        print()
        print("=" * 70)

        return {
            "timestamp": timestamp,
            "bank_nifty": bank_nifty,
            "rsi_1m": rsi_1m,
            "rsi_15m": rsi_15m,
        }


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        monitor = BankNiftyRSIMonitor()

        result = monitor.calculate()

        print()
        print("RSI CALCULATION : SUCCESS")

        print()
        print(result)

    except Exception as error:

        print()
        print("=" * 70)
        print("RSI MONITOR FAILED")
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