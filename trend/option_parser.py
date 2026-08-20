import re
import zipfile
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIG
# ============================================================

OPTIONS_DIR = Path(
    r"D:\Nif\trend\data\options"
)

TEST_ZIP = (
    OPTIONS_DIR
    / "20260505.zip"
)

TEST_DATE = "2026-05-05"

TEST_STRIKE = 24500


# ============================================================
# PARSE OPTION TICKER
# ============================================================

def parse_ticker(ticker):

    """
    Example:

    NIFTY05MAY26P20100

    Returns:

    underlying = NIFTY
    expiry     = 05MAY26
    option     = PE
    strike     = 20100
    """

    pattern = (
        r"^(NIFTY)"
        r"(\d{2}[A-Z]{3}\d{2})"
        r"([CP])"
        r"(\d+)$"
    )

    match = re.match(
        pattern,
        str(ticker)
    )

    if not match:

        return None

    underlying = (
        match.group(1)
    )

    expiry = (
        match.group(2)
    )

    option_code = (
        match.group(3)
    )

    strike = int(
        match.group(4)
    )

    option_type = (
        "CE"
        if option_code == "C"
        else "PE"
    )

    return {
        "underlying":
            underlying,

        "expiry":
            expiry,

        "option_type":
            option_type,

        "strike":
            strike,
    }


# ============================================================
# LOAD ZIP
# ============================================================

def load_zip(
    zip_file
):

    print()
    print(
        "Reading ZIP:"
    )

    print(
        zip_file
    )

    with zipfile.ZipFile(
        zip_file,
        "r"
    ) as z:

        names = z.namelist()

        csv_files = [
            name
            for name in names
            if name.lower().endswith(
                ".csv"
            )
        ]

        if not csv_files:

            raise RuntimeError(
                "No CSV found inside ZIP."
            )

        print()
        print(
            "CSV files found:",
            len(csv_files)
        )

        frames = []

        for csv_file in csv_files:

            print(
                "Reading:",
                csv_file
            )

            with z.open(
                csv_file
            ) as f:

                df = pd.read_csv(
                    f
                )

            frames.append(
                df
            )

    if not frames:

        raise RuntimeError(
            "No data loaded."
        )

    result = pd.concat(
        frames,
        ignore_index=True
    )

    return result


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data(
    df
):

    required = {
        "Date",
        "Timestamp",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "OI",
        "Ticker",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        raise RuntimeError(
            "Missing columns: "
            + str(missing)
        )

    # --------------------------------------------------------
    # Numeric fields
    # --------------------------------------------------------

    for column in [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "OI",
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        format="%d-%m-%Y %H:%M:%S",
        errors="coerce"
    )

    # --------------------------------------------------------
    # Parse ticker
    # --------------------------------------------------------

    parsed = (
        df["Ticker"]
        .apply(parse_ticker)
    )

    df["Underlying"] = (
        parsed.apply(
            lambda x:
            x["underlying"]
            if x else None
        )
    )

    df["Expiry"] = (
        parsed.apply(
            lambda x:
            x["expiry"]
            if x else None
        )
    )

    df["Option_Type"] = (
        parsed.apply(
            lambda x:
            x["option_type"]
            if x else None
        )
    )

    df["Strike"] = (
        parsed.apply(
            lambda x:
            x["strike"]
            if x else None
        )
    )

    return df


# ============================================================
# GET OPTION DATA
# ============================================================

def get_option_contract(
    df,
    trade_date,
    strike
):

    target_date = pd.Timestamp(
        trade_date
    ).date()

    result = df[
        (
            df["Timestamp"].dt.date
            == target_date
        )
        &
        (
            df["Underlying"]
            == "NIFTY"
        )
        &
        (
            df["Strike"]
            == strike
        )
    ].copy()

    return result


# ============================================================
# GET TIME PRICE
# ============================================================

def get_time_price(
    df,
    time_text
):

    if df.empty:

        return None

    target = pd.Timestamp(
        f"{TEST_DATE} "
        f"{time_text}:00"
    )

    rows = df[
        df["Timestamp"]
        == target
    ]

    if rows.empty:

        return None

    return float(
        rows.iloc[0]["Close"]
    )


# ============================================================
# BUILD CONTRACT SUMMARY
# ============================================================

def build_summary(
    df,
    option_type
):

    if df.empty:

        return None

    df = df[
        df["Option_Type"]
        == option_type
    ].copy()

    if df.empty:

        return None

    # --------------------------------------------------------
    # Time readings
    # --------------------------------------------------------

    result = {

        "Option_Type":
            option_type,

        "Strike":
            TEST_STRIKE,

        "Open":
            float(
                df["Open"].iloc[0]
            ),

        "High":
            float(
                df["High"].max()
            ),

        "Low":
            float(
                df["Low"].min()
            ),

        "Average":
            float(
                df["Close"].mean()
            ),

        "Close":
            float(
                df["Close"].iloc[-1]
            ),

        "Volume":
            float(
                df["Volume"].sum()
            ),

        "Max_OI":
            float(
                df["OI"].max()
            ),
    }

    # --------------------------------------------------------
    # Required time slots
    # --------------------------------------------------------

    times = [
        "09:30",
        "10:00",
        "12:30",
        "14:00",
        "15:15",
        "15:35",
        "15:40",
    ]

    for time_text in times:

        result[
            time_text.replace(
                ":",
                "_"
            )
        ] = get_time_price(
            df,
            time_text
        )

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)
    print("NIFTY OPTION PARSER")
    print("=" * 75)

    print()
    print(
        "Date  :",
        TEST_DATE
    )

    print(
        "Strike:",
        TEST_STRIKE
    )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_zip(
        TEST_ZIP
    )

    print()
    print(
        "Rows loaded:",
        len(df)
    )

    # --------------------------------------------------------
    # Prepare
    # --------------------------------------------------------

    df = prepare_data(
        df
    )

    print()
    print(
        "Unique tickers:",
        df["Ticker"].nunique()
    )

    # --------------------------------------------------------
    # Get contract
    # --------------------------------------------------------

    contract = get_option_contract(
        df,
        TEST_DATE,
        TEST_STRIKE
    )

    print()
    print(
        "Rows for strike:",
        len(contract)
    )

    if contract.empty:

        print()
        print(
            "No 24500 CE/PE found "
            "in this ZIP."
        )

        print()
        print(
            "Available strikes:"
        )

        print(
            sorted(
                contract[
                    "Strike"
                ].dropna()
                .unique()
                .tolist()
            )
        )

        return

    # --------------------------------------------------------
    # Print available expiries
    # --------------------------------------------------------

    print()
    print(
        "Available expiries:"
    )

    print(
        sorted(
            contract[
                "Expiry"
            ].dropna()
            .unique()
            .tolist()
        )
    )

    # --------------------------------------------------------
    # CE
    # --------------------------------------------------------

    ce = build_summary(
        contract,
        "CE"
    )

    # --------------------------------------------------------
    # PE
    # --------------------------------------------------------

    pe = build_summary(
        contract,
        "PE"
    )

    # --------------------------------------------------------
    # Print
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print("CALL OPTION")
    print("=" * 75)

    if ce:

        for key, value in ce.items():

            print(
                f"{key:20} : "
                f"{value}"
            )

    else:

        print(
            "CE not found."
        )

    print()
    print("=" * 75)
    print("PUT OPTION")
    print("=" * 75)

    if pe:

        for key, value in pe.items():

            print(
                f"{key:20} : "
                f"{value}"
            )

    else:

        print(
            "PE not found."
        )

    print()
    print("=" * 75)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()