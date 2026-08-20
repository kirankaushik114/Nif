import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(r"D:\Nif\trend")

V2_FILE = (
    BASE_DIR
    / "data"
    / "cas_nifty_v2.csv"
)

NIFTY_FILE = (
    BASE_DIR
    / "data"
    / "nifty_free_training.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "cas_daily_forecast.csv"
)

STRIKE_STEP = 50


# ============================================================
# LOAD
# ============================================================

def load_data():

    v2 = pd.read_csv(
        V2_FILE
    )

    nifty = pd.read_csv(
        NIFTY_FILE
    )

    v2["Date"] = pd.to_datetime(
        v2["Date"],
        errors="coerce"
    )

    nifty["Date"] = pd.to_datetime(
        nifty["Date"],
        errors="coerce"
    )

    return v2, nifty


# ============================================================
# SELECT STRIKE
# ============================================================

def select_strike(nifty_close):

    return int(
        round(
            nifty_close
            / STRIKE_STEP
        )
        * STRIKE_STEP
    )


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

def calculate_levels(
    current_close,
    expected_high,
    expected_low,
    expected_range
):

    # --------------------------------------------------------
    # Expected range boundaries
    # --------------------------------------------------------

    support_1 = expected_low

    resistance_1 = expected_high

    # --------------------------------------------------------
    # Inner levels
    # --------------------------------------------------------

    support_2 = (
        current_close
        - expected_range * 0.25
    )

    resistance_2 = (
        current_close
        + expected_range * 0.25
    )

    return (
        support_1,
        support_2,
        resistance_2,
        resistance_1,
    )


# ============================================================
# SCENARIO
# ============================================================

def scenario(
    current,
    predicted_close,
    expected_high,
    expected_low
):

    upside = (
        expected_high
        - current
    )

    downside = (
        current
        - expected_low
    )

    close_move = (
        predicted_close
        - current
    )

    # --------------------------------------------------------
    # Strong upside
    # --------------------------------------------------------

    if (
        close_move > 40
        and upside > downside
    ):

        return "BULLISH"

    # --------------------------------------------------------
    # Strong downside
    # --------------------------------------------------------

    if (
        close_move < -40
        and downside > upside
    ):

        return "BEARISH"

    # --------------------------------------------------------
    # Otherwise
    # --------------------------------------------------------

    return "SIDEWAYS"


# ============================================================
# CONFIDENCE
# ============================================================

def confidence(
    volatility_regime,
    direction_signal
):

    signal = abs(
        float(direction_signal)
    )

    # Low directional signal
    if signal < 15:

        direction_confidence = 45

    elif signal < 35:

        direction_confidence = 60

    elif signal < 60:

        direction_confidence = 72

    else:

        direction_confidence = 82

    # High volatility reduces confidence
    if volatility_regime == "HIGH_VOLATILITY":

        direction_confidence -= 8

    elif volatility_regime == "EXPANSION":

        direction_confidence -= 12

    elif volatility_regime == "LOW_VOLATILITY":

        direction_confidence += 3

    direction_confidence = max(
        20,
        min(
            direction_confidence,
            90
        )
    )

    return direction_confidence


# ============================================================
# OPTION SCENARIO
# ============================================================

