"""Generate and send a daily newsletter digest via the Buttondown API.

Collects today's posts and signal status changes, builds an editorial
digest using OpenAI, then sends it through Buttondown.

Usage:
    python scripts/send_newsletter.py                 # last 1 day
    python scripts/send_newsletter.py --days 3        # last 3 days
    python scripts/send_newsletter.py --dry-run        # preview without sending
    python scripts/send_newsletter.py --send           # send immediately
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from openai import OpenAI

POSTS_DIR = Path("_posts")
SIGNALS_DATA_FILE = Path("_data/signals.yml")
SITE_URL = "https://stoxfeed.com"

SYSTEM_PROMPT = """You are the editor of StoxFeed, a stock market and financial markets newsletter. Write a concise, engaging daily digest email.

Format (150–250 words, markdown):
- Open with a 1–2 sentence editorial hook capturing the day's market theme.
- ## Today's Stories — 2–5 bullet points, each with a bold title and 1-sentence summary. Include the post URL as a markdown link.
- ## Signal Watch — Brief note on any signal status changes or notable evidence today. If none, skip this section.
- Close with a single forward-looking sentence.

Style:
• Direct, confident editorial voice — not a dry list.
• No hype, no clichés.
• Each bullet should give the reader a reason to click through.
• Keep it scannable — busy professionals read this on their phone.
"""

USER_PROMPT_TEMPLATE = """Write the daily digest for {period}.

Posts from this period:
{article_summaries}

Signal changes this period:
{signal_updates}
"""


def parse_front_matter(content: str) -> tuple[dict, str]:
    if not content.startswith("---\n"):
        return {}, content
    end = content.find("\n---\n", 4)
    if end == -1:
        return {}, content
    fm_text = content[4:end]
    body = content[end + 5:]
    fm = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip().strip('"')
    return fm, body.strip()


def collect_recent_posts(since: datetime.date) -> list[dict]:
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})-", path.name)
        if not match:
            continue
        post_date = datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        if post_date < since:
            continue

        content = path.read_text(encoding="utf-8")
        fm, body = parse_front_matter(content)

        # Skip monthly summaries
        if "monthly-summary" in fm.get("categories", ""):
            continue

        title = fm.get("title", "").strip()
        if not title:
            continue

        slug = path.stem[11:]  # strip date prefix
        post_url = f"{SITE_URL}/articles/{post_date.strftime('%Y/%m/%d')}/{slug}.html"

        posts.append({
            "title": title,
            "date": post_date.isoformat(),
            "url": post_url,
            "excerpt": fm.get("excerpt", body[:300]),
            "publisher": fm.get("publisher", ""),
            "signal_ids": fm.get("signal_ids", ""),
            "signal_stance": fm.get("signal_stance", ""),
        })
    return posts


def load_signals() -> dict[str, dict]:
    if not SIGNALS_DATA_FILE.exists():
        return {}
    signals = {}
    current = {}
    for line in SIGNALS_DATA_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if current.get("id"):
                signals[current["id"]] = current
            current = {"id": stripped.split(":", 1)[1].strip().strip('"')}
        elif ":" in stripped and current:
            key, val = stripped.split(":", 1)
            current[key.strip()] = val.strip().strip('"')
    if current.get("id"):
        signals[current["id"]] = current
    return signals


def build_signal_summary(posts: list[dict], signals: dict[str, dict]) -> str:
    mentioned = {}
    for post in posts:
        ids_raw = post.get("signal_ids", "")
        if not ids_raw:
            continue
        ids = [s.strip().strip('"').strip("'") for s in ids_raw.strip("[]").split(",") if s.strip()]
        stance = post.get("signal_stance", "mentions")
        for sid in ids:
            mentioned.setdefault(sid, []).append(stance)

    if not mentioned:
        return "No notable signal activity today."

    lines = []
    for sid, stances in sorted(mentioned.items()):
        signal = signals.get(sid, {})
        title = signal.get("title", sid)
        status = signal.get("current_status", "unknown")
        lines.append(f"- {title} (status: {status}) — {len(stances)} post(s): {', '.join(stances)}")
    return "\n".join(lines)


def generate_digest(posts: list[dict], signals: dict[str, dict], period_label: str) -> str:
    article_lines = []
    for i, post in enumerate(posts, 1):
        article_lines.append(
            f"{i}. [{post['title']}]({post['url']})\n"
            f"   Publisher: {post['publisher'] or 'Unknown'}\n"
            f"   Summary: {post['excerpt']}\n"
        )

    signal_summary = build_signal_summary(posts, signals)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        period=period_label,
        article_summaries="\n".join(article_lines) or "No posts this period.",
        signal_updates=signal_summary,
    )

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()


def main():
    parser = argparse.ArgumentParser(description="Generate and send daily newsletter digest.")
    parser.add_argument("--days", type=int, default=1, help="Number of days to look back (default: 1)")
    parser.add_argument("--dry-run", action="store_true", help="Generate digest but don't send")
    parser.add_argument("--send", action="store_true", help="Send immediately instead of creating as draft")
    args = parser.parse_args()

    since = datetime.date.today() - datetime.timedelta(days=args.days)
    today = datetime.date.today()
    if args.days == 1:
        period_label = today.strftime("%B %d, %Y")
    else:
        period_label = f"{since.strftime('%b %d')} – {today.strftime('%b %d, %Y')}"

    print(f"Collecting posts from {since} to {today}...")
    posts = collect_recent_posts(since)
    print(f"Found {len(posts)} posts.")

    if not posts:
        print("No posts found for this period. Skipping newsletter.")
        return

    signals = load_signals()
    print("Generating digest with OpenAI...")
    digest = generate_digest(posts, signals, period_label)

    subject = f"StoxFeed Daily: {today.strftime('%b %d, %Y')}"

    if args.dry_run:
        print("\n--- DRY RUN ---")
        print(f"Subject: {subject}\n")
        print(digest)
        print("--- END DRY RUN ---")
        return

    api_key = os.getenv("BUTTONDOWN_API_KEY")
    if not api_key:
        print("Error: BUTTONDOWN_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    payload_status = "about_to_send" if args.send else "draft"

    payload = json.dumps({
        "subject": subject,
        "body": digest,
        "status": payload_status,
    }).encode("utf-8")

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }
    if args.send:
        headers["X-Buttondown-Live-Dangerously"] = "true"

    req = Request(
        "https://api.buttondown.com/v1/emails",
        data=payload,
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        action = "Sent" if args.send else "Created draft"
        print(f"{action} newsletter: {result.get('id', 'unknown')}")
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        safe_body = error_body[:200] if error_body else "(no body)"
        for secret_key in ("api_key", "token", "authorization", "password", "secret"):
            if secret_key in safe_body.lower():
                safe_body = "(redacted — response contained sensitive fields)"
                break
        print(f"Buttondown API error {e.code}: {safe_body}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
