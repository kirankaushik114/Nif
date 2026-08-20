# ============================================================
# BANK NIFTY PAPER TRADING DASHBOARD
# ============================================================

import sys
from pathlib import Path

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

import sqlite3
import time
from datetime import datetime

import streamlit as st

from data.historical_data import GrowwHistoricalData

from indicators.rsi import (
    candle_closes_to_series,
    calculate_latest_rsi,
)

from config.settings import (
    RSI_PERIOD,
    RSI_1_BULLISH,
    RSI_1_BEARISH,
    RSI_15_EXTREME_OVERSOLD,
    RSI_15_EXTREME_OVERBOUGHT,
    RSI_15_BULLISH,
    RSI_15_BEARISH,
    RSI_1_COMBINED_BULLISH,
    RSI_1_COMBINED_BEARISH,
    PAPER_DATABASE_FILE,
    TIME_ZONE,
)

from paper_trading.trade_manager import PaperTradeManager


# ============================================================
# TIMEZONE
# ============================================================

try:
    from zoneinfo import ZoneInfo

    TIMEZONE = ZoneInfo(TIME_ZONE)

except Exception:
    TIMEZONE = None


# ============================================================
# STREAMLIT PAGE
# ============================================================

st.set_page_config(
    page_title="Bank Nifty Paper Trading",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# DATABASE
# ============================================================

DATABASE = PAPER_DATABASE_FILE


# ============================================================
# PAPER TRADE MANAGER
# ============================================================

@st.cache_resource
def get_paper_manager():

    return PaperTradeManager(
        database_file=DATABASE,
        timezone=TIME_ZONE,
    )


# ============================================================
# HISTORICAL DATA
# ============================================================

@st.cache_resource
def get_historical():

    return GrowwHistoricalData()


# ============================================================
# MARKET DATA
# ============================================================

def get_market_data():

    historical = get_historical()

    data_1m = historical.get_1_minute_candles()

    data_15m = historical.get_15_minute_candles()

    candles_1m = data_1m.get(
        "candles",
        []
    )

    candles_15m = data_15m.get(
        "candles",
        []
    )

    if not candles_1m:
        return None

    if not candles_15m:
        return None

    closes_1m = candle_closes_to_series(
        candles_1m
    )

    closes_15m = candle_closes_to_series(
        candles_15m
    )

    rsi_1m = calculate_latest_rsi(
        closes_1m,
        period=RSI_PERIOD,
    )

    rsi_15m = calculate_latest_rsi(
        closes_15m,
        period=RSI_PERIOD,
    )

    bank_nifty = float(
        candles_1m[-1][4]
    )

    candle_time = candles_1m[-1][0]

    return {
        "rsi_1m": rsi_1m,
        "rsi_15m": rsi_15m,
        "bank_nifty": bank_nifty,
        "candle_time": candle_time,
    }


# ============================================================
# SIX RSI CONDITIONS
# ============================================================

def get_conditions(
    rsi_1m,
    rsi_15m,
):

    return [

        {
            "number": 1,

            "condition":
                f"1M <= {RSI_1_BULLISH}",

            "strategy":
                "1M_CE",

            "option":
                "CE",

            "target":
                15,

            "met":
                rsi_1m <= RSI_1_BULLISH,
        },

        {
            "number": 2,

            "condition":
                f"1M >= {RSI_1_BEARISH}",

            "strategy":
                "1M_PE",

            "option":
                "PE",

            "target":
                15,

            "met":
                rsi_1m >= RSI_1_BEARISH,
        },

        {
            "number": 3,

            "condition":
                f"15M < {RSI_15_EXTREME_OVERSOLD}",

            "strategy":
                "15M_CE",

            "option":
                "CE",

            "target":
                45,

            "met":
                rsi_15m < RSI_15_EXTREME_OVERSOLD,
        },

        {
            "number": 4,

            "condition":
                f"15M > {RSI_15_EXTREME_OVERBOUGHT}",

            "strategy":
                "15M_PE",

            "option":
                "PE",

            "target":
                45,

            "met":
                rsi_15m > RSI_15_EXTREME_OVERBOUGHT,
        },

        {
            "number": 5,

            "condition":
                (
                    f"1M < "
                    f"{RSI_1_COMBINED_BULLISH} "
                    f"AND "
                    f"15M < "
                    f"{RSI_15_BULLISH}"
                ),

            "strategy":
                "COMBINED_CE",

            "option":
                "CE",

            "target":
                75,

            "met":
                (
                    rsi_1m < RSI_1_COMBINED_BULLISH
                    and
                    rsi_15m < RSI_15_BULLISH
                ),
        },

        {
            "number": 6,

            "condition":
                (
                    f"1M > "
                    f"{RSI_1_COMBINED_BEARISH} "
                    f"AND "
                    f"15M > "
                    f"{RSI_15_BEARISH}"
                ),

            "strategy":
                "COMBINED_PE",

            "option":
                "PE",

            "target":
                75,

            "met":
                (
                    rsi_1m > RSI_1_COMBINED_BEARISH
                    and
                    rsi_15m > RSI_15_BEARISH
                ),
        },
    ]


# ============================================================
# DATABASE - GET ALL TRADES
# ============================================================

def get_trades():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    rows = connection.execute(
        """
        SELECT
            id,
            strategy,
            signal,
            option_type,
            strike,
            trading_symbol,
            entry_time,
            entry_price,
            target_price,
            target_points,
            exit_time,
            exit_price,
            quantity,
            pnl_points,
            pnl_value,
            status,
            entry_rsi_1m,
            entry_rsi_15m,
            entry_bank_nifty,
            exit_reason
        FROM paper_trades
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# CURRENT OPTION LTP
# ============================================================

def get_option_price(symbol):

    try:

        historical = get_historical()

        value = (
            historical
            .get_option_ltp_by_symbol(
                symbol
            )
        )

        if value is None:
            return None

        return float(value)

    except Exception:
        return None


# ============================================================
# UPDATE LIVE PAPER VALUES
# ============================================================

def update_current_values(trades):

    for trade in trades:

        if trade["status"] == "OPEN":

            current = get_option_price(
                trade["trading_symbol"]
            )

            trade["current_price"] = current

            if current is not None:

                trade["current_pnl_points"] = (
                    current
                    -
                    trade["entry_price"]
                )

                trade["current_pnl_value"] = (
                    trade["current_pnl_points"]
                    *
                    trade["quantity"]
                )

                trade["to_target"] = (
                    trade["target_price"]
                    -
                    current
                )

            else:

                trade["current_pnl_points"] = None

                trade["current_pnl_value"] = None

                trade["to_target"] = None

        else:

            trade["current_price"] = (
                trade["exit_price"]
            )

            trade["current_pnl_points"] = (
                trade["pnl_points"]
            )

            trade["current_pnl_value"] = (
                trade["pnl_value"]
            )

            trade["to_target"] = 0

    return trades


# ============================================================
# P&L CALCULATION
# ============================================================

def calculate_pnl_statistics(
    trades
):

    closed = [
        trade
        for trade in trades
        if trade["status"] == "CLOSED"
    ]

    open_trades = [
        trade
        for trade in trades
        if trade["status"] == "OPEN"
    ]

    # --------------------------------------------------------
    # CLOSED P&L
    # --------------------------------------------------------

    winning = [
        trade
        for trade in closed
        if (
            trade["pnl_points"] is not None
            and
            trade["pnl_points"] > 0
        )
    ]

    losing = [
        trade
        for trade in closed
        if (
            trade["pnl_points"] is not None
            and
            trade["pnl_points"] < 0
        )
    ]

    breakeven = [
        trade
        for trade in closed
        if (
            trade["pnl_points"] is not None
            and
            trade["pnl_points"] == 0
        )
    ]

    gross_profit = sum(
        (
            trade["pnl_value"] or 0
        )
        for trade in winning
    )

    gross_loss = sum(
        (
            trade["pnl_value"] or 0
        )
        for trade in losing
    )

    closed_pnl = sum(
        (
            trade["pnl_value"] or 0
        )
        for trade in closed
    )

    # --------------------------------------------------------
    # OPEN P&L
    # --------------------------------------------------------

    open_pnl = sum(
        (
            trade["current_pnl_value"] or 0
        )
        for trade in open_trades
    )

    total_pnl = (
        closed_pnl
        +
        open_pnl
    )

    # --------------------------------------------------------
    # WIN RATE
    # --------------------------------------------------------

    if closed:

        win_rate = (
            len(winning)
            /
            len(closed)
            *
            100
        )

    else:

        win_rate = 0.0

    # --------------------------------------------------------
    # AVERAGES
    # --------------------------------------------------------

    if winning:

        average_profit = (
            gross_profit
            /
            len(winning)
        )

    else:

        average_profit = 0.0

    if losing:

        average_loss = (
            gross_loss
            /
            len(losing)
        )

    else:

        average_loss = 0.0

    # --------------------------------------------------------
    # LARGEST WIN / LOSS
    # --------------------------------------------------------

    if winning:

        largest_profit = max(
            trade["pnl_value"]
            for trade in winning
        )

    else:

        largest_profit = 0.0

    if losing:

        largest_loss = min(
            trade["pnl_value"]
            for trade in losing
        )

    else:

        largest_loss = 0.0

    # --------------------------------------------------------
    # PROFIT FACTOR
    #
    # Gross Profit / Absolute Gross Loss
    # --------------------------------------------------------

    if gross_loss < 0:

        profit_factor = (
            gross_profit
            /
            abs(gross_loss)
        )

    else:

        profit_factor = (
            float("inf")
            if gross_profit > 0
            else 0.0
        )

    return {

        "total_trades":
            len(trades),

        "closed_trades":
            len(closed),

        "open_trades":
            len(open_trades),

        "winning":
            len(winning),

        "losing":
            len(losing),

        "breakeven":
            len(breakeven),

        "gross_profit":
            gross_profit,

        "gross_loss":
            gross_loss,

        "closed_pnl":
            closed_pnl,

        "open_pnl":
            open_pnl,

        "total_pnl":
            total_pnl,

        "win_rate":
            win_rate,

        "average_profit":
            average_profit,

        "average_loss":
            average_loss,

        "largest_profit":
            largest_profit,

        "largest_loss":
            largest_loss,

        "profit_factor":
            profit_factor,
    }


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 Bank Nifty Paper Trading Dashboard"
)

st.caption(
    "PAPER TRADING ONLY • NO REAL ORDERS"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "Dashboard Settings"
)

refresh_seconds = st.sidebar.number_input(
    "Refresh interval",
    min_value=3,
    max_value=60,
    value=3,
    step=1,
)


if st.sidebar.button(
    "Refresh Now"
):

    st.rerun()


# ============================================================
# MARKET DATA
# ============================================================

try:

    market = get_market_data()

except Exception as error:

    st.error(
        f"Market data error: {error}"
    )

    st.stop()


if market is None:

    st.warning(
        "Market data unavailable."
    )

    st.stop()


rsi_1m = market["rsi_1m"]

rsi_15m = market["rsi_15m"]

bank_nifty = market["bank_nifty"]

candle_time = market["candle_time"]


# ============================================================
# MARKET DISPLAY
# ============================================================

st.subheader(
    "Market"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Bank Nifty",
    f"{bank_nifty:,.2f}",
)

col2.metric(
    "1M RSI",
    f"{rsi_1m:.2f}",
)

col3.metric(
    "15M RSI",
    f"{rsi_15m:.2f}",
)

current_time = (
    datetime.now(TIMEZONE)
    if TIMEZONE
    else
    datetime.now()
)

col4.metric(
    "Current Time",
    current_time.strftime("%H:%M:%S"),
)

st.caption(
    f"Latest candle: {candle_time}"
)


# ============================================================
# SIX CONDITIONS
# ============================================================

st.subheader(
    "Six RSI Trading Conditions"
)

conditions = get_conditions(
    rsi_1m,
    rsi_15m,
)

condition_table = []

for condition in conditions:

    condition_table.append({

        "Condition":
            condition["number"],

        "Rule":
            condition["condition"],

        "Strategy":
            condition["strategy"],

        "Option":
            condition["option"],

        "Target":
            f"+{condition['target']}",

        "Status":
            (
                "🟢 MET"
                if condition["met"]
                else
                "⚪ NOT MET"
            ),
    })


st.dataframe(
    condition_table,
    width="stretch",
    hide_index=True,
)


# ============================================================
# PAPER TRADES
# ============================================================

trades = get_trades()

trades = update_current_values(
    trades
)

open_trades = [
    trade
    for trade in trades
    if trade["status"] == "OPEN"
]

closed_trades = [
    trade
    for trade in trades
    if trade["status"] == "CLOSED"
]


# ============================================================
# P&L STATISTICS
# ============================================================

pnl = calculate_pnl_statistics(
    trades
)


# ============================================================
# PROFIT & LOSS STATEMENT
# ============================================================

st.subheader(
    "💰 Profit & Loss Statement"
)

st.caption(
    "Closed P&L uses actual SELL prices. "
    "Open P&L uses the latest live option price."
)


# ============================================================
# TOP P&L METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Closed P&L",
    f"{pnl['closed_pnl']:+,.2f}",
)

col2.metric(
    "Open P&L",
    f"{pnl['open_pnl']:+,.2f}",
)

col3.metric(
    "Total P&L",
    f"{pnl['total_pnl']:+,.2f}",
)

col4.metric(
    "Win Rate",
    f"{pnl['win_rate']:.2f}%",
)


# ============================================================
# TRADE STATISTICS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Trades",
    pnl["total_trades"],
)

col2.metric(
    "Winning",
    pnl["winning"],
)

col3.metric(
    "Losing",
    pnl["losing"],
)

col4.metric(
    "Breakeven",
    pnl["breakeven"],
)

col5.metric(
    "Open",
    pnl["open_trades"],
)


# ============================================================
# PROFIT / LOSS DETAILS
# ============================================================

st.markdown(
    "### P&L Details"
)

pnl_details = [

    {
        "Metric":
            "Gross Profit",

        "Value":
            pnl["gross_profit"],
    },

    {
        "Metric":
            "Gross Loss",

        "Value":
            pnl["gross_loss"],
    },

    {
        "Metric":
            "Net Closed P&L",

        "Value":
            pnl["closed_pnl"],
    },

    {
        "Metric":
            "Open P&L",

        "Value":
            pnl["open_pnl"],
    },

    {
        "Metric":
            "Total P&L",

        "Value":
            pnl["total_pnl"],
    },

    {
        "Metric":
            "Average Profit / Winning Trade",

        "Value":
            pnl["average_profit"],
    },

    {
        "Metric":
            "Average Loss / Losing Trade",

        "Value":
            pnl["average_loss"],
    },

    {
        "Metric":
            "Largest Profit",

        "Value":
            pnl["largest_profit"],
    },

    {
        "Metric":
            "Largest Loss",

        "Value":
            pnl["largest_loss"],
    },

]


pnl_display = [

    {
        "Metric":
            row["Metric"],

        "P&L":
            f"{row['Value']:+,.2f}",
    }

    for row in pnl_details
]


st.dataframe(
    pnl_display,
    width="stretch",
    hide_index=True,
)


# ============================================================
# PERFORMANCE RATIO
# ============================================================

col1, col2, col3 = st.columns(3)

if pnl["profit_factor"] == float("inf"):

    profit_factor_text = "∞"

else:

    profit_factor_text = (
        f"{pnl['profit_factor']:.2f}"
    )


col1.metric(
    "Profit Factor",
    profit_factor_text,
)

col2.metric(
    "Average Winner",
    f"{pnl['average_profit']:+,.2f}",
)

col3.metric(
    "Average Loser",
    f"{pnl['average_loss']:+,.2f}",
)


# ============================================================
# MANUAL EXIT
# ============================================================

if open_trades:

    st.subheader(
        "🔴 Manual Paper Exit"
    )

    st.warning(
        "Manual exit is available at any time. "
        "The price entered below becomes the actual "
        "paper SELL price. It can be above or below "
        "the BUY price and above or below the target."
    )

    for trade in open_trades:

        st.markdown(
            f"### {trade['strategy']} "
            f"— {trade['trading_symbol']}"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "BUY",
            f"{trade['entry_price']:.2f}",
        )

        if trade["current_price"] is None:

            col2.metric(
                "CURRENT",
                "N/A",
            )

        else:

            col2.metric(
                "CURRENT",
                f"{trade['current_price']:.2f}",
            )

        col3.metric(
            "TARGET",
            f"{trade['target_price']:.2f}",
        )

        if trade["current_price"] is None:

            current_display = "N/A"

        else:

            current_display = (
                f"{trade['current_price']:.2f}"
            )

        st.caption(
            f"ID {trade['id']} | "
            f"BUY {trade['entry_price']:.2f} | "
            f"CURRENT {current_display} | "
            f"TARGET {trade['target_price']:.2f}"
        )

        price_key = (
            f"manual_exit_price_{trade['id']}"
        )

        manual_price = st.number_input(
            "Manual SELL Price",
            min_value=0.01,
            value=(
                float(
                    trade["current_price"]
                )
                if trade["current_price"]
                is not None
                else float(
                    trade["entry_price"]
                )
            ),
            step=0.05,
            format="%.2f",
            key=price_key,
        )

        exit_button_key = (
            f"manual_exit_{trade['id']}"
        )

        if st.button(
            "🔴 MANUAL EXIT",
            key=exit_button_key,
            type="primary",
        ):

            try:

                manager = get_paper_manager()

                success = manager.manual_exit(
                    trade_id=trade["id"],
                    exit_price=manual_price,
                )

                if success:

                    buy_price = float(
                        trade["entry_price"]
                    )

                    pnl_points = (
                        manual_price
                        -
                        buy_price
                    )

                    st.success(
                        f"Trade ID {trade['id']} "
                        f"manually exited at "
                        f"{manual_price:.2f}. "
                        f"P&L: "
                        f"{pnl_points:+.2f} points."
                    )

                    time.sleep(1)

                    st.rerun()

                else:

                    st.error(
                        "Manual exit failed. "
                        "The trade may already be closed."
                    )

            except Exception as error:

                st.error(
                    f"Manual exit error: {error}"
                )

        st.divider()


# ============================================================
# OPEN PAPER TRADES
# ============================================================

st.subheader(
    "🟢 Open Paper Trades"
)


if not open_trades:

    st.info(
        "No open paper trades."
    )

else:

    open_table = []

    for trade in open_trades:

        open_table.append({

            "ID":
                trade["id"],

            "Strategy":
                trade["strategy"],

            "Option":
                trade["option_type"],

            "Strike":
                int(
                    trade["strike"]
                ),

            "Symbol":
                trade["trading_symbol"],

            "BUY":
                trade["entry_price"],

            "CURRENT":
                trade["current_price"],

            "P&L Points":
                trade[
                    "current_pnl_points"
                ],

            "TARGET":
                trade["target_price"],

            "To Target":
                trade["to_target"],

            "Status":
                trade["status"],
        })


    st.dataframe(
        open_table,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# POSITION DETAILS
# ============================================================

if open_trades:

    st.subheader(
        "Position Details"
    )

    for trade in open_trades:

        with st.container(
            border=True
        ):

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.write(
                f"**{trade['strategy']}**"
            )

            col2.metric(
                "BUY",
                f"{trade['entry_price']:.2f}",
            )

            if trade["current_price"] is None:

                col3.metric(
                    "CURRENT",
                    "N/A",
                )

            else:

                col3.metric(
                    "CURRENT",
                    f"{trade['current_price']:.2f}",
                )

            if trade["current_pnl_points"] is None:

                col4.metric(
                    "P&L Points",
                    "N/A",
                )

            else:

                col4.metric(
                    "P&L Points",
                    f"{trade['current_pnl_points']:+.2f}",
                )

            col5.metric(
                "TARGET",
                f"{trade['target_price']:.2f}",
            )

            st.caption(
                f"ID {trade['id']} | "
                f"{trade['option_type']} | "
                f"{trade['trading_symbol']} | "
                f"Entry {trade['entry_time']}"
            )


# ============================================================
# TRADE HISTORY
# ============================================================

st.subheader(
    "Paper Trade History"
)


if trades:

    history_table = []

    for trade in trades:

        if trade["status"] == "CLOSED":

            pnl_value = (
                trade["pnl_value"]
                or
                0
            )

            pnl_points = (
                trade["pnl_points"]
                or
                0
            )

        else:

            pnl_value = (
                trade["current_pnl_value"]
                or
                0
            )

            pnl_points = (
                trade["current_pnl_points"]
                or
                0
            )

        history_table.append({

            "ID":
                trade["id"],

            "Strategy":
                trade["strategy"],

            "Option":
                trade["option_type"],

            "Strike":
                int(
                    trade["strike"]
                ),

            "BUY":
                trade["entry_price"],

            "SELL":
                trade["exit_price"],

            "CURRENT":
                trade["current_price"],

            "TARGET":
                trade["target_price"],

            "P&L Points":
                pnl_points,

            "P&L Value":
                pnl_value,

            "Exit Reason":
                trade["exit_reason"],

            "Status":
                trade["status"],

            "Entry":
                trade["entry_time"],

            "Exit":
                trade["exit_time"],
        })


    st.dataframe(
        history_table,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "No paper trades yet."
    )


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Paper trading only. "
    "This dashboard does not place broker orders."
)


# ============================================================
# AUTO REFRESH
# ============================================================

time.sleep(
    refresh_seconds
)

st.rerun()