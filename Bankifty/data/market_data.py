"""
Bank Nifty Live Index Monitor
Groww API 1.5.0

ALERT ONLY
NO ORDER PLACEMENT
"""

import time
from datetime import datetime

from growwapi import GrowwAPI, GrowwFeed

from config.settings import (
    GROWW_API_KEY,
    GROWW_API_SECRET,
)


class GrowwMarketData:

    def __init__(self):
        self.groww = None
        self.feed = None

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    def connect(self):

        if not GROWW_API_KEY:
            raise ValueError(
                "GROWW_API_KEY is missing."
            )

        if not GROWW_API_SECRET:
            raise ValueError(
                "GROWW_API_SECRET is missing."
            )

        print("Authenticating with Groww...")

        access_token = GrowwAPI.get_access_token(
            api_key=GROWW_API_KEY,
            secret=GROWW_API_SECRET,
        )

        self.groww = GrowwAPI(access_token)

        print("Groww authentication successful.")

    # ========================================================
    # CREATE FEED
    # ========================================================

    def create_feed(self):

        if self.groww is None:
            self.connect()

        self.feed = GrowwFeed(self.groww)

        print("Groww live feed created.")

    # ========================================================
    # SUBSCRIBE BANK NIFTY INDEX
    # ========================================================

    def subscribe_bank_nifty(self):

        if self.feed is None:
            self.create_feed()

        instruments = [
            {
                "exchange": "NSE",
                "segment": "CASH",
                "exchange_token": "BANKNIFTY",
            }
        ]

        print()
        print("Subscribing to Bank Nifty index...")

        self.feed.subscribe_index_value(
            instruments
        )

        print("Bank Nifty subscription successful.")

    # ========================================================
    # GET INDEX DATA
    # ========================================================

    def get_bank_nifty_data(self):

        if self.feed is None:
            self.subscribe_bank_nifty()

        return self.feed.get_index_value()

    # ========================================================
    # EXTRACT BANK NIFTY VALUE
    # ========================================================

    @staticmethod
    def extract_bank_nifty_value(data):

        try:

            value = (
                data
                ["NSE"]
                ["CASH"]
                ["BANKNIFTY"]
                ["value"]
            )

            if value is None:
                return None

            return float(value)

        except (KeyError, TypeError):

            return None

    # ========================================================
    # TEST
    # ========================================================

    def test_live_data(self):

        self.subscribe_bank_nifty()

        print()
        print("=" * 70)
        print("BANK NIFTY LIVE INDEX DATA")
        print("=" * 70)

        for _ in range(10):

            time.sleep(2)

            data = self.get_bank_nifty_data()

            bank_nifty = self.extract_bank_nifty_value(
                data
            )

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            print()
            print("Time       :", timestamp)
            print("Raw Data   :", data)
            print(
                "Bank Nifty :",
                bank_nifty
            )

        print()
        print("=" * 70)
        print("TEST FINISHED")
        print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("BANK NIFTY LIVE DATA TEST")
    print("=" * 70)

    try:

        market_data = GrowwMarketData()

        market_data.test_live_data()

    except Exception as error:

        print()
        print("=" * 70)
        print("LIVE DATA TEST FAILED")
        print("=" * 70)

        print(
            "Error type :",
            type(error).__name__
        )

        print(
            "Error      :",
            error
        )

        print("=" * 70)


if __name__ == "__main__":
    main()