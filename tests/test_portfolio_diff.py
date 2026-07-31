"""
Regression tests for graph.portfolio_workflow.compute_portfolio_diff.
Uses synthetic (fake) analysis results instead of real API calls, so
these run instantly and don't depend on network access or API keys.
Run with: python tests/test_portfolio_diff.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from graph.portfolio_workflow import compute_portfolio_diff


def fake_result(stock_flags, sector_flags):
    return {"stock_flags": stock_flags, "sector_flags": sector_flags}


def test_partial_trim():
    old_holdings = [{"ticker": "AAPL", "shares": 10.0}]
    new_holdings = [{"ticker": "AAPL", "shares": 7.0}]
    old_result = fake_result(
        [{"ticker": "AAPL", "weight": 1.0, "level": "red"}],
        [{"sector": "Technology", "weight": 1.0, "level": "red"}],
    )
    new_result = fake_result(
        [{"ticker": "AAPL", "weight": 1.0, "level": "red"}],
        [{"sector": "Technology", "weight": 1.0, "level": "red"}],
    )
    diff = compute_portfolio_diff(old_result, new_result, old_holdings, new_holdings)
    assert diff["added"] == []
    assert diff["removed"] == []
    assert diff["changed_shares"] == [{"ticker": "AAPL", "old_shares": 10.0, "new_shares": 7.0}]
    print("test_partial_trim: PASS")


def test_multi_holding_rebalance():
    old_holdings = [
        {"ticker": "AAPL", "shares": 10.0}, {"ticker": "MSFT", "shares": 5.0},
        {"ticker": "NVDA", "shares": 8.0}, {"ticker": "GOOGL", "shares": 6.0},
        {"ticker": "TSLA", "shares": 4.0},
    ]
    new_holdings = [
        {"ticker": "AAPL", "shares": 15.0}, {"ticker": "NVDA", "shares": 4.0},
        {"ticker": "GOOGL", "shares": 6.0}, {"ticker": "AMZN", "shares": 7.0},
        {"ticker": "META", "shares": 3.0},
    ]
    old_result = fake_result(
        [
            {"ticker": "AAPL", "weight": 0.29, "level": "yellow"},
            {"ticker": "MSFT", "weight": 0.15, "level": "green"},
            {"ticker": "NVDA", "weight": 0.16, "level": "yellow"},
            {"ticker": "GOOGL", "weight": 0.21, "level": "yellow"},
            {"ticker": "TSLA", "weight": 0.19, "level": "yellow"},
        ],
        [{"sector": "Technology", "weight": 0.67, "level": "red"}],
    )
    new_result = fake_result(
        [
            {"ticker": "AAPL", "weight": 0.41, "level": "red"},
            {"ticker": "NVDA", "weight": 0.07, "level": "green"},
            {"ticker": "GOOGL", "weight": 0.19, "level": "yellow"},
            {"ticker": "AMZN", "weight": 0.17, "level": "yellow"},
            {"ticker": "META", "weight": 0.16, "level": "yellow"},
        ],
        [{"sector": "Technology", "weight": 0.49, "level": "yellow"}],
    )
    diff = compute_portfolio_diff(old_result, new_result, old_holdings, new_holdings)
    assert set(diff["added"]) == {"AMZN", "META"}
    assert set(diff["removed"]) == {"MSFT", "TSLA"}
    changed_tickers = {c["ticker"] for c in diff["changed_shares"]}
    assert changed_tickers == {"AAPL", "NVDA"}
    assert "GOOGL" not in changed_tickers, "GOOGL shares didn't change -- should not appear here"
    assert len(diff["weight_changes"]) >= 1, "Expected at least one weight shift"
    assert len(diff["sector_changes"]) >= 1, "Expected at least one sector shift"
    print("test_multi_holding_rebalance: PASS")


def test_no_change():
    holdings = [{"ticker": "AAPL", "shares": 10.0}, {"ticker": "MSFT", "shares": 5.0}]
    result = fake_result(
        [
            {"ticker": "AAPL", "weight": 0.6, "level": "yellow"},
            {"ticker": "MSFT", "weight": 0.4, "level": "green"},
        ],
        [{"sector": "Technology", "weight": 1.0, "level": "red"}],
    )
    diff = compute_portfolio_diff(result, result, holdings, holdings)
    has_any_change = (
        diff["added"] or diff["removed"] or diff["changed_shares"]
        or diff["weight_changes"] or diff["sector_changes"]
    )
    assert not has_any_change, "Identical before/after should produce zero detected changes"
    print("test_no_change: PASS")


def test_new_user_returns_none():
    from data.history_store import load_most_recent
    result = load_most_recent("portfolio", "definitely_never_used_test_key_xyz")
    assert result is None, "A user_key with no saved history should return None"
    print("test_new_user_returns_none: PASS")


if __name__ == "__main__":
    test_partial_trim()
    test_multi_holding_rebalance()
    test_no_change()
    test_new_user_returns_none()
    print("\nAll portfolio diff tests passed.")