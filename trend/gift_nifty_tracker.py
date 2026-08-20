# ============================================================
# D:\Nif\trend\gift_nifty_tracker.py
#
# GIFT NIFTY 3:40 PM TRACKER
#
# Uses the existing gift_nifty_collector.py
#
# Records snapshots during the afternoon.
# Saves the observation closest to 15:40 IST.
#
# Run this script continuously during market hours.
# ============================================================

import csv
import subprocess
import sys
import time

from pathlib import Path
from datetime import datetime
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

CURRENT_FILE = (
    DATA_DIR
    / "gift_nifty_current.csv"
)

TRACKER_FILE = (
    DATA_DIR
    / "gift_nifty_tracker.csv"
)

THREE_FORTY_FILE = (
    DATA_DIR
    / "gift_nifty_340.csv"
)

PYTHON = sys.executable

COLLECTOR = (
    BASE_DIR
    / "gift_nifty_collector.py"
)

IST = ZoneInfo(
    "Asia/Kolkata"
)


# ============================================================
# SETTINGS
# ============================================================

# Take one observation every 1 minute.
INTERVAL_SECONDS = 60

# Start recording from 15:20.
START_HOUR = 15
START_MINUTE = 20

# Stop after 15:45.
END_HOUR = 15
END_MINUTE = 45


# ============================================================
# READ CURRENT GIFT
# ============================================================

def read_current():

    if not CURRENT_FILE.exists():
        return None

    try:

        with open(
            CURRENT_FILE,
            "r",
            encoding="utf-8-sig"
        ) as f:

            rows = list(
                csv.DictReader(f)
            )

        if not rows:
            return None

        value = rows[-1].get(
            "GIFT_NIFTY_Current"
        )

        if value is None:
            return None

        value = float(
            str(value)
            .replace(",", "")
        )

        # Safety check
        if not (
            20000
            <= value
            <= 30000
        ):
            return None

        return value

    except Exception:

        return None


# ============================================================
# SAVE TRACKER SNAPSHOT
# ============================================================

def save_snapshot(
    now,
    price
):

    fields = [
        "Date",
        "Time",
        "Timestamp_IST",
        "GIFT_NIFTY"
    ]

    row = {
        "Date":
            now.strftime(
                "%Y-%m-%d"
            ),

        "Time":
            now.strftime(
                "%H:%M:%S"
            ),

        "Timestamp_IST":
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "GIFT_NIFTY":
            price
    }

    rows = []

    if TRACKER_FILE.exists():

        try:

            with open(
                TRACKER_FILE,
                "r",
                encoding="utf-8-sig"
            ) as f:

                rows = list(
                    csv.DictReader(f)
                )

        except Exception:

            rows = []

    # Don't duplicate exact timestamp

    exists = any(
        r.get(
            "Timestamp_IST"
        )
        == row[
            "Timestamp_IST"
        ]
        for r in rows
    )

    if not exists:

        rows.append(row)

    with open(
        TRACKER_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


# ============================================================
# SAVE 3:40 VALUE
# ============================================================

def save_340():

    today = datetime.now(
        IST
    ).strftime(
        "%Y-%m-%d"
    )

    if not TRACKER_FILE.exists():

        return None

    try:

        with open(
            TRACKER_FILE,
            "r",
            encoding="utf-8-sig"
        ) as f:

            rows = list(
                csv.DictReader(f)
            )

    except Exception:

        return None

    candidates = []

    target_minutes = (
        15 * 60 + 40
    )

    for row in rows:

        if row.get(
            "Date"
        ) != today:

            continue

        try:

            t = datetime.strptime(
                row["Time"][:8],
                "%H:%M:%S"
            )

            minutes = (
                t.hour * 60
                + t.minute
            )

            price = float(
                row[
                    "GIFT_NIFTY"
                ]
            )

        except Exception:

            continue

        distance = abs(
            minutes
            -
            target_minutes
        )

        candidates.append(
            (
                distance,
                row,
                price
            )
        )

    if not candidates:

        return None

    candidates.sort(
        key=lambda x: x[0]
    )

    distance, row, price = (
        candidates[0]
    )

    # Accept only within 5 minutes.
    if distance > 5:

        return None

    result = {

        "Date":
            row["Date"],

        "Time":
            row["Time"],

        "GIFT_NIFTY_340":
            round(
                price,
                2
            ),

        "Distance_Minutes":
            distance,

        "Source":
            "Local Tracker"
    }

    fields = [
        "Date",
        "Time",
        "GIFT_NIFTY_340",
        "Distance_Minutes",
        "Source"
    ]

    existing = []

    if THREE_FORTY_FILE.exists():

        try:

            with open(
                THREE_FORTY_FILE,
                "r",
                encoding="utf-8-sig"
            ) as f:

                existing = list(
                    csv.DictReader(f)
                )

        except Exception:

            existing = []

    # Replace today's value

    existing = [
        r for r in existing
        if r.get("Date")
        != today
    ]

    existing.append(
        result
    )

    existing.sort(
        key=lambda r:
            r.get(
                "Date",
                ""
            )
    )

    with open(
        THREE_FORTY_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields
        )

        writer.writeheader()

        writer.writerows(
            existing
        )

    return result


# ============================================================
# RUN EXISTING COLLECTOR
# ============================================================

def update_quote():

    if not COLLECTOR.exists():

        print(
            "ERROR: "
            "gift_nifty_collector.py "
            "not found"
        )

        return False

    result = subprocess.run(

        [
            PYTHON,
            str(COLLECTOR)
        ],

        cwd=str(BASE_DIR),

        stdout=subprocess.DEVNULL,

        stderr=subprocess.PIPE,

        text=True
    )

    return (
        result.returncode == 0
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "=" * 50
    )

    print(
        "GIFT NIFTY 3:40 TRACKER"
    )

    print(
        "=" * 50
    )

    print(
        "Tracking : 15:20 - 15:45 IST"
    )

    print(
        "Interval : 1 minute"
    )

    print()

    while True:

        now = datetime.now(
            IST
        )

        start = now.replace(
            hour=START_HOUR,
            minute=START_MINUTE,
            second=0,
            microsecond=0
        )

        end = now.replace(
            hour=END_HOUR,
            minute=END_MINUTE,
            second=0,
            microsecond=0
        )

        # ----------------------------------------------------
        # Before tracking window
        # ----------------------------------------------------

        if now < start:

            remaining = (
                start - now
            ).total_seconds()

            print(
                f"Waiting for "
                f"15:20... "
                f"{int(remaining)} sec"
            )

            time.sleep(
                min(
                    60,
                    max(
                        1,
                        remaining
                    )
                )
            )

            continue

        # ----------------------------------------------------
        # Finished
        # ----------------------------------------------------

        if now > end:

            result = save_340()

            print()

            if result:

                print(
                    f"3:40 PRICE : "
                    f"{result['GIFT_NIFTY_340']:.2f}"
                )

                print(
                    f"TIME       : "
                    f"{result['Time']}"
                )

                print(
                    f"DISTANCE   : "
                    f"{result['Distance_Minutes']} min"
                )

                print(
                    "STATUS     : SAVED"
                )

            else:

                print(
                    "3:40 PRICE : "
                    "NOT FOUND"
                )

                print(
                    "STATUS     : "
                    "NO_VALID_OBSERVATION"
                )

            break

        # ----------------------------------------------------
        # Update quote
        # ----------------------------------------------------

        update_quote()

        price = read_current()

        if price is not None:

            save_snapshot(
                now,
                price
            )

            print(
                f"{now.strftime('%H:%M:%S')}  "
                f"GIFT NIFTY : "
                f"{price:.2f}"
            )

        else:

            print(
                f"{now.strftime('%H:%M:%S')}  "
                f"GIFT NIFTY : N/A"
            )

        # ----------------------------------------------------
        # Wait
        # ----------------------------------------------------

        time.sleep(
            INTERVAL_SECONDS
        )

    return 0


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )