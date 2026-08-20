import yfinance as yf
import pandas as pd

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


# ============================================================
# CONFIG
# ============================================================

SYMBOL = "BZ=F"

BASE_DIR = Path(r"D:\Nif\trend")

CRUDE_DIR = (
    BASE_DIR
    / "data"
    / "crude"
)

SNAPSHOT_FILE = (
    CRUDE_DIR
    / "brent_current.csv"
)

DAILY_FILE = (
    CRUDE_DIR
    / "brent_daily.csv"
)

MAX_QUOTE_AGE_HOURS = 12


# ============================================================
# TIME
# ============================================================

def get_ist_now():

    return datetime.now(
        ZoneInfo("Asia/Kolkata")
    )


# ============================================================
# GET CURRENT BRENT
# ============================================================

def get_current_brent():

    print()
    print("Getting latest Brent price...")

    df = yf.download(
        SYMBOL,
        period="2d",
        interval="5m",
        auto_adjust=False,
        prepost=True,
        progress=False,
    )

    if df.empty:
        return None

    # --------------------------------------------------------
    # Yahoo MultiIndex
    # --------------------------------------------------------

    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        df.columns = (
            df.columns
            .get_level_values(0)
        )

    df = df.reset_index()

    if "Close" not in df.columns:
        return None

    df["Close"] = pd.to_numeric(
        df["Close"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Close"]
    )

    if df.empty:
        return None

    # --------------------------------------------------------
    # Timestamp column
    # --------------------------------------------------------

    timestamp_column = None

    for column in [
        "Datetime",
        "Date",
    ]:

        if column in df.columns:

            timestamp_column = column
            break

    if timestamp_column is None:
        return None

    latest = df.iloc[-1]

    price = float(
        latest["Close"]
    )

    timestamp = pd.Timestamp(
        latest[timestamp_column]
    )

    # --------------------------------------------------------
    # Ensure timezone
    # --------------------------------------------------------

    if timestamp.tzinfo is None:

        timestamp = (
            timestamp
            .tz_localize("UTC")
        )

    timestamp_ist = (
        timestamp
        .tz_convert("Asia/Kolkata")
    )

    timestamp_ny = (
        timestamp
        .tz_convert("America/New_York")
    )

    return (
        price,
        timestamp_ist,
        timestamp_ny
    )


# ============================================================
# GET PREVIOUS COMPLETED BRENT CLOSE
# ============================================================

def get_previous_completed_close(
    quote_timestamp_ny
):

    print(
        "Getting previous completed Brent close..."
    )

    df = yf.download(
        SYMBOL,
        period="15d",
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    if df.empty:
        return None

    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        df.columns = (
            df.columns
            .get_level_values(0)
        )

    df = df.reset_index()

    if "Close" not in df.columns:
        return None

    df["Close"] = pd.to_numeric(
        df["Close"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Close"]
    )

    if df.empty:
        return None

    # --------------------------------------------------------
    # Convert Yahoo daily dates
    # --------------------------------------------------------

    date_column = None

    for column in [
        "Date",
        "Datetime",
    ]:

        if column in df.columns:

            date_column = column
            break

    if date_column is None:
        return None

    df["Session_Date"] = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Session_Date"]
    )

    # --------------------------------------------------------
    # Yahoo daily futures dates represent
    # the trading session date.
    #
    # We need the last session BEFORE
    # the current quote's New York date.
    # --------------------------------------------------------

    quote_date_ny = (
        quote_timestamp_ny
        .date()
    )

    df = df[
        df["Session_Date"].dt.date
        < quote_date_ny
    ].copy()

    if df.empty:

        return None

    df = df.sort_values(
        "Session_Date"
    )

    last_row = df.iloc[-1]

    previous_close = float(
        last_row["Close"]
    )

    previous_date = (
        last_row["Session_Date"]
        .date()
    )

    return (
        previous_close,
        previous_date
    )


# ============================================================
# OIL PRESSURE
# ============================================================

def get_oil_pressure(
    change_pct,
    quote_fresh
):

    if not quote_fresh:
        return "STALE"

    if change_pct is None:
        return "UNKNOWN"

    if change_pct >= 2.0:
        return "STRONG_NEGATIVE"

    if change_pct >= 1.0:
        return "NEGATIVE"

    if change_pct <= -2.0:
        return "STRONG_POSITIVE"

    if change_pct <= -1.0:
        return "POSITIVE"

    return "NEUTRAL"


# ============================================================
# SAVE SNAPSHOT
# ============================================================

def save_snapshot(record):

    CRUDE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    new_row = pd.DataFrame(
        [record]
    )

    if SNAPSHOT_FILE.exists():

        try:

            old = pd.read_csv(
                SNAPSHOT_FILE
            )

            result = pd.concat(
                [
                    old,
                    new_row
                ],
                ignore_index=True
            )

        except Exception:

            result = new_row

    else:

        result = new_row

    result.to_csv(
        SNAPSHOT_FILE,
        index=False
    )


# ============================================================
# SAVE DAILY INFORMATION
# ============================================================

def save_daily_record(
    session_date,
    close
):

    CRUDE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    new_row = pd.DataFrame(
        [{
            "Date":
                str(session_date),

            "Brent_Daily_Close":
                round(
                    close,
                    2
                ),
        }]
    )

    if DAILY_FILE.exists():

        try:

            old = pd.read_csv(
                DAILY_FILE
            )

            result = pd.concat(
                [
                    old,
                    new_row
                ],
                ignore_index=True
            )

            result = (
                result
                .drop_duplicates(
                    subset=["Date"],
                    keep="last"
                )
            )

        except Exception:

            result = new_row

    else:

        result = new_row

    result.to_csv(
        DAILY_FILE,
        index=False
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 80)
    print("BRENT OVERNIGHT CURRENT PRICE COLLECTOR")
    print("=" * 80)

    # --------------------------------------------------------
    # Current IST
    # --------------------------------------------------------

    now_ist = get_ist_now()

    print()
    print(
        "Current IST:",
        now_ist.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    # --------------------------------------------------------
    # Current quote
    # --------------------------------------------------------

    quote = get_current_brent()

    if quote is None:

        print()
        print(
            "ERROR: Could not get current Brent."
        )

        return

    (
        current_price,
        quote_timestamp_ist,
        quote_timestamp_ny,
    ) = quote

    # --------------------------------------------------------
    # Quote age
    # --------------------------------------------------------

    quote_age = (
        now_ist
        - quote_timestamp_ist
    )

    quote_age_hours = (
        quote_age.total_seconds()
        / 3600
    )

    quote_fresh = (
        0 <= quote_age_hours
        <= MAX_QUOTE_AGE_HOURS
    )

    # --------------------------------------------------------
    # Previous completed close
    # --------------------------------------------------------

    previous_data = (
        get_previous_completed_close(
            quote_timestamp_ny
        )
    )

    if previous_data is None:

        print()
        print(
            "ERROR: Previous completed "
            "Brent close unavailable."
        )

        return

    (
        previous_close,
        previous_session_date
    ) = previous_data

    # --------------------------------------------------------
    # Overnight / current change
    # --------------------------------------------------------

    change = (
        current_price
        - previous_close
    )

    change_pct = (
        change
        / previous_close
    ) * 100

    # --------------------------------------------------------
    # Oil pressure
    # --------------------------------------------------------

    oil_pressure = get_oil_pressure(
        change_pct,
        quote_fresh
    )

    # --------------------------------------------------------
    # Save snapshot
    # --------------------------------------------------------

    record = {

        "Timestamp_IST":
            now_ist.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Brent_Current_Price":
            round(
                current_price,
                2
            ),

        "Brent_Quote_Timestamp_IST":
            quote_timestamp_ist.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Brent_Quote_Timestamp_NY":
            quote_timestamp_ny.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Brent_Quote_Age_Hours":
            round(
                quote_age_hours,
                2
            ),

        "Brent_Quote_Status":
            (
                "FRESH"
                if quote_fresh
                else "STALE"
            ),

        "Previous_Completed_Session":
            str(
                previous_session_date
            ),

        "Brent_Previous_Close":
            round(
                previous_close,
                2
            ),

        "Brent_Change":
            round(
                change,
                2
            ),

        "Brent_Change_Pct":
            round(
                change_pct,
                2
            ),

        "Oil_Pressure":
            oil_pressure,
    }

    save_snapshot(
        record
    )

    # --------------------------------------------------------
    # Save previous completed session
    # --------------------------------------------------------

    save_daily_record(
        previous_session_date,
        previous_close
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    print()
    print("=" * 80)
    print("BRENT MARKET SNAPSHOT")
    print("=" * 80)

    print()

    print(
        "Current IST                 :",
        record[
            "Timestamp_IST"
        ]
    )

    print(
        "Current Brent               :",
        record[
            "Brent_Current_Price"
        ]
    )

    print(
        "Quote timestamp IST         :",
        record[
            "Brent_Quote_Timestamp_IST"
        ]
    )

    print(
        "Quote timestamp NY          :",
        record[
            "Brent_Quote_Timestamp_NY"
        ]
    )

    print(
        "Quote age hours             :",
        record[
            "Brent_Quote_Age_Hours"
        ]
    )

    print(
        "Quote status                :",
        record[
            "Brent_Quote_Status"
        ]
    )

    print(
        "Previous session            :",
        record[
            "Previous_Completed_Session"
        ]
    )

    print(
        "Previous Brent close       :",
        record[
            "Brent_Previous_Close"
        ]
    )

    print(
        "Current vs previous close  :",
        record[
            "Brent_Change"
        ]
    )

    print(
        "Change %                   :",
        record[
            "Brent_Change_Pct"
        ]
    )

    print(
        "Oil pressure               :",
        record[
            "Oil_Pressure"
        ]
    )

    print()
    print(
        "Snapshot:",
        SNAPSHOT_FILE
    )

    print(
        "Daily file:",
        DAILY_FILE
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