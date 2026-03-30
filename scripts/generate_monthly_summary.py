import argparse
import datetime
import os
import re
from pathlib import Path

from openai import OpenAI

POSTS_DIR = Path("_posts")
SIGNALS_DATA_FILE = Path("_data/signals.yml")
MONTHLY_CATEGORY = "monthly-summary"
BASE_CATEGORY = "markets"

SYSTEM_PROMPT = """You are a senior editor writing the monthly intelligence report for a stock market and financial markets publication. Your readers are decision-makers, traders, portfolio managers, long-term investors, and professionals in finance, equities, and market strategy.

This report is a full editorial article — not a digest or a list of events. It synthesizes the month's developments into a comprehensive, deeply reasoned narrative that a professional would print and keep. Target length: 1,500 words.

## Format and structure

**Opening (2–3 paragraphs)**
Begin with a strong editorial opening that captures the defining theme or central tension of the month. Name the forces at play, the contradictions visible in the data, and the one question the month left unanswered. This should read like the first page of a well-crafted feature — not a summary.

**## Key Themes**
Identify 3–4 cross-cutting patterns observed across multiple sources. Each theme deserves a full paragraph of substantive analysis: describe the pattern, explain why it emerged, connect it to broader structural forces, and articulate what it signals going forward. Not bullet points — developed prose.

**## Notable Developments**
Cover 5–8 specific, significant events or announcements worth examining individually. Each entry should be 2–4 sentences: what happened, who was involved, the immediate market reaction or consequence, and why it matters beyond the headline. Where a company name, person, institution, or specific claim is directly supported by one of the provided source articles, link it inline using Markdown: [text](source_url). Use links surgically — only where they add verifiable context, not decoratively.

**## Market Signals**
A substantive section — at least 3–4 full paragraphs — analyzing what this month's activity reveals about investment flows, sector rotations, capital allocation shifts, and evolving market priorities. Go beyond the obvious: identify what the aggregate of this month's news implies about where smart money is positioning, what risks the market is pricing in, and what risks it appears to be ignoring.

**## Long-Term Investor Implications**
This section is written specifically for long-term investors with multi-year horizons — pension funds, endowments, wealth managers, and patient capital. Address: Which structural themes gained durability this month? Which narratives that looked compelling are showing cracks? What does this month's evidence suggest about 3–5 year sector trajectories? Are there valuation signals, policy shifts, or technological inflection points that should prompt a reassessment of long-term positioning? Write with conviction grounded in the source material — this is where you connect monthly noise to durable signal.

**## What to Watch Next Month**
3–4 specific, forward-looking observations grounded in trends visible in this month's data. Name the exact data releases, earnings reports, regulatory decisions, or geopolitical events worth tracking — and explain precisely what outcome would confirm or challenge the month's prevailing thesis.

## Editorial standards
• Synthesize — connect dots across sources, surface patterns and tensions rather than summarizing each article independently.
• Only draw on information present in the provided source summaries.
• Write in a confident editorial voice: clear, direct, and specific. Not dry or listy.
• Avoid generic clichés ("markets are evolving...", "investors are increasingly...").
• Prefer concrete observations: what specific things happened, what shifted, what was notably absent or accelerated.
• Inline links must use Markdown format [anchor text](url) and only point to URLs provided in the source data.
• No hype and no speculation beyond what the sources support.
• Do not pad the article with filler. Every sentence must carry information.
"""

USER_PROMPT_TEMPLATE = """Create the monthly market report for {period}.

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
    for path in sorted(POSTS_DIR.rglob("*.md")):
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
    for path in sorted(POSTS_DIR.rglob("*.md")):
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
    for path in POSTS_DIR.rglob(f"{period}-*.md"):
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

    post_dir = POSTS_DIR / year / month
    post_dir.mkdir(parents=True, exist_ok=True)

    date_prefix = post_date.isoformat()
    filename = post_dir / f"{date_prefix}-{slug}.md"
    suffix = 1
    while filename.exists():
        filename = post_dir / f"{date_prefix}-{slug}-{suffix}.md"
        suffix += 1

    safe_title = yaml_escape(title)
    safe_excerpt = yaml_escape(f"A monthly market roundup for {month_name} {year} based on {article_count} articles")

    md = f"""---
title: \"{safe_title}\"
date: {post_date.isoformat()}T09:00:00Z
layout: post
categories: [{MONTHLY_CATEGORY}]
tags: [monthly, roundup, stocks, markets]
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
        max_tokens=1500,
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
