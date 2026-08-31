# Retail Research Assistant

An S&P 500 research platform: an agentic assistant that pulls market data and helps research retail-sector (and broader S&P 500) equities.

**Live app:** https://retailresearch-raj.streamlit.app/

## Demo
![RetailResearchAssistant demo](retailresearch-demo.gif)

## Stack
- Streamlit (frontend)
- LangGraph + LangChain (OpenAI) — agent orchestration
- yfinance / pandas — market data
- SQLite (`cache.sqlite3`, `history.sqlite3`) — caching and history

## Architecture

The app is not one graph but five separate LangGraph workflows in `graph/`, one per feature. `graph/nodes.py` holds shared node implementations used by Stock Research; Deep Compare reuses the compiled Deep Stock Research graph itself as a subgraph rather than duplicating its logic.

```mermaid
flowchart TD
    subgraph SR["Stock Research (graph/workflow.py)"]
        SR_fetch["fetch (fetch_company_data)"] --> SR_summarize["summarize"]
    end

    subgraph CMP["Compare (graph/compare_workflow.py)"]
        CMP_fetch["fetch_all"] --> CMP_summarize["summarize (summarize_compare)"]
    end

    subgraph DR["Deep Stock Research (graph/deep_research_workflow.py)"]
        DR_fetch["fetch (fetch_all_factors)"] --> DR_overview["overview (write_overview)"]
        DR_overview --> DR_notes["notes (write_factor_notes)"]
    end

    subgraph DCMP["Deep Compare (graph/deep_compare_workflow.py)"]
        DCMP_run["run_subgraph_per_ticker"] --> DCMP_summary["write_summary"]
    end

    subgraph PORT["Portfolio Analysis (graph/portfolio_workflow.py)"]
        PORT_fetch["fetch (fetch_holdings_data)"] --> PORT_risk["compute_risk (compute_risk_metrics)"]
        PORT_risk --> PORT_narrate["narrate (narrate_flags)"]
    end

    DCMP_run -. "invokes compiled DR graph once per ticker (research_subgraph)" .-> DR_fetch
    DR_notes -. "returns result to caller" .-> DCMP_run
```

## Run locally
```bash
pip install -r requirements.txt
streamlit run frontend/app.py
```
