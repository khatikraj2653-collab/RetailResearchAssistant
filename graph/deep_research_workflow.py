"""
Deep Stock Research workflow — SemiBot-style factor breakdown, but
strictly factual. All numbers come from yfinance/FRED. The LLM node
ONLY writes one plain factual sentence per factor from the real value
already fetched — it never scores, ranks, or labels anything
bullish/bearish, and never predicts direction.
"""

from dotenv import load_dotenv
load_dotenv()

import json
from typing import TypedDict
from concurrent.futures import ThreadPoolExecutor

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from data.yfinance_client import (
    get_company_info, get_quote, get_recent_news,
    get_insider_activity, get_technical_signal,
)
from data.macro_tools import get_macro_snapshot

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class DeepResearchState(TypedDict, total=False):
    ticker: str
    info: dict
    quote: dict
    news: list
    insider: dict
    technical: str
    macro: dict
    overview: str
    factor_notes: dict


def fetch_all_factors(state: DeepResearchState) -> DeepResearchState:
    ticker = state["ticker"]
    with ThreadPoolExecutor(max_workers=6) as pool:
        info_f = pool.submit(get_company_info, ticker)
        quote_f = pool.submit(get_quote, ticker)
        news_f = pool.submit(get_recent_news, ticker)
        insider_f = pool.submit(get_insider_activity, ticker)
        technical_f = pool.submit(get_technical_signal, ticker)
        macro_f = pool.submit(get_macro_snapshot)

        return {
            "info": info_f.result(),
            "quote": quote_f.result(),
            "news": news_f.result(),
            "insider": insider_f.result(),
            "technical": technical_f.result(),
            "macro": macro_f.result(),
        }


OVERVIEW_PROMPT = """Write a short, factual 2-3 sentence company
overview for {ticker}, based on this business summary. No predictions,
no recommendations.

Business summary: {summary}
CEO (if known): {ceo}"""


def write_overview(state: DeepResearchState) -> DeepResearchState:
    info = state["info"]
    prompt = OVERVIEW_PROMPT.format(
        ticker=state["ticker"],
        summary=(info.get("longBusinessSummary") or "No summary available.")[:1500],
        ceo=info.get("ceo") or "not available",
    )
    response = llm.invoke(prompt)
    return {"overview": response.content}


NOTES_PROMPT = """You are writing short, purely factual notes for a
retail investor about {ticker}. For EACH factor below, write ONE short
sentence stating what the data shows. Do NOT say "bullish", "bearish",
"buy", "sell", or give any recommendation or prediction — just describe
the fact plainly. If a value is missing, say so rather than inventing one.

MACROECONOMIC
CPI: {cpi}
PPI: {ppi}
Fed Funds Rate: {fed_rate}
USD Index: {usd_index}

FUNDAMENTAL
Trailing P/E: {pe}
Forward P/E: {forward_pe}
Market Cap: {market_cap}
Revenue Growth: {revenue_growth}
Earnings Growth: {earnings_growth}
Profit Margin: {profit_margin}
Dividend Yield: {dividend_yield}
Beta: {beta}
Insider Activity: {insider}

MARKET INTELLIGENCE
Analyst Recommendation: {recommendation}
Analyst Target Price: {target_price}
Technical Signal (50d vs 200d moving average): {technical}

IMPORTANT: For technical_signal specifically, copy the moving-average
sentence provided above VERBATIM, word for word, with no paraphrasing,
no reformatting, and no changes to spacing or punctuation.

Return ONLY valid JSON (no markdown fences) with EXACTLY these keys:
cpi, ppi, fed_rate, usd_index, trailing_pe, forward_pe, market_cap,
revenue_growth, earnings_growth, profit_margin, dividend_yield, beta,
insider_activity, analyst_recommendation, analyst_target_price,
technical_signal — each mapping to your one-sentence note."""


def write_factor_notes(state: DeepResearchState) -> DeepResearchState:
    info = state["info"]
    macro = state["macro"]
    prompt = NOTES_PROMPT.format(
        ticker=state["ticker"],
        cpi=macro.get("cpi"), ppi=macro.get("ppi"),
        fed_rate=macro.get("fed_rate"), usd_index=macro.get("usd_index"),
        pe=info.get("trailingPE"), forward_pe=info.get("forwardPE"),
        market_cap=info.get("marketCap"), revenue_growth=info.get("revenueGrowth"),
        earnings_growth=info.get("earningsGrowth"), profit_margin=info.get("profitMargins"),
        dividend_yield=info.get("dividendYield"), beta=info.get("beta"),
        insider=state["insider"].get("summary"),
        recommendation=info.get("recommendationKey"),
        target_price=info.get("targetMeanPrice"),
        technical=state["technical"],
    )
    response = llm.invoke(prompt)
    text = response.content.strip()
    if text.startswith("```"):
        text = text.strip("`").replace("json", "", 1).strip()
    try:
        notes = json.loads(text)
    except json.JSONDecodeError:
        notes = {}

    # Technical signal is already a clean, correctly-formatted sentence
    # from our own code (get_technical_signal) -- never let the LLM
    # rewrite/reformat it, since that's what caused the mangled spacing.
    notes["technical_signal"] = state["technical"]

    return {"factor_notes": notes}


def build_deep_research_graph():
    graph = StateGraph(DeepResearchState)
    graph.add_node("fetch", fetch_all_factors)
    graph.add_node("overview", write_overview)
    graph.add_node("notes", write_factor_notes)
    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "overview")
    graph.add_edge("overview", "notes")
    graph.add_edge("notes", END)
    return graph.compile()


deep_research_graph = build_deep_research_graph()


def run_deep_research(ticker: str) -> dict:
    return deep_research_graph.invoke({"ticker": ticker.upper()})


# --- Subgraph export ---
# `deep_research_graph` (fetch -> overview -> notes) is a complete,
# independently-compiled LangGraph. It is reused as a genuine SUBGRAPH
# by graph/deep_compare_workflow.py, which invokes this exact same
# compiled graph once per ticker rather than duplicating the fetch/
# overview/notes logic in a second, parallel implementation.
research_subgraph = deep_research_graph