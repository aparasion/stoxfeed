---
layout: default
title: Topics
permalink: /topics/
nav: true
nav_order: 2
description: "Browse all longevity and healthspan articles by topic — therapeutics, biomarkers, nutrition, technology, and policy."
---

<section class="topics-hero">
  <h1>All Articles by Topic</h1>
  <p class="topics-subtitle">Browse the full archive — filter by topic or view everything chronologically.</p>
</section>

<section class="topic-filter-panel" aria-label="Filter by topic">
  <div class="topic-filter-buttons" role="group" aria-label="Topic filters">
    <button class="topic-pill active" data-topic="all">All</button>
    <button class="topic-pill" data-topic="therapeutics">Therapeutics</button>
    <button class="topic-pill" data-topic="biomarkers">Biomarkers</button>
    <button class="topic-pill" data-topic="nutrition">Nutrition</button>
    <button class="topic-pill" data-topic="technology">Technology</button>
    <button class="topic-pill" data-topic="policy">Policy</button>
  </div>
</section>

{% comment %}
  Define signal IDs and keywords for each topic.
  We compute topic assignments at build time and store as data-topics attribute.
{% endcomment %}

{% assign therapeutics_signals = "senolytic-clinical-validation,rapamycin-healthspan-extension" | split: "," %}
{% assign therapeutics_keywords = "senolytic,rapamycin,dasatinib,quercetin,fisetin,anti-aging drug,longevity therapeutic,age-related disease,clinical trial,drug candidate" | split: "," %}

{% assign biomarkers_signals = "epigenetic-clock-adoption,blood-biomarker-panels" | split: "," %}
{% assign biomarkers_keywords = "epigenetic clock,biological age,dna methylation,horvath,grimace,dunedinpace,biomarker,proteomics,metabolomics,aging clock" | split: "," %}

{% assign nutrition_signals = "caloric-restriction-mimetics,gut-microbiome-aging" | split: "," %}
{% assign nutrition_keywords = "caloric restriction,intermittent fasting,nad+,nmn,nicotinamide,spermidine,microbiome,diet,nutrition,metformin,resveratrol" | split: "," %}

{% assign tech_signals = "ai-drug-discovery-aging,gene-therapy-aging" | split: "," %}
{% assign tech_keywords = "gene therapy,crispr,ai drug discovery,machine learning,yamanaka,telomerase,reprogramming,computational biology,wearable" | split: "," %}

{% assign policy_signals = "longevity-regulatory-frameworks,longevity-funding-surge" | split: "," %}
{% assign policy_keywords = "fda aging,regulatory,funding,venture capital,investment,government grant,clinical pathway,policy,nih,aging research funding" | split: "," %}

<section class="articles-section">
  <div class="post-grid" id="topics-post-grid">
    {% for post in site.posts %}
      {% assign topics_list = "" %}
      {% assign signal_ids_str = post.signal_ids | join: ',' | downcase %}
      {% assign source_text = post.title | append: ' ' | append: post.excerpt | downcase %}

      {% comment %} Therapeutics {% endcomment %}
      {% assign match = false %}
      {% for sid in therapeutics_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in therapeutics_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "therapeutics " %}{% endif %}

      {% comment %} Biomarkers {% endcomment %}
      {% assign match = false %}
      {% for sid in biomarkers_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in biomarkers_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "biomarkers " %}{% endif %}

      {% comment %} Nutrition {% endcomment %}
      {% assign match = false %}
      {% for sid in nutrition_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in nutrition_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "nutrition " %}{% endif %}

      {% comment %} Technology {% endcomment %}
      {% assign match = false %}
      {% for sid in tech_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in tech_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "technology " %}{% endif %}

      {% comment %} Policy {% endcomment %}
      {% assign match = false %}
      {% for sid in policy_signals %}{% if signal_ids_str contains sid %}{% assign match = true %}{% endif %}{% endfor %}
      {% if match == false %}{% for kw in policy_keywords %}{% if source_text contains kw %}{% assign match = true %}{% endif %}{% endfor %}{% endif %}
      {% if match %}{% assign topics_list = topics_list | append: "policy " %}{% endif %}

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
