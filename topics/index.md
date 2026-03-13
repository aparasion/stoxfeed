---
layout: default
title: Topics
permalink: /topics/
nav: true
nav_order: 2
description: "Browse all localization industry articles by topic — quality, operations, governance, market dynamics, and strategy."
---

<section class="topics-hero">
  <h1>All Articles by Topic</h1>
  <p class="topics-subtitle">Browse the full archive — filter by topic or view everything chronologically.</p>
</section>

<section class="topic-filter-panel" aria-label="Filter by topic">
  <div class="topic-filter-buttons" role="group" aria-label="Topic filters">
    <button class="topic-pill active" data-topic="all">All</button>
    <button class="topic-pill" data-topic="quality">Quality</button>
    <button class="topic-pill" data-topic="operations">Operations</button>
    <button class="topic-pill" data-topic="governance">Governance</button>
    <button class="topic-pill" data-topic="market">Market</button>
    <button class="topic-pill" data-topic="strategy">Strategy</button>
  </div>
</section>

{% comment %}
  Define signal IDs and keywords for each topic.
  We compute topic assignments at build time and store as data-topics attribute.
{% endcomment %}

{% assign quality_signals = "quality-gap-closure,measurable-quality-evaluation" | split: "," %}
{% assign quality_keywords = "mqm,mtpe,post-edit,linguistic quality,quality assurance,quality evaluation,lqa" | split: "," %}

{% assign ops_signals = "localization-operating-system,translation-memory-obsolescence,agentic-localization-workflows,multimodal-content-localization" | split: "," %}
{% assign ops_keywords = "translation memory,tms,cat tool,localization platform,dubbing,subtitl,agentic,ai agent" | split: "," %}

{% assign gov_signals = "governance-in-ai-workflows,regulatory-fragmentation" | split: "," %}
{% assign gov_keywords = "eu ai act,ai regulation,compliance requirement,language law,ai governance,guardrail" | split: "," %}

{% assign market_signals = "human-post-editing-contraction" | split: "," %}
{% assign market_keywords = "freelance translator,translator demand,post-editor,language services market,translation rates" | split: "," %}

{% assign strategy_signals = "localization-first-content-design" | split: "," %}
{% assign strategy_keywords = "internationalization,i18n,locale-aware,transcreation,localization-first" | split: "," %}

<section class="articles-section">
  <div class="post-grid" id="topics-post-grid">
    {% for post in site.posts %}
      {% assign topics_list = "" %}
      {% assign signal_ids_str = post.signal_ids | join: ',' | downcase %}
      {% assign source_text = post.title | append: ' ' | append: post.excerpt | downcase %}

      {% comment %} Quality {% endcomment %}
      {% assign match = false %}
      {% for sid in quality_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in quality_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "quality " %}{% endif %}

      {% comment %} Operations {% endcomment %}
      {% assign match = false %}
      {% for sid in ops_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in ops_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "operations " %}{% endif %}

      {% comment %} Governance {% endcomment %}
      {% assign match = false %}
      {% for sid in gov_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in gov_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "governance " %}{% endif %}

      {% comment %} Market {% endcomment %}
      {% assign match = false %}
      {% for sid in market_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in market_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "market " %}{% endif %}

      {% comment %} Strategy {% endcomment %}
      {% assign match = false %}
      {% for sid in strategy_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in strategy_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "strategy " %}{% endif %}

      {% assign topics_trimmed = topics_list | strip %}

      <article class="post-card" data-topics="{{ topics_trimmed }}">
        <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}</p>
        <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
        <p>{{ post.excerpt | strip_html | truncate: 140 }}</p>
        <span class="read-more">Read more &rarr;</span>
      </article>
    {% endfor %}
  </div>
</section>
