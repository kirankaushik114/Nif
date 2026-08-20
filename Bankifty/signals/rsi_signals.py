"""
Bank Nifty RSI Alert Rules

ALERT ONLY.
No orders.
"""


# ============================================================
# CHECK RSI CONDITIONS
# ============================================================

def check_signals(
    rsi_1m: float,
    rsi_15m: float,
):
    """
    Check all Bank Nifty RSI alert conditions.

    Rules:

    1. 15M RSI < 20
       Extreme Oversold

    2. 15M RSI > 80
       Extreme Overbought

    3. 15M RSI <= 40 AND 1M RSI <= 30
       Bullish Setup

    4. 15M RSI >= 60 AND 1M RSI >= 70
       Bearish Setup

    5. 1M RSI <= 30
       1M Oversold

    6. 1M RSI >= 70
       1M Overbought
    """

    signals = []

    # --------------------------------------------------------
    # 15M EXTREME OVERSOLD
    # --------------------------------------------------------

    if rsi_15m < 20:

        signals.append({
            "type": "EXTREME_OVERSOLD",
            "timeframe": "15M",
            "message": (
                f"15M RSI {rsi_15m:.2f} < 20"
            ),
        })

    # --------------------------------------------------------
    # 15M EXTREME OVERBOUGHT
    # --------------------------------------------------------

    if rsi_15m > 80:

        signals.append({
            "type": "EXTREME_OVERBOUGHT",
            "timeframe": "15M",
            "message": (
                f"15M RSI {rsi_15m:.2f} > 80"
            ),
        })

    # --------------------------------------------------------
    # BULLISH SETUP
    # --------------------------------------------------------

    if (
        rsi_15m <= 40
        and
        rsi_1m <= 30
    ):

        signals.append({
            "type": "BULLISH_SETUP",
            "timeframe": "15M + 1M",
            "message": (
                f"15M RSI {rsi_15m:.2f} <= 40 "
                f"AND 1M RSI {rsi_1m:.2f} <= 30"
            ),
        })

    # --------------------------------------------------------
    # BEARISH SETUP
    # --------------------------------------------------------

    if (
        rsi_15m >= 60
        and
        rsi_1m >= 70
    ):

        signals.append({
            "type": "BEARISH_SETUP",
            "timeframe": "15M + 1M",
            "message": (
                f"15M RSI {rsi_15m:.2f} >= 60 "
                f"AND 1M RSI {rsi_1m:.2f} >= 70"
            ),
        })

    # --------------------------------------------------------
    # 1M OVERSOLD
    # --------------------------------------------------------

    if rsi_1m <= 30:

        signals.append({
            "type": "1M_OVERSOLD",
            "timeframe": "1M",
            "message": (
                f"1M RSI {rsi_1m:.2f} <= 30"
            ),
        })

    # --------------------------------------------------------
    # 1M OVERBOUGHT
    # --------------------------------------------------------

    if rsi_1m >= 70:

        signals.append({
            "type": "1M_OVERBOUGHT",
            "timeframe": "1M",
            "message": (
                f"1M RSI {rsi_1m:.2f} >= 70"
            ),
        })

    return signals