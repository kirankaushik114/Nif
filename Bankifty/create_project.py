from pathlib import Path

# ============================================================
# BANK NIFTY RSI MONITOR
# Project root
# ============================================================

PROJECT_ROOT = Path(r"D:\Nif\Bankifty")


# ============================================================
# Folder structure
# ============================================================

FOLDERS = [
    "config",
    "data",
    "indicators",
    "signals",
    "alerts",
    "tests",
    "logs",
]


# ============================================================
# Files
# ============================================================

FILES = [
    "main.py",
    "requirements.txt",
    ".env",
    ".gitignore",

    "config/__init__.py",
    "config/settings.py",

    "data/__init__.py",
    "data/market_data.py",

    "indicators/__init__.py",
    "indicators/rsi.py",

    "signals/__init__.py",
    "signals/rsi_signals.py",

    "alerts/__init__.py",
    "alerts/console_alert.py",

    "tests/__init__.py",
    "tests/test_data_until_4pm.py",
]


# ============================================================
# Initial file contents
# ============================================================

FILE_CONTENTS = {

    "requirements.txt": """growwapi
pandas
numpy
python-dotenv
pytest
""",

    ".gitignore": """# Virtual environment
.venv/
venv/

# Environment variables
.env

# Python cache
__pycache__/
*.py[cod]

# PyCharm
.idea/

# Logs
logs/*.log

# Test cache
.pytest_cache/
""",

    ".env": """# Groww API credentials
GROWW_API_KEY=
GROWW_API_SECRET=
GROWW_ACCESS_TOKEN=
""",

    "config/settings.py": '''"""
Application settings for Bank Nifty RSI Monitor.
"""

from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


# ------------------------------------------------------------
# Groww
# ------------------------------------------------------------

GROWW_API_KEY = os.getenv("GROWW_API_KEY", "")
GROWW_API_SECRET = os.getenv("GROWW_API_SECRET", "")
GROWW_ACCESS_TOKEN = os.getenv("GROWW_ACCESS_TOKEN", "")


# ------------------------------------------------------------
# Market
# ------------------------------------------------------------

INDEX_NAME = "BANKNIFTY"

RSI_PERIOD = 14

ONE_MINUTE_INTERVAL = 1
FIFTEEN_MINUTE_INTERVAL = 15


# ------------------------------------------------------------
# RSI thresholds
# ------------------------------------------------------------

RSI_15_EXTREME_OVERSOLD = 20
RSI_15_EXTREME_OVERBOUGHT = 80

RSI_15_BULLISH = 40
RSI_1_BULLISH = 30

RSI_15_BEARISH = 60
RSI_1_BEARISH = 70


# ------------------------------------------------------------
# Monitoring
# ------------------------------------------------------------

CHECK_INTERVAL_SECONDS = 60
''',

    "indicators/rsi.py": '''"""
RSI calculation module.
"""

import pandas as pd


def calculate_rsi(
    prices: pd.Series,
    period: int = 14,
) -> float:
    """
    Calculate RSI using Wilder's smoothing method.

    Returns the latest RSI value.
    """

    if len(prices) < period + 1:
        raise ValueError(
            f"Not enough price data. "
            f"Need at least {period + 1} prices."
        )

    delta = prices.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False,
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False,
    ).mean()

    if avg_loss.iloc[-1] == 0:
        return 100.0

    rs = avg_gain.iloc[-1] / avg_loss.iloc[-1]

    rsi = 100 - (100 / (1 + rs))

    return float(rsi)
''',

    "signals/rsi_signals.py": '''"""
Bank Nifty RSI signal engine.
"""

from config.settings import (
    RSI_15_EXTREME_OVERSOLD,
    RSI_15_EXTREME_OVERBOUGHT,
    RSI_15_BULLISH,
    RSI_1_BULLISH,
    RSI_15_BEARISH,
    RSI_1_BEARISH,
)


def check_signals(
    rsi_1m: float,
    rsi_15m: float,
) -> list[dict]:
    """
    Check all configured RSI conditions.

    Returns a list of active signals.
    """

    signals = []

    # --------------------------------------------------------
    # Priority 1: 15-minute extreme conditions
    # --------------------------------------------------------

    if rsi_15m < RSI_15_EXTREME_OVERSOLD:
        signals.append({
            "type": "EXTREME_OVERSOLD",
            "level": "HIGH",
            "message": "15M RSI < 20",
        })

    if rsi_15m > RSI_15_EXTREME_OVERBOUGHT:
        signals.append({
            "type": "EXTREME_OVERBOUGHT",
            "level": "HIGH",
            "message": "15M RSI > 80",
        })

    # --------------------------------------------------------
    # Priority 2: Multi-timeframe setups
    # --------------------------------------------------------

    if (
        rsi_15m <= RSI_15_BULLISH
        and rsi_1m <= RSI_1_BULLISH
    ):
        signals.append({
            "type": "BULLISH_SETUP",
            "level": "MEDIUM",
            "message": "15M RSI <= 40 AND 1M RSI <= 30",
        })

    if (
        rsi_15m >= RSI_15_BEARISH
        and rsi_1m >= RSI_1_BEARISH
    ):
        signals.append({
            "type": "BEARISH_SETUP",
            "level": "MEDIUM",
            "message": "15M RSI >= 60 AND 1M RSI >= 70",
        })

    # --------------------------------------------------------
    # Priority 3: 1-minute conditions
    # --------------------------------------------------------

    if rsi_1m <= RSI_1_BULLISH:
        signals.append({
            "type": "1M_OVERSOLD",
            "level": "LOW",
            "message": "1M RSI <= 30",
        })

    if rsi_1m >= RSI_1_BEARISH:
        signals.append({
            "type": "1M_OVERBOUGHT",
            "level": "LOW",
            "message": "1M RSI >= 70",
        })

    return signals
''',

    "alerts/console_alert.py": '''"""
Console alert system.
"""

from datetime import datetime


def show_market_status(
    bank_nifty: float,
    rsi_1m: float,
    rsi_15m: float,
    signals: list[dict],
) -> None:

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print("=" * 65)
    print("BANK NIFTY RSI MONITOR")
    print("=" * 65)

    print(f"Time       : {now}")
    print(f"Bank Nifty : {bank_nifty:.2f}")
    print(f"1M RSI     : {rsi_1m:.2f}")
    print(f"15M RSI    : {rsi_15m:.2f}")

    print("-" * 65)

    if not signals:
        print("STATUS     : WAIT")
    else:
        print("SIGNALS:")

        for signal in signals:
            print(
                f"  [{signal['level']}] "
                f"{signal['type']} "
                f"-> {signal['message']}"
            )

    print("=" * 65)
''',

    "data/market_data.py": '''"""
Groww market-data module.

Groww connection will be implemented here.
This version intentionally contains no order functionality.
"""


class GrowwMarketData:

    def __init__(self):
        self.connected = False

    def connect(self):
        """
        Connect to Groww API.

        TODO:
        Implement Groww authentication/feed connection.
        """
        raise NotImplementedError(
            "Groww connection will be implemented next."
        )

    def get_bank_nifty_1m(self):
        """
        Return Bank Nifty 1-minute candle data.
        """
        raise NotImplementedError

    def get_bank_nifty_15m(self):
        """
        Return Bank Nifty 15-minute candle data.
        """
        raise NotImplementedError
''',

    "tests/test_data_until_4pm.py": '''"""
Tests for RSI calculations and signal conditions.
"""

import pandas as pd

from indicators.rsi import calculate_rsi
from signals.rsi_signals import check_signals


def test_rsi_returns_value():
    prices = pd.Series(
        [
            100, 101, 102, 101, 103,
            104, 105, 103, 106, 107,
            108, 107, 109, 110, 111,
            112, 113, 114, 115, 116,
        ]
    )

    rsi = calculate_rsi(prices, period=14)

    assert 0 <= rsi <= 100


def test_extreme_oversold():
    signals = check_signals(
        rsi_1m=50,
        rsi_15m=19,
    )

    assert any(
        signal["type"] == "EXTREME_OVERSOLD"
        for signal in signals
    )


def test_extreme_overbought():
    signals = check_signals(
        rsi_1m=50,
        rsi_15m=81,
    )

    assert any(
        signal["type"] == "EXTREME_OVERBOUGHT"
        for signal in signals
    )


def test_bullish_setup():
    signals = check_signals(
        rsi_1m=28,
        rsi_15m=38,
    )

    assert any(
        signal["type"] == "BULLISH_SETUP"
        for signal in signals
    )


def test_bearish_setup():
    signals = check_signals(
        rsi_1m=72,
        rsi_15m=62,
    )

    assert any(
        signal["type"] == "BEARISH_SETUP"
        for signal in signals
    )
''',

    "main.py": '''"""
Bank Nifty RSI Monitor.

Alert-only version.
NO ORDER PLACEMENT.
"""

from indicators.rsi import calculate_rsi
from signals.rsi_signals import check_signals
from alerts.console_alert import show_market_status


def main():
    print("=" * 65)
    print("BANK NIFTY RSI MONITOR")
    print("=" * 65)
    print()
    print("Mode       : ALERT ONLY")
    print("Orders     : DISABLED")
    print()
    print("Groww market-data connection will be added next.")
    print()

    # --------------------------------------------------------
    # Temporary test values
    # --------------------------------------------------------
    #
    # These are ONLY for testing the signal engine.
    # They are NOT live Bank Nifty values.
    #

    bank_nifty = 56000.00

    rsi_1m = 28.0
    rsi_15m = 38.0

    signals = check_signals(
        rsi_1m=rsi_1m,
        rsi_15m=rsi_15m,
    )

    show_market_status(
        bank_nifty=bank_nifty,
        rsi_1m=rsi_1m,
        rsi_15m=rsi_15m,
        signals=signals,
    )


if __name__ == "__main__":
    main()
''',
}


# ============================================================
# Create project
# ============================================================

def create_project():

    print()
    print("=" * 70)
    print("Creating Bank Nifty RSI Monitor")
    print("=" * 70)
    print(f"Location: {PROJECT_ROOT}")
    print()

    # Create root
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)

    # Create folders
    for folder in FOLDERS:
        folder_path = PROJECT_ROOT / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"[DIR ]  {folder_path}")

    # Create files
    for file_name in FILES:

        file_path = PROJECT_ROOT / file_name

        # Make sure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        content = FILE_CONTENTS.get(file_name, "")

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        print(f"[FILE]  {file_path}")

    print()
    print("=" * 70)
    print("PROJECT CREATED SUCCESSFULLY")
    print("=" * 70)
    print()
    print(f"Open this folder in PyCharm:")
    print(PROJECT_ROOT)
    print()


if __name__ == "__main__":
    create_project()