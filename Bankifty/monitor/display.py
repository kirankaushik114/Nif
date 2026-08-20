from datetime import datetime

from config.settings import (
    RSI_1_BULLISH,
    RSI_1_BEARISH,
    RSI_15_EXTREME_OVERSOLD,
    RSI_15_EXTREME_OVERBOUGHT,
    RSI_15_BULLISH,
    RSI_15_BEARISH,
)


GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def green(text):

    return (
        f"{GREEN}{text}{RESET}"
    )


def red(text):

    return (
        f"{RED}{text}{RESET}"
    )


# ============================================================
# STATUS
# ============================================================

def get_status(
    rsi_1m,
    rsi_15m,
):

    bullish_1m = (
        rsi_1m <= RSI_1_BULLISH
    )

    bullish_15m = (
        rsi_15m <= RSI_15_BULLISH
    )

    bearish_1m = (
        rsi_1m >= RSI_1_BEARISH
    )

    bearish_15m = (
        rsi_15m >= RSI_15_BEARISH
    )

    bullish_count = (
        int(bullish_1m)
        +
        int(bullish_15m)
    )

    bearish_count = (
        int(bearish_1m)
        +
        int(bearish_15m)
    )

    if bullish_count == 2:

        return (
            "BULLISH",
            "GREEN"
        )

    if bullish_count == 1:

        return (
            "PARTIAL BULLISH",
            "GREEN"
        )

    if bearish_count == 2:

        return (
            "BEARISH",
            "RED"
        )

    if bearish_count == 1:

        return (
            "PARTIAL BEARISH",
            "RED"
        )

    return (
        "BANK NIFTY RSI",
        "NORMAL"
    )


# ============================================================
# DISPLAY
# ============================================================

def show(
    rsi_1m,
    rsi_15m,
    bank_nifty,
    candle_time,
    market_status,
):

    status, status_color = get_status(
        rsi_1m,
        rsi_15m,
    )

    now_text = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    heading_text = (
        "              BANK NIFTY RSI - "
        f"{status} - "
        f"{market_status} - "
        f"{now_text}"
    )

    if status_color == "GREEN":

        heading = green(
            heading_text
        )

    elif status_color == "RED":

        heading = red(
            heading_text
        )

    else:

        heading = heading_text

    print()
    print("=" * 90)

    print(
        heading
    )

    print("=" * 90)

    print()

    # ========================================================
    # 1 MINUTE
    # ========================================================

    print(
        "============================= 1 MIN ==============================="
    )

    condition_1 = (
        rsi_1m <= RSI_1_BULLISH
    )

    condition_2 = (
        rsi_1m >= RSI_1_BEARISH
    )

    text = (
        f"1) 1M <= {RSI_1_BULLISH} → MET"
        if condition_1
        else
        f"1) 1M <= {RSI_1_BULLISH} → NOT MET"
    )

    print(
        green(text)
        if condition_1
        else text
    )

    text = (
        f"2) 1M >= {RSI_1_BEARISH} → MET"
        if condition_2
        else
        f"2) 1M >= {RSI_1_BEARISH} → NOT MET"
    )

    print(
        red(text)
        if condition_2
        else text
    )

    print()

    # ========================================================
    # 15 MINUTE
    # ========================================================

    print(
        "============================ 15 MIN ==============================="
    )

    condition_3 = (
        rsi_15m
        <
        RSI_15_EXTREME_OVERSOLD
    )

    condition_4 = (
        rsi_15m
        >
        RSI_15_EXTREME_OVERBOUGHT
    )

    text = (
        f"3) 15M < {RSI_15_EXTREME_OVERSOLD} → MET"
        if condition_3
        else
        f"3) 15M < {RSI_15_EXTREME_OVERSOLD} → NOT MET"
    )

    print(
        green(text)
        if condition_3
        else text
    )

    text = (
        f"4) 15M > {RSI_15_EXTREME_OVERBOUGHT} → MET"
        if condition_4
        else
        f"4) 15M > {RSI_15_EXTREME_OVERBOUGHT} → NOT MET"
    )

    print(
        red(text)
        if condition_4
        else text
    )

    print()

    # ========================================================
    # 1 MIN + 15 MIN
    # ========================================================

    print(
        "======================== 1 MIN + 15 MIN ==========================="
    )

    bullish_1m = (
        rsi_1m <= RSI_1_BULLISH
    )

    bullish_15m = (
        rsi_15m <= RSI_15_BULLISH
    )

    print(
        "5) BULLISH"
    )

    text_1 = (
        f"1M <= {RSI_1_BULLISH} → MET"
        if bullish_1m
        else
        f"1M <= {RSI_1_BULLISH} → NOT MET"
    )

    text_2 = (
        f"15M <= {RSI_15_BULLISH} → MET"
        if bullish_15m
        else
        f"15M <= {RSI_15_BULLISH} → NOT MET"
    )

    if bullish_1m:

        text_1 = green(
            text_1
        )

    if bullish_15m:

        text_2 = green(
            text_2
        )

    print(
        "   "
        +
        text_1
        +
        " | "
        +
        text_2
    )

    # ========================================================
    # BEARISH
    # ========================================================

    bearish_1m = (
        rsi_1m >= RSI_1_BEARISH
    )

    bearish_15m = (
        rsi_15m >= RSI_15_BEARISH
    )

    print()

    print(
        "6) BEARISH"
    )

    text_1 = (
        f"1M >= {RSI_1_BEARISH} → MET"
        if bearish_1m
        else
        f"1M >= {RSI_1_BEARISH} → NOT MET"
    )

    text_2 = (
        f"15M >= {RSI_15_BEARISH} → MET"
        if bearish_15m
        else
        f"15M >= {RSI_15_BEARISH} → NOT MET"
    )

    if bearish_1m:

        text_1 = red(
            text_1
        )

    if bearish_15m:

        text_2 = red(
            text_2
        )

    print(
        "   "
        +
        text_1
        +
        " | "
        +
        text_2
    )

    print()

    # ========================================================
    # CURRENT VALUE
    # ========================================================

    print(
        "========================== CURRENT VALUE =========================="
    )

    print(
        green(
            f"   1M         : {rsi_1m:.2f}"
        )
    )

    print(
        green(
            f"   15M        : {rsi_15m:.2f}"
        )
    )

    print(
        f"   Bank Nifty : {bank_nifty:,.2f}"
    )

    print(
        green(
            f"   Candle     : {candle_time}"
        )
    )

    print(
        f"   Current    : {now_text}"
    )

    print()

    print(
        "=" * 90
    )