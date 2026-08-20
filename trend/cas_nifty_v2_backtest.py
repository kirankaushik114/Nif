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
    / "cas_nifty_v2_backtest.csv"
)


# ============================================================
# LOAD
# ============================================================

def load_data():

    v2 = pd.read_csv(V2_FILE)
    nifty = pd.read_csv(NIFTY_FILE)

    v2["Date"] = pd.to_datetime(
        v2["Date"],
        errors="coerce"
    )

    nifty["Date"] = pd.to_datetime(
        nifty["Date"],
        errors="coerce"
    )

    numeric_columns = [
        "NIFTY_High",
        "NIFTY_Low",
        "NIFTY_Average",
        "NIFTY_Close",
    ]

    for column in numeric_columns:

        nifty[column] = pd.to_numeric(
            nifty[column],
            errors="coerce"
        )

    return v2, nifty


# ============================================================
# ADD ACTUAL NEXT DAY
# ============================================================

def add_actual_data(
    v2,
    nifty
):

    actual = nifty[
        [
            "Date",
            "NIFTY_High",
            "NIFTY_Low",
            "NIFTY_Average",
            "NIFTY_Close",
        ]
    ].copy()

    actual = actual.sort_values(
        "Date"
    ).reset_index(drop=True)

    # The actual values of the next row
    # belong to the current prediction date.

    actual["Prediction_Date"] = (
        actual["Date"].shift(1)
    )

    actual = actual.rename(
        columns={
            "NIFTY_High":
                "Actual_Next_High",

            "NIFTY_Low":
                "Actual_Next_Low",

            "NIFTY_Average":
                "Actual_Next_Average",

            "NIFTY_Close":
                "Actual_Next_Close",
        }
    )

    actual = actual[
        [
            "Prediction_Date",
            "Actual_Next_High",
            "Actual_Next_Low",
            "Actual_Next_Average",
            "Actual_Next_Close",
        ]
    ]

    result = v2.merge(
        actual,
        left_on="Date",
        right_on="Prediction_Date",
        how="left"
    )

    result.drop(
        columns=["Prediction_Date"],
        inplace=True,
        errors="ignore"
    )

    return result


# ============================================================
# CALCULATE ERRORS
# ============================================================

def calculate_errors(df):

    # --------------------------------------------------------
    # HIGH
    # --------------------------------------------------------

    df["High_Error"] = (
        df["Predicted_Next_High"]
        - df["Actual_Next_High"]
    )

    df["High_Abs_Error"] = (
        df["High_Error"].abs()
    )

    # --------------------------------------------------------
    # LOW
    # --------------------------------------------------------

    df["Low_Error"] = (
        df["Predicted_Next_Low"]
        - df["Actual_Next_Low"]
    )

    df["Low_Abs_Error"] = (
        df["Low_Error"].abs()
    )

    # --------------------------------------------------------
    # AVERAGE
    # --------------------------------------------------------

    df["Average_Error"] = (
        df["Predicted_Next_Average"]
        - df["Actual_Next_Average"]
    )

    df["Average_Abs_Error"] = (
        df["Average_Error"].abs()
    )

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    df["Close_Error"] = (
        df["Predicted_Next_Close"]
        - df["Actual_Next_Close"]
    )

    df["Close_Abs_Error"] = (
        df["Close_Error"].abs()
    )

    # --------------------------------------------------------
    # RANGE
    # --------------------------------------------------------

    df["Actual_Next_Range"] = (
        df["Actual_Next_High"]
        - df["Actual_Next_Low"]
    )

    df["Range_Error"] = (
        df["Expected_Range"]
        - df["Actual_Next_Range"]
    )

    df["Range_Abs_Error"] = (
        df["Range_Error"].abs()
    )

    return df


# ============================================================
# ACTUAL MARKET BIAS
# ============================================================

def calculate_bias(df):

    df["Actual_Move"] = (
        df["Actual_Next_Close"]
        - df["Current_Close"]
    )

    def get_bias(move):

        if pd.isna(move):

            return "UNKNOWN"

        if move > 15:

            return "BULLISH"

        if move < -15:

            return "BEARISH"

        return "SIDEWAYS"

    df["Actual_Bias"] = (
        df["Actual_Move"]
        .apply(get_bias)
    )

    df["Bias_Correct"] = (
        df["Bias"]
        == df["Actual_Bias"]
    )

    return df


# ============================================================
# RANGE HIT
# ============================================================

def calculate_range_hit(df):

    df["Close_Inside_Range"] = (

        df["Actual_Next_Close"]
        >=
        df["Predicted_Next_Low"]

    ) & (

        df["Actual_Next_Close"]
        <=
        df["Predicted_Next_High"]

    )

    # --------------------------------------------------------
    # Did predicted HIGH reach actual HIGH?
    # --------------------------------------------------------

    df["High_Within_50"] = (
        (
            df["Actual_Next_High"]
            - df["Predicted_Next_High"]
        ).abs()
        <= 50
    )

    # --------------------------------------------------------
    # Did predicted LOW reach actual LOW?
    # --------------------------------------------------------

    df["Low_Within_50"] = (
        (
            df["Actual_Next_Low"]
            - df["Predicted_Next_Low"]
        ).abs()
        <= 50
    )

    return df


# ============================================================
# SUMMARY
# ============================================================

def summary(df):

    valid = df[
        df["Actual_Next_Close"].notna()
    ].copy()

    print()
    print("=" * 80)
    print("V2 BACKTEST SUMMARY")
    print("=" * 80)

    print()

    print(
        "Predictions tested:",
        len(valid)
    )

    if valid.empty:

        print(
            "No completed predictions."
        )

        return

    # --------------------------------------------------------
    # Errors
    # --------------------------------------------------------

    metrics = {

        "Average High Error":
            valid["High_Abs_Error"].mean(),

        "Average Low Error":
            valid["Low_Abs_Error"].mean(),

        "Average Average Error":
            valid["Average_Abs_Error"].mean(),

        "Average Close Error":
            valid["Close_Abs_Error"].mean(),

        "Average Range Error":
            valid["Range_Abs_Error"].mean(),
    }

    for name, value in metrics.items():

        print(
            f"{name:<28}: "
            f"{value:.2f}"
        )

    # --------------------------------------------------------
    # Direction
    # --------------------------------------------------------

    directional = valid[
        valid["Actual_Bias"]
        != "UNKNOWN"
    ]

    if not directional.empty:

        accuracy = (
            directional[
                "Bias_Correct"
            ].mean()
            * 100
        )

        print()

        print(
            "Direction Accuracy"
            f"{'':11}: "
            f"{accuracy:.2f}%"
        )

    # --------------------------------------------------------
    # Range hit
    # --------------------------------------------------------

    range_hit = (
        valid[
            "Close_Inside_Range"
        ].mean()
        * 100
    )

    high_hit = (
        valid[
            "High_Within_50"
        ].mean()
        * 100
    )

    low_hit = (
        valid[
            "Low_Within_50"
        ].mean()
        * 100
    )

    print(
        "Close inside range"
        f"{'':12}: "
        f"{range_hit:.2f}%"
    )

    print(
        "High within ±50"
        f"{'':14}: "
        f"{high_hit:.2f}%"
    )

    print(
        "Low within ±50"
        f"{'':15}: "
        f"{low_hit:.2f}%"
    )

    # --------------------------------------------------------
    # Volatility regimes
    # --------------------------------------------------------

    print()
    print("-" * 80)
    print("VOLATILITY REGIME PERFORMANCE")
    print("-" * 80)

    for regime in sorted(
        valid[
            "Volatility_Regime"
        ].dropna().unique()
    ):

        subset = valid[
            valid[
                "Volatility_Regime"
            ]
            == regime
        ]

        if subset.empty:
            continue

        close_error = (
            subset[
                "Close_Abs_Error"
            ].mean()
        )

        range_error = (
            subset[
                "Range_Abs_Error"
            ].mean()
        )

        print()

        print(
            f"{regime}:"
        )

        print(
            "  Days:",
            len(subset)
        )

        print(
            "  Close error:",
            round(
                close_error,
                2
            )
        )

        print(
            "  Range error:",
            round(
                range_error,
                2
            )
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 80)
    print("CAS NIFTY V2 BACKTEST")
    print("=" * 80)

    v2, nifty = load_data()

    result = add_actual_data(
        v2,
        nifty
    )

    result = calculate_errors(
        result
    )

    result = calculate_bias(
        result
    )

    result = calculate_range_hit(
        result
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Detailed table
    # --------------------------------------------------------

    columns = [

        "Date",

        "Current_Close",

        "Current_Range",
        "Volatility_Regime",

        "Predicted_Next_High",
        "Actual_Next_High",
        "High_Abs_Error",

        "Predicted_Next_Low",
        "Actual_Next_Low",
        "Low_Abs_Error",

        "Predicted_Next_Close",
        "Actual_Next_Close",
        "Close_Abs_Error",

        "Expected_Range",
        "Actual_Next_Range",
        "Range_Abs_Error",

        "Bias",
        "Actual_Bias",
        "Bias_Correct",

        "Close_Inside_Range",
    ]

    columns = [
        c
        for c in columns
        if c in result.columns
    ]

    print()

    print(
        result[
            columns
        ].to_string(
            index=False
        )
    )

    summary(
        result
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