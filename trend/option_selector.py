import math
from datetime import datetime


# ============================================================
# CONFIG
# ============================================================

STRIKE_STEP = 50


# ============================================================
# NEXT ₹50 STRIKE
# ============================================================

def get_strike(nifty_previous_close):

    if nifty_previous_close is None:

        raise ValueError(
            "NIFTY previous close is required."
        )

    return (
        math.ceil(
            nifty_previous_close
            / STRIKE_STEP
        )
        * STRIKE_STEP
    )


# ============================================================
# OPTION SYMBOL
# ============================================================

def build_option_symbol(
    expiry,
    strike,
    option_type
):

    """
    Temporary symbol builder.

    We will verify the exact NSE/Yahoo
    symbol format in the next step.
    """

    expiry_date = datetime.strptime(
        expiry,
        "%Y-%m-%d"
    )

    day = expiry_date.strftime(
        "%d"
    )

    month = expiry_date.strftime(
        "%b"
    ).upper()

    year = expiry_date.strftime(
        "%y"
    )

    return (
        f"NIFTY"
        f"{day}"
        f"{month}"
        f"{year}"
        f"{int(strike)}"
        f"{option_type}"
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    previous_close = 24471.70

    strike = get_strike(
        previous_close
    )

    print()
    print("=" * 70)
    print("NIFTY OPTION SELECTION")
    print("=" * 70)

    print(
        f"Previous NIFTY Close : "
        f"{previous_close}"
    )

    print(
        f"Strike Step          : "
        f"{STRIKE_STEP}"
    )

    print(
        f"Selected Strike      : "
        f"{strike}"
    )

    # Example only.
    # We will automatically discover
    # the real expiry next.

    example_expiry = "2026-08-13"

    ce = build_option_symbol(
        example_expiry,
        strike,
        "CE"
    )

    pe = build_option_symbol(
        example_expiry,
        strike,
        "PE"
    )

    print(
        f"Example CE           : "
        f"{ce}"
    )

    print(
        f"Example PE           : "
        f"{pe}"
    )

    print("=" * 70)