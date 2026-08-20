"""
Find Bank Nifty instrument details from Groww.

READ ONLY.
No orders.
"""

from growwapi import GrowwAPI

from config.settings import (
    GROWW_API_KEY,
    GROWW_API_SECRET,
)


def authenticate():

    print("Authenticating with Groww...")

    access_token = GrowwAPI.get_access_token(
        api_key=GROWW_API_KEY,
        secret=GROWW_API_SECRET,
    )

    groww = GrowwAPI(access_token)

    print("Groww authentication successful.")

    return groww


def find_banknifty():

    groww = authenticate()

    print()
    print("=" * 80)
    print("SEARCHING GROWW INSTRUMENT DATABASE")
    print("=" * 80)

    print()
    print("Downloading instrument data...")

    instruments = groww.get_all_instruments()

    print("Instrument data loaded.")

    print()
    print("Total instruments:", len(instruments))

    print()
    print("=" * 80)
    print("BANKNIFTY RESULTS")
    print("=" * 80)

    # --------------------------------------------------------
    # Search trading symbol
    # --------------------------------------------------------

    results = instruments[
        instruments["trading_symbol"]
        .astype(str)
        .str.upper()
        .eq("BANKNIFTY")
    ]

    # --------------------------------------------------------
    # Also search groww symbol
    # --------------------------------------------------------

    if results.empty:

        results = instruments[
            instruments["groww_symbol"]
            .astype(str)
            .str.upper()
            .eq("NSE-BANKNIFTY")
        ]

    if results.empty:

        print()
        print("BANKNIFTY was not found.")

        print()
        print("Searching rows containing BANKNIFTY...")

        results = instruments[
            instruments.astype(str)
            .apply(
                lambda column:
                column.str.contains(
                    "BANKNIFTY",
                    case=False,
                    na=False
                )
            )
            .any(axis=1)
        ]

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    if results.empty:

        print()
        print("No Bank Nifty instruments found.")

        return

    print()
    print(
        results.to_string(
            index=False
        )
    )

    print()
    print("=" * 80)
    print("IMPORTANT COLUMNS")
    print("=" * 80)

    columns = [
        "exchange",
        "exchange_token",
        "trading_symbol",
        "groww_symbol",
        "instrument_type",
        "segment",
        "underlying_symbol",
        "underlying_exchange_token",
    ]

    available_columns = [
        column
        for column in columns
        if column in results.columns
    ]

    print(
        results[available_columns]
        .to_string(index=False)
    )

    print()
    print("=" * 80)
    print("SEARCH COMPLETE")
    print("=" * 80)


if __name__ == "__main__":

    try:

        find_banknifty()

    except Exception as error:

        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)

        print(
            "Error type:",
            type(error).__name__
        )

        print(
            "Error:",
            error
        )

        print("=" * 80)