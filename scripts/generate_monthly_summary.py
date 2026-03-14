import argparse
import datetime
import os
import re
from pathlib import Path

from openai import OpenAI

POSTS_DIR = Path("_posts")
SIGNALS_DATA_FILE = Path("_data/signals.yml")
MONTHLY_CATEGORY = "monthly-summary"
BASE_CATEGORY = "longevity"

SYSTEM_PROMPT = """You are a senior editor writing the monthly intelligence report for a longevity science and healthspan research publication. Your readers are decision-makers, researchers, and professionals in aging biology, longevity therapeutics, biotech, and healthspan science.

This report synthesizes the month's developments into a coherent narrative — not a list of events, but an editorial interpretation of what moved the field forward, what created uncertainty, and what professionals should track.

Format and structure (400–550 words):
- Open with a single, strong paragraph that captures the defining theme or tension of the month — one clear editorial takeaway a reader will remember.
- ## Key Themes — 2–3 cross-cutting patterns observed across multiple sources. Describe the pattern and what it signals, not individual events.
- ## Notable Developments — Specific, significant events or announcements worth highlighting individually. Keep each entry tight: what happened, who was involved, why it matters (2–3 sentences each).
- ## Research and Market Signals — What does this month's activity suggest about where investment, clinical development, or research priorities are heading in longevity science?
- ## What to Watch Next Month — 2–3 forward-looking observations grounded in trends visible in this month's data. Be specific, not generic.

Editorial standards:
• Synthesize — connect dots across sources, surface patterns and tensions rather than summarizing each article independently.
• Only draw on information present in the provided source summaries.
• Write in a confident editorial voice: clear, direct, and specific. Not dry or listy.
• Avoid generic clichés ("science is advancing...", "researchers are increasingly...").
• Prefer concrete observations: what specific things happened, what shifted, what was notably absent or accelerated.
• No hype and no speculation beyond what the sources support.
"""

USER_PROMPT_TEMPLATE = """Create the monthly industry report for {period}.

{article_summaries}
"""


def yaml_escape(text: str) -> str:
    return (text or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()


def slugify(text: str) -> str:
    slug_raw = re.sub(r"\s+", "-", text.lower().strip())
    return "".join(c for c in slug_raw if c.isalnum() or c == "-").strip("-")


def parse_front_matter(content: str) -> tuple[dict, str]:
    if not content.startswith("---\n"):
        return {}, content

    end = content.find("\n---\n", 4)
    if end == -1:
        return {}, content

    fm_text = content[4:end]
    body = content[end + 5 :]
    fm = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip()
    return fm, body.strip()


def post_month_from_filename(path: Path) -> str | None:
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})-", path.name)
    if not match:
        return None
    return f"{match.group(1)}-{match.group(2)}"


def is_monthly_post(front_matter: dict) -> bool:
    categories = front_matter.get("categories", "")
    return MONTHLY_CATEGORY in categories


def collect_month_articles(period: str) -> list[dict]:
    rows = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        if post_month_from_filename(path) != period:
            continue

        content = path.read_text(encoding="utf-8")
        front_matter, body = parse_front_matter(content)

        if is_monthly_post(front_matter):
            continue

        title = front_matter.get("title", "").strip().strip('"')
        source_url = front_matter.get("source_url", "").strip().strip('"')
        publisher = front_matter.get("publisher", "").strip().strip('"')
        excerpt = front_matter.get("excerpt", "").strip().strip('"')

        summary_text = excerpt if excerpt else body[:500]
        if not title:
            continue

        rows.append(
            {
                "title": title,
                "publisher": publisher,
                "source_url": source_url,
                "summary": summary_text,
            }
        )
    return rows


def build_article_prompt_rows(articles: list[dict]) -> str:
    chunks = []
    for idx, article in enumerate(articles, start=1):
        chunks.append(
            f"{idx}. Title: {article['title']}\n"
            f"Publisher: {article['publisher'] or 'Unknown'}\n"
            f"Source: {article['source_url'] or 'N/A'}\n"
            f"Summary: {article['summary']}\n"
        )
    return "\n".join(chunks)


def parse_inline_list(value: str) -> list[str]:
    cleaned = (value or "").strip()
    if not cleaned.startswith("[") or not cleaned.endswith("]"):
        return []
    inner = cleaned[1:-1].strip()
    if not inner:
        return []
    return [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]


def load_signal_titles() -> dict[str, str]:
    if not SIGNALS_DATA_FILE.exists():
        return {}

    current_id = None
    title_by_id: dict[str, str] = {}
    for raw in SIGNALS_DATA_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("- id:"):
            current_id = line.split(":", 1)[1].strip().strip('"').strip("'")
            continue
        if current_id and line.startswith("title:"):
            title_by_id[current_id] = line.split(":", 1)[1].strip().strip('"').strip("'")
            current_id = None
    return title_by_id


