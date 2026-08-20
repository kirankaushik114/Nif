"""
Bank Nifty RSI Monitor
Application Settings
"""

from pathlib import Path
import os

from dotenv import load_dotenv


# ============================================================
# PROJECT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# GROWW API
# ============================================================

GROWW_API_KEY = os.getenv(
    "GROWW_API_KEY",
    ""
)

GROWW_API_SECRET = os.getenv(
    "GROWW_API_SECRET",
    ""
)


# ============================================================
# MARKET
# ============================================================

INDEX_NAME = "BANKNIFTY"

TIME_ZONE = "Asia/Kolkata"

PRE_MARKET_TIME = "09:00"

MARKET_OPEN_TIME = "09:15"

MARKET_CLOSE_TIME = "15:30"

MONITOR_CLOSE_TIME = "16:30"


# ============================================================
# HISTORICAL DATA DATE SETTINGS
# ============================================================

DATA_SELECTION_TIME = "09:00"

HISTORICAL_START_TIME = "09:15"

HISTORICAL_END_TIME = "16:30"

HISTORICAL_LOOKBACK_DAYS = 10


# ============================================================
# RSI SETTINGS
# ============================================================

RSI_PERIOD = 14


# ============================================================
# 15-MINUTE RSI CONDITIONS
# ============================================================

# Individual 15M conditions
#
# 15M < 30  -> CE
# 15M > 70  -> PE

RSI_15_EXTREME_OVERSOLD = 30

RSI_15_EXTREME_OVERBOUGHT = 70


# Combined conditions
#
# 1M < 20 AND 15M < 25 -> CE
#
# 1M > 80 AND 15M > 75 -> PE

RSI_15_BULLISH = 25

RSI_15_BEARISH = 75


# ============================================================
# 1-MINUTE RSI CONDITIONS
# ============================================================

# Individual conditions
#
# 1M <= 30 -> CE
# 1M >= 70 -> PE

RSI_1_BULLISH = 30

RSI_1_BEARISH = 70


# ============================================================
# COMBINED 1-MINUTE RSI CONDITIONS
# ============================================================

# IMPORTANT:
#
# These are intentionally different from the individual
# 1-minute conditions.
#
# Condition 5:
#
# 1M < 20 AND 15M < 25 -> CE
#
# Condition 6:
#
# 1M > 80 AND 15M > 75 -> PE

RSI_1_COMBINED_BULLISH = 20

RSI_1_COMBINED_BEARISH = 80


# ============================================================
# PAPER TRADING TIME WINDOW
# ============================================================

# NEW PAPER BUYs are allowed only between:
#
# 10:00 AM and 3:00 PM IST.
#
# Existing OPEN paper trades are not affected by this
# entry window. Their normal SELL/target monitoring can
# continue.

PAPER_TRADING_START_TIME = "10:00"

PAPER_TRADING_END_TIME = "15:00"


# ============================================================
# MONITORING
# ============================================================

CHECK_INTERVAL_SECONDS = 3


# ============================================================
# EMAIL SETTINGS
# ============================================================

# Master email switch.
#
# True  = emails enabled
# False = no emails

EMAIL_ENABLED = True


EMAIL_SMTP_SERVER = os.getenv(
    "EMAIL_SMTP_SERVER",
    "smtp.gmail.com"
)

EMAIL_SMTP_PORT = int(
    os.getenv(
        "EMAIL_SMTP_PORT",
        "587"
    )
)

EMAIL_SENDER = os.getenv(
    "EMAIL_SENDER",
    ""
)

EMAIL_PASSWORD = os.getenv(
    "EMAIL_PASSWORD",
    ""
)

EMAIL_RECIPIENT_1 = os.getenv(
    "EMAIL_RECIPIENT_1",
    ""
)

EMAIL_RECIPIENT_2 = os.getenv(
    "EMAIL_RECIPIENT_2",
    ""
)


# ============================================================
# EMAIL NOTIFICATION CONTROL
# ============================================================

# IMPORTANT:
#
# Normal RSI condition emails are DISABLED.
#
# Example:
#
# BULLISH
# BEARISH
# PARTIAL BULLISH
# PARTIAL BEARISH
#
# will NOT generate an email.

EMAIL_ON_CONDITION = False


# No-condition emails are also disabled.

EMAIL_ON_NO_CONDITION = False


# Kept for compatibility with existing monitor code.

NO_CONDITION_EMAIL_INTERVAL_MINUTES = 5


# No outside-market emails.

EMAIL_OUTSIDE_MARKET = False


# No market-close emails.

EMAIL_ON_MARKET_CLOSE = False


# Protect against duplicate paper-trade emails.

EMAIL_DUPLICATE_PROTECTION = True


# Send to all configured recipients.

EMAIL_TO_ALL_RECIPIENTS = True


# ============================================================
# PAPER TRADE EMAIL
# ============================================================

# ONLY send an email after a virtual BUY
# has actually been created successfully.

EMAIL_ON_PAPER_PURCHASE = True


