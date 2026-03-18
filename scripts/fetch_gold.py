"""
Fetches Gold ETF and precious metals data from Yahoo Finance
and writes the results to _data/gold.json for Jekyll to consume.

No API key required — uses the public Yahoo Finance chart endpoint.
Intended to run at build time (e.g. via GitHub Actions cron).

Fetches:
  - GLD, IAU, GLDM, SGOL, GDX, GDXJ daily prices
  - GC=F (Gold Futures) for spot price and YTD change
  - SI=F (Silver Futures) for Gold/Silver ratio
  - GLD 52-week high/low using 1y range
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ETFs to display with hover descriptions
GOLD_ETFS = [
    ("GLD",  "GLD",  "SPDR Gold Shares",          "Largest gold ETF (~$70B AUM); tracks London gold price fix"),
    ("IAU",  "IAU",  "iShares Gold Trust",         "Physical gold ETF with 0.25% expense ratio; second largest by AUM"),
    ("GLDM", "GLDM", "SPDR Gold MiniShares",       "Lowest-cost large gold ETF at 0.10% expense ratio"),
    ("SGOL", "SGOL", "Aberdeen Physical Gold ETF", "Physical gold stored in Swiss and UK vaults"),
    ("GDX",  "GDX",  "VanEck Gold Miners ETF",     "Tracks large gold mining companies, not physical gold"),
    ("GDXJ", "GDXJ", "VanEck Junior Gold Miners",  "Smaller mining stocks; higher risk/reward than major miners"),
]

OUTPUT_FILE = Path("_data/gold.json")
DAILY_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
YEARLY_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d"
MONTHLY_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1mo&interval=1d"


def fetch_url(url: str) -> dict | None:
    """Fetch JSON from a Yahoo Finance URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        print(f"  WARN: Request failed for {url}: {e}", file=sys.stderr)
        return None


def fetch_daily(yahoo_symbol: str, display: str, name: str, desc: str) -> dict | None:
    """Fetch a single ticker's daily price data."""
    url = DAILY_URL.format(symbol=urllib.request.quote(yahoo_symbol, safe=""))
    data = fetch_url(url)
    if not data:
        return None
    try:
        meta = data["chart"]["result"][0]["meta"]
        prev_close = meta["chartPreviousClose"]
        current = meta["regularMarketPrice"]
        change_pct = ((current - prev_close) / prev_close) * 100
        return {
            "symbol": display,
            "name": name,
            "desc": desc,
            "price": round(current, 2),
            "change_pct": round(change_pct, 2),
            "prev_close": round(prev_close, 2),
        }
    except (KeyError, IndexError, ZeroDivisionError) as e:
        print(f"  WARN: Bad daily data for {yahoo_symbol}: {e}", file=sys.stderr)
        return None


def fetch_history(yahoo_symbol: str, count: int = 30) -> list[float]:
    """Fetch last `count` daily closing prices for a ticker."""
    url = MONTHLY_URL.format(symbol=urllib.request.quote(yahoo_symbol, safe=""))
    data = fetch_url(url)
    if not data:
        return []
    try:
        result = data["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        filtered = [round(c, 2) for c in closes if c is not None]
        return filtered[-count:]
    except (KeyError, IndexError) as e:
        print(f"  WARN: Bad history data for {yahoo_symbol}: {e}", file=sys.stderr)
        return []


def fetch_52w_high_low(yahoo_symbol: str) -> tuple[float | None, float | None]:
    """Fetch 52-week high and low from 1-year daily data."""
    url = YEARLY_URL.format(symbol=urllib.request.quote(yahoo_symbol, safe=""))
    data = fetch_url(url)
    if not data:
        return None, None
    try:
        result = data["chart"]["result"][0]
        quotes = result["indicators"]["quote"][0]
        highs = [h for h in quotes["high"] if h is not None]
        lows = [l for l in quotes["low"] if l is not None]
        if not highs or not lows:
            return None, None
        return round(max(highs), 2), round(min(lows), 2)
    except (KeyError, IndexError) as e:
        print(f"  WARN: Bad 52w data for {yahoo_symbol}: {e}", file=sys.stderr)
        return None, None


def main():
    output = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "spot": None,
        "silver_price": None,
        "gold_silver_ratio": None,
        "gld_52w_high": None,
        "gld_52w_low": None,
        "gld_history": [],
        "etfs": [],
    }

    # --- Fetch ETF prices ---
    print("Fetching Gold ETF prices...")
    for yahoo_sym, display, name, desc in GOLD_ETFS:
        print(f"  {yahoo_sym}...", end=" ")
        result = fetch_daily(yahoo_sym, display, name, desc)
        if result:
            direction = "up" if result["change_pct"] >= 0 else "down"
            print(f"{direction} {result['change_pct']:+.2f}%")
            output["etfs"].append(result)
        else:
            print("SKIPPED")

    # --- Fetch spot gold (GC=F) ---
    print("Fetching spot gold price (GC=F)...")
    gold_data = fetch_daily("GC=F", "GC=F", "Gold Futures", "")
    if gold_data:
        output["spot"] = {
            "price": gold_data["price"],
            "change_pct": gold_data["change_pct"],
        }
        print(f"  Spot gold: ${gold_data['price']} ({gold_data['change_pct']:+.2f}%)")
    else:
        print("  WARN: Could not fetch spot gold", file=sys.stderr)

    # --- Fetch silver (SI=F) for Gold/Silver ratio ---
    print("Fetching silver price (SI=F)...")
    silver_data = fetch_daily("SI=F", "SI=F", "Silver Futures", "")
    if silver_data and gold_data:
        ratio = gold_data["price"] / silver_data["price"]
        output["silver_price"] = silver_data["price"]
        output["gold_silver_ratio"] = round(ratio, 1)
        print(f"  Silver: ${silver_data['price']}, G:S Ratio: {output['gold_silver_ratio']}")
    else:
        print("  WARN: Could not compute Gold/Silver ratio", file=sys.stderr)

    # --- Fetch GLD 30-day price history for sparkline ---
    print("Fetching GLD 30-day history for sparkline...")
    history = fetch_history("GLD")
    if history:
        output["gld_history"] = history
        print(f"  {len(history)} data points")
    else:
        print("  WARN: Could not fetch GLD history", file=sys.stderr)

    # --- Fetch GLD 52-week high/low ---
    print("Fetching GLD 52-week high/low...")
    hi, lo = fetch_52w_high_low("GLD")
    if hi and lo:
        output["gld_52w_high"] = hi
        output["gld_52w_low"] = lo
        print(f"  GLD 52w: High ${hi}, Low ${lo}")
    else:
        print("  WARN: Could not fetch GLD 52w data", file=sys.stderr)

    if not output["etfs"]:
        print("ERROR: No ETF data fetched. Keeping existing data.", file=sys.stderr)
        sys.exit(1)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote gold data ({len(output['etfs'])} ETFs) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
