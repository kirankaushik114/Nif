"""
Bank Nifty RSS Feed Configuration
=================================

Central configuration for RSS news sources.

Keep provider logic separate from feed configuration.
"""

# ============================================================
# GENERAL MARKET / INDIA
# ============================================================

RSS_FEEDS = [

    {
        "name": "Google News - Bank Nifty",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Bank+Nifty"
            "&hl=en-IN"
            "&gl=IN"
            "&ceid=IN:en"
        ),
        "category": "market",
        "importance": 0.7,
        "country": "India",
        "symbols": ["BANKNIFTY"],
    },

    # --------------------------------------------------------
    # Indian banking
    # --------------------------------------------------------

    {
        "name": "Google News - Indian Banks",
        "url": (
            "https://news.google.com/rss/search?"
            "q=Indian+banks+HDFC+ICICI+SBI+Axis"
            "&hl=en-IN"
            "&gl=IN"
            "&ceid=IN:en"
        ),
        "category": "banking",
        "importance": 0.8,
        "country": "India",
        "symbols": [
            "BANKNIFTY",
            "HDFCBANK",
            "ICICIBANK",
            "SBIN",
            "AXISBANK",
        ],
    },

    # --------------------------------------------------------
    # RBI / monetary policy
    # --------------------------------------------------------

    {
        "name": "Google News - RBI",
        "url": (
            "https://news.google.com/rss/search?"
            "q=RBI+Reserve+Bank+India"
            "&hl=en-IN"
            "&gl=IN"
            "&ceid=IN:en"
        ),
        "category": "monetary_policy",
        "importance": 0.9,
        "country": "India",
        "symbols": ["BANKNIFTY"],
    },

    # --------------------------------------------------------
    # Crude oil
    # --------------------------------------------------------

    {
        "name": "Google News - Crude Oil",
        "url": (
            "https://news.google.com/rss/search?"
            "q=crude+oil+Brent"
            "&hl=en-IN"
            "&gl=IN"
            "&ceid=IN:en"
        ),
        "category": "commodities",
        "importance": 0.8,
        "country": "Global",
        "symbols": ["BANKNIFTY"],
    },

    # --------------------------------------------------------
    # US / Iran / Middle East
    # --------------------------------------------------------

    {
        "name": "Google News - US Iran",
        "url": (
            "https://news.google.com/rss/search?"
            "q=US+Iran"
            "&hl=en-IN"
            "&gl=IN"
            "&ceid=IN:en"
        ),
        "category": "geopolitics",
        "importance": 0.9,
        "country": "Global",
        "symbols": ["BANKNIFTY"],
    },

    # --------------------------------------------------------
    # China / US
    # --------------------------------------------------------

    {
        "name": "Google News - US China",
        "url": (
            "https://news.google.com/rss/search?"
            "q=US+China+trade"
            "&hl=en-IN"
            "&gl=IN"
            "&ceid=IN:en"
        ),
        "category": "geopolitics",
        "importance": 0.7,
        "country": "Global",
        "symbols": ["BANKNIFTY"],
    },
]