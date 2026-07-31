"""
Deep Compare workflow -- built as a LangGraph whose per-ticker work is
delegated to the exact same compiled subgraph used by Stock Research
(graph.deep_research_workflow.research_subgraph), rather than a second,
separately-implemented fetch/overview/notes pipeline. Compare's own
graph has two nodes: one that fans the ticker list out across the
subgraph in parallel, and one that writes the factual comparison
summary. No scores, no bullish/bearish, no upside/downside.
"""

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict
from concurrent.futures import ThreadPoolExecutor

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from graph.deep_research_workflow import research_subgraph

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


class CompareState(TypedDict, total=False):
    tickers: list
    compare_results: dict
    summary: str


def run_subgraph_for_all_tickers(state: CompareState) -> CompareState:
    """Invokes the research_subgraph once per ticker, in parallel. This
    is the actual subgraph-composition step: each call below is a full
    run of the SAME compiled graph Stock Research uses, not a
    re-implementation of its fetch/overview/notes logic."""
    tickers = state["tickers"]
    results = {}

    def run_one(ticker: str) -> tuple:
        try:
            return ticker, research_subgraph.invoke({"ticker": ticker.upper()})
        except Exception as e:
            return ticker, {"error": str(e)}

    with ThreadPoolExecutor(max_workers=max(len(tickers), 1)) as pool:
        for ticker, result in pool.map(run_one, tickers):
            results[ticker] = result

    return {"compare_results": results}


SUMMARY_PROMPT = """You are writing a short, purely factual comparison
summary across {n} companies: {tickers}. Use ONLY the data below. Do
NOT rank them, do NOT declare a winner, do NOT predict direction, and
NEVER use the words "bullish" or "bearish".

{company_blocks}

Write 3-4 sentences noting the most notable factual differences across
these companies (e.g. valuation, growth, sector, size)."""


def write_comparison_summary(state: CompareState) -> CompareState:
    compare_results = state["compare_results"]
    tickers = list(compare_results.keys())
    blocks = []
    for t in tickers:
        r = compare_results[t]
        if "error" in r:
            blocks.append(f"{t}: data unavailable ({r['error']})")
            continue
        info = r.get("info", {})
        notes = r.get("factor_notes", {})
        blocks.append(
            f"--- {info.get('shortName') or t} ({t}) ---\n"
            f"Sector: {info.get('sector')}\n"
            f"Trailing P/E: {notes.get('trailing_pe')}\n"
            f"Revenue Growth: {notes.get('revenue_growth')}\n"
            f"Market Cap: {notes.get('market_cap')}\n"
        )
    prompt = SUMMARY_PROMPT.format(
        n=len(tickers), tickers=", ".join(tickers), company_blocks="\n".join(blocks)
    )
    response = llm.invoke(prompt)
    return {"summary": response.content}


def build_compare_graph():
    graph = StateGraph(CompareState)
    graph.add_node("run_subgraph_per_ticker", run_subgraph_for_all_tickers)
    graph.add_node("write_summary", write_comparison_summary)
    graph.set_entry_point("run_subgraph_per_ticker")
    graph.add_edge("run_subgraph_per_ticker", "write_summary")
    graph.add_edge("write_summary", END)
    return graph.compile()


compare_graph = build_compare_graph()


def run_deep_compare(tickers: list) -> dict:
    final_state = compare_graph.invoke({"tickers": [t.upper() for t in tickers]})
    return final_state["compare_results"]


def summarize_compare(compare_results: dict) -> str:
    """Kept for compatibility with existing page code, which calls this
    separately after run_deep_compare. Internally it now just re-invokes
    the same summary-writing logic used inside the graph."""
    tickers = list(compare_results.keys())
    blocks = []
    for t in tickers:
        r = compare_results[t]
        if "error" in r:
            blocks.append(f"{t}: data unavailable ({r['error']})")
            continue
        info = r.get("info", {})
        notes = r.get("factor_notes", {})
        blocks.append(
            f"--- {info.get('shortName') or t} ({t}) ---\n"
            f"Sector: {info.get('sector')}\n"
            f"Trailing P/E: {notes.get('trailing_pe')}\n"
            f"Revenue Growth: {notes.get('revenue_growth')}\n"
            f"Market Cap: {notes.get('market_cap')}\n"
        )
    prompt = SUMMARY_PROMPT.format(
        n=len(tickers), tickers=", ".join(tickers), company_blocks="\n".join(blocks)
    )
    response = llm.invoke(prompt)
    return response.content