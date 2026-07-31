"""
Company name -> ticker search, built from the existing S&P 500 universe.
Powers a searchable dropdown so Stock Research, Compare, and Portfolio
all accept full company names ("Apple", "Microsoft") as well as raw
tickers, instead of requiring exact tickers only.
"""

from universe.sp500 import get_universe


def build_search_options() -> list:
    universe = get_universe()
    return sorted(f"{r['name']} ({r['ticker']})" for r in universe)


def extract_ticker_from_option(option: str) -> str:
    if "(" in option and option.endswith(")"):
        return option.rsplit("(", 1)[1].rstrip(")").strip()
    return option.strip()


# Common everyday names that don't literally match the official S&P 500
# constituent name (e.g. "Google" -> Alphabet's actual ticker).
COMMON_ALIASES = {
    "GOOGLE": "GOOGL",
    "FACEBOOK": "META",
    "TESLA MOTORS": "TSLA",
    "AMAZON": "AMZN",
}


def resolve_company_query(query: str, options: list) -> str:
    """Resolves a raw ticker or company name to an actual ticker, trying
    (in order): known alias, exact/substring match against the S&P 500
    search index, then falling back to the raw uppercased input."""
    raw = query.strip().upper()
    if raw in COMMON_ALIASES:
        return COMMON_ALIASES[raw]
    match = next((o for o in options if raw in o.upper()), None)
    if match:
        return extract_ticker_from_option(match)
    return raw