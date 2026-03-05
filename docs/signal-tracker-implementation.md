# Signal Tracker – Implementation Proposal

## Objective
Build a **Signal Tracker** that turns announcement-heavy localization/AI news into an evidence-oriented timeline:

- Track important market claims over time (quality, speed, cost, governance).
- Link each claim to supporting/contradicting coverage.
- Provide quick status indicators for decision-makers.

This complements the existing reverse-chronological feed and monthly summaries.

---

## User value

### Localization and AI leaders
- Quickly determine whether vendor/product claims are repeatedly substantiated.
- Reduce time spent reading repetitive launch news.

### Linguists and language quality specialists
- Track where human-in-the-loop validation appears in real deployments.
- Compare quality/governance narratives across providers and months.

### Analysts / researchers
- Revisit a claim and inspect evidence progression over 3–12 months.

---

## Scope (MVP)

1. **Structured signal metadata** in posts.
2. **Central signal registry** containing canonical claim definitions and status.
3. **Signal Tracker page** with per-signal cards and linked evidence posts.
4. **Monthly report integration** block listing newly-updated signals.

---

## Data model

### 1) Add to post front matter

Add these optional fields to post front matter:

```yaml
signal_ids: [quality-gap-closure, governance-in-assistant-workflows]
signal_stance: supports   # supports | contradicts | mixed | mentions
signal_confidence: medium # low | medium | high
```

Notes:
- `signal_ids` allows one post to contribute evidence to multiple signals.
- `signal_stance` is how the post relates to the claim.
- `signal_confidence` captures editorial confidence in the evidence quality.

### 2) Add a canonical signal registry

Create `_data/signals.yml`:

```yaml
- id: quality-gap-closure
  title: AI quality gap can be closed via human validation in workflow
  category: quality
  first_seen: 2026-03-04
  current_status: mixed      # supported | mixed | unclear
  owner: editorial
  description: >-
    Tracks claims that enterprise workflows can close quality gaps in
    AI-generated multilingual content using human verification loops.

- id: governance-in-assistant-workflows
  title: Translation governance is moving into AI assistant interfaces
  category: governance
  first_seen: 2026-03-04
  current_status: supported
  owner: editorial
  description: >-
    Tracks whether translation governance and review controls are being
    integrated directly into assistant/agent workflows.
```

---

## Page architecture

### New page: `signals.md`

Create a top-level page in nav:

```yaml
---
layout: page
title: Signal Tracker
permalink: /signals/
nav: true
nav_order: 3
---
```

Then render cards by looping over `site.data.signals` and resolving matching posts:

```liquid
{% for signal in site.data.signals %}
  {% assign evidence = site.posts | where_exp: "p", "p.signal_ids contains signal.id" %}
  <article class="post-preview">
    <h2>{{ signal.title }}</h2>
    <p class="post-meta">Status: {{ signal.current_status }} · First seen: {{ signal.first_seen }}</p>
    <p>{{ signal.description }}</p>

    {% if evidence.size > 0 %}
      <ul>
        {% for post in evidence limit: 6 %}
          <li>
            <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
            ({{ post.date | date: "%Y-%m-%d" }}, {{ post.signal_stance | default: "mentions" }})
          </li>
        {% endfor %}
      </ul>
    {% else %}
      <p>No evidence posts linked yet.</p>
    {% endif %}
  </article>
{% endfor %}
```

---

## Monthly report integration

At the end of monthly report generation, add a section:

```markdown
## Signal Tracker Updates
- **quality-gap-closure**: status remains **mixed** (3 supporting mentions, 1 contradiction).
- **governance-in-assistant-workflows**: moved to **supported** (4 evidence posts this month).
```

Implementation path:
1. Extend `scripts/generate_monthly_summary.py` to scan posts in the selected month.
2. Count stance occurrences for each signal (`supports`, `contradicts`, `mixed`, `mentions`).
3. Emit a markdown block into the generated monthly report body.

---

## Editorial workflow

1. Publish daily gist post as normal.
2. If relevant, tag with `signal_ids`, `signal_stance`, and `signal_confidence`.
3. Weekly/biweekly: update `_data/signals.yml` `current_status` based on accumulated evidence.
4. Monthly: generated report includes signal update block.

---

## Rollout plan

### Phase 1 (1–2 days)
- Add fields to editorial template/checklist.
- Create `_data/signals.yml` with 5–10 initial signals.
- Create `signals.md` page.

### Phase 2 (2–4 days)
- Backfill high-impact posts from recent 2–3 months with `signal_ids` and `signal_stance`.
- Add lightweight consistency checks (see below).

### Phase 3 (2–3 days)
- Extend monthly generator to append `Signal Tracker Updates`.
- Tune status update rules and confidence thresholds.

---

## Quality checks (automation)

Add a lightweight validation script (or CI step) that verifies:

- Every `signal_id` used by posts exists in `_data/signals.yml`.
- `signal_stance` values are from the allowed enum.
- `signal_confidence` values are from the allowed enum.
- No duplicate signal IDs in `_data/signals.yml`.

This prevents taxonomy drift and broken tracker pages.

---

## Suggested success metrics

- % of monthly posts tagged with at least one `signal_id`.
- Median clicks from `/signals/` to evidence posts.
- Return visits to `/signals/` within 30 days.
- Time-to-insight feedback from editorial/users (“found relevant trend in < 2 minutes”).

---

## Future extensions

- Signal heatmap by month and category (quality/cost/governance/regulatory).
- “Contradictions first” view for critical evaluation.
- Optional newsletter block: “3 signals that changed status this month”.
- API/JSON endpoint for analysts.

