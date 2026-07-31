import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from graph.portfolio_workflow import run_portfolio_analysis, compute_portfolio_diff
from data.holdings_parser import parse_csv, parse_image, parse_pdf
from data.company_search import build_search_options, extract_ticker_from_option, resolve_company_query, COMMON_ALIASES
from data.yfinance_client import get_company_info, get_quote, get_peer_companies
from data.history_store import save_history, load_history, load_most_recent
from style import apply_style

st.set_page_config(page_title="Portfolio Analysis", page_icon="📈", layout="wide")
apply_style()

from nav_bar import render_nav_bar
render_nav_bar(active="Portfolio")

st.title("📈 Portfolio Analysis")
st.caption("Structural risk analysis only — no price prediction, no buy/sell advice.")

USER_KEY = "default_user"  # single-user app; placeholder for future multi-user support

if "search_options" not in st.session_state:
    st.session_state.search_options = build_search_options()
if "portfolio_chat" not in st.session_state:
    st.session_state.portfolio_chat = []
if "portfolio_result" not in st.session_state:
    st.session_state.portfolio_result = None
if "portfolio_diff" not in st.session_state:
    st.session_state.portfolio_diff = None

if "holding_ids" not in st.session_state:
    st.session_state.holding_ids = [0]
    st.session_state.next_holding_id = 1
    st.session_state["holding_option_0"] = "Apple Inc. (AAPL)"
    st.session_state["holding_shares_0"] = 1.0

# --- Long-term memory: show past saved snapshots ---
past_snapshots = load_history("portfolio", USER_KEY, limit=5)
if past_snapshots:
    with st.expander(f"📜 Past portfolio snapshots ({len(past_snapshots)} saved)"):
        for snap in past_snapshots:
            import datetime
            ts = datetime.datetime.fromtimestamp(snap["timestamp"]).strftime("%Y-%m-%d %H:%M")
            holdings_str = ", ".join(f"{h['ticker']} ({h['shares']} sh)" for h in snap["data"].get("holdings", []))
            st.caption(f"{ts} — {holdings_str}")

st.subheader("Add Holdings")

input_method = st.radio(
    "How would you like to add your holdings?",
    ["Manual entry", "Upload CSV", "Upload screenshot", "Upload PDF statement"],
    horizontal=True,
)


def _load_extracted_holdings(extracted: list):
    st.session_state.holding_ids = list(range(len(extracted)))
    st.session_state.next_holding_id = len(extracted)
    for idx, e in enumerate(extracted):
        match = next((o for o in st.session_state.search_options if e["ticker"] in o), e["ticker"])
        st.session_state[f"holding_option_{idx}"] = match
        st.session_state[f"holding_shares_{idx}"] = e["shares"]


if input_method == "Upload CSV":
    uploaded = st.file_uploader("Upload a CSV with ticker + shares columns", type=["csv"])
    if uploaded and st.button("Extract from CSV"):
        with st.spinner("Reading CSV..."):
            extracted = parse_csv(uploaded.read())
        if extracted:
            _load_extracted_holdings(extracted)
            st.success(f"Extracted {len(extracted)} holdings. Review below before analyzing.")
            st.rerun()
        else:
            st.warning("Couldn't find recognizable ticker/shares columns in this CSV.")

elif input_method == "Upload screenshot":
    uploaded = st.file_uploader("Upload a screenshot of your portfolio", type=["png", "jpg", "jpeg"])
    if uploaded and st.button("Extract from screenshot"):
        with st.spinner("Reading screenshot with AI..."):
            mime = "image/png" if uploaded.type == "image/png" else "image/jpeg"
            extracted = parse_image(uploaded.read(), mime_type=mime)
        if extracted:
            _load_extracted_holdings(extracted)
            st.success(f"Extracted {len(extracted)} holdings. Review below — screenshot extraction can miss or misread things, so double-check before analyzing.")
            st.rerun()
        else:
            st.warning("Couldn't extract any holdings from this screenshot.")

elif input_method == "Upload PDF statement":
    uploaded = st.file_uploader("Upload a broker statement PDF", type=["pdf"])
    if uploaded and st.button("Extract from PDF"):
        with st.spinner("Reading PDF with AI..."):
            extracted = parse_pdf(uploaded.read())
        if extracted:
            _load_extracted_holdings(extracted)
            st.success(f"Extracted {len(extracted)} holdings. Review below — PDF extraction can miss or misread things, so double-check before analyzing.")
            st.rerun()
        else:
            st.warning("Couldn't extract any holdings from this PDF.")

