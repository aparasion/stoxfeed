---
layout: default
title: Topics
permalink: /topics/
nav: true
nav_order: 1
description: "Browse all stock market and financial articles by topic — technology, healthcare, energy, finance, and crypto."
---

<section class="topics-hero">
  <h1>All Articles by Topic</h1>
  <p class="topics-subtitle">Browse the full archive — filter by topic or view everything chronologically.</p>
</section>

<section class="topic-filter-panel" aria-label="Filter by topic">
  <div class="topic-filter-buttons" role="group" aria-label="Topic filters">
    <button class="topic-pill active" data-topic="all">All</button>
    <button class="topic-pill" data-topic="technology">Technology</button>
    <button class="topic-pill" data-topic="healthcare">Healthcare</button>
    <button class="topic-pill" data-topic="energy">Energy</button>
    <button class="topic-pill" data-topic="finance">Finance</button>
    <button class="topic-pill" data-topic="crypto">Crypto</button>
  </div>
</section>

{% comment %}
  Define signal IDs and keywords for each topic.
  We compute topic assignments at build time and store as data-topics attribute.
{% endcomment %}

{% assign technology_signals = "ai-stocks-momentum,tech-earnings-trend" | split: "," %}
{% assign technology_keywords = "nvidia,apple,microsoft,google,alphabet,meta,amazon,ai chip,semiconductor,cloud computing,saas,software,tech stock,artificial intelligence" | split: "," %}

{% assign healthcare_signals = "biotech-pipeline-catalyst,pharma-ma-wave" | split: "," %}
{% assign healthcare_keywords = "biotech,pharmaceutical,fda approval,clinical trial,drug pipeline,healthcare stock,medical device,gene therapy,vaccine,hospital" | split: "," %}

{% assign energy_signals = "oil-price-trajectory,renewable-energy-shift" | split: "," %}
{% assign energy_keywords = "oil,natural gas,energy stock,solar,wind,renewable,exxon,chevron,opec,crude,pipeline,utility,clean energy,ev,electric vehicle" | split: "," %}

{% assign finance_signals = "fed-rate-trajectory,bank-earnings-cycle" | split: "," %}
{% assign finance_keywords = "fed,interest rate,bank,jpmorgan,goldman sachs,morgan stanley,insurance,fintech,treasury,bond,yield,inflation,monetary policy" | split: "," %}

{% assign crypto_signals = "bitcoin-institutional-adoption,defi-market-growth" | split: "," %}
{% assign crypto_keywords = "bitcoin,ethereum,crypto,blockchain,defi,nft,coinbase,binance,stablecoin,token,mining,web3,digital asset" | split: "," %}

<section class="articles-section">
  <div class="post-grid" id="topics-post-grid">
    {% for post in site.posts %}
      {% assign topics_list = "" %}
      {% assign signal_ids_str = post.signal_ids | join: ',' | downcase %}
      {% assign source_text = post.title | append: ' ' | append: post.excerpt | downcase %}

      {% comment %} Technology {% endcomment %}
      {% assign match = false %}
      {% for sid in technology_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in technology_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "technology " %}{% endif %}

      {% comment %} Healthcare {% endcomment %}
      {% assign match = false %}
      {% for sid in healthcare_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in healthcare_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "healthcare " %}{% endif %}

      {% comment %} Energy {% endcomment %}
      {% assign match = false %}
      {% for sid in energy_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in energy_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "energy " %}{% endif %}

      {% comment %} Finance {% endcomment %}
      {% assign match = false %}
      {% for sid in finance_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in finance_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "finance " %}{% endif %}

      {% comment %} Crypto {% endcomment %}
      {% assign match = false %}
      {% for sid in crypto_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in crypto_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "crypto " %}{% endif %}

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
