import pandas as pd

from indicators.rsi import (
    calculate_rsi,
    calculate_latest_rsi,
)


def test_rsi_returns_value():

    prices = pd.Series([
        100, 101, 102, 101, 103,
        104, 105, 103, 106, 107,
        108, 107, 109, 110, 111,
        112, 113, 114, 115, 116,
    ])

    rsi = calculate_rsi(
        prices,
        period=14,
    )

    assert isinstance(rsi, pd.Series)

    valid_rsi = rsi.dropna()

    assert (valid_rsi >= 0).all()
    assert (valid_rsi <= 100).all()


def test_latest_rsi():

    prices = pd.Series([
        100, 101, 102, 101, 103,
        104, 105, 103, 106, 107,
        108, 107, 109, 110, 111,
        112, 113, 114, 115, 116,
    ])

    rsi = calculate_latest_rsi(
        prices,
        period=14,
    )

    assert isinstance(rsi, float)
    assert 0 <= rsi <= 100