import sys
from pathlib import Path
import datetime

sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from style import apply_style
from data.company_search import build_search_options, extract_ticker_from_option, COMMON_ALIASES
from data.yfinance_client import get_company_info, get_quote, get_peer_companies
from graph.deep_research_workflow import run_deep_research
from data.history_store import save_history, load_history

st.set_page_config(page_title="Stock Research", page_icon="🔎", layout="wide")
apply_style()

from log_client import log_event
if "visit_logged_stock_research" not in st.session_state:
    st.session_state.visit_logged_stock_research = True
    log_event("visit", detail="Stock Research page")

from nav_bar import render_nav_bar
render_nav_bar(active="Stock Research")

st.title("🔎 Stock Research")
st.caption("Factual company research — no predictions, no bullish/bearish calls.")

if "search_options" not in st.session_state:
    st.session_state.search_options = build_search_options()
if "research_result" not in st.session_state:
    st.session_state.research_result = None
if "research_ticker" not in st.session_state:
    st.session_state.research_ticker = None
if "research_chat" not in st.session_state:
    st.session_state.research_chat = []

past_sessions = load_history("stock_research", None, limit=15)
if past_sessions:
    with st.expander(f"📜 Past research sessions ({len(past_sessions)} saved)"):
        for s in past_sessions:
            ts = datetime.datetime.fromtimestamp(s["timestamp"]).strftime("%Y-%m-%d %H:%M")
            st.caption(f"{ts} — {s['key_label']}")

selected = st.selectbox(
    "Search by company name or ticker",
    options=["Type to search..."] + st.session_state.search_options,
)

if st.button("Research", type="primary") and selected != "Type to search...":
    ticker = extract_ticker_from_option(selected)
    with st.spinner(f"Pulling factor data for {ticker}..."):
        try:
            result = run_deep_research(ticker)
        except Exception as e:
            st.error(f"Couldn't fetch data for {ticker}: {e}")
        else:
            save_history("stock_research", ticker, {"result": result})
            st.session_state.research_result = result
            st.session_state.research_ticker = ticker
            st.session_state.research_chat = []

