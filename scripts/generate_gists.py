import feedparser
import os
import json
import datetime
import trafilatura
import time
import re
import urllib.request
from urllib.parse import urlparse
from openai import OpenAI

SIGNALS_FILE = "_data/signals.yml"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FEEDS = [
    "https://aparasion.github.io/rss-generator/rss/GALA-Global.xml",
    "https://news.google.com/rss/search?q=%22localization+industry%22+OR+%22translation+services%22+OR+%22LSP%22+OR+%22machine+translation%22+-DNA+-biological+when:90d&hl=en-US&gl=US&ceid=US:en",
    "https://slator.com/feed/",
    "https://techcrunch.com/tag/translation/feed/",
    "https://techcrunch.com/tag/ai-translation/feed/",
    "https://techcrunch.com/tag/machine-translation/feed/",
    "https://techcrunch.com/tag/localization/feed/",
    "https://techcrunch.com/tag/translate/feed/",
    "https://techcrunch.com/tag/translations/feed/",
    "https://www.atanet.org/news/industry-news/feed/",
    "https://elia-association.org/news/feed/",
    "https://multilingual.com/news/feed",
    "https://aparasion.github.io/rss-generator/rss/XTM-Blog.xml",
]

SEEN_FILE = "seen.json"
YOUR_AREA = "Translation"
MAX_ARTICLES = 18
MIN_ARTICLE_CHARS = 500
MIN_ARTICLE_WORDS = 90

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
    """Extract clean domain name from URL (e.g. 'distractify.com')"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove common prefixes
        if domain.startswith(('www.', 'amp.', 'm.')):
            domain = domain.split('.', 1)[1] if '.' in domain[4:] else domain[4:]
        # Remove port if present (rare)
        domain = domain.split(':', 1)[0]
        return domain if domain else "Unknown Publisher"
    except Exception:
        return "Unknown Publisher"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def normalize_url(url: str) -> str:
    """Normalize a URL for deduplication: strip fragment and trailing slash."""
    cleaned = (url or "").strip()
    if not cleaned:
        return ""
    return cleaned.split("#", 1)[0].rstrip("/")


def extract_article_text(url: str) -> str:
    """Fetch and extract readable article text from a URL."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return ""

    extracted = trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
    return normalize_text(extracted)


def is_google_news_url(url: str) -> bool:
    try:
        return urlparse(url or "").netloc.lower().endswith("news.google.com")
    except Exception:
        return False


def resolve_google_news_url(url: str, timeout: int = 10) -> str:
    """Follow the Google News redirect and return the final article URL.

    Google News RSS links are redirect wrappers (news.google.com/rss/articles/…)
    that issue a 301/302 to the real publisher URL. urllib follows redirects
    automatically, so response.url is the resolved destination.
    Falls back to the original URL on any error.
    """
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [("User-Agent", "Mozilla/5.0")]
        with opener.open(url, timeout=timeout) as response:
            final = response.url
        resolved = normalize_url(final)
        return resolved if resolved and not is_google_news_url(resolved) else url
    except Exception:
        return url


def extract_links_from_html(text: str) -> list[str]:
    if not text:
        return []
    return re.findall(r'href=["\'](https?://[^"\']+)["\']', text)


def candidate_urls_for_entry(entry) -> list[str]:
    candidates = []

    primary_link = normalize_url(getattr(entry, "link", ""))
    if primary_link:
        candidates.append(primary_link)

    if primary_link and is_google_news_url(primary_link):
        # 1. Follow the redirect — most reliable, works for any Google News link.
        resolved = resolve_google_news_url(primary_link)
        if resolved and resolved != primary_link:
            candidates.append(resolved)
        else:
            # 2. Fallback: source.href embedded in the feed XML.
            source = getattr(entry, "source", None)
            source_href = normalize_url(getattr(source, "href", "")) if source else ""
            if source_href:
                candidates.append(source_href)

            # 3. Fallback: links scraped from the summary HTML.
            summary_html = getattr(entry, "summary", "") or getattr(entry, "description", "")
            for link in extract_links_from_html(summary_html):
                normalized = normalize_url(link)
                if normalized and not is_google_news_url(normalized):
                    candidates.append(normalized)

    deduped = []
    seen = set()
    for url in candidates:
        if url and url not in seen:
            deduped.append(url)
            seen.add(url)
    return deduped


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


def parse_signal_ids_from_yaml(path: str) -> list[str]:
    if not os.path.exists(path):
        return []

    ids = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if line.startswith("- id:"):
                ids.append(line.split(":", 1)[1].strip().strip('"').strip("'"))
    return ids


KNOWN_SIGNAL_IDS = set(parse_signal_ids_from_yaml(SIGNALS_FILE))
SIGNAL_KEYWORDS = {
    "quality-gap-closure": ["quality", "human", "review", "post-edit", "validation", "mqm", "error"],
    "governance-in-ai-workflows": ["governance", "audit", "compliance", "control", "policy", "risk", "guardrail"],
    "localization-operating-system": ["platform", "end-to-end", "workflow", "integration", "api", "orchestration"],
    "measurable-quality-evaluation": ["mqm", "metric", "evaluation", "benchmark", "score", "assessment"],
}


NEGATIVE_MARKERS = [
    "failed", "fails", "lawsuit", "criticized", "criticises", "criticizes", "serious issue", "data quality issues"
]
MIXED_MARKERS = ["however", "but", "trade-off", "while"]


