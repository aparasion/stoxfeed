---
layout: page
title: "AI Governance & Regulation"
permalink: /topics/governance/
description: "Articles on AI governance, EU AI Act compliance, regulatory fragmentation, and language-related policy developments in localization."
---

Coverage of AI governance frameworks, regulatory compliance, the EU AI Act, and how diverging regional policies affect localization workflows.

{% assign gov_signals = "governance-in-ai-workflows,regulatory-fragmentation" | split: "," %}
{% assign gov_keywords = "eu ai act,ai regulation,compliance requirement,language law,ai governance,guardrail" | split: "," %}

<section class="post-list">
{% for post in site.posts %}
  {% assign dominated = false %}
  {% assign signal_ids_str = post.signal_ids | join: ',' | downcase %}

  {% for sid in gov_signals %}
    {% if signal_ids_str contains sid %}
      {% assign dominated = true %}
    {% endif %}
  {% endfor %}

  {% if dominated == false %}
    {% assign source_text = post.title | append: ' ' | append: post.excerpt | downcase %}
    {% for kw in gov_keywords %}
      {% if source_text contains kw %}
        {% assign dominated = true %}
      {% endif %}
    {% endfor %}
  {% endif %}

  {% if dominated %}
  <article class="post-preview">
    <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
    <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}</p>
    <p>{{ post.excerpt }}</p>
  </article>
  {% endif %}
{% endfor %}
</section>

### Tracked signals

{% for signal in site.data.signals %}
  {% if signal.category == "governance" %}
- [{{ signal.title }}](/signals/#{{ signal.id }})
  {% endif %}
{% endfor %}
