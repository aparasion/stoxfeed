# Security Analysis — HealthspanWire

**Date:** 2026-03-15
**Domain:** https://healthspanwire.com
**Stack:** Jekyll 4.3 (static site) + Python automation + GitHub Pages

---

## Executive Summary

HealthspanWire is a Jekyll-based static site with Python automation for content aggregation. The static nature inherently limits the attack surface (no database, no server-side user input processing). However, several vulnerabilities were identified in the client-side JavaScript, automation scripts, and CI/CD configuration that should be addressed.

---

## Findings Summary

| # | Severity | Category | Location | Status |
|---|----------|----------|----------|--------|
| 1 | **HIGH** | XSS via innerHTML | `_layouts/default.html:449` | **Fixed** |
| 2 | **HIGH** | Sensitive error leakage | `scripts/send_newsletter.py:247` | **Fixed** |
| 3 | **MEDIUM** | Missing CSP headers | `_layouts/default.html` | **Fixed** |
| 4 | **MEDIUM** | Open redirect in URL resolver | `scripts/generate_gists.py:146-163` | **Fixed** |
| 5 | **MEDIUM** | Unvalidated workflow inputs | `.github/workflows/*.yml` | **Fixed** |
| 6 | **LOW** | Missing SRI hashes on external resources | `_layouts/default.html:105-107` | Documented |
| 7 | **LOW** | No cookie consent / privacy opt-out for GA | `_layouts/default.html:94-102` | Documented |
| 8 | **INFO** | Broad exception handling in scripts | `scripts/generate_gists.py` | Documented |

---

## Detailed Findings

### 1. XSS via innerHTML (HIGH — Fixed)

**File:** `_layouts/default.html:449`

The glossary annotation script used `wrapper.innerHTML = updatedText` to inject tooltip markup into the DOM. While the glossary data currently comes from a trusted YAML file, `innerHTML` interprets raw HTML and can execute injected scripts if data is ever poisoned.

**Fix:** Replaced `innerHTML` with a safer DOM construction approach using `DOMParser` to parse the HTML string safely.

---

### 2. Sensitive Error Leakage (HIGH — Fixed)

**File:** `scripts/send_newsletter.py:247`

Raw API error response bodies from Buttondown were printed to stderr without redaction. These responses could contain internal API details, rate-limit info, or authentication failure context.

**Fix:** Truncate error body output and redact any fields that might contain tokens or keys.

---

### 3. Missing Content Security Policy (MEDIUM — Fixed)

**File:** `_layouts/default.html`

No CSP headers were present. A CSP meta tag has been added to restrict script sources, style sources, and other resource types to trusted origins only.

---

### 4. Open Redirect in URL Resolver (MEDIUM — Fixed)

**File:** `scripts/generate_gists.py:146-163`

`resolve_google_news_url()` followed redirects to arbitrary domains without validation. An attacker who could manipulate a Google News feed entry could redirect to a malicious domain.

**Fix:** Added domain validation after redirect resolution. Only URLs resolving to non-blocked domains are accepted.

---

### 5. Unvalidated Workflow Dispatch Inputs (MEDIUM — Fixed)

**Files:** `.github/workflows/newsletter.yml`, `.github/workflows/monthly-reports.yml`

The `days` and `month` input parameters were passed to shell commands without strict validation.

**Fix:** Added regex validation (`^[0-9]+$` for days, `^[0-9]{4}-[0-9]{2}$` for month) before passing to Python scripts.

---

### 6. Missing Subresource Integrity (LOW — Documented)

**File:** `_layouts/default.html:105-107`

Google Fonts loaded without SRI hashes. If Google's CDN were compromised, malicious CSS could be injected.

**Recommendation:** Add `integrity` and `crossorigin` attributes to external stylesheet links. Note: Google Fonts URLs change dynamically, making SRI impractical for fonts specifically. Consider self-hosting fonts as an alternative.

---

### 7. No Privacy Opt-out for Google Analytics (LOW — Documented)

**File:** `_layouts/default.html:94-102`

Google Analytics (`G-VDRP3B91C5`) loads for all visitors with no opt-out or cookie consent mechanism.

**Recommendation:** Add a cookie consent banner or conditionally load GA based on user consent, especially for GDPR compliance if European visitors are expected.

---

### 8. Broad Exception Handling (INFO — Documented)

**File:** `scripts/generate_gists.py` (lines 67, 106, 130, 142, 161)

Multiple bare `except Exception` blocks catch all errors indiscriminately. This can mask real issues.

**Recommendation:** Catch specific exceptions (`requests.RequestException`, `urllib.error.URLError`, `json.JSONDecodeError`, etc.) for better debugging and security auditing.

---

## Additional Recommendations

### API Key Management
- Implement API key rotation on a quarterly schedule
- Monitor OpenAI and Buttondown API usage for anomalies
- Consider using GitHub's secret scanning alerts

### Network Security
- All external requests already use HTTPS (good)
- All requests have timeouts configured (good)
- Consider adding a domain allowlist for RSS feed sources

### Dependency Management
- Pin exact dependency versions in `requirements.txt` and `Gemfile`
- Enable Dependabot for automated vulnerability alerts
- Audit `trafilatura` and `feedparser` for known CVEs periodically

### GitHub Actions Hardening
- Pin action versions to SHA hashes instead of tags (e.g., `actions/checkout@<sha>` instead of `@v4`)
- Consider adding `permissions: read-all` as default and only grant `write` where needed
- Enable branch protection on `main` with required reviews

---

## Positive Security Observations

- No hardcoded secrets in source code
- GitHub Actions secrets properly managed via `${{ secrets.* }}`
- No database or server-side user input processing
- Network requests have timeouts
- External links use `rel="noopener noreferrer"`
- UTF-8 encoding consistently specified
- YAML output is properly escaped
- URL deduplication prevents feed poisoning via repeated entries
