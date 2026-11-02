"""
Portfolio Analysis -- structural risk only, no prediction.

Pipeline:
1. fetch_holdings_data: get current price + sector for each ticker, and
   1y price history for correlation calc. Any ticker that can't resolve
   to real market data is skipped (not crashed on) and surfaced back to
   the UI as a warning.
2. compute_risk_metrics: pure Python/pandas math -- concentration (largest
   single holding %), sector concentration, pairwise return correlation.
   Thresholds decide red/yellow/green HERE, deterministically. The LLM
   never invents a flag -- it only narrates numbers we've already computed.
3. narrate_flags: LLM turns the computed flags into plain-English text.
"""

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from data.yfinance_client import get_company_info, get_quote, get_price_history

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# --- Thresholds (deterministic, not LLM-decided) ---
SINGLE_STOCK_RED = 0.25
SINGLE_STOCK_YELLOW = 0.15
SECTOR_RED = 0.40
SECTOR_YELLOW = 0.25
CORRELATION_RED = 0.70


class PortfolioState(TypedDict, total=False):
    holdings: list
    enriched: list
    total_value: float
    skipped_tickers: list
    stock_flags: list
    sector_flags: list
    correlation_flags: list
    summary: str


def fetch_holdings_data(state: PortfolioState) -> PortfolioState:
    holdings = state["holdings"]

    def fetch_one(h: dict):
        ticker = h["ticker"].upper()
        try:
            info = get_company_info(ticker)
            quote = get_quote(ticker)
            price = quote.get("lastPrice") or 0
            if price == 0:
                # No real price data -- almost certainly an invalid/unresolved ticker.
                return None
            return {
                "ticker": ticker,
                "shares": h["shares"],
                "price": price,
                "market_value": price * h["shares"],
                "sector": info.get("sector") or "Unknown",
            }
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=max(len(holdings), 1)) as pool:
        raw_results = list(pool.map(fetch_one, holdings))

    skipped = [h["ticker"] for h, r in zip(holdings, raw_results) if r is None]
    enriched = [r for r in raw_results if r is not None]

    if skipped:
        print(f"[Portfolio] Skipped unresolved/invalid tickers: {skipped}")

    total_value = sum(e["market_value"] for e in enriched)
    for e in enriched:
        e["weight"] = e["market_value"] / total_value if total_value else 0

    return {"enriched": enriched, "total_value": total_value, "skipped_tickers": skipped}


def compute_risk_metrics(state: PortfolioState) -> PortfolioState:
    enriched = state["enriched"]

    stock_flags = []
    for e in enriched:
        if e["weight"] > SINGLE_STOCK_RED:
            level = "red"
        elif e["weight"] > SINGLE_STOCK_YELLOW:
            level = "yellow"
        else:
            level = "green"
        stock_flags.append(
            {"ticker": e["ticker"], "weight": round(e["weight"], 4), "level": level}
        )

    sector_weights = {}
    for e in enriched:
        sector_weights[e["sector"]] = sector_weights.get(e["sector"], 0) + e["weight"]

    sector_flags = []
    for sector, weight in sector_weights.items():
        if weight > SECTOR_RED:
            level = "red"
        elif weight > SECTOR_YELLOW:
            level = "yellow"
        else:
            level = "green"
        sector_flags.append({"sector": sector, "weight": round(weight, 4), "level": level})

    correlation_flags = []
    if len(enriched) >= 2:
        price_series = {}
        for e in enriched:
            try:
                history = get_price_history(e["ticker"], period="1y")
                df = pd.DataFrame(history)
                if not df.empty:
                    df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_localize(None)
                    price_series[e["ticker"]] = df.set_index("Date")["Close"]
            except Exception:
                continue

        if len(price_series) >= 2:
            price_df = pd.DataFrame(price_series).dropna()
            returns_df = price_df.pct_change().dropna()
            corr_matrix = returns_df.corr()

            tickers = list(corr_matrix.columns)
            for i in range(len(tickers)):
                for j in range(i + 1, len(tickers)):
                    corr_value = corr_matrix.iloc[i, j]
                    if corr_value > CORRELATION_RED:
                        correlation_flags.append(
                            {
                                "pair": [tickers[i], tickers[j]],
                                "correlation": round(float(corr_value), 3),
                                "level": "red",
                            }
                        )

    return {
        "stock_flags": stock_flags,
        "sector_flags": sector_flags,
        "correlation_flags": correlation_flags,
    }


