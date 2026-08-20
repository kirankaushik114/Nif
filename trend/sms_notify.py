# ============================================================
# D:\Nif\trend\sms_notify.py
# CAS SIMPLE SMS MESSAGE
# ============================================================

import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DECISION_FILE = (
    BASE_DIR
    / "data"
    / "cas_decision.csv"
)

PHONE_NUMBER = "+918861470754"


# ============================================================
# LOAD DECISION
# ============================================================

def load_decision():

    if not DECISION_FILE.exists():

        raise FileNotFoundError(
            f"Decision file not found:\n{DECISION_FILE}"
        )

    with open(
        DECISION_FILE,
        "r",
        encoding="utf-8-sig"
    ) as f:

        rows = list(
            csv.DictReader(f)
        )

    if not rows:

        raise RuntimeError(
            "cas_decision.csv is empty."
        )

    return rows[-1]


# ============================================================
# FORMAT
# ============================================================

def fmt(value):

    if value in (None, "", "None"):
        return "N/A"

    try:
        return f"{float(value):.2f}"

    except Exception:
        return str(value)


# ============================================================
# CREATE SMS
# ============================================================

def build_message(row):

    return (
        "CAS MORNING\n"
        f"NIFTY: {fmt(row.get('NIFTY_Current'))}\n"
        f"GIFT: {fmt(row.get('Gift_Nifty_Current'))} "
        f"({fmt(row.get('Gift_Nifty_Change_Pct'))}%)\n"
        f"BRENT: {fmt(row.get('Brent_Current'))} "
        f"({fmt(row.get('Brent_Change_Pct'))}%)\n"
        f"BIAS: {row.get('V2_Bias', 'N/A')}\n"
        f"ACTION: {row.get('Action', 'N/A')}\n"
        f"CE > {fmt(row.get('CE_Trigger'))}\n"
        f"PE < {fmt(row.get('PE_Trigger'))}\n"
        f"CONFIDENCE: {fmt(row.get('Confidence'))}%"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    row = load_decision()

    message = build_message(row)

    print()
    print("=" * 50)
    print("CAS SMS")
    print("=" * 50)

    print(
        "To:",
        PHONE_NUMBER
    )

    print()
    print(message)

    print()
    print("=" * 50)
    print(
        "SMS MESSAGE READY"
    )
    print("=" * 50)

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )