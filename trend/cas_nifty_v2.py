import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(r"D:\Nif\trend")

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "nifty_free_training.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "cas_nifty_v2.csv"
)

START_DATE = pd.Timestamp("2026-08-03")


# ============================================================
# LOAD
# ============================================================

def load_data():

    df = pd.read_csv(INPUT_FILE)

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df = df[
        df["Date"] >= START_DATE
    ].copy()

    df = df.sort_values(
        "Date"
    ).reset_index(drop=True)

    columns = [
        "NIFTY_Previous_Close",
        "NIFTY_Open",
        "NIFTY_09_30",
        "NIFTY_10_00",
        "NIFTY_12_30",
        "NIFTY_14_00",
        "NIFTY_15_15",
        "NIFTY_High",
        "NIFTY_Low",
        "NIFTY_Average",
        "NIFTY_Close",
        "NIFTY_Gap",
        "NIFTY_Day_Range",
    ]

    for col in columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    return df


# ============================================================
# FEATURES
# ============================================================

def create_features(df):

    df["MOVE_09_30"] = (
        df["NIFTY_09_30"]
        - df["NIFTY_Open"]
    )

    df["MOVE_10_00"] = (
        df["NIFTY_10_00"]
        - df["NIFTY_Open"]
    )

    df["MOVE_12_30"] = (
        df["NIFTY_12_30"]
        - df["NIFTY_Open"]
    )

    df["MOVE_14_00"] = (
        df["NIFTY_14_00"]
        - df["NIFTY_Open"]
    )

    df["MOVE_15_15"] = (
        df["NIFTY_15_15"]
        - df["NIFTY_Open"]
    )

    df["MORNING_MOVE"] = (
        df["NIFTY_10_00"]
        - df["NIFTY_09_30"]
    )

    df["MIDDAY_MOVE"] = (
        df["NIFTY_14_00"]
        - df["NIFTY_10_00"]
    )

    df["LATE_MOVE"] = (
        df["NIFTY_15_15"]
        - df["NIFTY_14_00"]
    )

    df["FULL_INTRADAY_MOVE"] = (
        df["NIFTY_15_15"]
        - df["NIFTY_09_30"]
    )

    df["CLOSE_MOVE"] = (
        df["NIFTY_Close"]
        - df["NIFTY_Previous_Close"]
    )

    # --------------------------------------------------------
    # Rolling volatility
    # --------------------------------------------------------

    df["RANGE_3"] = (
        df["NIFTY_Day_Range"]
        .rolling(3)
        .mean()
    )

    df["RANGE_5"] = (
        df["NIFTY_Day_Range"]
        .rolling(5)
        .mean()
    )

    df["RANGE_MEDIAN_3"] = (
        df["NIFTY_Day_Range"]
        .rolling(3)
        .median()
    )

    # Previous day's range
    df["PREVIOUS_RANGE"] = (
        df["NIFTY_Day_Range"]
        .shift(1)
    )

    # Range acceleration
    df["RANGE_ACCELERATION"] = (
        df["NIFTY_Day_Range"]
        /
        df["PREVIOUS_RANGE"]
    )

    return df


# ============================================================
# VOLATILITY REGIME
# ============================================================

def volatility_regime(
    df,
    index
):

    row = df.iloc[index]

    current_range = row[
        "NIFTY_Day_Range"
    ]

    previous_range = row[
        "PREVIOUS_RANGE"
    ]

    range_3 = row[
        "RANGE_3"
    ]

    range_5 = row[
        "RANGE_5"
    ]

    if pd.isna(current_range):

        return (
            "UNKNOWN",
            1.0
        )

    if pd.isna(range_3):

        range_3 = current_range

    if pd.isna(range_5):

        range_5 = range_3

    # --------------------------------------------------------
    # Current volatility relative to recent volatility
    # --------------------------------------------------------

    ratio_3 = (
        current_range
        / range_3
        if range_3 > 0
        else 1
    )

    ratio_5 = (
        current_range
        / range_5
        if range_5 > 0
        else 1
    )

    ratio = (
        0.60 * ratio_3
        +
        0.40 * ratio_5
    )

    # --------------------------------------------------------
    # Regime
    # --------------------------------------------------------

    if ratio >= 1.50:

        regime = "EXPANSION"

        multiplier = 1.30

    elif ratio >= 1.20:

        regime = "HIGH_VOLATILITY"

        multiplier = 1.15

    elif ratio <= 0.75:

        regime = "LOW_VOLATILITY"

        multiplier = 0.85

    else:

        regime = "NORMAL"

        multiplier = 1.00

    return (
        regime,
        multiplier
    )


# ============================================================
# HISTORICAL RANGE
# ============================================================

def expected_range(
    df,
    index
):

    row = df.iloc[index]

    previous_range = row[
        "PREVIOUS_RANGE"
    ]

    range_3 = row[
        "RANGE_3"
    ]

    range_5 = row[
        "RANGE_5"
    ]

    candidates = [
        previous_range,
        range_3,
        range_5,
    ]

    candidates = [
        float(x)
        for x in candidates
        if pd.notna(x)
        and float(x) > 0
    ]

    if not candidates:

        return float(
            row["NIFTY_Day_Range"]
        )

    # More weight to recent volatility
    if len(candidates) == 3:

        base = (
            0.50 * candidates[0]
            +
            0.30 * candidates[1]
            +
            0.20 * candidates[2]
        )

    else:

        base = np.mean(
            candidates
        )

    return base


# ============================================================
# DIRECTION
# ============================================================

def direction_signal(
    df,
    index
):

    row = df.iloc[index]

    close_move = row[
        "CLOSE_MOVE"
    ]

    morning = row[
        "MORNING_MOVE"
    ]

    midday = row[
        "MIDDAY_MOVE"
    ]

    late = row[
        "LATE_MOVE"
    ]

    # Missing values
    close_move = (
        0
        if pd.isna(close_move)
        else close_move
    )

    morning = (
        0
        if pd.isna(morning)
        else morning
    )

    midday = (
        0
        if pd.isna(midday)
        else midday
    )

    late = (
        0
        if pd.isna(late)
        else late
    )

    # --------------------------------------------------------
    # Momentum
    # --------------------------------------------------------

    momentum = (
        0.25 * morning
        +
        0.25 * midday
        +
        0.50 * late
    )

    # --------------------------------------------------------
    # Reversal
    # --------------------------------------------------------

    reversal = 0

    if close_move < -100:

        reversal = (
            abs(close_move)
            * 0.20
        )

    elif close_move > 100:

        reversal = (
            -abs(close_move)
            * 0.20
        )

    # --------------------------------------------------------
    # Combined directional movement
    # --------------------------------------------------------

    signal = (
        0.45 * momentum
        +
        0.35 * close_move
        +
        0.20 * reversal
    )

    # Limit extreme forecast
    signal = max(
        min(signal, 100),
        -100
    )

    return signal


# ============================================================
# RANGE FORECAST
# ============================================================

def forecast_range(
    df,
    index
):

    base_range = expected_range(
        df,
        index
    )

    regime, multiplier = (
        volatility_regime(
            df,
            index
        )
    )

    final_range = (
        base_range
        * multiplier
    )

    # Prevent unrealistic collapse
    final_range = max(
        final_range,
        70
    )

    return (
        final_range,
        regime,
        multiplier,
    )


# ============================================================
# FORECAST
# ============================================================

def forecast(
    df,
    index
):

    row = df.iloc[index]

    current_close = float(
        row["NIFTY_Close"]
    )

    signal = direction_signal(
        df,
        index
    )

    expected_rng, regime, multiplier = (
        forecast_range(
            df,
            index
        )
    )

    # --------------------------------------------------------
    # Directional centre
    # --------------------------------------------------------

    # Only part of the signal is used
    # as expected close movement.
    close_adjustment = (
        signal * 0.35
    )

    predicted_close = (
        current_close
        + close_adjustment
    )

    # --------------------------------------------------------
    # High / Low
    # --------------------------------------------------------

    # Slight asymmetric range according
    # to directional signal.
    upside_fraction = 0.50

    downside_fraction = 0.50

    if signal > 20:

        upside_fraction = 0.56
        downside_fraction = 0.44

    elif signal < -20:

        upside_fraction = 0.44
        downside_fraction = 0.56

    predicted_high = (
        predicted_close
        + expected_rng
        * upside_fraction
    )

    predicted_low = (
        predicted_close
        - expected_rng
        * downside_fraction
    )

    predicted_average = (
        predicted_high
        + predicted_low
    ) / 2

    return {

        "Predicted_Next_High":
            predicted_high,

        "Predicted_Next_Low":
            predicted_low,

        "Predicted_Next_Average":
            predicted_average,

        "Predicted_Next_Close":
            predicted_close,

        "Expected_Range":
            predicted_high
            - predicted_low,

        "Direction_Signal":
            signal,

        "Volatility_Regime":
            regime,

        "Volatility_Multiplier":
            multiplier,
    }


# ============================================================
# BIAS
# ============================================================

def calculate_bias(
    signal
):

    if signal > 35:

        return "BULLISH"

    if signal < -35:

        return "BEARISH"

    return "SIDEWAYS"


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 80)
    print("CAS NIFTY V2")
    print("DYNAMIC VOLATILITY + MOMENTUM")
    print("=" * 80)

    df = load_data()

    if len(df) < 3:

        print(
            "Not enough data."
        )

        return

    df = create_features(
        df
    )

    results = []

    # --------------------------------------------------------
    # Walk forward
    # --------------------------------------------------------

    for index in range(
        len(df)
    ):

        if index < 2:
            continue

        row = df.iloc[index]

        prediction = forecast(
            df,
            index
        )

        bias = calculate_bias(
            prediction[
                "Direction_Signal"
            ]
        )

        results.append({

            "Date":
                row["Date"].date(),

            "Current_Close":
                row["NIFTY_Close"],

            "Current_Range":
                row["NIFTY_Day_Range"],

            "Previous_Range":
                row["PREVIOUS_RANGE"],

            "Range_3":
                row["RANGE_3"],

            "Range_5":
                row["RANGE_5"],

            "Volatility_Regime":
                prediction[
                    "Volatility_Regime"
                ],

            "Volatility_Multiplier":
                prediction[
                    "Volatility_Multiplier"
                ],

            "Direction_Signal":
                prediction[
                    "Direction_Signal"
                ],

            "Predicted_Next_High":
                prediction[
                    "Predicted_Next_High"
                ],

            "Predicted_Next_Low":
                prediction[
                    "Predicted_Next_Low"
                ],

            "Predicted_Next_Average":
                prediction[
                    "Predicted_Next_Average"
                ],

            "Predicted_Next_Close":
                prediction[
                    "Predicted_Next_Close"
                ],

            "Expected_Range":
                prediction[
                    "Expected_Range"
                ],

            "Bias":
                bias,
        })

    result = pd.DataFrame(
        results
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # TABLE
    # ========================================================

    print()
    print(
        result.to_string(
            index=False
        )
    )

    # ========================================================
    # LATEST
    # ========================================================

    latest = result.iloc[-1]

    print()
    print("=" * 80)
    print("LATEST V2 FORECAST")
    print("=" * 80)

    print()
    print(
        "Date:",
        latest["Date"]
    )

    print(
        "Current NIFTY:",
        round(
            latest["Current_Close"],
            2
        )
    )

    print(
        "Current Range:",
        round(
            latest["Current_Range"],
            2
        )
    )

    print(
        "Previous Range:",
        round(
            latest["Previous_Range"],
            2
        )
    )

    print(
        "3-Day Range:",
        round(
            latest["Range_3"],
            2
        )
    )

    print(
        "5-Day Range:",
        round(
            latest["Range_5"],
            2
        )
    )

    print()
    print(
        "Volatility Regime:",
        latest["Volatility_Regime"]
    )

    print(
        "Volatility Multiplier:",
        round(
            latest[
                "Volatility_Multiplier"
            ],
            2
        )
    )

    print(
        "Direction Signal:",
        round(
            latest[
                "Direction_Signal"
            ],
            2
        )
    )

    print()
    print(
        "Expected High:",
        round(
            latest[
                "Predicted_Next_High"
            ],
            2
        )
    )

    print(
        "Expected Low:",
        round(
            latest[
                "Predicted_Next_Low"
            ],
            2
        )
    )

    print(
        "Expected Average:",
        round(
            latest[
                "Predicted_Next_Average"
            ],
            2
        )
    )

    print(
        "Expected Close:",
        round(
            latest[
                "Predicted_Next_Close"
            ],
            2
        )
    )

    print(
        "Expected Range:",
        round(
            latest[
                "Expected_Range"
            ],
            2
        )
    )

    print()
    print(
        "Bias:",
        latest["Bias"]
    )

    print()
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