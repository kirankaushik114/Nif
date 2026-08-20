# ============================================================
# D:\Nif\trend\cas_decision_engine.py
#
# CAS DECISION ENGINE
#
# NIFTY
# + GIFT NIFTY
# + BRENT
# + PREVIOUS 3:15 -> 3:30
# + PREVIOUS 3:30 -> TODAY 9:15
# ============================================================

import csv

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

NIFTY_V2_FILE = (
    DATA_DIR /
    "cas_nifty_v2.csv"
)

GIFT_FILE = (
    DATA_DIR /
    "gift_nifty" /
    "gift_nifty_current.csv"
)

BRENT_FILE = (
    DATA_DIR /
    "crude" /
    "brent_current.csv"
)

NIFTY_HISTORY_FILE = (
    DATA_DIR /
    "nifty_free_training.csv"
)

OPEN_FILE = (
    DATA_DIR /
    "nifty_open" /
    "nifty_open_current.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "cas_decision.csv"
)

IST = ZoneInfo(
    "Asia/Kolkata"
)

BREAKOUT_BUFFER = 10.0


# ============================================================
# CSV
# ============================================================

def read_last_row(path):

    if not path.exists():
        return None

    try:

        with open(
            path,
            "r",
            encoding="utf-8-sig"
        ) as f:

            rows = list(
                csv.DictReader(f)
            )

        return rows[-1] if rows else None

    except Exception:

        return None


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


# ============================================================
# NUMBER
# ============================================================

def number(value):

    if value in (
        None,
        "",
        "None",
        "nan",
        "NaN"
    ):

        return None

    try:

        return float(
            str(value)
            .replace(",", "")
            .replace("%", "")
        )

    except Exception:

        return None


# ============================================================
# NIFTY
# ============================================================

def load_nifty():

    row = read_last_row(
        NIFTY_V2_FILE
    )

    if not row:

        raise RuntimeError(
            "NIFTY V2 data unavailable."
        )

    return {

        "current":
            number(
                row.get(
                    "Current_Close"
                )
            ),

        "high":
            number(
                row.get(
                    "Predicted_Next_High"
                )
            ),

        "low":
            number(
                row.get(
                    "Predicted_Next_Low"
                )
            ),

        "average":
            number(
                row.get(
                    "Predicted_Next_Average"
                )
            ),

        "close":
            number(
                row.get(
                    "Predicted_Next_Close"
                )
            ),

        "range":
            number(
                row.get(
                    "Expected_Range"
                )
            ),

        "bias":
            row.get(
                "Bias",
                "UNKNOWN"
            ),

        "volatility":
            row.get(
                "Volatility_Regime",
                "UNKNOWN"
            )
    }


# ============================================================
# GIFT
# ============================================================

def load_gift():

    row = read_last_row(
        GIFT_FILE
    )

    if not row:

        return {
            "current": None,
            "change_pct": None,
            "direction": "UNKNOWN"
        }

    return {

        "current":
            number(
                row.get(
                    "GIFT_NIFTY_Current"
                )
            ),

        "change_pct":
            number(
                row.get(
                    "Change_Pct"
                )
            ),

        "direction":
            row.get(
                "Direction",
                "UNKNOWN"
            )
    }


# ============================================================
# BRENT
# ============================================================

def load_brent():

    row = read_last_row(
        BRENT_FILE
    )

    if not row:

        return {
            "current": None,
            "change_pct": None,
            "pressure": "UNKNOWN"
        }

    return {

        "current":
            number(
                row.get(
                    "Brent_Current_Price"
                )
            ),

        "change_pct":
            number(
                row.get(
                    "Brent_Change_Pct"
                )
            ),

        "pressure":
            row.get(
                "Oil_Pressure",
                "UNKNOWN"
            )
    }


# ============================================================
# PREVIOUS 3:15 -> 3:30
# ============================================================

