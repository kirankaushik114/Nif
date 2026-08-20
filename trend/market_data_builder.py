import pandas as pd
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(r"D:\Nif\trend")

NIFTY_FILE = (
    BASE_DIR
    / "data"
    / "nifty_free_training.csv"
)

BRENT_FILE = (
    BASE_DIR
    / "data"
    / "crude"
    / "brent_daily.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "market"
    / "cas_market_data.csv"
)


# ============================================================
# LOAD FILE
# ============================================================

def load_csv(path):

    if not path.exists():

        raise FileNotFoundError(
            f"File not found:\n{path}"
        )

    df = pd.read_csv(path)

    if df.empty:

        raise RuntimeError(
            f"File is empty:\n{path}"
        )

    if "Date" not in df.columns:

        raise RuntimeError(
            f"'Date' column missing:\n{path}"
        )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Date"]
    )

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 80)
    print("CAS MARKET DATA BUILDER")
    print("=" * 80)

    # --------------------------------------------------------
    # Load NIFTY
    # --------------------------------------------------------

    print()
    print("Loading NIFTY...")

    nifty = load_csv(
        NIFTY_FILE
    )

    print(
        "NIFTY rows:",
        len(nifty)
    )

    print(
        "NIFTY first:",
        nifty["Date"].min().date()
    )

    print(
        "NIFTY last :",
        nifty["Date"].max().date()
    )

    # --------------------------------------------------------
    # Load Brent
    # --------------------------------------------------------

    print()
    print("Loading Brent...")

    brent = load_csv(
        BRENT_FILE
    )

    print(
        "Brent rows:",
        len(brent)
    )

    print(
        "Brent first:",
        brent["Date"].min().date()
    )

    print(
        "Brent last :",
        brent["Date"].max().date()
    )

    # --------------------------------------------------------
    # Keep only required Brent columns
    # --------------------------------------------------------

    brent_columns = [
        "Date",
        "Brent_Previous_Close",
        "Brent_Open",
        "Brent_High",
        "Brent_Low",
        "Brent_Close",
        "Brent_Change",
        "Brent_Change_Pct",
        "Brent_Day_Range",
    ]

    available_columns = [
        column
        for column in brent_columns
        if column in brent.columns
    ]

    brent = brent[
        available_columns
    ].copy()

    # --------------------------------------------------------
    # Merge
    #
    # LEFT JOIN means:
    # Keep every NIFTY trading day.
    #
    # If Brent is not available for a date,
    # Brent fields remain NaN.
    # --------------------------------------------------------

    market = pd.merge(
        nifty,
        brent,
        on="Date",
        how="left",
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    market = (
        market
        .sort_values("Date")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Calculate Brent change if possible
    # --------------------------------------------------------

    if "Brent_Close" in market.columns:

        market[
            "Brent_Change_Pct"
        ] = market[
            "Brent_Close"
        ].pct_change() * 100

        market[
            "Brent_Change_Pct"
        ] = market[
            "Brent_Change_Pct"
        ].round(2)

    # --------------------------------------------------------
    # Calculate oil pressure
    #
    # This is descriptive only.
    # It does NOT change the NIFTY prediction yet.
    # --------------------------------------------------------

    if "Brent_Change_Pct" in market.columns:

        def oil_pressure(value):

            if pd.isna(value):

                return "UNKNOWN"

            if value >= 2.0:

                return "STRONG_NEGATIVE"

            if value >= 1.0:

                return "NEGATIVE"

            if value <= -2.0:

                return "STRONG_POSITIVE"

            if value <= -1.0:

                return "POSITIVE"

            return "NEUTRAL"

        market[
            "Oil_Pressure"
        ] = market[
            "Brent_Change_Pct"
        ].apply(
            oil_pressure
        )

    # --------------------------------------------------------
    # Date format
    # --------------------------------------------------------

    market["Date"] = (
        market["Date"]
        .dt.strftime("%Y-%m-%d")
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    market.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 80)
    print("MERGE COMPLETE")
    print("=" * 80)

    print()
    print(
        "Combined rows:",
        len(market)
    )

    print(
        "Output:",
        OUTPUT_FILE
    )

    print()

    # --------------------------------------------------------
    # Last 10 rows
    # --------------------------------------------------------

    display_columns = [
        "Date",
        "NIFTY_Close",
        "NIFTY_Day_Range",
        "Brent_Close",
        "Brent_Change_Pct",
        "Oil_Pressure",
    ]

    display_columns = [
        column
        for column in display_columns
        if column in market.columns
    ]

    print(
        market[
            display_columns
        ].tail(10).to_string(
            index=False
        )
    )

    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()