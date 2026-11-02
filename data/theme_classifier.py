"""
One-time (periodic) classification of the S&P 500 universe into theme
buckets, based on business summary. Batched to keep LLM calls manageable
(~25-35 calls for 500 companies instead of 500 individual calls).

Result cached to disk for 30 days — business classification is stable,
unlike price/fundamentals which need short TTLs.
"""

from dotenv import load_dotenv
load_dotenv()

import json
import time
from pathlib import Path

from langchain_openai import ChatOpenAI

from universe.sp500 import get_universe
from universe.themes import THEMES
from data.yfinance_client import get_company_info

CLASSIFICATION_CACHE_PATH = Path("theme_classification.json")
CLASSIFICATION_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days
BATCH_SIZE = 15

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

CLASSIFY_PROMPT = """Classify each company below into zero or more of these
themes, based on its business summary. Only assign a theme if the
company's core business genuinely matches — do not force-fit.

Available themes:
{themes}

Companies:
{companies}

Return ONLY valid JSON (no markdown fences), mapping each ticker to a list
of matching theme keys (empty list if none match):
{{"TICKER1": ["theme_key1", "theme_key2"], "TICKER2": []}}"""


def _classify_batch(batch: list) -> dict:
    themes_text = "\n".join(f"- {t['key']}: {t['description']}" for t in THEMES)
    companies_text = "\n".join(
        f"{c['ticker']}: {c['summary'][:300]}" for c in batch if c["summary"]
    )
    if not companies_text:
        return {}

    prompt = CLASSIFY_PROMPT.format(themes=themes_text, companies=companies_text)
    response = llm.invoke(prompt)
    text = response.content.strip()
    if text.startswith("```"):
        text = text.strip("`").replace("json", "", 1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def build_classification(progress_callback=None) -> dict:
    """Runs the full classification pass. Slow (~a few minutes) — call
    explicitly via a UI button, not automatically on every page load."""
    universe = get_universe()
    tickers_with_summaries = []
    for record in universe:
        info = get_company_info(record["ticker"])
        tickers_with_summaries.append(
            {"ticker": record["ticker"], "summary": info.get("longBusinessSummary")}
        )

    classification: dict = {}
    total_batches = (len(tickers_with_summaries) + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(0, len(tickers_with_summaries), BATCH_SIZE):
        batch = tickers_with_summaries[i : i + BATCH_SIZE]
        result = _classify_batch(batch)
        classification.update(result)
        if progress_callback:
            progress_callback((i // BATCH_SIZE) + 1, total_batches)

    CLASSIFICATION_CACHE_PATH.write_text(
        json.dumps({"built_at": time.time(), "classification": classification})
    )
    return classification


def get_classification(force_refresh: bool = False) -> dict:
    if not force_refresh and CLASSIFICATION_CACHE_PATH.exists():
        cached = json.loads(CLASSIFICATION_CACHE_PATH.read_text())
        if time.time() - cached["built_at"] < CLASSIFICATION_TTL_SECONDS:
            return cached["classification"]
    return {}  # empty means "needs building" — caller decides whether to trigger it


def get_companies_for_theme(theme_key: str, classification: dict) -> list:
    universe = {r["ticker"]: r for r in get_universe()}
    tickers = [t for t, themes in classification.items() if theme_key in themes]
    return [universe[t] for t in tickers if t in universe]


def get_theme_counts(classification: dict) -> dict:
    counts: dict = {}
    for themes in classification.values():
        for theme_key in themes:
            counts[theme_key] = counts.get(theme_key, 0) + 1
    return counts