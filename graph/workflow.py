from langgraph.graph import StateGraph, END

from graph.nodes import ResearchState, fetch_company_data, summarize


def build_research_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("fetch", fetch_company_data)
    graph.add_node("summarize", summarize)
    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()


research_graph = build_research_graph()


def run_research(ticker: str) -> dict:
    return research_graph.invoke({"ticker": ticker.upper()})