def infer_signal_tags(title: str, gist: str) -> tuple[list[str], str, str]:
    text = f"{title} {gist}".lower()

    matched = []
    for signal_id, keywords in SIGNAL_KEYWORDS.items():
        if signal_id not in KNOWN_SIGNAL_IDS:
            continue
        hits = sum(1 for kw in keywords if kw in text)
        if hits >= 2:
            matched.append(signal_id)

    if any(marker in text for marker in NEGATIVE_MARKERS):
        stance = "contradicts"
    elif any(marker in text for marker in MIXED_MARKERS):
        stance = "mixed"
    else:
        stance = "supports" if matched else "mentions"

    confidence = "high" if len(matched) >= 2 else "medium" if len(matched) == 1 else "low"
    return matched, stance, confidence


def main() -> None:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as seen_file:
            seen = json.load(seen_file)
    else:
        seen = []

    normalized_seen = {normalize_url(url) for url in seen}
    posts = []
    count = 0

    for feed_url in FEEDS:
        if count >= MAX_ARTICLES:
            break

        normalized_feed_url = normalize_url(feed_url)
        try:
            feed = feedparser.parse(normalized_feed_url)
        except Exception as e:
            print(f"Skipping feed due to parse error for {feed_url}: {e}")
            continue

        for entry in feed.entries[:10]:
            if count >= MAX_ARTICLES:
                break

            candidate_urls = candidate_urls_for_entry(entry)
            if not candidate_urls:
                continue

            url = candidate_urls[0]
            google_news_source = is_google_news_url(candidate_urls[0])

            # Skip if ANY candidate URL for this entry has already been seen.
            # This handles cases where the Google News redirect URL and the
            # resolved article URL are both recorded across runs.
            if any(c in normalized_seen for c in candidate_urls):
                continue

            fallback_description = normalize_text(getattr(entry, "description", ""))
            extracted_text = ""
            for candidate_url in candidate_urls:
                extracted_text = extract_article_text(candidate_url)
                if is_usable_article_text(extracted_text, entry.title):
                    url = candidate_url
                    break
                if google_news_source and extracted_text:
                    url = candidate_url
                    break

            if is_usable_article_text(extracted_text, entry.title):
                text = extracted_text
            elif google_news_source and extracted_text:
                text = extracted_text
            elif is_usable_article_text(fallback_description, entry.title):
                text = fallback_description
            elif google_news_source and fallback_description:
                text = fallback_description
            else:
                print(f"Skipping low-quality content for {url}")
                continue

            prompt = (
                "Write a gist for this article (120–160 words).\n"
                "Frame it for a localization and language services professional audience.\n\n"
                f"Article text:\n{text[:15000]}"
            )

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a skilled editorial writer for a localization and translation industry news platform. Your readers are professionals working in enterprise localization, language technology, translation services, and AI-driven language workflows.

Write a clear, engaging gist in 3 short paragraphs (120–160 words total).

Opening paragraph: Lead with the most significant development in a strong, direct sentence. Establish what happened and who is involved immediately.

Middle paragraph: Explain why it matters to the localization and language services industry — connect to business impact, technology trends, workflow changes, or market dynamics as relevant. Use specific details from the source material.

Closing paragraph: Offer one concrete, industry-relevant takeaway or implication. Close with a natural, genuine invitation for the reader to explore the full story at the original source — write this as if you genuinely recommend the article, not as a generic disclaimer.

Tone and style:
• Write like a knowledgeable colleague sharing a notable finding, not like a press release.
• Use active voice, varied sentence length, and concrete language.
• Avoid corporate jargon, filler phrases ("in a world where...", "it's worth noting that..."), and vague superlatives.
• Neutral and factual — no editorial opinion, no speculation beyond what the source states.
• The gist should make a localization professional curious enough to click through to the original article.

If the provided text is mostly cookie/privacy/legal notices rather than article content, respond exactly with: UNUSABLE_CONTENT""",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=300,
                    temperature=0.4,
                )
                gist = response.choices[0].message.content.strip()
                if gist == "UNUSABLE_CONTENT":
                    print(f"Skipping unusable generated content for {url}")
                    continue
            except Exception as e:
                print(f"OpenAI API error for {url}: {e}")
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

            publisher = get_publisher_domain(url)
            safe_title = yaml_escape(entry.title)
            safe_excerpt = yaml_escape(gist[:160])
            safe_publisher = yaml_escape(publisher)
            safe_source_url = yaml_escape(url)
            signal_ids, signal_stance, signal_confidence = infer_signal_tags(entry.title, gist)
            signal_ids_yaml = ", ".join(signal_ids)

            md_content = f"""---
title: "{safe_title}"
date: {post_date_str}T{time_str}Z
layout: post
categories: [{YOUR_AREA.lower()}]
tags: [translation, localization, news, gist]
excerpt: "{safe_excerpt}..."
publisher: "{safe_publisher}"
source_url: "{safe_source_url}"
signal_ids: [{signal_ids_yaml}]
signal_stance: {signal_stance}
signal_confidence: {signal_confidence}
---

{gist}

[Read full article via {safe_publisher}]({safe_source_url})
"""

            os.makedirs("_posts", exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(md_content)

            posts.append(
                {
                    "title": entry.title,
                    "publisher": publisher,
                    "url": url,
                    "gist": gist,
                    "date": post_date_str,
                }
            )

            for candidate in candidate_urls:
                if candidate not in normalized_seen:
                    seen.append(candidate)
                    normalized_seen.add(candidate)
            count += 1
            time.sleep(2)

    print(f"Generated {len(posts)} individual gist posts")
    with open(SEEN_FILE, "w", encoding="utf-8") as seen_file:
        json.dump(seen[-500:], seen_file, indent=2)


if __name__ == "__main__":
    main()
