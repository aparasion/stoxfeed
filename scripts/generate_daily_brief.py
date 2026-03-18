import argparse
import datetime
import os
import re
from pathlib import Path

from openai import OpenAI

POSTS_DIR = Path("_posts")
DAILY_BRIEF_CATEGORY = "daily-brief"
SKIP_CATEGORIES = {"daily-brief", "monthly-summary"}

SYSTEM_PROMPT = """You are a professional financial market analyst. Write a concise end-of-day market brief based only on today's news articles.
The summary must synthesize all articles into a single, coherent narrative. Do not assume or add data that is not explicitly mentioned. If something is not covered in the articles, omit it.
Structure the brief in two clear sections (total 150–250 words):
1. What Happened Today
* Highlight major events
* Summarize the overall market direction and sentiment based on the articles
* Highlight the key drivers (macroeconomic data, central bank news, earnings, geopolitics)
* Include any sectors, assets, or companies that were repeatedly mentioned as movers
2. Expectations for the Next Session
* Describe what market participants are focusing on next, based on the articles
* Include any forward-looking signals (upcoming data, events, risks, sentiment shifts, geopolitical impact)
* Reflect whether expectations are bullish, bearish, or uncertain
Keep the tone professional, analytical, and concise."""

USER_PROMPT_TEMPLATE = """Create the end-of-day market brief for {date}.

{article_summaries}"""


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
    body = content[end + 5:]
    fm = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip()
    return fm, body.strip()


def build_article_prompt_rows(articles: list[dict]) -> str:
    chunks = []
    for idx, article in enumerate(articles, start=1):
        chunks.append(
            f"{idx}. Title: {article['title']}\n"
            f"Publisher: {article['publisher'] or 'Unknown'}\n"
            f"Summary: {article['summary']}\n"
        )
    return "\n".join(chunks)


def collect_today_articles(date_str: str) -> list[dict]:
    rows = []
    for path in sorted(POSTS_DIR.glob(f"{date_str}-*.md")):
        content = path.read_text(encoding="utf-8")
        front_matter, body = parse_front_matter(content)

        categories = front_matter.get("categories", "")
        if any(cat in categories for cat in SKIP_CATEGORIES):
            continue

        title = front_matter.get("title", "").strip().strip('"')
        publisher = front_matter.get("publisher", "").strip().strip('"')
        excerpt = front_matter.get("excerpt", "").strip().strip('"')

        summary_text = excerpt if excerpt else body[:500]
        if not title:
            continue

        rows.append(
            {
                "title": title,
                "publisher": publisher,
                "summary": summary_text,
            }
        )
    return rows


def daily_brief_exists(date_str: str) -> bool:
    for path in POSTS_DIR.glob(f"{date_str}-*.md"):
        content = path.read_text(encoding="utf-8")
        front_matter, _ = parse_front_matter(content)
        if DAILY_BRIEF_CATEGORY in front_matter.get("categories", ""):
            return True
    return False


def write_daily_brief(date_str: str, article_count: int, content: str) -> Path:
    date_obj = datetime.date.fromisoformat(date_str)
    month_name = date_obj.strftime("%B")
    day = date_obj.day
    year = date_obj.year

    title = f"Daily Brief: {month_name} {day}, {year}"
    slug = slugify(f"daily-brief-{month_name}-{day}-{year}")
    filename = POSTS_DIR / f"{date_str}-{slug}.md"

    suffix = 1
    while filename.exists():
        filename = POSTS_DIR / f"{date_str}-{slug}-{suffix}.md"
        suffix += 1

    safe_title = yaml_escape(title)
    safe_excerpt = yaml_escape(
        f"End-of-day market brief for {month_name} {day}, {year} based on {article_count} articles"
    )

    md = f"""---
title: "{safe_title}"
date: {date_str}T20:00:00Z
layout: post
categories: [{DAILY_BRIEF_CATEGORY}]
tags: [daily-brief, markets, summary]
excerpt: "{safe_excerpt}."
source_count: {article_count}
---

{content}
"""
    filename.write_text(md, encoding="utf-8")
    return filename


def generate_daily_brief(date_str: str, force: bool = False) -> Path | None:
    if not POSTS_DIR.exists():
        raise FileNotFoundError("_posts directory does not exist")

    if daily_brief_exists(date_str) and not force:
        print(f"Daily brief already exists for {date_str}. Use --force to regenerate.")
        return None

    articles = collect_today_articles(date_str)
    if not articles:
        print(f"No articles found for {date_str}. Skipping daily brief.")
        return None

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    article_summaries = build_article_prompt_rows(articles)
    user_prompt = USER_PROMPT_TEMPLATE.format(date=date_str, article_summaries=article_summaries)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,
        temperature=0.4,
    )
    brief_content = response.choices[0].message.content.strip()
    out_file = write_daily_brief(date_str, len(articles), brief_content)
    print(f"Created daily brief: {out_file}")
    return out_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate end-of-day daily brief from today's posts.")
    parser.add_argument(
        "--date",
        default=datetime.date.today().isoformat(),
        help="Date to summarize in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument("--force", action="store_true", help="Generate even if a daily brief already exists")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.date):
        raise ValueError("--date must be in YYYY-MM-DD format")
    generate_daily_brief(args.date, force=args.force)
