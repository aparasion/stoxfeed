"""Send the daily brief post as a newsletter via the Buttondown API.

Reads the daily brief for a given date from _posts/ and sends its
content verbatim — the newsletter is exactly what is published on the
website.

Usage:
    python scripts/send_newsletter.py                  # today's brief
    python scripts/send_newsletter.py --date 2026-03-19
    python scripts/send_newsletter.py --dry-run        # preview only
    python scripts/send_newsletter.py --send           # send immediately
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

POSTS_DIR = Path("_posts")
SITE_URL = "https://stoxfeed.com"


def parse_front_matter(content: str) -> tuple[dict, str]:
    if not content.startswith("---\n"):
        return {}, content
    end = content.find("\n---\n", 4)
    if end == -1:
        return {}, content
    fm = {}
    for line in content[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip().strip('"')
    return fm, content[end + 5:].strip()


def find_daily_brief(date: datetime.date) -> Path | None:
    for path in POSTS_DIR.glob(f"{date.strftime('%Y-%m-%d')}-daily-brief-*.md"):
        return path
    return None


def main():
    parser = argparse.ArgumentParser(description="Send daily brief as newsletter.")
    parser.add_argument("--date", help="Date of the brief to send (YYYY-MM-DD, default: today)")
    parser.add_argument("--dry-run", action="store_true", help="Print without sending")
    parser.add_argument("--send", action="store_true", help="Send immediately (default: create as draft)")
    args = parser.parse_args()

    target_date = datetime.date.fromisoformat(args.date) if args.date else datetime.date.today()

    brief_path = find_daily_brief(target_date)
    if not brief_path:
        print(f"No daily brief found for {target_date}. Skipping newsletter.")
        return

    print(f"Using brief: {brief_path}")
    fm, body = parse_front_matter(brief_path.read_text(encoding="utf-8"))

    subject = fm.get("title", f"Daily Brief: {target_date.strftime('%B %d, %Y')}").strip().strip('"')

    post_slug = brief_path.stem[11:]  # strip YYYY-MM-DD- prefix
    post_url = f"{SITE_URL}/articles/{target_date.strftime('%Y/%m/%d')}/{post_slug}.html"
    full_body = f"{body}\n\n---\n[Read on StoxFeed]({post_url})"

    if args.dry_run:
        print("\n--- DRY RUN ---")
        print(f"Subject: {subject}\n")
        print(full_body)
        print("--- END DRY RUN ---")
        return

    api_key = os.getenv("BUTTONDOWN_API_KEY")
    if not api_key:
        print("Error: BUTTONDOWN_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    payload_status = "about_to_send" if args.send else "draft"
    payload = json.dumps({
        "subject": subject,
        "body": full_body,
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