st.subheader("Your Holdings")
st.caption("Search by company name or ticker for each row.")

id_to_remove = None
for hid in st.session_state.holding_ids:
    with st.container(border=True):
        c1, c2, c3 = st.columns([5, 2, 1])
        with c1:
            st.selectbox(
                "Company", ["Type to search..."] + st.session_state.search_options,
                key=f"holding_option_{hid}", label_visibility="collapsed",
            )
        with c2:
            st.number_input(
                "Shares", min_value=0.0,
                key=f"holding_shares_{hid}", label_visibility="collapsed",
            )
        with c3:
            if st.button("✕", key=f"remove_holding_{hid}"):
                id_to_remove = hid

if id_to_remove is not None:
    st.session_state.holding_ids.remove(id_to_remove)
    del st.session_state[f"holding_option_{id_to_remove}"]
    del st.session_state[f"holding_shares_{id_to_remove}"]
    st.rerun()

if st.button("+ Add Holding"):
    new_id = st.session_state.next_holding_id
    st.session_state.holding_ids.append(new_id)
    st.session_state[f"holding_option_{new_id}"] = "Type to search..."
    st.session_state[f"holding_shares_{new_id}"] = 1.0
    st.session_state.next_holding_id += 1
    st.rerun()

st.write("")

if st.button("Analyze Portfolio", type="primary"):
    holdings = []
    for hid in st.session_state.holding_ids:
        option = st.session_state.get(f"holding_option_{hid}", "Type to search...")
        shares = st.session_state.get(f"holding_shares_{hid}", 0.0)
        if option == "Type to search..." or shares <= 0:
            continue
        ticker = extract_ticker_from_option(option)
        holdings.append({"ticker": ticker, "shares": float(shares)})

    if len(holdings) < 1:
        st.warning("Add at least one holding with shares greater than 0.")
    else:
        with st.spinner("Fetching data and computing risk metrics..."):
            try:
                result = run_portfolio_analysis(holdings)
            except Exception as e:
                st.error(f"Couldn't analyze portfolio: {e}")
            else:
                # Long-term memory: diff against the most recent saved
                # snapshot (deterministically, in Python) BEFORE saving
                # the new one, then persist this snapshot for next time.
                previous = load_most_recent("portfolio", USER_KEY)
                diff = None
                if previous:
                    prev_data = previous["data"]
                    diff = compute_portfolio_diff(
                        prev_data.get("result", {}), result,
                        prev_data.get("holdings", []), holdings,
                    )

                save_history("portfolio", USER_KEY, {"holdings": holdings, "result": result})

                st.session_state.portfolio_result = result
                st.session_state.portfolio_holdings = holdings
                st.session_state.portfolio_diff = diff
                st.session_state.portfolio_chat = []

if st.session_state.portfolio_result:
    result = st.session_state.portfolio_result
    holdings = st.session_state.get("portfolio_holdings", [])
    diff = st.session_state.portfolio_diff

    if result.get("skipped_tickers"):
        st.warning(
            f"Couldn't find valid market data for: {', '.join(result['skipped_tickers'])}. "
            "These were excluded from the analysis — check the spelling or ticker."
        )

    st.metric("Total Portfolio Value", f"${result['total_value']:,.2f}")

    st.subheader("Single-Stock Concentration")
    for f in result["stock_flags"]:
        emoji = {"red": "🔴", "yellow": "🟡", "green": "🟢"}[f["level"]]
        st.write(f"{emoji} **{f['ticker']}**: {f['weight']*100:.1f}% of portfolio")

    st.subheader("Sector Concentration")
    for f in result["sector_flags"]:
        emoji = {"red": "🔴", "yellow": "🟡", "green": "🟢"}[f["level"]]
        st.write(f"{emoji} **{f['sector']}**: {f['weight']*100:.1f}% of portfolio")

    st.subheader("Correlation")
    if len(holdings) < 2:
        st.write("⚪ Add 2+ holdings to check for correlation.")
    elif result["correlation_flags"]:
        for f in result["correlation_flags"]:
            st.write(
                f"🔴 **{f['pair'][0]} & {f['pair'][1]}**: correlation {f['correlation']} — these tend to move together"
            )
    else:
        st.write("🟢 No pairs found moving together above the 0.70 correlation threshold.")

    st.subheader("Summary")
    safe_summary = result["summary"].replace("$", "\\$")
    st.markdown(safe_summary)

    if diff and (diff["added"] or diff["removed"] or diff["changed_shares"] or diff["weight_changes"] or diff["sector_changes"]):
        st.subheader("What Changed Since Your Last Analysis")
        st.caption("Purely factual — describes what changed, not whether it was a good or bad move.")
        for t in diff["added"]:
            st.write(f"➕ Added **{t}**")
        for t in diff["removed"]:
            st.write(f"➖ Removed **{t}**")
        for c in diff["changed_shares"]:
            st.write(f"🔄 **{c['ticker']}**: {c['old_shares']} → {c['new_shares']} shares")
        for w in diff["weight_changes"]:
            direction = "increased" if w["delta"] > 0 else "decreased"
            st.write(f"📊 **{w['ticker']}** concentration {direction}: {w['old_weight']*100:.1f}% → {w['new_weight']*100:.1f}%")
        for s in diff["sector_changes"]:
            direction = "increased" if s["delta"] > 0 else "decreased"
            st.write(f"🏷️ **{s['sector']}** exposure {direction}: {s['old_weight']*100:.1f}% → {s['new_weight']*100:.1f}%")

    st.markdown("---")
    st.markdown("#### Ask a follow-up question")
    st.caption("Stock market and finance questions only — this assistant won't help with unrelated topics.")

    for msg in st.session_state.portfolio_chat:
        safe_content = msg["content"].replace("$", "\\$")
        if msg["role"] == "user":
            st.markdown(f"**You:** {safe_content}")
        else:
            st.markdown(f"**Assistant:** {safe_content}")

    followup_q = st.text_input("Ask about your portfolio or the market", key="portfolio_followup_input")
    if st.button("Ask", key="portfolio_ask_btn") and followup_q:

        @tool
        def lookup_company(company_name_or_ticker: str) -> str:
            """Look up live data for ANY company by name or ticker --
            CEO, sector, current price, or same-sector peers."""
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
                f"Current price: ${quote.get('lastPrice')}\n"
                f"Same-sector peers: {', '.join(peers) if peers else 'Not available'}"
            )

        chat_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2).bind_tools([lookup_company])

        holdings_summary = ", ".join(f"{h['ticker']} ({h['shares']} shares)" for h in holdings)
        diff_summary = "No previous portfolio saved to compare against." if not diff else str(diff)
        system_prompt = f"""You are the Retail Research Assistant's
Portfolio chat, created by Raj Tejpal Khatik for factual stock market
and finance research -- not predictions or recommendations.

If greeted or asked who you are, briefly introduce yourself first.

The user's current portfolio holdings: {holdings_summary}
Computed structural risk flags (already calculated deterministically,
not by you): {result['stock_flags']}, {result['sector_flags']}, {result['correlation_flags']}
Summary already written: {result['summary']}

Change since the user's last saved portfolio (already computed
deterministically -- these are facts, not your judgment):
{diff_summary}

RULES:
- Answer questions about this portfolio, any company (CEOs, prices,
  sectors, competitors), the market, investing, finance, or economics.
- If asked what changed since last time, describe ONLY the facts already
  computed above (additions, removals, share changes, concentration/
  sector shifts) -- e.g. "you added X and increased Y's weight from A%
  to B%, and Technology sector exposure rose from C% to D%."
- NEVER characterize a change as good, bad, risky, or smart. NEVER say
  a change was "well diversified" or "concentrated" as praise/criticism
  -- state the number and let the user draw their own conclusion.
- Use the lookup_company tool for CEO/price/sector/competitor questions
  about any company.
- NEVER give a buy/sell/hold recommendation, price prediction, or tell
  the user what to add/remove from their portfolio.
- NEVER say "bullish" or "bearish".
- If asked something unrelated to stocks/companies/finance/markets,
  refuse exactly with: "I can only help with stock market and finance related questions."
- Base answers only on tool results, the data given, or well-known public facts."""

        messages = [SystemMessage(content=system_prompt)]
        for prev in st.session_state.portfolio_chat[-6:]:
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
        st.session_state.portfolio_chat.append({"role": "user", "content": followup_q})
        st.session_state.portfolio_chat.append({"role": "assistant", "content": answer})
        st.rerun()

from data.ticker_tape import render_ticker_tape
render_ticker_tape()