# ONLY send an email after a virtual SELL
# has actually been completed successfully.

EMAIL_ON_PAPER_SELL = True


# ============================================================
# PAPER TRADING
# ============================================================

# Real market data + virtual trading.

PAPER_TRADING_ENABLED = True


# ============================================================
# REAL ORDER SAFETY
# ============================================================

# MUST remain False.
#
# No real order will ever be sent.

REAL_ORDERS_ENABLED = False


# ============================================================
# PAPER TRADING TARGETS
# ============================================================

# ------------------------------------------------------------
# 1-MINUTE
# ------------------------------------------------------------
#
# 1M <= 30
#     CE
#     Entry + 15
#
# 1M >= 70
#     PE
#     Entry + 15

PAPER_1M_TARGET_POINTS = 15


# ------------------------------------------------------------
# 15-MINUTE
# ------------------------------------------------------------
#
# 15M < 30
#     CE
#     Entry + 45
#
# 15M > 70
#     PE
#     Entry + 45

PAPER_15M_TARGET_POINTS = 45


# ------------------------------------------------------------
# 1M + 15M
# ------------------------------------------------------------
#
# 1M < 20 AND 15M < 25
#     CE
#     Entry + 75
#
# 1M > 80 AND 15M > 75
#     PE
#     Entry + 75

PAPER_COMBINED_TARGET_POINTS = 75


# ============================================================
# PAPER OPTION SETTINGS
# ============================================================

# Bank Nifty strike interval.

PAPER_STRIKE_STEP = 100


# Number of virtual lots.

PAPER_LOTS = 1


# ============================================================
# PAPER DATABASE
# ============================================================

PAPER_DATABASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "paper_trading.db"
)


# ============================================================
# TRADING SAFETY
# ============================================================

# Monitor remains alert-only.

ALERT_ONLY = True


# Real orders remain disabled.

ORDERS_ENABLED = False


# ============================================================
# VALIDATE SETTINGS
# ============================================================

def validate_settings():

    # --------------------------------------------------------
    # GROWW API
    # --------------------------------------------------------

    if not GROWW_API_KEY:

        raise ValueError(
            "GROWW_API_KEY is missing in .env"
        )

    if not GROWW_API_SECRET:

        raise ValueError(
            "GROWW_API_SECRET is missing in .env"
        )

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    if not ALERT_ONLY:

        raise ValueError(
            "ALERT_ONLY must remain True."
        )

    if ORDERS_ENABLED:

        raise ValueError(
            "ORDERS_ENABLED must remain False."
        )

    if (
        PAPER_TRADING_ENABLED
        and
        REAL_ORDERS_ENABLED
    ):

        raise ValueError(
            "REAL_ORDERS_ENABLED must remain False "
            "while PAPER_TRADING_ENABLED is True."
        )

    # --------------------------------------------------------
    # MONITORING
    # --------------------------------------------------------

    if CHECK_INTERVAL_SECONDS <= 0:

        raise ValueError(
            "CHECK_INTERVAL_SECONDS must be "
            "greater than 0."
        )

    # --------------------------------------------------------
    # EMAIL INTERVAL
    # --------------------------------------------------------

    if NO_CONDITION_EMAIL_INTERVAL_MINUTES <= 0:

        raise ValueError(
            "NO_CONDITION_EMAIL_INTERVAL_MINUTES "
            "must be greater than 0."
        )

    # --------------------------------------------------------
    # HISTORICAL DATA
    # --------------------------------------------------------

    if HISTORICAL_LOOKBACK_DAYS <= 0:

        raise ValueError(
            "HISTORICAL_LOOKBACK_DAYS "
            "must be greater than 0."
        )

    # --------------------------------------------------------
    # PAPER TARGETS
    # --------------------------------------------------------

    if PAPER_1M_TARGET_POINTS <= 0:

        raise ValueError(
            "PAPER_1M_TARGET_POINTS "
            "must be greater than 0."
        )

    if PAPER_15M_TARGET_POINTS <= 0:

        raise ValueError(
            "PAPER_15M_TARGET_POINTS "
            "must be greater than 0."
        )

    if PAPER_COMBINED_TARGET_POINTS <= 0:

        raise ValueError(
            "PAPER_COMBINED_TARGET_POINTS "
            "must be greater than 0."
        )

    # --------------------------------------------------------
    # OPTION SETTINGS
    # --------------------------------------------------------

    if PAPER_STRIKE_STEP <= 0:

        raise ValueError(
            "PAPER_STRIKE_STEP "
            "must be greater than 0."
        )

    if PAPER_LOTS <= 0:

        raise ValueError(
            "PAPER_LOTS must be greater than 0."
        )

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    if EMAIL_ENABLED:

        if not EMAIL_SENDER:

            raise ValueError(
                "EMAIL_SENDER is missing in .env"
            )

        if not EMAIL_PASSWORD:

            raise ValueError(
                "EMAIL_PASSWORD is missing in .env"
            )

        if (
            not EMAIL_RECIPIENT_1
            and
            not EMAIL_RECIPIENT_2
        ):

            raise ValueError(
                "At least one email recipient "
                "is required."
            )

    return True


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)

    print(
        "BANK NIFTY RSI MONITOR - SETTINGS"
    )

    print("=" * 65)

    try:

        validate_settings()

        print(
            "Groww API Key    : Loaded"
        )

        print(
            "Groww API Secret : Loaded"
        )

        print()
        print("Market:")

        print(
            "  Index             :",
            INDEX_NAME
        )

        print(
            "  Time Zone         :",
            TIME_ZONE
        )

        print(
            "  Monitor Start     :",
            PRE_MARKET_TIME
        )

        print(
            "  Market Open       :",
            MARKET_OPEN_TIME
        )

        print(
            "  Market Close      :",
            MARKET_CLOSE_TIME
        )

        print(
            "  Monitor Close     :",
            MONITOR_CLOSE_TIME
        )

        print()
        print("Historical Data:")

        print(
            "  Date Selection    :",
            DATA_SELECTION_TIME
        )

        print(
            "  Start Time        :",
            HISTORICAL_START_TIME
        )

        print(
            "  End Time          :",
            HISTORICAL_END_TIME
        )

        print(
            "  Lookback Days     :",
            HISTORICAL_LOOKBACK_DAYS
        )

        print()
        print("RSI:")

        print(
            "  Period            :",
            RSI_PERIOD
        )

        print()
        print("15-Minute:")

        print(
            "  Oversold          :",
            f"< {RSI_15_EXTREME_OVERSOLD}"
        )

        print(
            "  Overbought        :",
            f"> {RSI_15_EXTREME_OVERBOUGHT}"
        )

        print(
            "  Combined Bullish  :",
            f"< {RSI_15_BULLISH}"
        )

        print(
            "  Combined Bearish  :",
            f"> {RSI_15_BEARISH}"
        )

        print()
        print("1-Minute:")

        print(
            "  Bullish           :",
            f"<= {RSI_1_BULLISH}"
        )

        print(
            "  Bearish           :",
            f">= {RSI_1_BEARISH}"
        )

        print()
        print("Combined 1-Minute:")

        print(
            "  Bullish           :",
            f"< {RSI_1_COMBINED_BULLISH}"
        )

        print(
            "  Bearish           :",
            f"> {RSI_1_COMBINED_BEARISH}"
        )

        print()
        print("Paper Trading Window:")

        print(
            "  Start             :",
            PAPER_TRADING_START_TIME
        )

        print(
            "  End               :",
            PAPER_TRADING_END_TIME
        )

        print()
        print("Monitoring:")

        print(
            "  Check interval    :",
            f"{CHECK_INTERVAL_SECONDS} seconds"
        )

        print()
        print("Email:")

        print(
            "  Email Enabled     :",
            EMAIL_ENABLED
        )

        print(
            "  RSI Condition     :",
            EMAIL_ON_CONDITION
        )

        print(
            "  No Condition      :",
            EMAIL_ON_NO_CONDITION
        )

        print(
            "  Outside Market    :",
            EMAIL_OUTSIDE_MARKET
        )

        print(
            "  Market Close      :",
            EMAIL_ON_MARKET_CLOSE
        )

        print(
            "  Duplicate Protect :",
            EMAIL_DUPLICATE_PROTECTION
        )

        print(
            "  All Recipients    :",
            EMAIL_TO_ALL_RECIPIENTS
        )

        print()
        print("Paper Trade Email:")

        print(
            "  Purchase Email    :",
            EMAIL_ON_PAPER_PURCHASE
        )

        print(
            "  Sell Email        :",
            EMAIL_ON_PAPER_SELL
        )

        print()
        print("Paper Trading:")

        print(
            "  Paper Trading     :",
            PAPER_TRADING_ENABLED
        )

        print(
            "  Real Orders       :",
            REAL_ORDERS_ENABLED
        )

        print(
            "  1M Target         :",
            f"+{PAPER_1M_TARGET_POINTS}"
        )

        print(
            "  15M Target        :",
            f"+{PAPER_15M_TARGET_POINTS}"
        )

        print(
            "  Combined Target   :",
            f"+{PAPER_COMBINED_TARGET_POINTS}"
        )

        print(
            "  Strike Step       :",
            PAPER_STRIKE_STEP
        )

        print(
            "  Paper Lots        :",
            PAPER_LOTS
        )

        print(
            "  Database          :",
            PAPER_DATABASE_FILE
        )

        print()
        print("Safety:")

        print(
            "  Alert Only        :",
            ALERT_ONLY
        )

        print(
            "  Orders Enabled    :",
            ORDERS_ENABLED
        )

        print()
        print("=" * 65)

        print(
            "SETTINGS OK"
        )

        print("=" * 65)

    except ValueError as error:

        print()
        print("=" * 65)

        print(
            "SETTINGS ERROR"
        )

        print("=" * 65)

        print(error)

        print("=" * 65)