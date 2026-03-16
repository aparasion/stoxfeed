"""
Fetches market data for a list of ticker symbols from Yahoo Finance
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

TICKERS = [
    # Major ETFs
    "SPY",   # S&P 500
    "QQQ",   # Nasdaq 100
    "DIA",   # Dow Jones
    "IWM",   # Russell 2000
    # Volatility
    "^VIX",  # VIX
    # Sector ETFs
    "XLF",   # Financials
    "XLE",   # Energy
    "XLK",   # Technology
]

OUTPUT_FILE = Path("_data/tickers.json")
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"

# Display names (override Yahoo's sometimes verbose names)
DISPLAY_NAMES = {
    "^VIX": "VIX",
}


def fetch_ticker(symbol: str) -> dict | None:
    """Fetch a single ticker's daily data from Yahoo Finance."""
    url = YAHOO_URL.format(symbol=urllib.request.quote(symbol, safe=""))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        print(f"  WARN: Failed to fetch {symbol}: {e}", file=sys.stderr)
        return None

    try:
        result = data["chart"]["result"][0]
        meta = result["meta"]
        prev_close = meta["chartPreviousClose"]
        current = meta["regularMarketPrice"]
        change_pct = ((current - prev_close) / prev_close) * 100
        display = DISPLAY_NAMES.get(symbol, symbol.upper().replace("^", ""))

        return {
            "symbol": display,
            "price": round(current, 2),
            "change_pct": round(change_pct, 2),
            "prev_close": round(prev_close, 2),
        }
    except (KeyError, IndexError, ZeroDivisionError) as e:
        print(f"  WARN: Bad data for {symbol}: {e}", file=sys.stderr)
        return None


def main():
    print(f"Fetching {len(TICKERS)} tickers...")
    results = []

    for symbol in TICKERS:
        print(f"  {symbol}...", end=" ")
        ticker_data = fetch_ticker(symbol)
        if ticker_data:
            direction = "up" if ticker_data["change_pct"] >= 0 else "down"
            print(f"{direction} {ticker_data['change_pct']:+.2f}%")
            results.append(ticker_data)
        else:
            print("SKIPPED")

    if not results:
        print("ERROR: No tickers fetched. Keeping existing data.", file=sys.stderr)
        sys.exit(1)

    output = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tickers": results,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote {len(results)} tickers to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
