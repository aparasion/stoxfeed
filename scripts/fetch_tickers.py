"""
Fetches market data for ticker symbols from Yahoo Finance
and writes the results to _data/tickers.json for Jekyll to consume.

No API key required — uses the public Yahoo Finance chart endpoint.
Intended to run at build time (e.g. via GitHub Actions cron).
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# Each group becomes a separate widget in the sidebar.
# Format: (group_label, [(yahoo_symbol, display_symbol, full_name), ...])
TICKER_GROUPS = [
    ("Market Pulse", [
        ("SPY",  "SPY", "SPDR S&P 500 ETF"),
        ("QQQ",  "QQQ", "Invesco Nasdaq 100 ETF"),
        ("DIA",  "DIA", "SPDR Dow Jones ETF"),
        ("IWM",  "IWM", "iShares Russell 2000 ETF"),
        ("^VIX", "VIX", "CBOE Volatility Index"),
        ("XLF",  "XLF", "Financial Select Sector ETF"),
        ("XLE",  "XLE", "Energy Select Sector ETF"),
        ("XLK",  "XLK", "Technology Select Sector ETF"),
    ]),
    ("Big Tech", [
        ("AAPL",  "AAPL",  "Apple"),
        ("MSFT",  "MSFT",  "Microsoft"),
        ("GOOGL", "GOOGL", "Alphabet"),
        ("AMZN",  "AMZN",  "Amazon"),
        ("META",  "META",  "Meta"),
        ("NVDA",  "NVDA",  "NVIDIA"),
        ("TSLA",  "TSLA",  "Tesla"),
    ]),
]

OUTPUT_FILE = Path("_data/tickers.json")
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"


def fetch_ticker(yahoo_symbol: str, display: str, name: str) -> dict | None:
    """Fetch a single ticker's daily data from Yahoo Finance."""
    url = YAHOO_URL.format(symbol=urllib.request.quote(yahoo_symbol, safe=""))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        print(f"  WARN: Failed to fetch {yahoo_symbol}: {e}", file=sys.stderr)
        return None

    try:
        result = data["chart"]["result"][0]
        meta = result["meta"]
        prev_close = meta["chartPreviousClose"]
        current = meta["regularMarketPrice"]
        change_pct = ((current - prev_close) / prev_close) * 100

        return {
            "symbol": display,
            "name": name,
            "price": round(current, 2),
            "change_pct": round(change_pct, 2),
            "prev_close": round(prev_close, 2),
        }
    except (KeyError, IndexError, ZeroDivisionError) as e:
        print(f"  WARN: Bad data for {yahoo_symbol}: {e}", file=sys.stderr)
        return None


def main():
    groups = []

    for label, symbols in TICKER_GROUPS:
        print(f"Group: {label} ({len(symbols)} tickers)")
        results = []
        for yahoo_sym, display, name in symbols:
            print(f"  {yahoo_sym}...", end=" ")
            ticker_data = fetch_ticker(yahoo_sym, display, name)
            if ticker_data:
                direction = "up" if ticker_data["change_pct"] >= 0 else "down"
                print(f"{direction} {ticker_data['change_pct']:+.2f}%")
                results.append(ticker_data)
            else:
                print("SKIPPED")

        if results:
            groups.append({"label": label, "tickers": results})

    if not groups:
        print("ERROR: No tickers fetched. Keeping existing data.", file=sys.stderr)
        sys.exit(1)

    output = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "groups": groups,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2) + "\n")
    total = sum(len(g["tickers"]) for g in groups)
    print(f"Wrote {total} tickers in {len(groups)} groups to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
