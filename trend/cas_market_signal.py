# ============================================================
# D:\Nif\trend\cas_market_signal.py
#
# CAS MARKET SIGNAL
#
# Inputs:
#   NIFTY V2
#   BRENT
#   GIFT NIFTY
#
# Output:
#   data\cas_market_signal.csv
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

NIFTY_FILE = (
    DATA_DIR /
    "cas_nifty_v2.csv"
)

BRENT_FILE = (
    DATA_DIR /
    "crude" /
    "brent_current.csv"
)

GIFT_FILE = (
    DATA_DIR /
    "gift_nifty" /
    "gift_nifty_current.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "cas_market_signal.csv"
)

IST = ZoneInfo(
    "Asia/Kolkata"
)


# ============================================================
# CSV
# ============================================================

def read_last_row(path):

    if not path.exists():

        print(
            "FILE NOT FOUND:",
            path
        )

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

        if not rows:

            print(
                "NO ROWS:",
                path
            )

            return None

        return rows[-1]

    except Exception as error:

        print(
            "CSV ERROR:",
            path
        )

        print(error)

        return None


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
# NIFTY
# ============================================================

def load_nifty():

    row = read_last_row(
        NIFTY_FILE
    )

    if row is None:

        return {
            "current": None,
            "high": None,
            "low": None,
            "average": None,
            "close": None,
            "range": None,
            "volatility": "UNKNOWN",
            "bias": "UNKNOWN",
        }

    return {

        "current":
            to_float(
                row.get(
                    "Current_Close"
                )
            ),

        "high":
            to_float(
                row.get(
                    "Predicted_Next_High"
                )
            ),

        "low":
            to_float(
                row.get(
                    "Predicted_Next_Low"
                )
            ),

        "average":
            to_float(
                row.get(
                    "Predicted_Next_Average"
                )
            ),

        "close":
            to_float(
                row.get(
                    "Predicted_Next_Close"
                )
            ),

        "range":
            to_float(
                row.get(
                    "Expected_Range"
                )
            ),

        "volatility":
            row.get(
                "Volatility_Regime",
                "UNKNOWN"
            ),

        "bias":
            row.get(
                "Bias",
                "UNKNOWN"
            ),
    }


# ============================================================
# BRENT
# ============================================================

def load_brent():

    row = read_last_row(
        BRENT_FILE
    )

    if row is None:

        return {
            "current": None,
            "previous": None,
            "change": None,
            "change_pct": None,
            "pressure": "UNKNOWN",
            "status": "UNAVAILABLE",
        }

    current = to_float(
        row.get(
            "Brent_Current_Price"
        )
    )

    previous = to_float(
        row.get(
            "Brent_Previous_Close"
        )
    )

    change = to_float(
        row.get(
            "Brent_Change"
        )
    )

    change_pct = to_float(
        row.get(
            "Brent_Change_Pct"
        )
    )

    pressure = row.get(
        "Oil_Pressure",
        "UNKNOWN"
    )

    status = row.get(
        "Brent_Quote_Status",
        "UNKNOWN"
    )

    return {

        "current":
            current,

        "previous":
            previous,

        "change":
            change,

        "change_pct":
            change_pct,

        "pressure":
            pressure,

        "status":
            status,
    }


# ============================================================
# GIFT NIFTY
# ============================================================

def load_gift():

    row = read_last_row(
        GIFT_FILE
    )

    if row is None:

        return {
            "current": None,
            "previous": None,
            "change": None,
            "change_pct": None,
            "direction": "UNKNOWN",
            "status": "UNAVAILABLE",
        }

    return {

        "current":
            to_float(
                row.get(
                    "GIFT_NIFTY_Current"
                )
            ),

        "previous":
            to_float(
                row.get(
                    "Previous_Session_Close"
                )
            ),

        "change":
            to_float(
                row.get(
                    "Change"
                )
            ),

        "change_pct":
            to_float(
                row.get(
                    "Change_Pct"
                )
            ),

        "direction":
            row.get(
                "Direction",
                "UNKNOWN"
            ),

        "status":
            row.get(
                "Quote_Status",
                "UNKNOWN"
            ),
    }


# ============================================================
# NIFTY SCORE
# ============================================================

