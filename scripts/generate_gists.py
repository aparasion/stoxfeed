import feedparser
import os
import json
import datetime
import trafilatura
import time
import re
import urllib.request
import requests as req_lib
from urllib.parse import urlparse
from openai import OpenAI

SIGNALS_FILE = "_data/signals.yml"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FEEDS = [
    "https://longevity.technology/feed/",
    "https://lifespan.io/feed/",
    "https://www.fightaging.org/feed",
"https://news.google.com/rss/search?q=healthspan&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=longevity&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=lifespan+extension&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=longevity+biotech&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=anti-aging+science&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=senolytics+aging&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=epigenetic+clock+aging&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=David+Sinclair+longevity&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=Peter+Attia+healthspan&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=rapamycin+longevity&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=NAD+aging+research&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=caloric+restriction+longevity&hl=en-US&gl=US&ceid=US:en",
]

SEEN_FILE = "seen.json"
YOUR_AREA = "Longevity"
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
    """Extract clean domain name from URL (e.g. 'longevity.technology')"""
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


def normalize_title(title: str) -> str:
    """Normalize an article title for deduplication: lowercase, collapse whitespace, strip punctuation."""
    lowered = (title or "").lower()
    stripped = re.sub(r"[^a-z0-9\s]", "", lowered)
    return re.sub(r"\s+", " ", stripped).strip()


def strip_html(text: str) -> str:
    """Remove HTML tags and decode common HTML entities."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    return text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def fetch_feed(url: str) -> feedparser.FeedParserDict:
    """Fetch a feed URL with a browser-like User-Agent and parse with feedparser."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; newsreader/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
        return feedparser.parse(content)
    except Exception as e:
        print(f"Failed to fetch feed {url}: {e}")
        return feedparser.FeedParserDict(entries=[])


