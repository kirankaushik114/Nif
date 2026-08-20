from data.historical_data import GrowwHistoricalData


def test_data_until_4pm():

    data = GrowwHistoricalData()

    candles_data = data.get_1_minute_candles()

    candles = candles_data.get("candles", [])

    print()
    print("=" * 70)
    print("BANK NIFTY DATA TEST — UNTIL 4:00 PM")
    print("=" * 70)

    print(f"Total candles : {len(candles)}")

    assert candles, "No candles returned"

    print(f"First candle  : {candles[0][0]}")
    print(f"Last candle   : {candles[-1][0]}")

    print("=" * 70)