def load_late_session():

    rows = read_rows(
        NIFTY_HISTORY_FILE
    )

    if not rows:

        return {
            "date": None,
            "price_315": None,
            "price_330": None,
            "difference": None,
            "direction": "UNKNOWN"
        }

    for row in reversed(rows):

        p315 = number(
            row.get(
                "NIFTY_15_15"
            )
        )

        p330 = number(
            row.get(
                "NIFTY_15_30"
            )
        )

        if (
            p315 is None
            or
            p330 is None
        ):
            continue

        difference = round(
            p330 - p315,
            2
        )

        if difference >= 5:

            direction = "POSITIVE"

        elif difference <= -5:

            direction = "NEGATIVE"

        else:

            direction = "NEUTRAL"

        return {

            "date":
                row.get("Date"),

            "price_315":
                p315,

            "price_330":
                p330,

            "difference":
                difference,

            "direction":
                direction
        }

    return {
        "date": None,
        "price_315": None,
        "price_330": None,
        "difference": None,
        "direction": "UNKNOWN"
    }


# ============================================================
# TODAY 9:15
# ============================================================

def load_open():

    row = read_last_row(
        OPEN_FILE
    )

    if not row:

        return {

            "open": None,
            "timestamp": None,
            "status": "UNAVAILABLE",
            "previous_330": None,
            "difference": None,
            "gap_pct": None,
            "direction": "UNAVAILABLE"
        }

    return {

        "open":
            number(
                row.get(
                    "NIFTY_09_15_OPEN"
                )
            ),

        "timestamp":
            row.get(
                "NIFTY_09_15_TIMESTAMP"
            ),

        "status":
            row.get(
                "NIFTY_09_15_STATUS",
                "UNKNOWN"
            ),

        "previous_330":
            number(
                row.get(
                    "Previous_NIFTY_15_30"
                )
            ),

        "difference":
            number(
                row.get(
                    "NIFTY_09_15_VS_PREVIOUS_15_30"
                )
            ),

        "gap_pct":
            number(
                row.get(
                    "NIFTY_09_15_GAP_PCT"
                )
            ),

        "direction":
            row.get(
                "NIFTY_09_15_DIRECTION",
                "UNKNOWN"
            )
    }


# ============================================================
# TECHNICAL
# ============================================================

def get_technical(
    current,
    high,
    low
):

    if current is None:
        return "UNKNOWN"

    if current >= high + BREAKOUT_BUFFER:
        return "BULLISH"

    if current <= low - BREAKOUT_BUFFER:
        return "BEARISH"

    return "NEUTRAL"


# ============================================================
# MACRO CONFIRMATION
# ============================================================

def get_macro(
    gift,
    brent,
    late,
    opening
):

    bullish = 0
    bearish = 0

    # --------------------------------------------------------
    # GIFT
    # --------------------------------------------------------

    gift_change = gift[
        "change_pct"
    ]

    if gift_change is not None:

        if gift_change >= 0.20:

            bullish += 1

        elif gift_change <= -0.20:

            bearish += 1

    # --------------------------------------------------------
    # BRENT
    # --------------------------------------------------------

    brent_change = brent[
        "change_pct"
    ]

    if brent_change is not None:

        if brent_change <= -0.50:

            bullish += 1

        elif brent_change >= 0.50:

            bearish += 1

    # --------------------------------------------------------
    # PREVIOUS 3:15 -> 3:30
    # --------------------------------------------------------

    late_diff = late[
        "difference"
    ]

    if late_diff is not None:

        if late_diff >= 5:

            bullish += 1

        elif late_diff <= -5:

            bearish += 1

    # --------------------------------------------------------
    # PREVIOUS 3:30 -> TODAY 9:15
    # --------------------------------------------------------

    opening_gap = opening[
        "gap_pct"
    ]

    if opening_gap is not None:

        if opening_gap >= 0.20:

            bullish += 1

        elif opening_gap <= -0.20:

            bearish += 1

    # --------------------------------------------------------
    # MACRO
    # --------------------------------------------------------

    if bullish > bearish:

        macro = "BULLISH"

    elif bearish > bullish:

        macro = "BEARISH"

    else:

        macro = "NEUTRAL"

    return (
        bullish,
        bearish,
        macro
    )


# ============================================================
# DECISION
# ============================================================