def nifty_score(
    bias
):

    bias = str(
        bias
    ).upper().strip()

    if bias in (
        "STRONG_BULLISH",
        "STRONG BULLISH",
    ):

        return 2.0

    if bias in (
        "BULLISH",
        "POSITIVE",
    ):

        return 1.0

    if bias in (
        "STRONG_BEARISH",
        "STRONG BEARISH",
    ):

        return -2.0

    if bias in (
        "BEARISH",
        "NEGATIVE",
    ):

        return -1.0

    return 0.0


# ============================================================
# GIFT SCORE
# ============================================================

def gift_score(
    gift
):

    direction = str(
        gift["direction"]
    ).upper().strip()

    if direction == "STRONG_POSITIVE":

        return 2.0

    if direction == "POSITIVE":

        return 1.0

    if direction == "STRONG_NEGATIVE":

        return -2.0

    if direction == "NEGATIVE":

        return -1.0

    return 0.0


# ============================================================
# OIL SCORE
# ============================================================

def oil_score(
    brent
):

    pct = brent[
        "change_pct"
    ]

    if pct is None:

        return 0.0

    # --------------------------------------------------------
    # FALLING OIL = POSITIVE FOR NIFTY
    # --------------------------------------------------------

    if pct <= -2.0:

        return 2.0

    if pct <= -0.50:

        return 1.0

    # --------------------------------------------------------
    # RISING OIL = NEGATIVE FOR NIFTY
    # --------------------------------------------------------

    if pct >= 2.0:

        return -2.0

    if pct >= 0.50:

        return -1.0

    return 0.0


# ============================================================
# COMBINED SIGNAL
# ============================================================

def calculate_signal(
    nifty,
    gift,
    brent
):

    nifty_s = nifty_score(
        nifty["bias"]
    )

    gift_s = gift_score(
        gift
    )

    oil_s = oil_score(
        brent
    )

    total = (
        nifty_s
        +
        gift_s
        +
        oil_s
    )

    # --------------------------------------------------------
    # FINAL BIAS
    # --------------------------------------------------------

    if total >= 3:

        bias = "STRONG_BULLISH"

    elif total >= 1.5:

        bias = "BULLISH"

    elif total <= -3:

        bias = "STRONG_BEARISH"

    elif total <= -1.5:

        bias = "BEARISH"

    else:

        bias = "SIDEWAYS"

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    confidence = (
        abs(total)
        /
        6.0
        *
        100
    )

    return {

        "nifty_score":
            nifty_s,

        "gift_score":
            gift_s,

        "oil_score":
            oil_s,

        "total":
            total,

        "bias":
            bias,

        "confidence":
            round(
                confidence,
                1
            ),
    }


# ============================================================
# SAVE
# ============================================================

