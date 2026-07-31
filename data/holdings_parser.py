"""
Multi-format portfolio input: converts CSV, screenshot, or PDF into the
same structured shape — [{"ticker": "AAPL", "shares": 5.0}, ...] — so
Portfolio Analysis downstream never needs to know or care which format
the holdings came from.

All paths are best-effort extraction. The result is always shown back to
the user in an editable table before analysis runs — never trusted blindly,
since broker screenshots/PDFs vary a lot in layout.
"""

from dotenv import load_dotenv
load_dotenv()

import base64
import io
import json

import pandas as pd
from pypdf import PdfReader
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

EXTRACTION_INSTRUCTIONS = """Extract stock holdings from this content. For
each holding, identify the ticker symbol (or company name if no ticker is
shown — convert well-known companies to their ticker, e.g. "Apple" -> AAPL)
and the number of shares held.

Return ONLY valid JSON (no markdown fences, no explanation), a list of
objects like:
[{"ticker": "AAPL", "shares": 5.0}, {"ticker": "MSFT", "shares": 2.0}]

If you cannot confidently determine shares for a holding, omit it rather
than guessing. If nothing looks like a stock holding, return []."""


def _parse_llm_json_list(text: str) -> list:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`").replace("json", "", 1).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return []


def parse_csv(file_bytes: bytes) -> list:
    """CSV expected to have some form of ticker/symbol column and a
    shares/quantity column — column names are matched flexibly."""
    df = pd.read_csv(io.BytesIO(file_bytes))
    df.columns = [c.strip().lower() for c in df.columns]

    ticker_col = next((c for c in df.columns if c in ("ticker", "symbol", "stock")), None)
    shares_col = next((c for c in df.columns if c in ("shares", "quantity", "qty", "units")), None)

    if not ticker_col or not shares_col:
        return []

    holdings = []
    for _, row in df.iterrows():
        ticker = str(row[ticker_col]).strip().upper()
        try:
            shares = float(row[shares_col])
        except (ValueError, TypeError):
            continue
        if ticker and ticker != "NAN":
            holdings.append({"ticker": ticker, "shares": shares})
    return holdings


def parse_image(image_bytes: bytes, mime_type: str = "image/png") -> list:
    """Broker screenshot -> structured holdings via vision LLM. Layouts
    vary a lot between apps (Trading212, Revolut, etc.), so this is
    best-effort — always confirm results before analyzing."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    message = HumanMessage(
        content=[
            {"type": "text", "text": EXTRACTION_INSTRUCTIONS},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64}"},
            },
        ]
    )
    response = llm.invoke([message])
    return _parse_llm_json_list(response.content)


def parse_pdf(file_bytes: bytes) -> list:
    """Broker statement PDF -> extract text, then LLM-parse into holdings.
    Multi-page statements can mix holdings with disclaimers/fine print,
    so this is best-effort — always confirm results before analyzing."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    text = text[:8000]  # cap length — most holdings tables appear early in a statement

    prompt = f"{EXTRACTION_INSTRUCTIONS}\n\nDocument text:\n{text}"
    response = llm.invoke(prompt)
    return _parse_llm_json_list(response.content)