def make_decision(
    nifty,
    gift,
    brent,
    late,
    opening
):

    current = nifty["current"]
    high = nifty["high"]
    low = nifty["low"]

    if high is None or low is None:

        raise RuntimeError(
            "NIFTY expected range unavailable."
        )

    ce_trigger = (
        high +
        BREAKOUT_BUFFER
    )

    pe_trigger = (
        low -
        BREAKOUT_BUFFER
    )

    technical = get_technical(
        current,
        high,
        low
    )

    (
        bullish,
        bearish,
        macro
    ) = get_macro(
        gift,
        brent,
        late,
        opening
    )

    # ========================================================
    # WAIT
    # ========================================================

    if technical == "NEUTRAL":

        action = "WAIT"

        location = "INSIDE_RANGE"

        direction = "N/A"

        confidence = 50.0

        reason = (
            "NIFTY is inside the expected range. "
            "Wait for breakout."
        )

    # ========================================================
    # BULLISH
    # ========================================================

    elif technical == "BULLISH":

        location = "ABOVE_RANGE"

        direction = "BULLISH"

        if macro == "BULLISH":

            action = "BUY_CE"
            confidence = 85.0

            reason = (
                "NIFTY bullish breakout confirmed "
                "by macro factors."
            )

        elif macro == "BEARISH":

            action = "WAIT"
            confidence = 55.0

            reason = (
                "Bullish breakout detected, "
                "but macro confirmation is bearish."
            )

        else:

            action = "BUY_CE"
            confidence = 70.0

            reason = (
                "NIFTY bullish breakout with "
                "neutral macro confirmation."
            )

    # ========================================================
    # BEARISH
    # ========================================================

    elif technical == "BEARISH":

        location = "BELOW_RANGE"

        direction = "BEARISH"

        if macro == "BEARISH":

            action = "BUY_PE"
            confidence = 85.0

            reason = (
                "NIFTY bearish breakdown confirmed "
                "by macro factors."
            )

        elif macro == "BULLISH":

            action = "WAIT"
            confidence = 55.0

            reason = (
                "Bearish breakdown detected, "
                "but macro confirmation is bullish."
            )

        else:

            action = "BUY_PE"
            confidence = 70.0

            reason = (
                "NIFTY bearish breakdown with "
                "neutral macro confirmation."
            )

    else:

        action = "WAIT"

        location = "UNKNOWN"

        direction = "N/A"

        confidence = 0.0

        reason = "Insufficient NIFTY data."

    # ========================================================
    # LATE SESSION TEXT
    # ========================================================

    if late["difference"] is not None:

        late_text = (
            f"Previous 3:15={late['price_315']:.2f}, "
            f"3:30={late['price_330']:.2f}, "
            f"Difference={late['difference']:+.2f} "
            f"({late['direction']})"
        )

    else:

        late_text = (
            "Previous 3:15-3:30 unavailable"
        )

    # ========================================================
    # OPENING TEXT
    # ========================================================

    if opening["difference"] is not None:

        opening_text = (
            f"Today 9:15={opening['open']:.2f}, "
            f"vs previous 3:30="
            f"{opening['difference']:+.2f} "
            f"({opening['gap_pct']:+.2f}%, "
            f"{opening['direction']})"
        )

    else:

        opening_text = (
            "Today 9:15 opening comparison unavailable"
        )

    confirmation = (
        f"CE above {ce_trigger:.2f}; "
        f"PE below {pe_trigger:.2f}. "
        f"Macro: {macro}. "
        f"{late_text}. "
        f"{opening_text}."
    )

    # ========================================================
    # RISK
    # ========================================================

    if action == "BUY_CE":

        risk = (
            f"Breakout invalid below "
            f"{ce_trigger:.2f}"
        )

    elif action == "BUY_PE":

        risk = (
            f"Breakdown invalid above "
            f"{pe_trigger:.2f}"
        )

    else:

        risk = "N/A"

    return {

        "action": action,
        "location": location,
        "direction": direction,

        "ce_trigger":
            round(ce_trigger, 2),

        "pe_trigger":
            round(pe_trigger, 2),

        "technical":
            technical,

        "macro":
            macro,

        "bullish":
            bullish,

        "bearish":
            bearish,

        "confidence":
            confidence,

        "reason":
            reason,

        "confirmation":
            confirmation,

        "risk":
            risk
    }


# ============================================================
# SAVE
# ============================================================