_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_article_text(url: str) -> str:
    """Fetch and extract readable article text from a URL."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        try:
            resp = req_lib.get(url, headers=_BROWSER_HEADERS, timeout=15, allow_redirects=True)
            if resp.ok:
                downloaded = resp.text
        except Exception:
            pass
    if not downloaded:
        return ""

    extracted = trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
    return normalize_text(extracted)


def is_google_news_url(url: str) -> bool:
    try:
        return urlparse(url or "").netloc.lower().endswith("news.google.com")
    except Exception:
        return False


_BLOCKED_DOMAINS = frozenset({
    "localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254",  # SSRF targets
})


def _is_safe_resolved_url(url: str) -> bool:
    """Validate that a resolved URL points to a safe, external domain."""
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower().split(":")[0]
        if not host or host in _BLOCKED_DOMAINS:
            return False
        if parsed.scheme not in ("http", "https"):
            return False
        # Block private IPs
        if host.startswith(("10.", "192.168.", "172.16.", "172.17.", "172.18.",
                            "172.19.", "172.2", "172.30.", "172.31.")):
            return False
        return True
    except Exception:
        return False


def resolve_google_news_url(url: str, timeout: int = 10) -> str:
    """Follow the Google News redirect and return the final article URL."""
    for attempt in ("requests", "urllib"):
        try:
            if attempt == "requests":
                resp = req_lib.get(url, headers=_BROWSER_HEADERS, timeout=timeout, allow_redirects=True)
                final = resp.url
            else:
                opener = urllib.request.build_opener()
                opener.addheaders = [("User-Agent", "Mozilla/5.0")]
                with opener.open(url, timeout=timeout) as response:
                    final = response.url
            resolved = normalize_url(final)
            if resolved and not is_google_news_url(resolved) and _is_safe_resolved_url(resolved):
                return resolved
        except Exception:
            continue
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
        resolved = resolve_google_news_url(primary_link)
        if resolved and resolved != primary_link:
            candidates.append(resolved)
        else:
            source = getattr(entry, "source", None)
            source_href = normalize_url(getattr(source, "href", "")) if source else ""
            if source_href:
                candidates.append(source_href)

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


def parse_signal_titles_from_yaml(path: str) -> dict[str, str]:
    """Return a dict mapping signal id -> title from the signals YAML file."""
    if not os.path.exists(path):
        return {}
    titles: dict[str, str] = {}
    current_id = ""
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if line.startswith("- id:"):
                current_id = line.split(":", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("title:") and current_id:
                titles[current_id] = line.split(":", 1)[1].strip().strip('"').strip("'")
    return titles


SIGNAL_TITLES = parse_signal_titles_from_yaml(SIGNALS_FILE)

SIGNAL_KEYWORDS = {
    # category: therapeutics
    "senolytic-clinical-validation": [
        "senolytic", "senescent cell", "dasatinib", "quercetin", "fisetin",
        "unity biotechnology", "senescence", "senostatic", "clearance of senescent",
        "zombie cell", "senescent cell elimination",
    ],
    "rapamycin-healthspan-extension": [
        "rapamycin", "rapalog", "mTOR", "mTOR inhibitor", "sirolimus",
        "everolimus", "mechanistic target", "TORC1", "rapamycin analog",
        "mTOR pathway",
    ],
    # category: biomarkers
    "epigenetic-clock-adoption": [
        "epigenetic clock", "DNA methylation", "Horvath", "GrimAge",
        "DunedinPACE", "biological age", "methylation age", "aging clock",
        "epigenetic age", "DNAm",
    ],
    "blood-biomarker-panels": [
        "blood biomarker", "proteomics", "metabolomics", "multi-omic",
        "aging panel", "blood test aging", "plasma protein", "biomarker panel",
        "liquid biopsy aging", "omic",
    ],
    # category: nutrition
    "caloric-restriction-mimetics": [
        "caloric restriction", "calorie restriction", "fasting mimetic",
        "metformin", "spermidine", "NAD+", "NMN", "nicotinamide riboside",
        "NR supplement", "CR mimetic", "intermittent fasting",
    ],
    "gut-microbiome-aging": [
        "microbiome", "gut bacteria", "gut flora", "probiotic aging",
        "inflammaging", "microbial diversity", "gut-brain axis",
        "fecal transplant", "microbiota", "gut health aging",
    ],
    # category: technology
    "ai-drug-discovery-aging": [
        "AI drug discovery", "machine learning aging", "computational drug",
        "drug repurposing", "in silico", "AlphaFold", "target identification",
        "AI-driven drug", "deep learning drug",
    ],
    "gene-therapy-aging": [
        "gene therapy", "CRISPR", "Yamanaka factors", "cellular reprogramming",
        "telomerase", "TERT", "AAV gene therapy", "epigenetic reprogramming",
        "partial reprogramming", "gene editing aging",
    ],
    # category: policy
    "longevity-regulatory-frameworks": [
        "FDA aging", "aging indication", "regulatory pathway",
        "geroscience", "TAME trial", "aging as disease",
        "regulatory framework aging", "EMA longevity",
    ],
    "longevity-funding-surge": [
        "longevity funding", "longevity investment", "aging biotech",
        "venture capital longevity", "Altos Labs", "Calico",
        "longevity startup", "aging research grant", "NIH aging",
        "longevity VC",
    ],
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

    normalized_seen = {normalize_url(e) for e in seen if not e.startswith("title::")}
    seen_titles = {e[len("title::"):] for e in seen if e.startswith("title::")}
    posts = []
    count = 0

    for feed_url in FEEDS:
        if count >= MAX_ARTICLES:
            break

        feed = fetch_feed(feed_url)

        for entry in feed.entries[:10]:
            if count >= MAX_ARTICLES:
                break

            candidate_urls = candidate_urls_for_entry(entry)
            if not candidate_urls:
                continue

            url = candidate_urls[0]
            google_news_source = is_google_news_url(candidate_urls[0])

            if any(c in normalized_seen for c in candidate_urls):
                continue

            entry_title_norm = normalize_title(getattr(entry, "title", ""))
            if entry_title_norm and entry_title_norm in seen_titles:
                print(f"Skipping duplicate title: '{getattr(entry, 'title', '')[:70]}'")
                continue

            fallback_raw = getattr(entry, "summary", "") or getattr(entry, "description", "")
            fallback_description = normalize_text(strip_html(fallback_raw))

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
                print(
                    f"Skipping (no usable content): '{getattr(entry, 'title', url)[:70]}' | "
                    f"extracted={len(extracted_text)}c, fallback={len(fallback_description)}c, "
                    f"gnews={google_news_source}"
                )
                continue

            prompt = (
                "Write a gist for this article (120–160 words).\n"
                "Frame it for a longevity science and healthspan research professional audience.\n\n"
                f"Article text:\n{text[:15000]}"
            )

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a skilled editorial writer for a longevity science and healthspan research news platform. Your readers are professionals working in aging biology, longevity therapeutics, biotech, and healthspan research.

Write a clear, engaging gist in 3 short paragraphs (120–160 words total).

Opening paragraph: Lead with the most significant development in a strong, direct sentence. Establish what happened and who is involved immediately.

Middle paragraph: Explain why it matters to the longevity and healthspan field — connect to clinical impact, research trends, therapeutic potential, or market dynamics as relevant. Use specific details from the source material.

Closing paragraph: Offer one concrete, field-relevant takeaway or implication. Close with a natural, genuine invitation for the reader to explore the full story at the original source — write this as if you genuinely recommend the article, not as a generic disclaimer.

Tone and style:
• Write like a knowledgeable colleague sharing a notable finding, not like a press release.
• Use active voice, varied sentence length, and concrete language.
• Avoid corporate jargon, filler phrases ("in a world where...", "it's worth noting that..."), and vague superlatives.
• Neutral and factual — no editorial opinion, no speculation beyond what the source states.
• The gist should make a longevity professional curious enough to click through to the original article.

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

            # Build optional signal reference for high-confidence matches
            signal_ref = ""
            if signal_confidence == "high" and signal_ids:
                first_signal = signal_ids[0]
                signal_title = SIGNAL_TITLES.get(first_signal, "")
                if signal_title:
                    signal_ref = (
                        f"\n*HealthspanWire tracks this as a research signal: "
                        f"[{signal_title}](/signals/#{first_signal})*\n"
                    )

            md_content = f"""---
title: "{safe_title}"
date: {post_date_str}T{time_str}Z
layout: post
categories: [{YOUR_AREA.lower()}]
tags: [longevity, healthspan, news, gist]
excerpt: "{safe_excerpt}..."
publisher: "{safe_publisher}"
source_url: "{safe_source_url}"
signal_ids: [{signal_ids_yaml}]
signal_stance: {signal_stance}
signal_confidence: {signal_confidence}
---

{gist}
{signal_ref}
[Source: {safe_publisher}]({safe_source_url})
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
            if entry_title_norm and entry_title_norm not in seen_titles:
                seen.append(f"title::{entry_title_norm}")
                seen_titles.add(entry_title_norm)
            count += 1
            time.sleep(2)

    print(f"Generated {len(posts)} individual gist posts")
    with open(SEEN_FILE, "w", encoding="utf-8") as seen_file:
        json.dump(seen[-500:], seen_file, indent=2)


if __name__ == "__main__":
    main()