def collect_signal_updates(period: str) -> dict[str, dict[str, int]]:
    updates: dict[str, dict[str, int]] = {}
    for path in sorted(POSTS_DIR.glob("*.md")):
        if post_month_from_filename(path) != period:
            continue

        content = path.read_text(encoding="utf-8")
        front_matter, _ = parse_front_matter(content)
        if is_monthly_post(front_matter):
            continue

        signal_ids = parse_inline_list(front_matter.get("signal_ids", ""))
        if not signal_ids:
            continue

        stance = front_matter.get("signal_stance", "mentions").strip().strip('"').strip("'")
        if stance not in {"supports", "contradicts", "mixed", "mentions"}:
            stance = "mentions"

        for signal_id in signal_ids:
            updates.setdefault(signal_id, {"supports": 0, "contradicts": 0, "mixed": 0, "mentions": 0})
            updates[signal_id][stance] += 1
    return updates


def build_signal_updates_section(period: str) -> str:
    updates = collect_signal_updates(period)
    if not updates:
        return ""

    titles = load_signal_titles()
    lines = ["## Signal Tracker Updates", ""]
    for signal_id in sorted(updates.keys()):
        counts = updates[signal_id]
        label = titles.get(signal_id, signal_id)
        total = sum(counts.values())
        lines.append(
            f"- **{label}** (`{signal_id}`): {total} linked post(s) "
            f"(supports: {counts['supports']}, contradicts: {counts['contradicts']}, "
            f"mixed: {counts['mixed']}, mentions: {counts['mentions']})."
        )
    return "\n".join(lines)


def monthly_post_exists(period: str) -> bool:
    for path in POSTS_DIR.glob(f"{period}-*.md"):
        content = path.read_text(encoding="utf-8")
        front_matter, _ = parse_front_matter(content)
        if is_monthly_post(front_matter) and front_matter.get("period", "").strip('"') == period:
            return True
    return False


def write_monthly_post(period: str, article_count: int, content: str) -> Path:
    year, month = period.split("-")
    month_name = datetime.date(int(year), int(month), 1).strftime("%B")
    title = f"Monthly Report: {month_name} {year}"
    slug = slugify(f"monthly-report-{month_name}-{year}")
    post_date = datetime.date(int(year), int(month), 1) + datetime.timedelta(days=27)
    while post_date.month != int(month):
        post_date -= datetime.timedelta(days=1)

    date_prefix = post_date.isoformat()
    filename = POSTS_DIR / f"{date_prefix}-{slug}.md"
    suffix = 1
    while filename.exists():
        filename = POSTS_DIR / f"{date_prefix}-{slug}-{suffix}.md"
        suffix += 1

    safe_title = yaml_escape(title)
    safe_excerpt = yaml_escape(f"A monthly roundup for {month_name} {year} based on {article_count} articles")

    md = f"""---
title: \"{safe_title}\"
date: {post_date.isoformat()}T09:00:00Z
layout: post
categories: [{MONTHLY_CATEGORY}]
tags: [monthly, roundup, longevity, healthspan]
excerpt: \"{safe_excerpt}.\"
period: \"{period}\"
source_count: {article_count}
---

{content}
"""
    filename.write_text(md, encoding="utf-8")
    return filename


def get_default_period() -> str:
    today = datetime.date.today().replace(day=1)
    last_month_end = today - datetime.timedelta(days=1)
    return last_month_end.strftime("%Y-%m")


def generate_monthly_summary(period: str, force: bool = False) -> Path | None:
    if not POSTS_DIR.exists():
        raise FileNotFoundError("_posts directory does not exist")

    if monthly_post_exists(period) and not force:
        print(f"Monthly report already exists for {period}. Use --force to generate another.")
        return None

    articles = collect_month_articles(period)
    if not articles:
        print(f"No articles found for {period}.")
        return None

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    article_summaries = build_article_prompt_rows(articles)
    user_prompt = USER_PROMPT_TEMPLATE.format(period=period, article_summaries=article_summaries)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=900,
        temperature=0.4,
    )
    monthly_content = response.choices[0].message.content.strip()
    signal_updates_section = build_signal_updates_section(period)
    if signal_updates_section:
        monthly_content = f"{monthly_content}\n\n{signal_updates_section}"
    out_file = write_monthly_post(period, len(articles), monthly_content)
    print(f"Created monthly report: {out_file}")
    return out_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate monthly summary posts from existing daily posts.")
    parser.add_argument("--month", default=get_default_period(), help="Month to summarize in YYYY-MM format")
    parser.add_argument("--force", action="store_true", help="Generate even if a monthly post already exists")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not re.match(r"^\d{4}-\d{2}$", args.month):
        raise ValueError("--month must be in YYYY-MM format")
    generate_monthly_summary(args.month, force=args.force)