def save_output(
    nifty,
    brent,
    gift,
    signal
):

    now = datetime.now(
        IST
    )

    row = {

        "Timestamp_IST":
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        # ----------------------------------------------------
        # NIFTY
        # ----------------------------------------------------

        "NIFTY_Current":
            nifty["current"],

        "NIFTY_Expected_High":
            nifty["high"],

        "NIFTY_Expected_Low":
            nifty["low"],

        "NIFTY_Expected_Average":
            nifty["average"],

        "NIFTY_Expected_Close":
            nifty["close"],

        "NIFTY_Expected_Range":
            nifty["range"],

        "NIFTY_Volatility":
            nifty["volatility"],

        "NIFTY_V2_Bias":
            nifty["bias"],

        # ----------------------------------------------------
        # BRENT
        # ----------------------------------------------------

        "Brent_Current":
            brent["current"],

        "Brent_Previous_Close":
            brent["previous"],

        "Brent_Change":
            brent["change"],

        "Brent_Change_Pct":
            brent["change_pct"],

        "Oil_Pressure":
            brent["pressure"],

        "Brent_Quote_Status":
            brent["status"],

        # ----------------------------------------------------
        # GIFT
        # ----------------------------------------------------

        "Gift_Nifty_Current":
            gift["current"],

        "Gift_Nifty_Previous_Close":
            gift["previous"],

        "Gift_Nifty_Change":
            gift["change"],

        "Gift_Nifty_Change_Pct":
            gift["change_pct"],

        "Gift_Nifty_Direction":
            gift["direction"],

        "Gift_Nifty_Status":
            gift["status"],

        # ----------------------------------------------------
        # SCORES
        # ----------------------------------------------------

        "NIFTY_Score":
            signal["nifty_score"],

        "Gift_Nifty_Score":
            signal["gift_score"],

        "Oil_Score":
            signal["oil_score"],

        "Combined_Score":
            signal["total"],

        # ----------------------------------------------------
        # FINAL
        # ----------------------------------------------------

        "Combined_Bias":
            signal["bias"],

        "Market_Signal":
            signal["bias"],

        "Macro_Confidence":
            signal["confidence"],
    }

    DATA_DIR.mkdir(
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
            fieldnames=list(
                row.keys()
            )
        )

        writer.writeheader()

        writer.writerow(
            row
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 80)
    print(
        "CAS NIFTY + BRENT + GIFT NIFTY MARKET SIGNAL"
    )
    print("=" * 80)

    # ========================================================
    # LOAD
    # ========================================================

    print()
    print(
        "Loading NIFTY V2..."
    )

    nifty = load_nifty()

    print(
        "Loading Brent..."
    )

    brent = load_brent()

    print(
        "Loading GIFT Nifty..."
    )

    gift = load_gift()

    # ========================================================
    # NIFTY
    # ========================================================

    print()
    print("=" * 80)
    print(
        "NIFTY TECHNICAL"
    )
    print("=" * 80)

    print(
        "V2 Bias               :",
        nifty["bias"]
    )

    print(
        "Current NIFTY         :",
        nifty["current"]
    )

    print(
        "Expected High         :",
        nifty["high"]
    )

    print(
        "Expected Low          :",
        nifty["low"]
    )

    print(
        "Expected Average      :",
        nifty["average"]
    )

    print(
        "Expected Close        :",
        nifty["close"]
    )

    print(
        "Expected Range        :",
        nifty["range"]
    )

    print(
        "Volatility            :",
        nifty["volatility"]
    )

    # ========================================================
    # BRENT
    # ========================================================

    print()
    print("=" * 80)
    print(
        "BRENT OVERNIGHT"
    )
    print("=" * 80)

    print(
        "Current Brent         :",
        brent["current"]
    )

    print(
        "Previous Brent Close  :",
        brent["previous"]
    )

    print(
        "Change                :",
        brent["change"]
    )

    print(
        "Change %              :",
        brent["change_pct"]
    )

    print(
        "Oil Pressure          :",
        brent["pressure"]
    )

    print(
        "Quote Status          :",
        brent["status"]
    )

    # ========================================================
    # GIFT
    # ========================================================

    print()
    print("=" * 80)
    print(
        "GIFT NIFTY"
    )
    print("=" * 80)

    print(
        "Current               :",
        gift["current"]
    )

    print(
        "Previous Close        :",
        gift["previous"]
    )

    print(
        "Change                :",
        gift["change"]
    )

    print(
        "Change %              :",
        gift["change_pct"]
    )

    print(
        "Direction             :",
        gift["direction"]
    )

    print(
        "Quote Status          :",
        gift["status"]
    )

    # ========================================================
    # SIGNAL
    # ========================================================

    signal = calculate_signal(
        nifty,
        gift,
        brent
    )

    print()
    print("=" * 80)
    print(
        "COMBINED MARKET SIGNAL"
    )
    print("=" * 80)

    print(
        "NIFTY Score           :",
        signal["nifty_score"]
    )

    print(
        "GIFT Nifty Score      :",
        signal["gift_score"]
    )

    print(
        "Oil Score             :",
        signal["oil_score"]
    )

    print(
        "Combined Score        :",
        signal["total"]
    )

    print(
        "V2 Bias               :",
        nifty["bias"]
    )

    print(
        "Gift Nifty Direction  :",
        gift["direction"]
    )

    if signal["oil_score"] > 0:

        oil_direction = "POSITIVE"

    elif signal["oil_score"] < 0:

        oil_direction = "NEGATIVE"

    else:

        oil_direction = "NEUTRAL"

    print(
        "Oil Direction         :",
        oil_direction
    )

    print(
        "Combined Bias         :",
        signal["bias"]
    )

    print(
        "Market Signal         :",
        signal["bias"]
    )

    print(
        "Macro Confidence      :",
        f'{signal["confidence"]:.1f}%'
    )

    # ========================================================
    # SAVE
    # ========================================================

    save_output(
        nifty,
        brent,
        gift,
        signal
    )

    print()
    print(
        "Output:",
        OUTPUT_FILE
    )

    print()
    print("=" * 80)
    print(
        "COMPLETE"
    )
    print("=" * 80)


if __name__ == "__main__":

    main()