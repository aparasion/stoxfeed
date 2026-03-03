import datetime
import json
import os
import re
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import feedparser
import trafilatura
from openai import OpenAI

FEEDS = [
    "https://news.google.com/rss/search?q=translation+localization+OR+interpreting+when:7d&hl=en-US&gl=US&ceid=US:en",
    "https://rss.app/feeds/I3pWmZPMwgWX6npo.xml",
    "https://techcrunch.com/tag/translation/feed/",
    "https://techcrunch.com/tag/ai-translation/feed/",
    "https://techcrunch.com/tag/machine-translation/feed/",
    "https://techcrunch.com/tag/localization/feed/",
    "https://techcrunch.com/tag/translate/feed/",
    "https://techcrunch.com/tag/translations/feed/",
    "https://rss.app/feeds/cNm8rHSnDFeEYLpt.xml",  # gala-blobal news feed
    "https://www.atanet.org/news/industry-news/feed/",
    "https://elia-association.org/news/feed/",
]

SEEN_FILE = "seen.json"
YOUR_AREA = "Translation"
MAX_ARTICLES = 18
MIN_ARTICLE_CHARS = 500
MIN_ARTICLE_WORDS = 90
REDIRECT_DOMAINS = {"news.google.com", "rss.app"}

BOILERPLATE_PATTERNS = [
    r"\bcookies?\b",
    r"\bprivacy policy\b",
    r"\baccept (all )?cookies\b",
    r"\bmanage (your )?(consent|preferences)\b",
    r"\bconsent\b",
    r"\bdata protection\b",
]


def yaml_escape(text: str) -> str:
    """Escape content for safe inclusion in quoted YAML scalar values."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()


def get_publisher_domain(url: str) -> str:
    """Extract clean domain name from URL (e.g. 'distractify.com')."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith(("www.", "amp.", "m.")):
            domain = domain.split(".", 1)[1] if "." in domain[4:] else domain[4:]
        domain = domain.split(":", 1)[0]
        return domain if domain else "Unknown Publisher"
    except Exception:
        return "Unknown Publisher"


def resolve_canonical_url(url: str) -> str:
    """Follow redirects for known aggregator links and return final URL."""
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        if domain not in REDIRECT_DOMAINS:
            return url

        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=15) as response:
            return response.geturl() or url
    except Exception:
        return url


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def title_keywords(title: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z]{4,}", (title or "").lower())
    return {token for token in tokens if token not in {"with", "from", "into", "that", "this"}}


def has_title_overlap(text: str, title: str) -> bool:
    keywords = title_keywords(title)
    if not keywords:
        return True
    text_l = text.lower()
    overlap = sum(1 for kw in keywords if kw in text_l)
    return overlap >= 1


def boilerplate_hits(text: str) -> int:
    text_l = text.lower()
    return sum(1 for pattern in BOILERPLATE_PATTERNS if re.search(pattern, text_l))


def is_usable_article_text(text: str, title: str) -> bool:
    cleaned = normalize_text(text)
    if len(cleaned) < MIN_ARTICLE_CHARS:
        return False
    if len(cleaned.split()) < MIN_ARTICLE_WORDS:
        return False
    if boilerplate_hits(cleaned) >= 3:
        return False
    if not has_title_overlap(cleaned, title):
        return False
    return True


def main() -> None:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as seen_file:
            seen = json.load(seen_file)
    else:
        seen = []

    posts = []
    count = 0

    for feed_url in FEEDS:
        if count >= MAX_ARTICLES:
            break

        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:10]:
            if count >= MAX_ARTICLES:
                break

            url = entry.link
            resolved_url = resolve_canonical_url(url)
            if url in seen or resolved_url in seen:
                continue

            downloaded = trafilatura.fetch_url(resolved_url)
            fallback_description = normalize_text(getattr(entry, "description", ""))
            extracted_text = normalize_text(
                trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
            )

            if is_usable_article_text(extracted_text, entry.title):
                text = extracted_text
            elif is_usable_article_text(fallback_description, entry.title):
                text = fallback_description
            else:
                print(f"Skipping low-quality content for {resolved_url}")
                continue

            prompt = f"""Create a concise gist (100–200 words) of this article.
Focus on key facts and implications.

Article text:
{text[:15000]}"""

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a professional news summarizer writing for a digital news platform read by the general public and business professionals.
Write a clear, engaging summary in 3–4 short paragraphs (120–180 words).
• Open with the most important development in a strong, direct sentence.
• Focus on verified facts: what happened, who is involved, and why it matters.
• Include relevant business, economic, or market impact when applicable.
• Maintain a neutral, professional tone — natural and human, not robotic or overly dramatic.
• Avoid speculation, opinion, exaggeration, and filler language.
• Use smooth transitions and varied sentence structure.
• End with a brief, natural sentence encouraging readers to read the full article for more details.
• If the provided text appears to be mostly cookie/privacy/legal notice rather than article content, respond exactly with: UNUSABLE_CONTENT
Keep the writing concise, informative, and easy to scan.""",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=300,
                    temperature=0.3,
                )
                gist = response.choices[0].message.content.strip()
                if gist == "UNUSABLE_CONTENT":
                    print(f"Skipping unusable generated content for {resolved_url}")
                    continue
            except Exception as e:
                print(f"OpenAI API error for {resolved_url}: {e}")
                gist = "Summary generation failed due to API error.\n\nRead the full article below."

            if "published_parsed" in entry and entry.published_parsed:
                pub_dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
            else:
                pub_dt = datetime.datetime.now(datetime.timezone.utc)

            post_date_str = pub_dt.strftime("%Y-%m-%d")
            time_str = pub_dt.strftime("%H:%M:%S")

            slug_raw = re.sub(r"\s+", "-", entry.title.lower().strip())
            slug = "".join(c for c in slug_raw if c.isalnum() or c == "-")[:60].strip("-")
            if not slug:
                slug = f"article-{int(pub_dt.timestamp())}"

            filename = f"_posts/{post_date_str}-{slug}.md"
            suffix = 1
            while os.path.exists(filename):
                filename = f"_posts/{post_date_str}-{slug}-{suffix}.md"
                suffix += 1

            source_url = resolved_url if resolved_url else (entry.link if entry.link else url)
            publisher = get_publisher_domain(source_url)

            safe_title = yaml_escape(entry.title)
            safe_excerpt = yaml_escape(gist[:160])
            safe_publisher = yaml_escape(publisher)
            safe_source_url = yaml_escape(source_url)

            md_content = f"""---
title: \"{safe_title}\"
date: {post_date_str}T{time_str}Z
layout: post
categories: [{YOUR_AREA.lower()}]
tags: [translation, localization, news, gist]
excerpt: \"{safe_excerpt}...\"
publisher: \"{safe_publisher}\"
source_url: \"{safe_source_url}\"
---

{gist}

[→ Read full article via {safe_publisher}]({safe_source_url})
"""

            os.makedirs("_posts", exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(md_content)

            posts.append(
                {
                    "title": entry.title,
                    "publisher": publisher,
                    "url": source_url,
                    "gist": gist,
                    "date": post_date_str,
                }
            )

            seen.append(url)
            if resolved_url != url:
                seen.append(resolved_url)
            count += 1

            time.sleep(2)

    print(f"Generated {len(posts)} individual gist posts")
    with open(SEEN_FILE, "w", encoding="utf-8") as seen_file:
        json.dump(seen[-500:], seen_file, indent=2)


if __name__ == "__main__":
    main()
