"""
LangGraph nodes for Stock Research (first feature — vertical slice).
"""

from typing import TypedDict
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

from data.yfinance_client import get_company_info, get_quote, get_recent_news

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


class ResearchState(TypedDict, total=False):
    ticker: str
    info: dict
    quote: dict
    news: list
    summary: str


def fetch_company_data(state: ResearchState) -> ResearchState:
    ticker = state["ticker"]
    with ThreadPoolExecutor(max_workers=3) as pool:
        info_f = pool.submit(get_company_info, ticker)
        quote_f = pool.submit(get_quote, ticker)
        news_f = pool.submit(get_recent_news, ticker)
        info, quote, news = info_f.result(), quote_f.result(), news_f.result()
    return {"info": info, "quote": quote, "news": news}


SUMMARY_PROMPT = """You are writing a factual, plain-English company research
profile for a retail investor. Use ONLY the data provided below. Do not
predict future price movement, do not give a buy/sell/hold recommendation,
and do not invent numbers that aren't present.

Company data:
{info}

Latest quote:
{quote}

Recent headlines:
{news}

Write 3 short sections:
1. Company overview (business, sector, CEO if known)
2. Valuation & financial snapshot (P/E, margins, growth, analyst target if present)
3. What's in the news right now (neutral summary of headlines, no spin)

Keep it concise. If a field is missing/null, simply omit it rather than
noting its absence."""


def summarize(state: ResearchState) -> ResearchState:
    prompt = SUMMARY_PROMPT.format(
        info=state["info"], quote=state["quote"], news=state["news"]
    )
    response = llm.invoke(prompt)
    return {"summary": response.content}