# Retail Research Assistant

An S&P 500 research platform: an agentic assistant that pulls market data and helps research retail-sector (and broader S&P 500) equities.

**Live app:** https://retailresearch-raj.streamlit.app/

## Stack
- Streamlit (frontend)
- LangGraph + LangChain (OpenAI) — agent orchestration
- yfinance / pandas — market data
- SQLite (`cache.sqlite3`, `history.sqlite3`) — caching and history

## Run locally
```bash
pip install -r requirements.txt
streamlit run frontend/app.py
```
