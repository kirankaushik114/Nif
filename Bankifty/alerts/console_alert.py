"""
Console alert system.
"""

from datetime import datetime


def show_market_status(
    bank_nifty: float,
    rsi_1m: float,
    rsi_15m: float,
    signals: list[dict],
) -> None:

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print("=" * 65)
    print("BANK NIFTY RSI MONITOR")
    print("=" * 65)

    print(f"Time       : {now}")
    print(f"Bank Nifty : {bank_nifty:.2f}")
    print(f"1M RSI     : {rsi_1m:.2f}")
    print(f"15M RSI    : {rsi_15m:.2f}")

    print("-" * 65)

    if not signals:
        print("STATUS     : WAIT")
    else:
        print("SIGNALS:")

        for signal in signals:
            print(
                f"  [{signal['level']}] "
                f"{signal['type']} "
                f"-> {signal['message']}"
            )

    print("=" * 65)
