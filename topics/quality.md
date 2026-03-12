---
layout: page
title: "Quality in Localization"
permalink: /topics/quality/
description: "Articles on translation quality evaluation, MQM scoring, human-in-the-loop validation, and AI quality assurance in localization."
---

Coverage of quality evaluation frameworks, human-in-the-loop review, MQM scoring, and the evolving gap between AI and human translation quality.

{% assign quality_signals = "quality-gap-closure,measurable-quality-evaluation" | split: "," %}
{% assign quality_keywords = "mqm,mtpe,post-edit,linguistic quality,quality assurance,quality evaluation,lqa" | split: "," %}

<section class="post-list">
{% for post in site.posts %}
  {% assign dominated = false %}
  {% assign signal_ids_str = post.signal_ids | join: ',' | downcase %}

  {% for sid in quality_signals %}
    {% if signal_ids_str contains sid %}
      {% assign dominated = true %}
    {% endif %}
  {% endfor %}

  {% if dominated == false %}
    {% assign source_text = post.title | append: ' ' | append: post.excerpt | downcase %}
    {% for kw in quality_keywords %}
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
  {% if signal.category == "quality" %}
- [{{ signal.title }}](/signals/#{{ signal.id }})
  {% endif %}
{% endfor %}