def save_decision(
    nifty,
    gift,
    brent,
    late,
    opening,
    decision
):

    now = datetime.now(
        IST
    )

    row = {

        "Timestamp_IST":
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "NIFTY_Current":
            nifty["current"],

        "Expected_High":
            nifty["high"],

        "Expected_Low":
            nifty["low"],

        "Expected_Close":
            nifty["close"],

        "Expected_Range":
            nifty["range"],

        "V2_Bias":
            nifty["bias"],

        "Volatility":
            nifty["volatility"],

        "Gift_Nifty_Current":
            gift["current"],

        "Gift_Nifty_Change_Pct":
            gift["change_pct"],

        "Gift_Nifty_Direction":
            gift["direction"],

        "Brent_Current":
            brent["current"],

        "Brent_Change_Pct":
            brent["change_pct"],

        "Oil_Pressure":
            brent["pressure"],

        # Previous session
        "NIFTY_3_15":
            late["price_315"],

        "NIFTY_3_30":
            late["price_330"],

        "NIFTY_3_15_to_3_30_Difference":
            late["difference"],

        "NIFTY_3_15_to_3_30_Direction":
            late["direction"],

        # Today opening
        "NIFTY_09_15_OPEN":
            opening["open"],

        "NIFTY_09_15_TIMESTAMP":
            opening["timestamp"],

        "NIFTY_09_15_STATUS":
            opening["status"],

        "NIFTY_09_15_VS_PREVIOUS_15_30":
            opening["difference"],

        "NIFTY_09_15_GAP_PCT":
            opening["gap_pct"],

        "NIFTY_09_15_DIRECTION":
            opening["direction"],

        # Decision
        "Technical":
            decision["technical"],

        "Macro_Confirmation":
            decision["macro"],

        "Bullish_Confirmations":
            decision["bullish"],

        "Bearish_Confirmations":
            decision["bearish"],

        "Confidence":
            decision["confidence"],

        "Action":
            decision["action"],

        "Location":
            decision["location"],

        "Direction":
            decision["direction"],

        "CE_Trigger":
            decision["ce_trigger"],

        "PE_Trigger":
            decision["pe_trigger"],

        "Reason":
            decision["reason"],

        "Confirmation":
            decision["confirmation"],

        "Risk":
            decision["risk"]
    }

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

    nifty = load_nifty()

    gift = load_gift()

    brent = load_brent()

    late = load_late_session()

    opening = load_open()

    decision = make_decision(
        nifty,
        gift,
        brent,
        late,
        opening
    )

    print()
    print(
        f"NIFTY       : "
        f"{fmt(nifty['current'])}"
    )

    print(
        f"Range       : "
        f"{fmt(nifty['low'])} - "
        f"{fmt(nifty['high'])}"
    )

    print(
        f"3:15→3:30   : "
        f"{fmt(late['difference'])} "
        f"({late['direction']})"
    )

    print(
        f"3:30→9:15   : "
        f"{fmt(opening['difference'])} "
        f"({fmt(opening['gap_pct'])}%, "
        f"{opening['direction']})"
    )

    print(
        f"GIFT        : "
        f"{fmt(gift['current'])} "
        f"({fmt(gift['change_pct'])}%)"
    )

    print(
        f"BRENT       : "
        f"{fmt(brent['current'])} "
        f"({fmt(brent['change_pct'])}%)"
    )

    print()

    print(
        f"Technical   : "
        f"{decision['technical']}"
    )

    print(
        f"Macro       : "
        f"{decision['macro']}"
    )

    print(
        f"Confidence  : "
        f"{decision['confidence']:.2f}%"
    )

    print()

    print(
        f"ACTION      : "
        f"{decision['action']}"
    )

    print(
        f"CE TRIGGER  : "
        f"{decision['ce_trigger']:.2f}"
    )

    print(
        f"PE TRIGGER  : "
        f"{decision['pe_trigger']:.2f}"
    )

    print(
        f"REASON      : "
        f"{decision['reason']}"
    )

    save_decision(
        nifty,
        gift,
        brent,
        late,
        opening,
        decision
    )

    print(
        f"\nOutput: {OUTPUT_FILE}"
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