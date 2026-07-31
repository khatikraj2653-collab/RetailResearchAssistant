"""
Compare feature — reuses the same fetch functions as Stock Research,
runs them across N tickers in parallel, then one LLM node writes
a factual delta summary. No "which is better" verdict.
"""

from typing import TypedDict
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from data.yfinance_client import get_company_info, get_quote

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


class CompareState(TypedDict, total=False):
    tickers: list
    companies: list
    summary: str


def fetch_all(state: CompareState) -> CompareState:
    tickers = state["tickers"]

    def fetch_one(ticker: str) -> dict:
        info = get_company_info(ticker)
        quote = get_quote(ticker)
        return {**info, "lastPrice": quote.get("lastPrice")}

    with ThreadPoolExecutor(max_workers=len(tickers)) as pool:
        companies = list(pool.map(fetch_one, tickers))

    return {"companies": companies}


COMPARE_PROMPT = """You are writing a factual comparison summary for a
retail investor. Use ONLY the data below. Do not declare a winner or make
a recommendation — describe the differences neutrally.

Companies data:
{companies}

Write 2-3 short paragraphs covering:
1. Valuation differences (P/E, P/B)
2. Growth and profitability differences (revenue growth, margins)
3. Any notable difference in analyst sentiment or size (market cap)

If a field is missing/null for a company, omit it rather than noting
its absence."""


def summarize_compare(state: CompareState) -> CompareState:
    prompt = COMPARE_PROMPT.format(companies=state["companies"])
    response = llm.invoke(prompt)
    return {"summary": response.content}


def build_compare_graph():
    graph = StateGraph(CompareState)
    graph.add_node("fetch_all", fetch_all)
    graph.add_node("summarize", summarize_compare)
    graph.set_entry_point("fetch_all")
    graph.add_edge("fetch_all", "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()


compare_graph = build_compare_graph()


def run_compare(tickers: list) -> dict:
    return compare_graph.invoke({"tickers": [t.upper() for t in tickers]})