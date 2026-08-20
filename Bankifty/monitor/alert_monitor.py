"""
Bank Nifty RSI Alert Monitor

ALERT ONLY
No orders are placed.
"""

from data.historical_data import GrowwHistoricalData
from indicators.rsi import (
    candle_closes_to_series,
    calculate_latest_rsi,
)
from signals.rsi_signals import check_signals


class BankNiftyAlertMonitor:

    def __init__(self):

        self.market_data = GrowwHistoricalData()

    # ========================================================
    # CHECK MARKET
    # ========================================================

    def check_market(self):

        print()
        print("=" * 70)
        print("BANK NIFTY RSI ALERT MONITOR")
        print("=" * 70)

        # ----------------------------------------------------
        # Get candles
        # ----------------------------------------------------

        data_1m = (
            self.market_data
            .get_1_minute_candles()
        )

        data_15m = (
            self.market_data
            .get_15_minute_candles()
        )

        candles_1m = data_1m.get(
            "candles",
            []
        )

        candles_15m = data_15m.get(
            "candles",
            []
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
        # Convert close prices
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

        candle_time = candles_1m[-1][0]

        # ----------------------------------------------------
        # Check signals
        # ----------------------------------------------------

        signals = check_signals(
            rsi_1m=rsi_1m,
            rsi_15m=rsi_15m,
        )

        # ----------------------------------------------------
        # Display market
        # ----------------------------------------------------

        print()
        print(
            "Candle Time :",
            candle_time
        )

        print(
            "Bank Nifty  :",
            f"{bank_nifty:,.2f}"
        )

        print(
            "1M RSI(14)  :",
            f"{rsi_1m:.2f}"
        )

        print(
            "15M RSI(14) :",
            f"{rsi_15m:.2f}"
        )

        # ----------------------------------------------------
        # Display alerts
        # ----------------------------------------------------

        print()
        print("-" * 70)

        if signals:

            print("🚨 RSI ALERTS")

            print("-" * 70)

            for signal in signals:

                print(
                    f"🔔 {signal['type']}"
                )

                print(
                    f"   {signal['message']}"
                )

                print()

        else:

            print("STATUS : NO ALERT")

        print("-" * 70)

        return {
            "bank_nifty": bank_nifty,
            "candle_time": candle_time,
            "rsi_1m": rsi_1m,
            "rsi_15m": rsi_15m,
            "signals": signals,
        }


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        monitor = BankNiftyAlertMonitor()

        result = monitor.check_market()

        print()
        print("=" * 70)
        print("MONITOR CHECK COMPLETE")
        print("=" * 70)

    except Exception as error:

        print()
        print("=" * 70)
        print("MONITOR ERROR")
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