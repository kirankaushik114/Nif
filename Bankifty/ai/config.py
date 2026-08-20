"""
Bank Nifty AI Configuration
===========================

Phase 1:
    Ollama + structured market context.

Phase 2:
    News collection + RSS + RAG preparation.

AI is analysis-only.
It does not execute trades.
It does not override SIC.

Ollama and News can be independently enabled/disabled
from this file.
"""


# ============================================================
# OLLAMA
# ============================================================

# Master switch for local Ollama AI.
#
# True  -> Ollama AI is enabled.
# False -> Ollama AI is disabled.
#
# The rest of the Bank Nifty system continues running
# when Ollama is disabled.

OLLAMA_ENABLED = True


# Ollama local server.
OLLAMA_BASE_URL = "http://127.0.0.1:11434"


# Current local model.
OLLAMA_MODEL = "qwen3:4b"


# ============================================================
# AI
# ============================================================

# Master AI switch.
#
# This is separate from OLLAMA_ENABLED because later
# another AI provider such as OpenAI may be added.

AI_ENABLED = True


# ============================================================
# AI ANALYSIS INTERVAL
# ============================================================

# Routine AI analysis interval.
#
# 900 seconds = 15 minutes.
#
# The normal Bank Nifty market monitor can continue
# running independently.

AI_ANALYSIS_INTERVAL_SECONDS = 900


# ============================================================
# OLLAMA GENERATION
# ============================================================

# Maximum number of tokens generated for routine analysis.

AI_MAX_TOKENS = 300


# Context size.
#
# Smaller context = faster routine analysis.

AI_CONTEXT_SIZE = 2048


# Temperature.
#
# Lower value = more consistent output.

AI_TEMPERATURE = 0.2


# ============================================================
# AI SAFETY
# ============================================================

# AI must never place real orders.

AI_REAL_ORDERS_ENABLED = False


# AI cannot override the existing SIC paper-trading logic.

AI_CAN_OVERRIDE_SIC = False


# ============================================================
# NEWS
# ============================================================

# Master switch for the news collection system.
#
# True  -> News collection is enabled.
# False -> News collection is disabled.
#
# The Bank Nifty market monitor continues running
# when News is disabled.

NEWS_ENABLED = True


# ============================================================
# NEWS COLLECTION INTERVAL
# ============================================================

# News collection interval.
#
# 900 seconds = 15 minutes.
#
# This is independent of the AI analysis interval.

NEWS_COLLECTION_INTERVAL_SECONDS = 900


# ============================================================
# NEWS RSS
# ============================================================

# Maximum number of RSS articles processed from
# each feed during one collection cycle.
#
# Current configuration:
#
# 6 feeds × 25 articles = maximum 150 articles/cycle.

NEWS_MAX_ITEMS_PER_FEED = 25


# HTTP timeout for RSS requests.

NEWS_REQUEST_TIMEOUT = 15