if st.session_state.research_result:
    result = st.session_state.research_result
    ticker = st.session_state.research_ticker
    info = result["info"]
    quote = result["quote"]
    notes = result.get("factor_notes", {})

    st.subheader(f"{info.get('shortName') or ticker}  ({ticker})")
    st.markdown(result.get("overview", ""))

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Last Price", f"${quote.get('lastPrice', 0):.2f}" if quote.get("lastPrice") else "N/A")
    with m2:
        st.metric("Market Cap", f"${info.get('marketCap'):,}" if info.get("marketCap") else "N/A")
    with m3:
        st.metric("Trailing P/E", info.get("trailingPE") or "N/A")
    with m4:
        st.metric("Sector", info.get("sector") or "N/A")

    def factor_card(label, key):
        note = notes.get(key, "Not available.")
        with st.container(border=True):
            st.markdown(f"**{label}**")
            st.caption(note)

    st.markdown("#### Macroeconomic")
    c1, c2, c3, c4 = st.columns(4)
    with c1: factor_card("CPI", "cpi")
    with c2: factor_card("PPI", "ppi")
    with c3: factor_card("Fed Funds Rate", "fed_rate")
    with c4: factor_card("USD Index", "usd_index")

    st.markdown("#### Fundamental")
    c1, c2, c3, c4 = st.columns(4)
    with c1: factor_card("Trailing P/E", "trailing_pe")
    with c2: factor_card("Forward P/E", "forward_pe")
    with c3: factor_card("Market Cap", "market_cap")
    with c4: factor_card("Revenue Growth", "revenue_growth")
    c5, c6, c7, c8 = st.columns(4)
    with c5: factor_card("Earnings Growth", "earnings_growth")
    with c6: factor_card("Profit Margin", "profit_margin")
    with c7: factor_card("Dividend Yield", "dividend_yield")
    with c8: factor_card("Beta", "beta")
    factor_card("Insider Activity", "insider_activity")

    st.markdown("#### Market Intelligence")
    c1, c2, c3 = st.columns(3)
    with c1: factor_card("Analyst Recommendation", "analyst_recommendation")
    with c2: factor_card("Analyst Target Price", "analyst_target_price")
    with c3: factor_card("Technical Signal (50d/200d MA)", "technical_signal")

    with st.expander("Recent headlines"):
        for n in result["news"]:
            st.markdown(f"- [{n['title']}]({n['link']}) — *{n['publisher']}*")

    st.markdown("---")
    st.markdown("#### Ask a follow-up question")
    st.caption("Stock market and finance questions only — this assistant won't help with unrelated topics.")

    for msg in st.session_state.research_chat:
        safe_content = msg["content"].replace("$", "\\$")
        if msg["role"] == "user":
            st.markdown(f"**You:** {safe_content}")
        else:
            st.markdown(f"**Assistant:** {safe_content}")

    followup_q = st.text_input("Ask about this stock or the market", key="research_followup_input")
    if st.button("Ask", key="research_ask_btn") and followup_q:

        @tool
        def lookup_company(company_name_or_ticker: str) -> str:
            """Look up live data for ANY company by name or ticker -- use
            this whenever the user asks about a company's CEO, sector,
            current stock price, or competitors, including companies
            other than the one currently loaded on this page."""
            query = company_name_or_ticker.strip().upper()
            options = st.session_state.get("search_options") or build_search_options()
            match = next((o for o in options if query in o.upper()), None)
            if not match and query not in COMMON_ALIASES:
                return (
                    f"'{company_name_or_ticker}' isn't in the S&P 500 dataset this app "
                    f"covers, so no data is available for it here."
                )
            resolved_ticker = extract_ticker_from_option(match) if match else COMMON_ALIASES.get(query, query)
            info_r = get_company_info(resolved_ticker)
            quote_r = get_quote(resolved_ticker)
            peers = get_peer_companies(resolved_ticker)
            return (
                f"Company: {info_r.get('shortName') or resolved_ticker}\n"
                f"Ticker: {resolved_ticker}\n"
                f"CEO: {info_r.get('ceo') or 'Not available'}\n"
                f"Sector: {info_r.get('sector') or 'Not available'}\n"
                f"Current price: ${quote_r.get('lastPrice')}\n"
                f"Same-sector peers (used as a proxy for competitors): {', '.join(peers) if peers else 'Not available'}"
            )

        chat_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2).bind_tools([lookup_company])

        prior_sessions_for_ticker = load_history("stock_research", ticker, limit=5)
        prior_summary = [
            {"when": datetime.datetime.fromtimestamp(s["timestamp"]).strftime("%Y-%m-%d %H:%M")}
            for s in prior_sessions_for_ticker
        ]

        system_prompt = f"""You are the Retail Research Assistant's Stock
Research chat, created by Raj Tejpal Khatik for factual stock market and
finance research -- not predictions or recommendations.

If the user greets you or asks who you are, briefly introduce yourself
along those lines before answering anything else.

Currently loaded ticker: {ticker}
Data you already have for {ticker}:
{notes}
Overview: {result.get('overview', '')}

Past research session timestamps on record for {ticker} (if asked how
many times this has been checked, or when): {prior_summary}

RULES:
- Answer questions about stocks, companies (including CEOs, sectors,
  current prices, and competitors/peers for ANY company, not just
  {ticker}), the stock market, investing, finance, or economics.
- Use the lookup_company tool whenever asked about a company's CEO,
  current price, sector, or competitors -- for {ticker} or any other
  company -- rather than saying you don't have the data.
- NEVER give a buy/sell/hold recommendation or a price prediction.
- NEVER say "bullish" or "bearish".
- If asked to do something with no connection to stocks/companies/finance/markets
  (e.g. writing unrelated code, general trivia, personal advice), refuse
  and say exactly: "I can only help with stock market and finance related questions."
- Base answers only on tool results, the data given, or well-known public
  facts; do not fabricate numbers."""

        messages = [SystemMessage(content=system_prompt)]
        for prev in st.session_state.research_chat[-6:]:
            if prev["role"] == "user":
                messages.append(HumanMessage(content=prev["content"]))
            else:
                messages.append(AIMessage(content=prev["content"]))
        messages.append(HumanMessage(content=followup_q))

        ai_msg = chat_llm.invoke(messages)
        rounds = 0
        while ai_msg.tool_calls and rounds < 3:
            messages.append(ai_msg)
            for call in ai_msg.tool_calls:
                try:
                    tool_result = lookup_company.invoke(call["args"])
                except Exception as e:
                    tool_result = f"Lookup failed: {e}"
                messages.append(ToolMessage(content=tool_result, tool_call_id=call["id"]))
            ai_msg = chat_llm.invoke(messages)
            rounds += 1

        stream_placeholder = st.empty()
        streamed_answer = ""
        try:
            for chunk in chat_llm.stream(messages):
                if chunk.content:
                    streamed_answer += chunk.content
                    safe_partial = streamed_answer.replace("$", "\\$")
                    stream_placeholder.markdown(f"**Assistant:** {safe_partial}")
        except Exception:
            streamed_answer = ""

        answer = streamed_answer or ai_msg.content or "I couldn't find a clear answer to that — could you rephrase the question?"
        st.session_state.research_chat.append({"role": "user", "content": followup_q})
        st.session_state.research_chat.append({"role": "assistant", "content": answer})
        st.rerun()

from data.ticker_tape import render_ticker_tape
render_ticker_tape()