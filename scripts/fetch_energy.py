"""
Fetches global energy market data from Yahoo Finance and writes the results
to _data/energy.json for the Energy Intelligence Dashboard.

No API key required — uses the public Yahoo Finance chart endpoint.
Intended to run at build time (e.g. via GitHub Actions cron).

Covers:
  - Crude oil benchmarks: WTI (CL=F), Brent (BZ=F)
  - Natural gas: Henry Hub (NG=F)
  - Oil products: Heating Oil (HO=F), Gasoline RBOB (RB=F)
  - Energy ETFs & equities: XLE, VDE, XOM, CVX, SHEL, BP, EQT, LNG, RRC
  - Renewable energy: NEE, ENPH, TSLA
  - 30-day price history for sparklines (WTI, Brent, NG)
  - Auto-generated market summary & key insight
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUTPUT_FILE = Path("_data/energy.json")

YAHOO_CHART  = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
YAHOO_HIST   = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=35d&interval=1d"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StoxFeedBot/1.0)"}


# ── Commodity definitions ────────────────────────────────────────────────────
COMMODITIES = [
    ("CL=F",  "WTI Crude",        "wti",         "$/bbl",    "oil",       True),
    ("BZ=F",  "Brent Crude",       "brent",       "$/bbl",    "oil",       True),
    ("NG=F",  "Natural Gas",       "henry_hub",   "$/MMBtu",  "gas",       True),
    ("HO=F",  "Heating Oil",       "heating_oil", "$/gal",    "oil",       False),
    ("RB=F",  "Gasoline RBOB",     "gasoline",    "$/gal",    "oil",       False),
]

# ── Equity definitions ───────────────────────────────────────────────────────
EQUITIES = [
    # (yahoo_sym, display_sym, full_name,                  category)
    ("XLE",  "XLE",  "Energy Select Sector ETF",          "etf"),
    ("VDE",  "VDE",  "Vanguard Energy ETF",                "etf"),
    ("XOM",  "XOM",  "ExxonMobil",                         "major"),
    ("CVX",  "CVX",  "Chevron",                            "major"),
    ("SHEL", "SHEL", "Shell plc",                          "major"),
    ("BP",   "BP",   "BP plc",                             "major"),
    ("COP",  "COP",  "ConocoPhillips",                     "major"),
    ("SLB",  "SLB",  "SLB (Schlumberger)",                 "oilfield"),
    ("EQT",  "EQT",  "EQT Corp (Nat. Gas)",                "gas"),
    ("LNG",  "LNG",  "Cheniere Energy (LNG)",              "gas"),
    ("RRC",  "RRC",  "Range Resources",                    "gas"),
    ("NEE",  "NEE",  "NextEra Energy",                     "renewable"),
    ("ENPH", "ENPH", "Enphase Energy",                     "renewable"),
    ("FSLR", "FSLR", "First Solar",                        "renewable"),
    ("TSLA", "TSLA", "Tesla",                              "renewable"),
]


def fetch_json(url: str) -> dict | None:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  WARN: fetch failed {url[:80]}: {e}", file=sys.stderr)
        return None


def parse_quote(data: dict) -> dict | None:
    """Extract current price + change_pct from a chart response."""
    try:
        result = data["chart"]["result"][0]
        meta   = result["meta"]
        prev   = meta["chartPreviousClose"]
        curr   = meta["regularMarketPrice"]
        pct    = ((curr - prev) / prev) * 100
        return {
            "price":      round(curr, 3),
            "prev_close": round(prev, 3),
            "change_pct": round(pct,  2),
        }
    except (KeyError, IndexError, ZeroDivisionError, TypeError):
        return None


def parse_history(data: dict, days: int = 30) -> list[float]:
    """Return up to `days` closing prices from a 35d chart response."""
    try:
        result  = data["chart"]["result"][0]
        closes  = result["indicators"]["quote"][0]["close"]
        # Filter None values, take last `days`
        cleaned = [round(c, 3) for c in closes if c is not None]
        return cleaned[-days:]
    except (KeyError, IndexError, TypeError):
        return []


def fetch_commodity(symbol: str, want_history: bool) -> dict:
    url   = YAHOO_HIST.format(symbol=urllib.parse.quote(symbol, safe="")) if want_history else \
            YAHOO_CHART.format(symbol=urllib.parse.quote(symbol, safe=""))
    data  = fetch_json(url)
    if not data:
        return {}
    quote = parse_quote(data)
    if not quote:
        return {}
    if want_history:
        quote["history"] = parse_history(data)
    return quote


def fetch_equity(symbol: str) -> dict | None:
    url  = YAHOO_CHART.format(symbol=urllib.parse.quote(symbol, safe=""))
    data = fetch_json(url)
    if not data:
        return None
    return parse_quote(data)


# ── Market summary generator ─────────────────────────────────────────────────
def generate_summary(commodities: dict, equities: list) -> str:
    parts = []

    wti   = commodities.get("wti",      {})
    brent = commodities.get("brent",    {})
    ng    = commodities.get("henry_hub",{})
    xle   = next((e for e in equities if e["symbol"] == "XLE"), None)

    if wti.get("price"):
        direction = "gained" if wti["change_pct"] >= 0 else "slipped"
        parts.append(
            f"WTI crude {direction} {abs(wti['change_pct']):.1f}% to ${wti['price']:.2f}/bbl"
        )
    if brent.get("price"):
        parts.append(f"Brent at ${brent['price']:.2f}/bbl ({brent['change_pct']:+.1f}%)")
    if ng.get("price"):
        direction = "rose" if ng["change_pct"] >= 0 else "fell"
        parts.append(
            f"Henry Hub nat-gas {direction} {abs(ng['change_pct']):.1f}% to ${ng['price']:.3f}/MMBtu"
        )
    if xle:
        direction = "outperformed" if xle["change_pct"] >= 0 else "underperformed"
        parts.append(f"Energy sector (XLE) {direction} at {xle['change_pct']:+.2f}%")

    if not parts:
        return "Energy market data is being updated. Please check back shortly."

    return ". ".join(parts) + "."


# ── Signal generator ─────────────────────────────────────────────────────────
def generate_signals(commodities: dict) -> list[dict]:
    signals = []
    wti = commodities.get("wti", {})
    ng  = commodities.get("henry_hub", {})

    if wti.get("price"):
        p = wti["price"]
        if p > 90:
            signals.append({"label": "Oil Spike Alert", "level": "warning",
                            "text": f"WTI above $90 — supply tightening signal"})
        elif p < 60:
            signals.append({"label": "Oil Weakness", "level": "bearish",
                            "text": f"WTI below $60 — demand concerns elevated"})
        else:
            signals.append({"label": "Oil Range-Bound", "level": "neutral",
                            "text": f"WTI in neutral zone $60–$90/bbl"})

    if ng.get("price"):
        p = ng["price"]
        if p > 4:
            signals.append({"label": "Gas Tightening", "level": "bullish",
                            "text": "Henry Hub above $4 — storage drawdown accelerating"})
        elif p < 2:
            signals.append({"label": "Gas Glut", "level": "bearish",
                            "text": "Henry Hub below $2 — oversupply dampening margins"})

    return signals


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    import urllib.parse  # needed inside functions above

    print("── Energy Data Fetch ───────────────────────────────")

    # 1. Commodities
    commodity_data: dict = {}
    for symbol, name, key, unit, sector, want_hist in COMMODITIES:
        print(f"  commodity: {symbol} ...", end=" ", flush=True)
        result = fetch_commodity(symbol, want_hist)
        if result:
            result.update({"symbol": symbol, "name": name, "unit": unit, "sector": sector})
            commodity_data[key] = result
            print(f"${result['price']} ({result['change_pct']:+.2f}%)")
        else:
            print("SKIPPED")

    # 2. Equities
    equity_rows: list = []
    for yahoo_sym, display, name, category in EQUITIES:
        print(f"  equity:    {yahoo_sym} ...", end=" ", flush=True)
        result = fetch_equity(yahoo_sym)
        if result:
            equity_rows.append({
                "symbol":     display,
                "name":       name,
                "category":   category,
                "price":      result["price"],
                "change_pct": result["change_pct"],
                "prev_close": result["prev_close"],
            })
            print(f"${result['price']} ({result['change_pct']:+.2f}%)")
        else:
            print("SKIPPED")

    if not commodity_data and not equity_rows:
        print("ERROR: No data fetched. Keeping existing file.", file=sys.stderr)
        sys.exit(1)

    # 3. Auto-generated insights
    summary = generate_summary(commodity_data, equity_rows)
    signals = generate_signals(commodity_data)

    # 4. Categorised equity views
    etfs       = [e for e in equity_rows if e["category"] == "etf"]
    majors     = [e for e in equity_rows if e["category"] == "major"]
    gas_stocks = [e for e in equity_rows if e["category"] == "gas"]
    renewables = [e for e in equity_rows if e["category"] == "renewable"]
    oilfield   = [e for e in equity_rows if e["category"] == "oilfield"]

    output = {
        "updated_at":    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "market_summary": summary,
        "signals":        signals,
        "commodities":    commodity_data,
        "equities": {
            "etfs":       etfs,
            "majors":     majors,
            "gas":        gas_stocks,
            "renewables": renewables,
            "oilfield":   oilfield,
            "all":        equity_rows,
        },
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2) + "\n")
    print(f"\nWrote energy data → {OUTPUT_FILE}")
    print(f"  {len(commodity_data)} commodities, {len(equity_rows)} equities")


if __name__ == "__main__":
    import urllib.parse
    main()
