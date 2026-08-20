"""
Bank Nifty RSI Indicator
RSI(14) using Wilder's smoothing method.
"""

import pandas as pd


def calculate_rsi(
    prices: pd.Series,
    period: int = 14,
) -> pd.Series:

    if not isinstance(prices, pd.Series):
        prices = pd.Series(
            prices,
            dtype="float64",
        )

    prices = prices.astype("float64")

    if len(prices) < period + 1:
        raise ValueError(
            f"Not enough price data for RSI({period}). "
            f"Need at least {period + 1} prices."
        )

    delta = prices.diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    average_gain = gain.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False,
    ).mean()

    average_loss = loss.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False,
    ).mean()

    rs = (
        average_gain
        / average_loss
    )

    rsi = 100 - (
        100 / (1 + rs)
    )

    rsi = rsi.mask(
        average_loss == 0,
        100.0,
    )

    rsi = rsi.mask(
        (average_gain == 0)
        &
        (average_loss == 0),
        50.0,
    )

    return rsi


def calculate_latest_rsi(
    prices: pd.Series,
    period: int = 14,
) -> float:

    rsi = calculate_rsi(
        prices=prices,
        period=period,
    )

    valid_rsi = rsi.dropna()

    if valid_rsi.empty:
        raise ValueError(
            "Unable to calculate RSI."
        )

    return float(
        valid_rsi.iloc[-1]
    )


def candle_closes_to_series(
    candles: list,
) -> pd.Series:

    if not candles:
        raise ValueError(
            "No candles received."
        )

    closes = []

    for candle in candles:

        if len(candle) < 5:
            raise ValueError(
                f"Invalid candle format: {candle}"
            )

        close_price = candle[4]

        if close_price is None:
            continue

        closes.append(
            float(close_price)
        )

    if not closes:
        raise ValueError(
            "No valid closing prices found."
        )

    return pd.Series(
        closes,
        dtype="float64",
    )


if __name__ == "__main__":

    print("=" * 60)
    print("RSI MODULE TEST")
    print("=" * 60)

    test_prices = pd.Series([
        100,
        101,
        102,
        101,
        103,
        104,
        105,
        103,
        106,
        107,
        108,
        107,
        109,
        110,
        111,
        112,
        113,
        114,
        115,
        116,
    ])

    rsi_series = calculate_rsi(
        test_prices,
        period=14,
    )

    latest_rsi = calculate_latest_rsi(
        test_prices,
        period=14,
    )

    print()
    print("RSI Series:")
    print(rsi_series)

    print()
    print(
        f"Latest RSI(14): {latest_rsi:.2f}"
    )

    print()
    print("RSI MODULE TEST : SUCCESS")
    print("=" * 60)