def option_scenario(
    bias,
    current_close,
    predicted_high,
    predicted_low,
    strike
):

    if bias == "BULLISH":

        primary = "CE"

        secondary = "PE"

    elif bias == "BEARISH":

        primary = "PE"

        secondary = "CE"

    else:

        primary = "WAIT"

        secondary = "WAIT"

    return {

        "Selected_Strike":
            strike,

        "Primary_Option":
            primary,

        "Secondary_Option":
            secondary,

        "CE_Trigger":
            predicted_high,

        "PE_Trigger":
            predicted_low,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 80)
    print("CAS DAILY NIFTY FORECAST")
    print("=" * 80)

    v2, nifty = load_data()

    if v2.empty:

        print(
            "No V2 data."
        )

        return

    # Latest completed NIFTY day
    latest = v2.iloc[-1]

    current_date = latest["Date"]

    current_close = float(
        latest["Current_Close"]
    )

    predicted_high = float(
        latest[
            "Predicted_Next_High"
        ]
    )

    predicted_low = float(
        latest[
            "Predicted_Next_Low"
        ]
    )

    predicted_average = float(
        latest[
            "Predicted_Next_Average"
        ]
    )

    predicted_close = float(
        latest[
            "Predicted_Next_Close"
        ]
    )

    expected_range = float(
        latest[
            "Expected_Range"
        ]
    )

    direction_signal = float(
        latest[
            "Direction_Signal"
        ]
    )

    volatility_regime = (
        latest[
            "Volatility_Regime"
        ]
    )

    # --------------------------------------------------------
    # Forecast date
    # --------------------------------------------------------

    nifty_dates = sorted(
        nifty["Date"].dropna().unique()
    )

    future_dates = [
        d
        for d in nifty_dates
        if d > current_date
    ]

    if future_dates:

        forecast_date = future_dates[0]

    else:

        # Next calendar day if NIFTY data
        # doesn't contain the future date.
        forecast_date = (
            current_date
            + pd.Timedelta(days=1)
        )

    # --------------------------------------------------------
    # Levels
    # --------------------------------------------------------

    (
        support_1,
        support_2,
        resistance_2,
        resistance_1,
    ) = calculate_levels(
        current_close,
        predicted_high,
        predicted_low,
        expected_range
    )

    # --------------------------------------------------------
    # Bias
    # --------------------------------------------------------

    bias = scenario(
        current_close,
        predicted_close,
        predicted_high,
        predicted_low
    )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    conf = confidence(
        volatility_regime,
        direction_signal
    )

    # --------------------------------------------------------
    # Strike
    # --------------------------------------------------------

    strike = select_strike(
        current_close
    )

    # --------------------------------------------------------
    # Options
    # --------------------------------------------------------

    options = option_scenario(
        bias,
        current_close,
        predicted_high,
        predicted_low,
        strike
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    print()
    print("=" * 80)
    print(
        f"FORECAST FOR: "
        f"{forecast_date.date()}"
    )
    print("=" * 80)

    print()

    print(
        "Previous/Current NIFTY:",
        f"{current_close:.2f}"
    )

    print()

    print(
        "Expected High:",
        f"{predicted_high:.2f}"
    )

    print(
        "Expected Low:",
        f"{predicted_low:.2f}"
    )

    print(
        "Expected Average:",
        f"{predicted_average:.2f}"
    )

    print(
        "Expected Close:",
        f"{predicted_close:.2f}"
    )

    print(
        "Expected Range:",
        f"{expected_range:.2f}"
    )

    print()

    print(
        "Volatility Regime:",
        volatility_regime
    )

    print(
        "Direction Signal:",
        f"{direction_signal:.2f}"
    )

    print(
        "Market Bias:",
        bias
    )

    print(
        "Model Confidence:",
        f"{conf:.1f}%"
    )

    print()

    print("=" * 80)
    print("KEY LEVELS")
    print("=" * 80)

    print()

    print(
        "Support 1:",
        f"{support_1:.2f}"
    )

    print(
        "Support 2:",
        f"{support_2:.2f}"
    )

    print(
        "Resistance 2:",
        f"{resistance_2:.2f}"
    )

    print(
        "Resistance 1:",
        f"{resistance_1:.2f}"
    )

    print()

    print("=" * 80)
    print("OPTION SCENARIO")
    print("=" * 80)

    print()

    print(
        "Selected Strike:",
        strike
    )

    print(
        "Primary:",
        options[
            "Primary_Option"
        ]
    )

    print(
        "Secondary:",
        options[
            "Secondary_Option"
        ]
    )

    print(
        "CE Trigger:",
        f"{options['CE_Trigger']:.2f}"
    )

    print(
        "PE Trigger:",
        f"{options['PE_Trigger']:.2f}"
    )

    print()

    if bias == "BULLISH":

        print(
            "Scenario:"
        )

        print(
            "NIFTY above resistance -> "
            "bullish continuation"
        )

        print(
            "NIFTY below support -> "
            "bullish setup invalid"
        )

    elif bias == "BEARISH":

        print(
            "Scenario:"
        )

        print(
            "NIFTY below support -> "
            "bearish continuation"
        )

        print(
            "NIFTY above resistance -> "
            "bearish setup invalid"
        )

    else:

        print(
            "Scenario:"
        )

        print(
            "Range-bound / wait for breakout."
        )

        print(
            "Above resistance -> bullish"
        )

        print(
            "Below support -> bearish"
        )

    # ========================================================
    # SAVE
    # ========================================================

    result = {

        "Forecast_Date":
            forecast_date.date(),

        "Current_Close":
            current_close,

        "Expected_High":
            predicted_high,

        "Expected_Low":
            predicted_low,

        "Expected_Average":
            predicted_average,

        "Expected_Close":
            predicted_close,

        "Expected_Range":
            expected_range,

        "Volatility_Regime":
            volatility_regime,

        "Direction_Signal":
            direction_signal,

        "Bias":
            bias,

        "Confidence":
            conf,

        "Support_1":
            support_1,

        "Support_2":
            support_2,

        "Resistance_2":
            resistance_2,

        "Resistance_1":
            resistance_1,

        "Selected_Strike":
            strike,

        "Primary_Option":
            options[
                "Primary_Option"
            ],

        "Secondary_Option":
            options[
                "Secondary_Option"
            ],

        "CE_Trigger":
            options[
                "CE_Trigger"
            ],

        "PE_Trigger":
            options[
                "PE_Trigger"
            ],
    }

    output = pd.DataFrame(
        [result]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 80)

    print(
        "Output:",
        OUTPUT_FILE
    )

    print("=" * 80)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()