NARRATIVE_PROMPT = """You are writing a structural risk summary for a
retail investor's portfolio. Use ONLY the flags below, which were computed
deterministically. Do NOT predict future performance, do NOT recommend
buying or selling anything, do NOT invent numbers not shown here.

Single-stock concentration flags (red = over 25% in one stock, yellow =
over 15%, green = fine):
{stock_flags}

Sector concentration flags (red = over 40% in one sector, yellow = over
25%, green = fine):
{sector_flags}

Highly correlated pairs (red = these two moved together with correlation
above 0.70 over the last year, meaning they tend to swing together):
{correlation_flags}

Write a short, plain-English summary (3-4 sentences) explaining what these
flags mean for diversification. If there are no red or yellow flags at
all, say the portfolio looks structurally reasonable on these metrics."""


def narrate_flags(state: PortfolioState) -> PortfolioState:
    prompt = NARRATIVE_PROMPT.format(
        stock_flags=state["stock_flags"],
        sector_flags=state["sector_flags"],
        correlation_flags=state["correlation_flags"],
    )
    response = llm.invoke(prompt)
    return {"summary": response.content}


def build_portfolio_graph():
    graph = StateGraph(PortfolioState)
    graph.add_node("fetch", fetch_holdings_data)
    graph.add_node("compute_risk", compute_risk_metrics)
    graph.add_node("narrate", narrate_flags)
    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "compute_risk")
    graph.add_edge("compute_risk", "narrate")
    graph.add_edge("narrate", END)
    return graph.compile()


portfolio_graph = build_portfolio_graph()


def run_portfolio_analysis(holdings: list) -> dict:
    return portfolio_graph.invoke({"holdings": holdings})


def compute_portfolio_diff(old_snapshot: dict, new_result: dict, old_holdings: list, new_holdings: list) -> dict:
    """Purely deterministic comparison between the previous saved
    portfolio snapshot and the current one. No LLM involvement -- every
    number here is computed directly, so the chatbot can only narrate
    facts that were actually calculated, never invent a change."""
    old_shares = {h["ticker"]: h["shares"] for h in old_holdings}
    new_shares = {h["ticker"]: h["shares"] for h in new_holdings}

    added = [t for t in new_shares if t not in old_shares]
    removed = [t for t in old_shares if t not in new_shares]
    changed_shares = [
        {"ticker": t, "old_shares": old_shares[t], "new_shares": new_shares[t]}
        for t in new_shares
        if t in old_shares and abs(new_shares[t] - old_shares[t]) > 1e-9
    ]

    old_weights = {f["ticker"]: f["weight"] for f in old_snapshot.get("stock_flags", [])}
    new_weights = {f["ticker"]: f["weight"] for f in new_result.get("stock_flags", [])}
    weight_changes = [
        {"ticker": t, "old_weight": old_weights[t], "new_weight": new_weights[t], "delta": new_weights[t] - old_weights[t]}
        for t in new_weights
        if t in old_weights and abs(new_weights[t] - old_weights[t]) > 0.01
    ]

    old_sector = {f["sector"]: f["weight"] for f in old_snapshot.get("sector_flags", [])}
    new_sector = {f["sector"]: f["weight"] for f in new_result.get("sector_flags", [])}
    all_sectors = set(old_sector) | set(new_sector)
    sector_changes = [
        {"sector": s, "old_weight": old_sector.get(s, 0), "new_weight": new_sector.get(s, 0), "delta": new_sector.get(s, 0) - old_sector.get(s, 0)}
        for s in all_sectors
        if abs(new_sector.get(s, 0) - old_sector.get(s, 0)) > 0.01
    ]

    return {
        "added": added,
        "removed": removed,
        "changed_shares": changed_shares,
        "weight_changes": weight_changes,
        "sector_changes": sector_changes,
    }