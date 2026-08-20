# ============================================================
# D:\Nif\trend\gift_nifty_340.py
#
# GIFT NIFTY 3:40 VALUE SELECTOR
#
# Logic:
#
# 1. Check today's 3:40 value
# 2. If unavailable -> yesterday
# 3. Continue backwards until a valid value is found
# 4. Maximum search = 10 calendar days
#
# This file DOES NOT require Upstox.
#
# It reads:
#     data\gift_nifty\gift_nifty_340.csv
#
# ============================================================

import csv

from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = (
    BASE_DIR
    / "data"
    / "gift_nifty"
)

HISTORY_FILE = (
    DATA_DIR
    / "gift_nifty_340.csv"
)

SELECTED_FILE = (
    DATA_DIR
    / "gift_nifty_340_selected.csv"
)

IST = ZoneInfo(
    "Asia/Kolkata"
)

MAX_SEARCH_DAYS = 10


# ============================================================
# NUMBER
# ============================================================

def to_float(value):

    if value is None:
        return None

    try:

        return float(
            str(value)
            .replace(",", "")
            .replace("%", "")
            .strip()
        )

    except Exception:

        return None


# ============================================================
# READ HISTORY
# ============================================================

def read_history():

    if not HISTORY_FILE.exists():

        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8-sig"
        ) as f:

            return list(
                csv.DictReader(f)
            )

    except Exception as error:

        print(
            f"ERROR reading history: {error}"
        )

        return []


# ============================================================
# FIND VALUE FOR DATE
# ============================================================

def find_for_date(
    rows,
    target_date
):

    target = target_date.strftime(
        "%Y-%m-%d"
    )

    matches = []

    for row in rows:

        if row.get(
            "Date"
        ) != target:

            continue

        price = to_float(
            row.get(
                "GIFT_NIFTY_340"
            )
        )

        if price is None:

            continue

        if not (
            20000
            <= price
            <= 30000
        ):

            continue

        time_value = row.get(
            "Time",
            ""
        )

        matches.append(
            {
                "date":
                    target,

                "time":
                    time_value,

                "price":
                    price,

                "distance":
                    to_float(
                        row.get(
                            "Distance_Minutes"
                        )
                    )
            }
        )

    if not matches:

        return None

    # Prefer the closest observation to 15:40

    matches.sort(
        key=lambda x:
            (
                x["distance"]
                if x["distance"] is not None
                else 999999
            )
    )

    return matches[0]


# ============================================================
# SELECT 3:40 VALUE
# ============================================================

def select_340():

    now = datetime.now(
        IST
    )

    today = now.date()

    rows = read_history()

    print()
    print(
        "=" * 60
    )

    print(
        "GIFT NIFTY 3:40 SELECTOR"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Current IST : "
        f"{now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print(
        f"History     : "
        f"{HISTORY_FILE}"
    )

    # --------------------------------------------------------
    # File check
    # --------------------------------------------------------

    if not rows:

        print()
        print(
            "STATUS      : "
            "HISTORY_FILE_NOT_FOUND"
        )

        return None

    print(
        f"History rows: "
        f"{len(rows)}"
    )

    # --------------------------------------------------------
    # Search backwards
    # --------------------------------------------------------

    for days_back in range(
        MAX_SEARCH_DAYS + 1
    ):

        target_date = (
            today
            -
            timedelta(
                days=days_back
            )
        )

        result = find_for_date(
            rows,
            target_date
        )

        if result:

            if days_back == 0:

                status = (
                    "FOUND_TODAY"
                )

            elif days_back == 1:

                status = (
                    "FOUND_YESTERDAY"
                )

            else:

                status = (
                    "FOUND_PREVIOUS_TRADING_DAY"
                )

            result["status"] = status

            result["days_back"] = (
                days_back
            )

            return result

        print(
            f"Checked     : "
            f"{target_date}"
            f" -> NOT FOUND"
        )

    return None


# ============================================================
# SAVE SELECTED RESULT
# ============================================================

def save_selected(
    result
):

    fields = [

        "Selected_At_IST",

        "Date",

        "Time",

        "GIFT_NIFTY_340",

        "Distance_Minutes",

        "Days_Back",

        "Status",

        "Source"
    ]

    now = datetime.now(
        IST
    )

    row = {

        "Selected_At_IST":
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Date":
            result["date"],

        "Time":
            result["time"],

        "GIFT_NIFTY_340":
            result["price"],

        "Distance_Minutes":
            result["distance"]
            if result["distance"]
            is not None
            else "",

        "Days_Back":
            result["days_back"],

        "Status":
            result["status"],

        "Source":
            "Local GIFT Tracker"
    }

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        SELECTED_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields
        )

        writer.writeheader()

        writer.writerow(
            row
        )


# ============================================================
# MAIN
# ============================================================

def main():

    result = select_340()

    print()

    if result is None:

        print(
            "=" * 60
        )

        print(
            "RESULT"
        )

        print(
            "=" * 60
        )

        print()

        print(
            "3:40 Date   : N/A"
        )

        print(
            "3:40 Price  : N/A"
        )

        print(
            "3:40 Time   : N/A"
        )

        print(
            "Status      : "
            "NO_3_40_VALUE_FOUND"
        )

        print()

        return 1

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_selected(
        result
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print(
        "=" * 60
    )

    print(
        "SELECTED GIFT NIFTY 3:40"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"3:40 Date   : "
        f"{result['date']}"
    )

    print(
        f"3:40 Time   : "
        f"{result['time']}"
    )

    print(
        f"3:40 Price  : "
        f"{result['price']:.2f}"
    )

    if result["distance"] is not None:

        print(
            f"Distance    : "
            f"{result['distance']:.0f} minute(s)"
        )

    print(
        f"Days Back   : "
        f"{result['days_back']}"
    )

    print(
        f"Status      : "
        f"{result['status']}"
    )

    print()

    print(
        f"Saved       : "
        f"{SELECTED_FILE}"
    )

    print()

    print(
        "=" * 60
    )

    return 0


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )