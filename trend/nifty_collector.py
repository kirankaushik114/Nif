# ============================================================
# D:\Nif\trend\nifty_open_collector.py
#
# NIFTY 9:15 OPEN
#
# Previous 3:30 -> Today's 9:15
# ============================================================

import csv
import yfinance as yf

from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


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

def number(value):

    if value in (
        None,
        "",
        "None",
        "nan"
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

        value = number(
            row.get(
                "NIFTY_15_30"
            )
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
        today
        + timedelta(days=1)
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

    if hasattr(
        df.columns,
        "levels"
    ):

        if len(df.columns.levels) > 1:

            df.columns = (
                df.columns
                .get_level_values(0)
            )

    df = df.reset_index()

    # --------------------------------------------------------
    # Datetime
    # --------------------------------------------------------

    dt_column = None

    for column in (
        "Datetime",
        "Date",
        "datetime"
    ):

        if column in df.columns:

            dt_column = column
            break

    if dt_column is None:

        return (
            None,
            None,
            "DATETIME_COLUMN_NOT_FOUND"
        )

    df[dt_column] = pd_to_datetime(
        df[dt_column]
    )

    # --------------------------------------------------------
    # Convert timezone
    # --------------------------------------------------------

    try:

        if (
            hasattr(
                df[dt_column].dt,
                "tz"
            )
            and
            df[dt_column].dt.tz
            is not None
        ):

            df[dt_column] = (
                df[dt_column]
                .dt.tz_convert(
                    "Asia/Kolkata"
                )
            )

        else:

            df[dt_column] = (
                df[dt_column]
                .dt.tz_localize(
                    "Asia/Kolkata"
                )
            )

    except Exception:

        pass

    # --------------------------------------------------------
    # Find 9:15 candle
    # --------------------------------------------------------

    target_date = today

    rows = df[
        (
            df[dt_column].dt.date
            == target_date
        )
        &
        (
            df[dt_column].dt.hour
            == 9
        )
        &
        (
            df[dt_column].dt.minute
            == 15
        )
    ]

    if rows.empty:

        # Yahoo sometimes labels the opening
        # candle at 09:15 differently.
        # Try first regular-market candle.

        rows = df[
            (
                df[dt_column].dt.date
                == target_date
            )
            &
            (
                df[dt_column].dt.hour
                == 9
            )
            &
            (
                df[dt_column].dt.minute
                == 15
            )
        ]

    if rows.empty:

        return (
            None,
            None,
            "09_15_DATA_NOT_AVAILABLE"
        )

    value = number(
        rows.iloc[0]["Open"]
    )

    timestamp = (
        rows.iloc[0][dt_column]
    )

    if value is None:

        return (
            None,
            None,
            "09_15_OPEN_INVALID"
        )

    return (
        round(value, 2),
        str(timestamp),
        "FRESH"
    )


# ============================================================
# DATETIME HELPER
# ============================================================

def pd_to_datetime(value):

    import pandas as pd

    return pd.to_datetime(
        value
    )


# ============================================================
# CALCULATE
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
        today_open
        - previous_330,
        2
    )

    gap_pct = round(
        (
            difference
            / previous_330
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
        open_timestamp,
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
            open_timestamp,

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

    save_result(
        row
    )

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