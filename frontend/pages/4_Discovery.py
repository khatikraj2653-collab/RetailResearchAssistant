import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from universe.themes import THEMES
from data.theme_classifier import (
    get_classification,
    build_classification,
    get_companies_for_theme,
    get_theme_counts,
)
from data.yfinance_client import get_quote, get_company_info, get_peer_companies
from data.company_search import build_search_options, resolve_company_query, COMMON_ALIASES
from style import apply_style

st.set_page_config(page_title="Discovery", page_icon="🔍", layout="wide")
apply_style()

from log_client import log_event
if "visit_logged_discovery" not in st.session_state:
    st.session_state.visit_logged_discovery = True
    log_event("visit", detail="Discovery page")

from nav_bar import render_nav_bar
render_nav_bar(active="Discovery")

st.title("🔍 Discovery")
st.caption("Browse S&P 500 companies grouped by sector/technology theme.")

if "search_options" not in st.session_state:
    st.session_state.search_options = build_search_options()
if "discovery_chat" not in st.session_state:
    st.session_state.discovery_chat = []

classification = get_classification()

if not classification:
    st.warning(
        "No theme classification found yet. Building this takes a few "
        "minutes on first run (classifies all S&P 500 companies), then "
        "it's cached for 30 days."
    )
    if st.button("Build Classification Now", type="primary"):
        progress_bar = st.progress(0, text="Starting classification...")

        def update_progress(current, total):
            progress_bar.progress(
                current / total, text=f"Classifying batch {current}/{total}..."
            )

        classification = build_classification(progress_callback=update_progress)
        st.success("Classification complete!")
        st.rerun()

else:
    if st.button("🔄 Rebuild Classification (manual refresh)"):
        with st.spinner("Rebuilding..."):
            classification = build_classification()
        st.rerun()

    theme_counts = get_theme_counts(classification)

    if "selected_theme" not in st.session_state:
        st.session_state.selected_theme = None

    if st.session_state.selected_theme is None:
        cols = st.columns(3)
        for i, theme in enumerate(THEMES):
            count = theme_counts.get(theme["key"], 0)
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{theme['label']}**")
                    st.caption(theme["description"])

                    tags_html = "".join(
                        f'<span class="theme-pill">{tag}</span>' for tag in theme.get("tags", [])
                    )
                    st.markdown(tags_html, unsafe_allow_html=True)

                    left, right = st.columns([3, 1])
                    with left:
                        st.write(f"{count} companies")
                    with right:
                        if st.button("→", key=f"view_{theme['key']}"):
                            st.session_state.selected_theme = theme["key"]
                            st.session_state.discovery_chat = []
                            st.rerun()
    else:
        theme = next(t for t in THEMES if t["key"] == st.session_state.selected_theme)
        if st.button("← Back to themes"):
            st.session_state.selected_theme = None
            st.rerun()

        st.subheader(theme["label"])
        st.caption(theme["description"])

        companies = get_companies_for_theme(theme["key"], classification)
        if not companies:
            st.info("No companies matched this theme.")
        else:
            cols = st.columns(2)
            for i, c in enumerate(companies):
                quote = get_quote(c["ticker"])
                price = quote.get("lastPrice")
                with cols[i % 2]:
                    with st.container(border=True):
                        pc1, pc2 = st.columns([2, 1])
                        with pc1:
                            st.markdown(f"**{c['name']}**")
                            st.caption(f"{c['ticker']} · {c['sector']}")
                        with pc2:
                            price_text = f"${price:,.2f}" if price else "N/A"
                            st.markdown(
                                f"<div style='text-align:right;font-size:1.3rem;font-weight:700;"
                                f"padding-top:8px;white-space:nowrap;'>{price_text}</div>",
                                unsafe_allow_html=True,
                            )

        st.markdown("---")
        st.markdown("#### Ask about companies in this theme")
        st.caption("Stock market and finance questions only — this assistant won't help with unrelated topics.")

        for msg in st.session_state.discovery_chat:
            safe_content = msg["content"].replace("$", "\\$")
            if msg["role"] == "user":
                st.markdown(f"**You:** {safe_content}")
            else:
                st.markdown(f"**Assistant:** {safe_content}")

        followup_q = st.text_input(
            "e.g. 'Why is NVIDIA considered an AI company?' or 'What does AMD do?'",
            key="discovery_followup_input",
        )
        if st.button("Ask", key="discovery_ask_btn") and followup_q:

            @tool
            def lookup_company(company_name_or_ticker: str) -> str:
                """Look up live data for ANY company by name or ticker --
                business summary, CEO, sector, current price, or peers."""
                options = st.session_state.search_options
                query = company_name_or_ticker.strip().upper()
                match = next((o for o in options if query in o.upper()), None)
                if not match and query not in COMMON_ALIASES:
                    return (
                        f"'{company_name_or_ticker}' isn't in the S&P 500 dataset this app "
                        f"covers, so no data is available for it here."
                    )
                resolved = resolve_company_query(company_name_or_ticker, options)
                info = get_company_info(resolved)
                quote = get_quote(resolved)
                peers = get_peer_companies(resolved)
                return (
                    f"Company: {info.get('shortName') or resolved}\n"
                    f"Ticker: {resolved}\nCEO: {info.get('ceo') or 'Not available'}\n"
                    f"Sector: {info.get('sector') or 'Not available'}\n"
                    f"Business summary: {(info.get('longBusinessSummary') or 'Not available')[:800]}\n"
                    f"Current price: ${quote.get('lastPrice')}\n"
                    f"Same-sector peers: {', '.join(peers) if peers else 'Not available'}"
                )

            chat_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2).bind_tools([lookup_company])

            company_list = ", ".join(f"{c['name']} ({c['ticker']})" for c in companies[:20])
            system_prompt = f"""You are the Retail Research Assistant's
Discovery chat, created by Raj Tejpal Khatik for factual stock market
and finance research -- not predictions or recommendations.

If greeted or asked who you are, briefly introduce yourself first.

Currently browsing theme: {theme['label']} -- {theme['description']}
Companies in this theme (partial list): {company_list}

RULES:
- Answer questions about why a company belongs in this theme, what any
  company does, its business model, CEO, sector, current price, or
  competitors/peers -- for companies in this theme OR any other company,
  same as the rest of this app (not limited only to this theme's list).
- Use the lookup_company tool to get real business-summary/CEO/price
  data for any company mentioned, whether or not it's in this theme.
- NEVER give a buy/sell/hold recommendation or price prediction.
- NEVER say "bullish" or "bearish".
- If asked something unrelated to stocks/companies/finance/markets,
  refuse exactly with: "I can only help with stock market and finance related questions."
- Base answers only on tool results, the data given, or well-known public facts."""

            messages = [SystemMessage(content=system_prompt)]
            for prev in st.session_state.discovery_chat[-6:]:
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
            st.session_state.discovery_chat.append({"role": "user", "content": followup_q})
            st.session_state.discovery_chat.append({"role": "assistant", "content": answer})
            st.rerun()

from data.ticker_tape import render_ticker_tape
render_ticker_tape()