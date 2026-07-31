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
from graph.deep_compare_workflow import run_deep_compare, summarize_compare
from data.history_store import save_history, load_history

st.set_page_config(page_title="Compare", page_icon="⚖️", layout="wide")
apply_style()

from nav_bar import render_nav_bar
render_nav_bar(active="Compare")

st.title("⚖️ Compare Stocks")
st.caption("Factual side-by-side comparison — no predictions, no bullish/bearish calls.")

if "search_options" not in st.session_state:
    st.session_state.search_options = build_search_options()
if "compare_count" not in st.session_state:
    st.session_state.compare_count = None
if "compare_results" not in st.session_state:
    st.session_state.compare_results = None
if "compare_summary" not in st.session_state:
    st.session_state.compare_summary = None
if "compare_chat" not in st.session_state:
    st.session_state.compare_chat = []

past_sessions = load_history("compare", None, limit=15)
if past_sessions:
    with st.expander(f"📜 Past comparison sessions ({len(past_sessions)} saved)"):
        for s in past_sessions:
            ts = datetime.datetime.fromtimestamp(s["timestamp"]).strftime("%Y-%m-%d %H:%M")
            st.caption(f"{ts} — {s['key_label']}")

st.markdown("**How many tickers do you want to compare?**")
count_cols = st.columns(5)
for i, col in enumerate(count_cols):
    with col:
        if st.button(str(i + 1), key=f"count_btn_{i+1}", use_container_width=True,
                     type="primary" if st.session_state.compare_count == (i + 1) else "secondary"):
            st.session_state.compare_count = i + 1
            st.rerun()

if st.session_state.compare_count:
    selections = []
    for i in range(st.session_state.compare_count):
        sel = st.selectbox(
            f"Ticker {i + 1}",
            options=["Type to search..."] + st.session_state.search_options,
            key=f"compare_ticker_{i}",
        )
        selections.append(sel)

    if st.button("Compare →", type="primary"):
        chosen = [s for s in selections if s != "Type to search..."]
        tickers = list(dict.fromkeys(extract_ticker_from_option(s) for s in chosen))
        if len(tickers) < 1:
            st.warning("Select at least one ticker.")
        else:
            with st.spinner(f"Analyzing {', '.join(tickers)}..."):
                st.session_state.compare_results = run_deep_compare(tickers)
                st.session_state.compare_summary = summarize_compare(st.session_state.compare_results)
                st.session_state.compare_chat = []
                save_history("compare", ",".join(tickers), {
                    "tickers": tickers, "summary": st.session_state.compare_summary,
                })

if st.session_state.compare_results:
    results = st.session_state.compare_results
    tickers = list(results.keys())

    def factor_card(label, note):
        with st.container(border=True):
            st.markdown(f"**{label}**")
            st.caption(note or "Not available.")

    cols = st.columns(len(tickers))
    for col, t in zip(cols, tickers):
        with col:
            r = results[t]
            if "error" in r:
                st.error(f"{t}: {r['error']}")
                continue
            info = r["info"]
            quote = r["quote"]
            notes = r.get("factor_notes", {})

            st.markdown(f"### {info.get('shortName') or t}")
            st.caption(t)
            st.metric("Last Price", f"${quote.get('lastPrice', 0):.2f}" if quote.get("lastPrice") else "N/A")
            st.write(f"**Market Cap:** {info.get('marketCap') or 'N/A'}")
            st.write(f"**Sector:** {info.get('sector') or 'N/A'}")

            st.markdown("**Macroeconomic**")
            factor_card("CPI", notes.get("cpi"))
            factor_card("PPI", notes.get("ppi"))
            factor_card("Fed Funds Rate", notes.get("fed_rate"))
            factor_card("USD Index", notes.get("usd_index"))

            st.markdown("**Fundamental**")
            factor_card("Trailing P/E", notes.get("trailing_pe"))
            factor_card("Forward P/E", notes.get("forward_pe"))
            factor_card("Revenue Growth", notes.get("revenue_growth"))
            factor_card("Earnings Growth", notes.get("earnings_growth"))
            factor_card("Profit Margin", notes.get("profit_margin"))
            factor_card("Dividend Yield", notes.get("dividend_yield"))
            factor_card("Beta", notes.get("beta"))
            factor_card("Insider Activity", notes.get("insider_activity"))

            st.markdown("**Market Intelligence**")
            factor_card("Analyst Recommendation", notes.get("analyst_recommendation"))
            factor_card("Analyst Target Price", notes.get("analyst_target_price"))
            factor_card("Technical Signal", notes.get("technical_signal"))

    st.markdown("---")
    st.markdown("### Comparison Summary")
    safe_summary = st.session_state.compare_summary.replace("$", "\\$")
    st.markdown(safe_summary)

    st.markdown("---")
    st.markdown("#### Ask a follow-up question")
    st.caption("Stock market and finance questions only — this assistant won't help with unrelated topics.")

    for msg in st.session_state.compare_chat:
        safe_content = msg["content"].replace("$", "\\$")
        if msg["role"] == "user":
            st.markdown(f"**You:** {safe_content}")
        else:
            st.markdown(f"**Assistant:** {safe_content}")

    followup_q = st.text_input("Ask about these stocks or the market", key="compare_followup_input")
    if st.button("Ask", key="compare_ask_btn") and followup_q:

        @tool
        def lookup_company(company_name_or_ticker: str) -> str:
            """Look up live data for ANY company by name or ticker --
            CEO, sector, current price, or same-sector peers."""
            query = company_name_or_ticker.strip().upper()
            options = st.session_state.get("search_options") or build_search_options()
            match = next((o for o in options if query in o.upper()), None)
            if not match and query not in COMMON_ALIASES:
                return (
                    f"'{company_name_or_ticker}' isn't in the S&P 500 dataset this app "
                    f"covers, so no data is available for it here."
                )
            resolved = extract_ticker_from_option(match) if match else COMMON_ALIASES.get(query, query)
            info = get_company_info(resolved)
            quote = get_quote(resolved)
            peers = get_peer_companies(resolved)
            return (
                f"Company: {info.get('shortName') or resolved}\n"
                f"Ticker: {resolved}\nCEO: {info.get('ceo') or 'Not available'}\n"
                f"Sector: {info.get('sector') or 'Not available'}\n"
                f"Current price: ${quote.get('lastPrice')}\n"
                f"Same-sector peers: {', '.join(peers) if peers else 'Not available'}"
            )

        chat_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2).bind_tools([lookup_company])

        compare_context = "\n".join(
            f"{t}: sector={results[t].get('info', {}).get('sector')}, "
            f"P/E={results[t].get('factor_notes', {}).get('trailing_pe')}"
            for t in tickers if "error" not in results[t]
        )

        past_compare_sessions = load_history("compare", None, limit=10)
        past_summary = [
            {"when": datetime.datetime.fromtimestamp(s["timestamp"]).strftime("%Y-%m-%d %H:%M"), "tickers": s["key_label"]}
            for s in past_compare_sessions
        ]

        system_prompt = f"""You are the Retail Research Assistant's
Compare chat, created by Raj Tejpal Khatik for factual stock market and
finance research -- not predictions or recommendations.

If greeted or asked who you are, briefly introduce yourself first.

Currently compared tickers: {', '.join(tickers)}
Summary data:
{compare_context}
Comparison summary already written: {st.session_state.compare_summary}

Past comparison sessions on record (if asked about comparison history):
{past_summary}

RULES:
- Answer questions about these stocks, any other company (CEOs, prices,
  sectors, competitors), the market, investing, finance, or economics.
- Use the lookup_company tool for CEO/price/sector/competitor questions
  about any company, including ones not currently compared.
- NEVER give a buy/sell/hold recommendation or price prediction.
- NEVER say "bullish" or "bearish".
- If asked something unrelated to stocks/companies/finance/markets,
  refuse exactly with: "I can only help with stock market and finance related questions."
- Base answers only on tool results, the data given, or well-known public facts."""

        messages = [SystemMessage(content=system_prompt)]
        for prev in st.session_state.compare_chat[-6:]:
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

        answer = streamed_answer or ai_msg.content or "I couldn't find a clear answer to that — could you rephrase?"
        st.session_state.compare_chat.append({"role": "user", "content": followup_q})
        st.session_state.compare_chat.append({"role": "assistant", "content": answer})
        st.rerun()

from data.ticker_tape import render_ticker_tape
render_ticker_tape()