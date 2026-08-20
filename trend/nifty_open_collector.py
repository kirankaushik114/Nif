# ============================================================
# D:\Nif\trend\nifty_open_collector.py
#
# NIFTY 9:15 OPEN COLLECTOR
#
# Compares:
# Previous 3:30 -> Today's 9:15 Open
# ============================================================

import csv
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

OUTPUT_FILE = (
    DATA_DIR
    / "nifty_open"
    / "nifty_open_current.csv"
)

HISTORY_FILE = (
    DATA_DIR
    / "nifty_free_training.csv"
)

SYMBOL = "^NSEI"

IST = ZoneInfo("Asia/Kolkata")


# ============================================================
# NUMBER
# ============================================================

def to_float(value):

    if value in (
        None,
        "",
        "None",
        "nan",
        "NaN"
    ):
        return None

    try:
        return float(value)

    except Exception:
        return None


# ============================================================
# PREVIOUS 3:30
# ============================================================

def get_previous_330():

    if not HISTORY_FILE.exists():
        return None, None

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8-sig"
        ) as f:

            rows = list(
                csv.DictReader(f)
            )

    except Exception:

        return None, None

    for row in reversed(rows):

        value = to_float(
            row.get("NIFTY_15_30")
        )

        if value is not None:

            return (
                row.get("Date"),
                value
            )

    return None, None


# ============================================================
# TODAY 9:15 OPEN
# ============================================================

def get_today_open():

    today = datetime.now(
        IST
    ).date()

    tomorrow = (
        today +
        timedelta(days=1)
    )

    try:

        df = yf.download(
            SYMBOL,
            start=str(today),
            end=str(tomorrow),
            interval="1m",
            auto_adjust=False,
            prepost=False,
            progress=False
        )

    except Exception as error:

        return (
            None,
            None,
            f"DOWNLOAD_ERROR: {error}"
        )

    if df.empty:

        return (
            None,
            None,
            "NO_DATA"
        )

    # --------------------------------------------------------
    # Flatten Yahoo MultiIndex
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

    # --------------------------------------------------------
    # Find datetime column
    # --------------------------------------------------------

    datetime_column = None

    for name in (
        "Datetime",
        "Date"
    ):

        if name in df.columns:

            datetime_column = name
            break

    if datetime_column is None:

        return (
            None,
            None,
            "DATETIME_COLUMN_NOT_FOUND"
        )

    # --------------------------------------------------------
    # Convert datetime
    # --------------------------------------------------------

    df[datetime_column] = pd.to_datetime(
        df[datetime_column],
        errors="coerce"
    )

    df = df.dropna(
        subset=[datetime_column]
    )

    if df.empty:

        return (
            None,
            None,
            "INVALID_DATETIME"
        )

    # --------------------------------------------------------
    # Convert to IST
    # --------------------------------------------------------

    try:

        if df[datetime_column].dt.tz is None:

            df[datetime_column] = (
                df[datetime_column]
                .dt.tz_localize("UTC")
                .dt.tz_convert(IST)
            )

        else:

            df[datetime_column] = (
                df[datetime_column]
                .dt.tz_convert(IST)
            )

    except Exception as error:

        return (
            None,
            None,
            f"TIMEZONE_ERROR: {error}"
        )

    # --------------------------------------------------------
    # Find 9:15 candle
    #
    # We use the candle timestamp 09:15.
    # Its OPEN is the NIFTY 09:15 opening price.
    # --------------------------------------------------------

    rows = df[
        (df[datetime_column].dt.date == today)
        &
        (df[datetime_column].dt.hour == 9)
        &
        (df[datetime_column].dt.minute == 15)
    ]

    if rows.empty:

        return (
            None,
            None,
            "09_15_DATA_NOT_AVAILABLE"
        )

    opening_price = to_float(
        rows.iloc[0]["Open"]
    )

    timestamp = (
        rows.iloc[0][datetime_column]
    )

    if opening_price is None:

        return (
            None,
            None,
            "09_15_OPEN_INVALID"
        )

    return (
        round(opening_price, 2),
        timestamp.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "FRESH"
    )


# ============================================================
# CALCULATE GAP
# ============================================================

def calculate_gap(
    today_open,
    previous_330
):

    if (
        today_open is None
        or
        previous_330 is None
    ):

        return (
            None,
            None,
            "UNAVAILABLE"
        )

    difference = round(
        today_open - previous_330,
        2
    )

    gap_pct = round(
        (
            difference /
            previous_330
        ) * 100,
        2
    )

    if gap_pct >= 0.10:

        direction = "POSITIVE"

    elif gap_pct <= -0.10:

        direction = "NEGATIVE"

    else:

        direction = "NEUTRAL"

    return (
        difference,
        gap_pct,
        direction
    )


# ============================================================
# SAVE
# ============================================================

def save_result(row):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=row.keys()
        )

        writer.writeheader()
        writer.writerow(row)


# ============================================================
# MAIN
# ============================================================

def main():

    now = datetime.now(
        IST
    )

    (
        previous_date,
        previous_330
    ) = get_previous_330()

    (
        today_open,
        timestamp,
        status
    ) = get_today_open()

    (
        difference,
        gap_pct,
        direction
    ) = calculate_gap(
        today_open,
        previous_330
    )

    row = {

        "Timestamp_IST":
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "NIFTY_09_15_OPEN":
            today_open,

        "NIFTY_09_15_TIMESTAMP":
            timestamp,

        "NIFTY_09_15_STATUS":
            status,

        "Previous_Session_Date":
            previous_date,

        "Previous_NIFTY_15_30":
            previous_330,

        "NIFTY_09_15_VS_PREVIOUS_15_30":
            difference,

        "NIFTY_09_15_GAP_PCT":
            gap_pct,

        "NIFTY_09_15_DIRECTION":
            direction
    }

    save_result(row)

    # --------------------------------------------------------
    # SHORT OUTPUT
    # --------------------------------------------------------

    print(
        f"PREV 3:30 : "
        f"{fmt(previous_330)}"
    )

    print(
        f"9:15 OPEN  : "
        f"{fmt(today_open)}"
    )

    print(
        f"DIFFERENCE : "
        f"{fmt(difference)} "
        f"({fmt(gap_pct)}%)"
    )

    print(
        f"DIRECTION  : "
        f"{direction}"
    )

    print(
        f"STATUS     : "
        f"{status}"
    )

    return 0


# ============================================================
# FORMAT
# ============================================================

def fmt(value):

    if value is None:
        return "N/A"

    try:
        return f"{float(value):.2f}"

    except Exception:
        return str(value)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )