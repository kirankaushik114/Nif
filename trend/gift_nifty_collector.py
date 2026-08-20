# ============================================================
# D:\Nif\trend\gift_nifty_collector.py
#
# GIFT NIFTY COLLECTOR
#
# Current price + historical intraday data
#
# Target:
#   GIFT Nifty 15:40 IST
#
# ============================================================

import csv
import json
import re
import requests

from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = (
    BASE_DIR /
    "data" /
    "gift_nifty"
)

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CURRENT_FILE = (
    DATA_DIR /
    "gift_nifty_current.csv"
)

HISTORY_FILE = (
    DATA_DIR /
    "gift_nifty_history.csv"
)

RAW_FILE = (
    DATA_DIR /
    "investing_gift_nifty_raw.html"
)

IST = ZoneInfo(
    "Asia/Kolkata"
)

PAGE_URL = (
    "https://www.investing.com/"
    "indices/gift-nifty-50-c1-futures"
)

HISTORICAL_URL = (
    "https://www.investing.com/"
    "indices/gift-nifty-50-c1-futures"
    "-historical-data"
)

HEADERS = {

    "User-Agent":
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/142.0 Safari/537.36",

    "Accept":
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8",

    "Accept-Language":
        "en-US,en;q=0.9",

    "Referer":
        "https://www.investing.com/"
}


# ============================================================
# NUMBER
# ============================================================

def clean_number(value):

    if value is None:
        return None

    text = str(value)

    text = (
        text
        .replace(",", "")
        .replace("%", "")
        .strip()
    )

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        text
    )

    if not match:
        return None

    try:

        return float(
            match.group(0)
        )

    except Exception:

        return None


# ============================================================
# VALID GIFT NIFTY PRICE
# ============================================================

def valid_price(value):

    price = clean_number(
        value
    )

    if price is None:
        return None

    # Safety protection against
    # accidentally reading NIFTYBEES etc.
    if price < 20000 or price > 30000:
        return None

    return round(
        price,
        2
    )


# ============================================================
# REQUEST SESSION
# ============================================================

def create_session():

    session = requests.Session()

    session.headers.update(
        HEADERS
    )

    return session


# ============================================================
# GET CURRENT PAGE
# ============================================================

def get_current_page():

    session = create_session()

    response = session.get(
        PAGE_URL,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ============================================================
# NEXT DATA
# ============================================================

def extract_next_data(
    html
):

    pattern = (
        r'<script[^>]+'
        r'id=["\']__NEXT_DATA__["\']'
        r'[^>]*>'
        r'(.*?)'
        r'</script>'
    )

    match = re.search(
        pattern,
        html,
        re.DOTALL |
        re.IGNORECASE
    )

    if not match:
        return None

    try:

        return json.loads(
            match.group(1)
        )

    except Exception:

        return None


# ============================================================
# RECURSIVE PRICE SEARCH
# ============================================================

def recursive_find_prices(
    obj,
    results=None
):

    if results is None:
        results = []

    if isinstance(
        obj,
        dict
    ):

        for key, value in obj.items():

            key_text = (
                str(key)
                .lower()
                .replace("_", "")
                .replace("-", "")
            )

            if key_text in (
                "last",
                "lastprice",
                "currentprice",
                "price"
            ):

                price = valid_price(
                    value
                )

                if price is not None:

                    results.append(
                        price
                    )

            recursive_find_prices(
                value,
                results
            )

    elif isinstance(
        obj,
        list
    ):

        for item in obj:

            recursive_find_prices(
                item,
                results
            )

    return results


# ============================================================
# CURRENT GIFT PRICE
# ============================================================

def get_current_gift():

    html = get_current_page()

    try:

        RAW_FILE.write_text(
            html,
            encoding="utf-8"
        )

    except Exception:
        pass

    data = extract_next_data(
        html
    )

    if data:

        # First try exact instrument
        try:

            instrument = (
                data
                ["props"]
                ["pageProps"]
                ["state"]
                ["indexStore"]
                ["instrument"]
            )

            price_obj = instrument.get(
                "price",
                {}
            )

            candidates = [

                price_obj.get(
                    "last"
                ),

                price_obj.get(
                    "lastPrice"
                ),

                price_obj.get(
                    "current"
                ),

                price_obj.get(
                    "currentPrice"
                ),

                price_obj.get(
                    "price"
                )
            ]

            for candidate in candidates:

                price = valid_price(
                    candidate
                )

                if price is not None:

                    return price

        except Exception:
            pass

        # Fallback recursive search
        prices = recursive_find_prices(
            data
        )

        if prices:

            return prices[0]

    return None


# ============================================================
# SAVE CURRENT
# ============================================================

def save_current(
    price,
    now
):

    row = {

        "Timestamp_IST":
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "GIFT_NIFTY_Current":
            price,

        "Source":
            "Investing.com"
    }

    with open(
        CURRENT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=row.keys()
        )

        writer.writeheader()

        writer.writerow(
            row
        )


# ============================================================
# SAVE HISTORY SNAPSHOT
# ============================================================

def save_history_snapshot(
    price,
    now
):

    fields = [

        "Timestamp_IST",

        "Date",

        "Time",

        "GIFT_NIFTY_Current",

        "Source"
    ]

    row = {

        "Timestamp_IST":
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Date":
            now.strftime(
                "%Y-%m-%d"
            ),

        "Time":
            now.strftime(
                "%H:%M:%S"
            ),

        "GIFT_NIFTY_Current":
            price,

        "Source":
            "Investing.com"
    }

    rows = []

    if HISTORY_FILE.exists():

        try:

            with open(
                HISTORY_FILE,
                "r",
                encoding="utf-8-sig"
            ) as f:

                old_rows = list(
                    csv.DictReader(f)
                )

            for old in old_rows:

                clean = {}

                for field in fields:

                    clean[field] = (
                        old.get(
                            field,
                            ""
                        )
                    )

                rows.append(
                    clean
                )

        except Exception:

            rows = []

    # Don't duplicate exact timestamp

    exists = any(
        r.get(
            "Timestamp_IST"
        )
        == row["Timestamp_IST"]
        for r in rows
    )

    if not exists:

        rows.append(
            row
        )

    rows.sort(
        key=lambda x: (
            x.get(
                "Date",
                ""
            ),
            x.get(
                "Time",
                ""
            )
        )
    )

    with open(
        HISTORY_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields,
            extrasaction="ignore"
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


# ============================================================
# TARGET 3:40 DATE
# ============================================================

def target_340_date():

    now = datetime.now(
        IST
    )

    cutoff = now.replace(
        hour=15,
        minute=40,
        second=0,
        microsecond=0
    )

    if now >= cutoff:

        return now.date()

    return (
        now.date()
        -
        timedelta(days=1)
    )


# ============================================================
# FIND 3:40 FROM LOCAL HISTORY
# ============================================================

def find_local_340():

    target_date = (
        target_340_date()
    )

    if not HISTORY_FILE.exists():

        return None

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

        return None

    candidates = []

    target_text = (
        target_date.strftime(
            "%Y-%m-%d"
        )
    )

    for row in rows:

        if row.get(
            "Date"
        ) != target_text:

            continue

        price = valid_price(
            row.get(
                "GIFT_NIFTY_Current"
            )
        )

        if price is None:
            continue

        time_text = row.get(
            "Time",
            ""
        )

        try:

            dt = datetime.strptime(
                f"{target_text} "
                f"{time_text[:8]}",
                "%Y-%m-%d %H:%M:%S"
            )

        except Exception:

            continue

        target = datetime.strptime(
            f"{target_text} 15:40:00",
            "%Y-%m-%d %H:%M:%S"
        )

        seconds = abs(
            (
                dt - target
            ).total_seconds()
        )

        candidates.append(
            (
                seconds,
                dt,
                price
            )
        )

    if not candidates:

        return None

    candidates.sort(
        key=lambda x: x[0]
    )

    seconds, dt, price = (
        candidates[0]
    )

    # Maximum 10 minutes away

    if seconds > 600:

        return None

    return {

        "date":
            target_text,

        "time":
            dt.strftime(
                "%H:%M:%S"
            ),

        "price":
            price
    }


# ============================================================
# MAIN
# ============================================================

def main():

    now = datetime.now(
        IST
    )

    print(
        f"Current IST : "
        f"{now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # --------------------------------------------------------
    # CURRENT
    # --------------------------------------------------------

    try:

        current = get_current_gift()

    except Exception as error:

        print(
            f"GIFT NIFTY ERROR: {error}"
        )

        return 1

    if current is None:

        print(
            "GIFT NIFTY : N/A"
        )

        print(
            "STATUS     : CURRENT_UNAVAILABLE"
        )

        return 1

    # --------------------------------------------------------
    # Save current
    # --------------------------------------------------------

    save_current(
        current,
        now
    )

    save_history_snapshot(
        current,
        now
    )

    # --------------------------------------------------------
    # Find 3:40
    # --------------------------------------------------------

    historical = find_local_340()

    print()

    print(
        f"GIFT NIFTY : "
        f"{current:.2f}"
    )

    if historical:

        difference = round(
            current
            -
            historical["price"],
            2
        )

        difference_pct = round(
            (
                difference
                /
                historical["price"]
            ) * 100,
            2
        )

        print(
            "3:40 Date  : "
            f"{historical['date']}"
        )

        print(
            "3:40 Price : "
            f"{historical['price']:.2f}"
        )

        print(
            "Difference : "
            f"{difference:.2f}"
        )

        print(
            "Difference%: "
            f"{difference_pct:.2f}%"
        )

        print(
            "STATUS     : "
            "3_40_FOUND"
        )

    else:

        print(
            "3:40 Date  : "
            f"{target_340_date()}"
        )

        print(
            "3:40 Price : N/A"
        )

        print(
            "Difference : N/A"
        )

        print(
            "Difference%: N/A"
        )

        print(
            "STATUS     : "
            "3_40_NOT_IN_LOCAL_HISTORY"
        )

    return 0


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )