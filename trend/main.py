# ============================================================
# D:\Nif\trend\main.py
#
# CAS MARKET PIPELINE
#
# NIFTY + GIFT NIFTY + BRENT
#
# GIFT NIFTY:
#   Before 15:40 -> previous date
#   After  15:40 -> current date
#
#   Current - 3:40
#
# EMAIL:
#   Gmail
# ============================================================

import csv
import os
import smtplib
import subprocess
import sys

from pathlib import Path
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from email.message import EmailMessage


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

PYTHON = sys.executable

IST = ZoneInfo("Asia/Kolkata")


# ============================================================
# EMAIL
# ============================================================

EMAIL_FROM = "maclax1990@gmail.com"

EMAIL_TO = "kirankaushikvs@gmail.com"

EMAIL_PASSWORD = os.getenv(
    "CAS_EMAIL_PASSWORD"
)


# ============================================================
# PIPELINE SCRIPTS
# ============================================================

SCRIPTS = [

    "nifty_collector.py",

    "crude_collector.py",

    "gift_nifty_collector.py",

    "nifty_open_collector.py",

    "cas_nifty_v2.py",

    "cas_market_signal.py",

    "cas_daily_forecast.py",

    "cas_decision_engine.py",
]


# ============================================================
# FILES
# ============================================================

NIFTY_FILE = (
    DATA_DIR /
    "cas_nifty_v2.csv"
)

GIFT_CURRENT_FILE = (
    DATA_DIR /
    "gift_nifty" /
    "gift_nifty_current.csv"
)

GIFT_340_FILE = (
    DATA_DIR /
    "gift_nifty" /
    "gift_nifty_340.csv"
)

BRENT_FILE = (
    DATA_DIR /
    "crude" /
    "brent_current.csv"
)

SIGNAL_FILE = (
    DATA_DIR /
    "cas_market_signal.csv"
)

DECISION_FILE = (
    DATA_DIR /
    "cas_decision.csv"
)

NIFTY_OPEN_FILE = (
    DATA_DIR /
    "nifty_open" /
    "nifty_open_current.csv"
)


# ============================================================
# CSV HELPERS
# ============================================================

def read_rows(path):

    if not path.exists():
        return []

    try:

        with open(
            path,
            "r",
            encoding="utf-8-sig"
        ) as f:

            return list(
                csv.DictReader(f)
            )

    except Exception:

        return []


def read_last_row(path):

    rows = read_rows(path)

    if not rows:
        return None

    return rows[-1]


# ============================================================
# NUMBER
# ============================================================

def number(value):

    if value in (
        None,
        "",
        "None",
        "nan",
        "NaN",
        "N/A"
    ):

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
# RUN SCRIPT
#
# No individual OK messages.
# ============================================================

def run_script(script):

    path = BASE_DIR / script

    if not path.exists():

        print(
            f"ERROR: Missing {script}"
        )

        return False

    result = subprocess.run(

        [
            PYTHON,
            str(path)
        ],

        cwd=str(BASE_DIR),

        stdout=subprocess.DEVNULL,

        stderr=subprocess.PIPE,

        text=True
    )

    if result.returncode != 0:

        print()
        print(
            f"ERROR: {script}"
        )

        if result.stderr:

            print(
                result.stderr[-1500:]
            )

        return False

    return True


# ============================================================
# GIFT 3:40 TARGET DATE
#
# Before 15:40:
#     previous calendar day
#
# At/after 15:40:
#     today
# ============================================================

def get_gift_target_date():

    now = datetime.now(
        IST
    )

    cutoff = datetime.combine(
        now.date(),
        time(
            15,
            40
        ),
        tzinfo=IST
    )

    if now >= cutoff:

        return now.date()

    return (
        now.date()
        -
        timedelta(days=1)
    )


# ============================================================
# GET CURRENT GIFT NIFTY
# ============================================================

def get_gift_current():

    row = read_last_row(
        GIFT_CURRENT_FILE
    )

    if not row:
        return None

    return number(
        row.get(
            "GIFT_NIFTY_Current"
        )
    )


# ============================================================
# GET GIFT 3:40 VALUE
# ============================================================

def get_gift_340():

    target_date = (
        get_gift_target_date()
    )

    target_text = (
        target_date.strftime(
            "%Y-%m-%d"
        )
    )

    rows = read_rows(
        GIFT_340_FILE
    )

    if not rows:

        return {

            "date":
                target_text,

            "price":
                None,

            "timestamp":
                None,

            "status":
                "HISTORY_FILE_NOT_FOUND"
        }

    # --------------------------------------------------------
    # Find target date
    # --------------------------------------------------------

    for row in rows:

        if row.get(
            "Date"
        ) != target_text:

            continue

        price = number(
            row.get(
                "GIFT_NIFTY_340"
            )
        )

        if price is None:
            continue

        date_value = row.get(
            "Date",
            target_text
        )

        time_value = row.get(
            "Time",
            ""
        )

        timestamp = (
            f"{date_value} "
            f"{time_value}"
        ).strip()

        return {

            "date":
                target_text,

            "price":
                price,

            "timestamp":
                timestamp,

            "status":
                "FOUND"
        }

    return {

        "date":
            target_text,

        "price":
            None,

        "timestamp":
            None,

        "status":
            "3_40_VALUE_NOT_FOUND"
    }


# ============================================================
# GIFT DIFFERENCE
#
# Current - 3:40
# ============================================================

def calculate_gift_difference(
    current,
    price_340
):

    if (
        current is None
        or
        price_340 is None
    ):

        return (
            None,
            None
        )

    difference = round(
        current -
        price_340,
        2
    )

    if price_340 == 0:

        return (
            difference,
            None
        )

    difference_pct = round(
        (
            difference /
            price_340
        ) * 100,
        2
    )

    return (
        difference,
        difference_pct
    )


# ============================================================
# NIFTY SESSION DATA
#
# Reads values from cas_decision.csv if available.
# ============================================================

def get_decision_value(
    decision,
    *names
):

    if not decision:
        return None

    for name in names:

        value = number(
            decision.get(
                name
            )
        )

        if value is not None:
            return value

    return None


# ============================================================
# EMAIL
# ============================================================

def send_email(
    nifty,
    gift,
    brent,
    signal,
    decision,
    gift_340,
    gift_difference,
    gift_difference_pct
):

    if not EMAIL_PASSWORD:

        return (
            False,
            "NOT_CONFIGURED"
        )

    nifty_current = (
        number(
            nifty.get(
                "Current_Close"
            )
        )
        if nifty
        else None
    )

    gift_current = (
        number(
            gift.get(
                "GIFT_NIFTY_Current"
            )
        )
        if gift
        else None
    )

    brent_current = (
        number(
            brent.get(
                "Brent_Current_Price"
            )
        )
        if brent
        else None
    )

    brent_change = (
        number(
            brent.get(
                "Brent_Change_Pct"
            )
        )
        if brent
        else None
    )

    market = (
        signal.get(
            "Market_Signal",
            "N/A"
        )
        if signal
        else "N/A"
    )

    confidence = (
        number(
            signal.get(
                "Macro_Confidence"
            )
        )
        if signal
        else None
    )

    action = (
        decision.get(
            "Action",
            "N/A"
        )
        if decision
        else "N/A"
    )

    reason = (
        decision.get(
            "Reason",
            "N/A"
        )
        if decision
        else "N/A"
    )

    body = f"""
CAS MARKET ALERT

Time IST
{datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")}

--------------------------------------------------

NIFTY

Current       : {fmt(nifty_current)}

Expected      : {fmt(nifty.get("Predicted_Next_Low") if nifty else None)} - {fmt(nifty.get("Predicted_Next_High") if nifty else None)}

Bias          : {nifty.get("Bias", "N/A") if nifty else "N/A"}

Volatility    : {nifty.get("Volatility_Regime", "N/A") if nifty else "N/A"}

--------------------------------------------------

GIFT NIFTY

3:40 Date     : {gift_340["date"]}

3:40 Price    : {fmt(gift_340["price"])}

3:40 Time     : {gift_340["timestamp"] or "N/A"}

Current       : {fmt(gift_current)}

Difference    : {fmt(gift_difference)}

Difference %  : {fmt(gift_difference_pct)}%

Status        : {gift_340["status"]}

--------------------------------------------------

BRENT

Current       : {fmt(brent_current)}

Change %      : {fmt(brent_change)}%

Oil           : {brent.get("Oil_Pressure", "N/A") if brent else "N/A"}

--------------------------------------------------

MARKET

Signal        : {market}

Confidence    : {fmt(confidence)}%

--------------------------------------------------

DECISION

Action        : {action}

CE Trigger    : {fmt(decision.get("CE_Trigger") if decision else None)}

PE Trigger    : {fmt(decision.get("PE_Trigger") if decision else None)}

Confidence    : {fmt(decision.get("Confidence") if decision else None)}%

Reason

{reason}

--------------------------------------------------

Data
{DATA_DIR}
"""

    message = EmailMessage()

    message["From"] = EMAIL_FROM

    message["To"] = EMAIL_TO

    message["Subject"] = (
        "CAS Market Alert - "
        f"{action}"
    )

    message.set_content(
        body.strip()
    )

    try:

        with smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=30
        ) as server:

            server.starttls()

            server.login(
                EMAIL_FROM,
                EMAIL_PASSWORD
            )

            server.send_message(
                message
            )

        return (
            True,
            "SENT"
        )

    except Exception as error:

        return (
            False,
            str(error)
        )


# ============================================================
# PRINT RESULT
# ============================================================

def print_result():

    nifty = read_last_row(
        NIFTY_FILE
    )

    gift = read_last_row(
        GIFT_CURRENT_FILE
    )

    brent = read_last_row(
        BRENT_FILE
    )

    signal = read_last_row(
        SIGNAL_FILE
    )

    decision = read_last_row(
        DECISION_FILE
    )

    # --------------------------------------------------------
    # GIFT
    # --------------------------------------------------------

    gift_current = (
        number(
            gift.get(
                "GIFT_NIFTY_Current"
            )
        )
        if gift
        else None
    )

    gift_340 = (
        get_gift_340()
    )

    (
        gift_difference,
        gift_difference_pct
    ) = calculate_gift_difference(
        gift_current,
        gift_340["price"]
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()

    print(
        "=" * 60
    )

    print(
        "CAS MORNING RESULT"
    )

    print(
        "=" * 60
    )

    # ========================================================
    # NIFTY
    # ========================================================

    print()

    print(
        "NIFTY"
    )

    print(
        f"Current     : "
        f"{fmt(nifty.get('Current_Close') if nifty else None)}"
    )

    print(
        f"Expected    : "
        f"{fmt(nifty.get('Predicted_Next_Low') if nifty else None)}"
        f" - "
        f"{fmt(nifty.get('Predicted_Next_High') if nifty else None)}"
    )

    print(
        f"Bias        : "
        f"{nifty.get('Bias', 'N/A') if nifty else 'N/A'}"
    )

    print(
        f"Volatility  : "
        f"{nifty.get('Volatility_Regime', 'N/A') if nifty else 'N/A'}"
    )

    # ========================================================
    # NIFTY SESSION
    # ========================================================

    n315 = get_decision_value(
        decision,
        "NIFTY_3_15",
        "NIFTY_15_15"
    )

    n330 = get_decision_value(
        decision,
        "NIFTY_3_30",
        "NIFTY_15_30",
        "NIFTY_1530"
    )

    n915 = get_decision_value(
        decision,
        "NIFTY_09_15_OPEN",
        "NIFTY_9_15_OPEN",
        "NIFTY_0915"
    )

    print()

    print(
        "NIFTY SESSION"
    )

    print(
        f"3:15       : "
        f"{fmt(n315)}"
    )

    print(
        f"3:30       : "
        f"{fmt(n330)}"
    )

    if (
        n315 is not None
        and
        n330 is not None
    ):

        diff_315_330 = round(
            n330 - n315,
            2
        )

        print(
            f"3:15→3:30  : "
            f"{diff_315_330:+.2f}"
        )

    else:

        print(
            "3:15→3:30  : N/A"
        )

    print(
        f"9:15 Open  : "
        f"{fmt(n915)}"
    )

    if (
        n915 is not None
        and
        n330 is not None
    ):

        diff_330_915 = round(
            n915 - n330,
            2
        )

        if n330 != 0:

            gap_pct = round(
                (
                    diff_330_915 /
                    n330
                ) * 100,
                2
            )

        else:

            gap_pct = None

        print(
            f"3:30→9:15  : "
            f"{diff_330_915:+.2f}"
            f" "
            f"({fmt(gap_pct)}%)"
        )

    else:

        print(
            "3:30→9:15  : N/A"
        )

    # ========================================================
    # GIFT NIFTY
    # ========================================================

    print()

    print(
        "GIFT NIFTY"
    )

    print(
        f"3:40 Date   : "
        f"{gift_340['date']}"
    )

    print(
        f"3:40 Price  : "
        f"{fmt(gift_340['price'])}"
    )

    print(
        f"3:40 Time   : "
        f"{gift_340['timestamp'] or 'N/A'}"
    )

    print(
        f"Current     : "
        f"{fmt(gift_current)}"
    )

    print(
        f"Difference  : "
        f"{fmt(gift_difference)}"
    )

    print(
        f"Difference% : "
        f"{fmt(gift_difference_pct)}%"
    )

    print(
        f"Status      : "
        f"{gift_340['status']}"
    )

    # ========================================================
    # BRENT
    # ========================================================

    print()

    print(
        "BRENT"
    )

    print(
        f"Current     : "
        f"{fmt(brent.get('Brent_Current_Price') if brent else None)}"
    )

    print(
        f"Change      : "
        f"{fmt(brent.get('Brent_Change_Pct') if brent else None)}%"
    )

    print(
        f"Oil         : "
        f"{brent.get('Oil_Pressure', 'N/A') if brent else 'N/A'}"
    )

    # ========================================================
    # MARKET
    # ========================================================

    print()

    print(
        "MARKET"
    )

    print(
        f"Signal      : "
        f"{signal.get('Market_Signal', 'N/A') if signal else 'N/A'}"
    )

    print(
        f"Confidence  : "
        f"{fmt(signal.get('Macro_Confidence') if signal else None)}%"
    )

    # ========================================================
    # DECISION
    # ========================================================

    if decision:

        print()

        print(
            "-" * 60
        )

        print(
            f"ACTION      : "
            f"{decision.get('Action', 'N/A')}"
        )

        print(
            f"CE TRIGGER  : "
            f"{fmt(decision.get('CE_Trigger'))}"
        )

        print(
            f"PE TRIGGER  : "
            f"{fmt(decision.get('PE_Trigger'))}"
        )

        print(
            f"CONFIDENCE  : "
            f"{fmt(decision.get('Confidence'))}%"
        )

        print(
            f"REASON      : "
            f"{decision.get('Reason', 'N/A')}"
        )

    # ========================================================
    # EMAIL
    # ========================================================

    sent, status = send_email(

        nifty,

        gift,

        brent,

        signal,

        decision,

        gift_340,

        gift_difference,

        gift_difference_pct
    )

    print()

    if sent:

        print(
            f"EMAIL       : "
            f"SENT → {EMAIL_TO}"
        )

    elif status == "NOT_CONFIGURED":

        print(
            "EMAIL       : "
            "NOT CONFIGURED"
        )

        print(
            "Set CAS_EMAIL_PASSWORD first."
        )

    else:

        print(
            "EMAIL       : FAILED"
        )

        print(
            f"Email error : "
            f"{status}"
        )

    print()

    print(
        "=" * 60
    )

    print(
        f"Data: {DATA_DIR}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    now = datetime.now(
        IST
    )

    # --------------------------------------------------------
    # Run pipeline
    # --------------------------------------------------------

    for script in SCRIPTS:

        if not run_script(
            script
        ):

            print()

            print(
                "=" * 60
            )

            print(
                "CAS PIPELINE FAILED"
            )

            print(
                "=" * 60
            )

            return 1

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print()

    print(
        f"Time IST : "
        f"{now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print_result()

    return 0


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )