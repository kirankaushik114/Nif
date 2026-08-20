# ============================================================
# BANK NIFTY PAPER TRADING API
# ============================================================
#
# FastAPI backend for mobile application
#
# REAL ORDERS: NO
# PAPER TRADING ONLY
#
# Endpoints:
#
# GET  /api/status
# GET  /api/market
# GET  /api/conditions
# GET  /api/trades
# GET  /api/open-trades
# GET  /api/pnl
# POST /api/manual-exit
#
# ============================================================

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# ============================================================
# IMPORT EXISTING PROJECT CODE
# ============================================================

from data.historical_data import (
    GrowwHistoricalData
)

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

from paper_trading.trade_manager import (
    PaperTradeManager
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Bank Nifty Paper Trading API",
    description=(
        "Paper trading API for the Bank Nifty system. "
        "No real broker orders are placed."
    ),
    version="1.0.0",
)


# ============================================================
# DATABASE
# ============================================================

DATABASE = PAPER_DATABASE_FILE


# ============================================================
# OBJECTS
# ============================================================

historical = GrowwHistoricalData()

paper_manager = PaperTradeManager(
    database_file=DATABASE,
    timezone=TIME_ZONE,
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ManualExitRequest(BaseModel):

    trade_id: int

    exit_price: float


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def root():

    return {

        "application":
            "Bank Nifty Paper Trading API",

        "status":
            "running",

        "real_orders":
            False,

    }


# ============================================================
# STATUS
# ============================================================

@app.get("/api/status")
def status():

    try:

        open_trades = (
            paper_manager
            .get_open_trades()
        )

        return {

            "status":
                "running",

            "paper_trading":
                True,

            "real_orders":
                False,

            "open_trades":
                len(open_trades),

            "database":
                str(DATABASE),

        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ============================================================
# MARKET DATA
# ============================================================

def get_market_data():

    data_1m = (
        historical
        .get_1_minute_candles()
    )

    data_15m = (
        historical
        .get_15_minute_candles()
    )

    candles_1m = (
        data_1m.get(
            "candles",
            []
        )
    )

    candles_15m = (
        data_15m.get(
            "candles",
            []
        )
    )

    if not candles_1m:

        raise ValueError(
            "1 minute market data unavailable."
        )

    if not candles_15m:

        raise ValueError(
            "15 minute market data unavailable."
        )

    closes_1m = (
        candle_closes_to_series(
            candles_1m
        )
    )

    closes_15m = (
        candle_closes_to_series(
            candles_15m
        )
    )

    rsi_1m = (
        calculate_latest_rsi(
            closes_1m,
            period=RSI_PERIOD,
        )
    )

    rsi_15m = (
        calculate_latest_rsi(
            closes_15m,
            period=RSI_PERIOD,
        )
    )

    bank_nifty = float(
        candles_1m[-1][4]
    )

    candle_time = (
        candles_1m[-1][0]
    )

    return {

        "bank_nifty":
            bank_nifty,

        "rsi_1m":
            float(rsi_1m),

        "rsi_15m":
            float(rsi_15m),

        "candle_time":
            candle_time,

        "current_time":
            datetime.now().isoformat(),

    }


# ============================================================
# MARKET ENDPOINT
# ============================================================

@app.get("/api/market")
def market():

    try:

        return get_market_data()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ============================================================
# SIX CONDITIONS
# ============================================================

def build_conditions(
    rsi_1m,
    rsi_15m,
):

    return [

        {
            "condition": 1,

            "rule":
                f"1M <= {RSI_1_BULLISH}",

            "strategy":
                "1M_CE",

            "option":
                "CE",

            "target_points":
                15,

            "met":
                rsi_1m <= RSI_1_BULLISH,
        },

        {
            "condition": 2,

            "rule":
                f"1M >= {RSI_1_BEARISH}",

            "strategy":
                "1M_PE",

            "option":
                "PE",

            "target_points":
                15,

            "met":
                rsi_1m >= RSI_1_BEARISH,
        },

        {
            "condition": 3,

            "rule":
                f"15M < {RSI_15_EXTREME_OVERSOLD}",

            "strategy":
                "15M_CE",

            "option":
                "CE",

            "target_points":
                45,

            "met":
                rsi_15m
                <
                RSI_15_EXTREME_OVERSOLD,
        },

        {
            "condition": 4,

            "rule":
                f"15M > {RSI_15_EXTREME_OVERBOUGHT}",

            "strategy":
                "15M_PE",

            "option":
                "PE",

            "target_points":
                45,

            "met":
                rsi_15m
                >
                RSI_15_EXTREME_OVERBOUGHT,
        },

        {
            "condition": 5,

            "rule":
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

            "target_points":
                75,

            "met":
                (
                    rsi_1m
                    <
                    RSI_1_COMBINED_BULLISH

                    and

                    rsi_15m
                    <
                    RSI_15_BULLISH
                ),
        },

        {
            "condition": 6,

            "rule":
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

            "target_points":
                75,

            "met":
                (
                    rsi_1m
                    >
                    RSI_1_COMBINED_BEARISH

                    and

                    rsi_15m
                    >
                    RSI_15_BEARISH
                ),
        },

    ]


# ============================================================
# CONDITIONS ENDPOINT
# ============================================================

@app.get("/api/conditions")
def conditions():

    try:

        market_data = (
            get_market_data()
        )

        return {

            "rsi_1m":
                market_data["rsi_1m"],

            "rsi_15m":
                market_data["rsi_15m"],

            "conditions":
                build_conditions(

                    market_data[
                        "rsi_1m"
                    ],

                    market_data[
                        "rsi_15m"
                    ],
                ),
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ============================================================
# DATABASE TRADES
# ============================================================

def get_all_trades():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = (
        sqlite3.Row
    )

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

            exit_reason,

            created_at

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
# CURRENT OPTION PRICE
# ============================================================

def get_current_option_price(
    symbol
):

    try:

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
# ADD LIVE PRICE / P&L
# ============================================================

def add_live_values(
    trade
):

    result = dict(
        trade
    )

    if trade["status"] == "OPEN":

        current_price = (
            get_current_option_price(
                trade[
                    "trading_symbol"
                ]
            )
        )

        result[
            "current_price"
        ] = current_price

        if current_price is not None:

            pnl_points = (
                current_price
                -
                float(
                    trade[
                        "entry_price"
                    ]
                )
            )

            result[
                "current_pnl_points"
            ] = pnl_points

            result[
                "current_pnl_value"
            ] = (
                pnl_points
                *
                int(
                    trade[
                        "quantity"
                    ]
                )
            )

            result[
                "to_target"
            ] = (
                float(
                    trade[
                        "target_price"
                    ]
                )
                -
                current_price
            )

        else:

            result[
                "current_pnl_points"
            ] = None

            result[
                "current_pnl_value"
            ] = None

            result[
                "to_target"
            ] = None

    else:

        result[
            "current_price"
        ] = trade[
            "exit_price"
        ]

        result[
            "current_pnl_points"
        ] = trade[
            "pnl_points"
        ]

        result[
            "current_pnl_value"
        ] = trade[
            "pnl_value"
        ]

        result[
            "to_target"
        ] = 0

    return result


# ============================================================
# ALL TRADES ENDPOINT
# ============================================================

@app.get("/api/trades")
def trades():

    try:

        rows = (
            get_all_trades()
        )

        return {

            "count":
                len(rows),

            "trades":
                [
                    add_live_values(
                        row
                    )
                    for row in rows
                ],
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ============================================================
# OPEN TRADES
# ============================================================

@app.get("/api/open-trades")
def open_trades():

    try:

        rows = (
            get_all_trades()
        )

        result = [

            add_live_values(
                row
            )

            for row in rows

            if row["status"] == "OPEN"
        ]

        return {

            "count":
                len(result),

            "trades":
                result,
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ============================================================
# P&L
# ============================================================

@app.get("/api/pnl")
def pnl():

    try:

        rows = (
            get_all_trades()
        )

        rows = [

            add_live_values(
                row
            )

            for row in rows
        ]

        closed = [

            row

            for row in rows

            if row["status"] == "CLOSED"
        ]

        opened = [

            row

            for row in rows

            if row["status"] == "OPEN"
        ]

        winning = [

            row

            for row in closed

            if (
                row["pnl_points"]
                is not None

                and

                row["pnl_points"] > 0
            )
        ]

        losing = [

            row

            for row in closed

            if (
                row["pnl_points"]
                is not None

                and

                row["pnl_points"] < 0
            )
        ]

        breakeven = [

            row

            for row in closed

            if (
                row["pnl_points"]
                is not None

                and

                row["pnl_points"] == 0
            )
        ]

        gross_profit = sum(

            (
                row["pnl_value"]
                or
                0
            )

            for row in winning
        )

        gross_loss = sum(

            (
                row["pnl_value"]
                or
                0
            )

            for row in losing
        )

        closed_pnl = sum(

            (
                row["pnl_value"]
                or
                0
            )

            for row in closed
        )

        open_pnl = sum(

            (
                row[
                    "current_pnl_value"
                ]
                or
                0
            )

            for row in opened
        )

        total_pnl = (
            closed_pnl
            +
            open_pnl
        )

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

        if gross_loss < 0:

            profit_factor = (
                gross_profit
                /
                abs(gross_loss)
            )

        else:

            profit_factor = None

        return {

            "total_trades":
                len(rows),

            "closed_trades":
                len(closed),

            "open_trades":
                len(opened),

            "winning_trades":
                len(winning),

            "losing_trades":
                len(losing),

            "breakeven_trades":
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

            "profit_factor":
                profit_factor,
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ============================================================
# MANUAL EXIT
# ============================================================

@app.post("/api/manual-exit")
def manual_exit(
    request: ManualExitRequest
):

    if request.exit_price <= 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "Exit price must be "
                "greater than 0."
            ),
        )

    try:

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # This uses the manually entered price.
        #
        # It does NOT use current LTP.
        #
        # It does NOT require the price to be
        # above or below the target.
        #
        # REAL ORDER = NO
        # ----------------------------------------------------

        success = (
            paper_manager
            .manual_exit(

                trade_id=
                    request.trade_id,

                exit_price=
                    request.exit_price,
            )
        )

        if not success:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Trade not found, "
                    "or trade is already closed."
                ),
            )

        return {

            "success":
                True,

            "trade_id":
                request.trade_id,

            "exit_price":
                request.exit_price,

            "exit_reason":
                "MANUAL EXIT",

            "real_order":
                False,

            "message":
                "Paper trade manually exited.",
        }

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )