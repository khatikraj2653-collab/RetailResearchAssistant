import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from data.learning_content import CHAPTERS, DISCLAIMER, get_chapter, build_full_document
from style import apply_style

st.set_page_config(page_title="Learning", page_icon="📚", layout="wide")
apply_style()

from log_client import log_event
if "visit_logged_learning" not in st.session_state:
    st.session_state.visit_logged_learning = True
    log_event("visit", detail="Learning page")

from nav_bar import render_nav_bar
render_nav_bar(active="Learning")

st.title("📚 Learning")
st.caption("A 5-chapter guide to stock market basics — for education only, not financial advice.")

if "current_chapter" not in st.session_state:
    st.session_state.current_chapter = 1
if "learning_chat" not in st.session_state:
    st.session_state.learning_chat = []

st.info(DISCLAIMER)

# --- Chapter navigation ---
st.markdown("### Chapters")
cols = st.columns(5)
for i, chapter in enumerate(CHAPTERS):
    with cols[i]:
        is_active = st.session_state.current_chapter == chapter["number"]
        if st.button(
            f"{chapter['number']}. {chapter['title'][:22]}{'...' if len(chapter['title']) > 22 else ''}",
            key=f"chapter_btn_{chapter['number']}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state.current_chapter = chapter["number"]
            st.rerun()

st.markdown("---")

# --- Download options ---
dl1, dl2 = st.columns(2)
with dl1:
    current = get_chapter(st.session_state.current_chapter)
    chapter_text = f"# Chapter {current['number']}: {current['title']}\n\n{current['content']}"
    st.download_button(
        label=f"⬇️ Download Chapter {current['number']} (.md)",
        data=chapter_text,
        file_name=f"Chapter_{current['number']}_{current['title'][:30].replace(' ', '_')}.md",
        mime="text/markdown",
    )
with dl2:
    st.download_button(
        label="⬇️ Download All 5 Chapters (.md)",
        data=build_full_document(),
        file_name="Understanding_the_Stock_Market_5_Chapters.md",
        mime="text/markdown",
    )

st.markdown("---")

# --- Current chapter content ---
current = get_chapter(st.session_state.current_chapter)
st.header(f"Chapter {current['number']}: {current['title']}")
st.markdown(current["content"])

# --- Prev/Next navigation ---
nav1, nav2, nav3 = st.columns([1, 3, 1])
with nav1:
    if current["number"] > 1:
        if st.button("← Previous"):
            st.session_state.current_chapter -= 1
            st.rerun()
with nav3:
    if current["number"] < 5:
        if st.button("Next →"):
            st.session_state.current_chapter += 1
            st.rerun()

st.markdown("---")

# --- Restricted chatbot: grounded ONLY in the 5 chapters ---
st.markdown("#### Ask a question about this guide")
st.caption(
    "This assistant only answers questions based on the 5 chapters above — "
    "it does not give investment advice, predictions, or recommendations."
)

for msg in st.session_state.learning_chat:
    safe_content = msg["content"].replace("$", "\\$")
    if msg["role"] == "user":
        st.markdown(f"**You:** {safe_content}")
    else:
        st.markdown(f"**Assistant:** {safe_content}")

followup_q = st.text_input("Ask about anything covered in the 5 chapters", key="learning_followup_input")
if st.button("Ask", key="learning_ask_btn") and followup_q:

    all_chapters_text = "\n\n".join(
        f"--- Chapter {c['number']}: {c['title']} ---\n{c['content']}" for c in CHAPTERS
    )

    chat_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    system_prompt = f"""You are the Retail Research Assistant's Learning
chat, created by Raj Tejpal Khatik. Your ONLY job is to answer questions
using the content of the 5 chapters below -- nothing else.

{all_chapters_text}

RULES:
- Answer ONLY using the content of these 5 chapters. If a question asks
  about something not covered in these chapters -- including questions
  about specific real-time stock prices, specific companies, or general
  stock market questions not addressed in this content -- say exactly:
  "That's outside what these 5 chapters cover. Try the Stock Research or
  Compare pages for live company data, or rephrase your question to be
  about the concepts in this guide."
- NEVER give a buy/sell/hold recommendation, price prediction, or
  personalized financial advice.
- NEVER say "bullish" or "bearish".
- CRITICAL: watch for general, impersonal advice-seeking questions that
  sound educational but are really asking "what should I do" -- e.g.
  "is X always a good idea", "what's the safest way to start investing",
  "should I do X", "is now a good time to Y", "what would you personally
  recommend". Even if the guide discusses the underlying concept (e.g.
  index funds, diversification), you must NOT give a yes/no verdict or
  personal recommendation. Instead: (1) explain factually what the
  relevant chapter says about the concept and its trade-offs, and (2)
  explicitly state that this is not personalized advice and the guide
  does not tell the reader what to personally do. Never collapse this
  into a simple "yes, that's a good idea" answer.
- ALSO watch for a subtler pattern: questions that ask you to EVALUATE a
  specific action or hypothetical rather than just define a concept --
  e.g. "is it smart/wise to do X", "would [author] approve of Y", "what
  should I actually do with my money given all this". Do NOT render a
  verdict on the action itself (e.g. "that would not be a wise decision",
  "he would advise against it"), and do NOT summarize the chapters as a
  numbered personal action plan or roadmap. Instead, describe only what
  principle the relevant chapter states and let the reader draw their
  own conclusion about how it applies -- e.g. "Chapter 5 describes [X] as
  a pattern investors should watch for; the guide does not evaluate
  whether any specific action is smart or unwise for you."
- If asked something with no connection to investing education at all
  (e.g. unrelated code, general trivia), refuse and say exactly:
  "I can only help with questions about this stock market learning guide."
- When answering, mention which chapter(s) the answer comes from, so the
  user can read more there.
- If greeted or asked who you are, briefly introduce yourself as the
  Learning guide's assistant first."""

    messages = [SystemMessage(content=system_prompt)]
    for prev in st.session_state.learning_chat[-6:]:
        if prev["role"] == "user":
            messages.append(HumanMessage(content=prev["content"]))
        else:
            messages.append(AIMessage(content=prev["content"]))
    messages.append(HumanMessage(content=followup_q))

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

    answer = streamed_answer or "I couldn't find a clear answer to that — could you rephrase?"
    st.session_state.learning_chat.append({"role": "user", "content": followup_q})
    st.session_state.learning_chat.append({"role": "assistant", "content": answer})
    st.rerun()

from data.ticker_tape import render_ticker_tape
render_ticker_tape()