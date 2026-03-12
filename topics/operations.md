---
layout: page
title: "Localization Operations"
permalink: /topics/operations/
description: "Articles on TMS platforms, translation memory, AI agents, multimodal localization, and end-to-end localization operating systems."
---

Coverage of localization tooling, TMS platforms, translation memory evolution, agentic workflows, multimodal content, and the shift toward end-to-end localization operating systems.

{% assign ops_signals = "localization-operating-system,translation-memory-obsolescence,agentic-localization-workflows,multimodal-content-localization" | split: "," %}
{% assign ops_keywords = "translation memory,tms,cat tool,localization platform,dubbing,subtitl,agentic,ai agent" | split: "," %}

<section class="post-list">
{% for post in site.posts %}
  {% assign dominated = false %}
  {% assign signal_ids_str = post.signal_ids | join: ',' | downcase %}

  {% for sid in ops_signals %}
    {% if signal_ids_str contains sid %}
      {% assign dominated = true %}
    {% endif %}
  {% endfor %}

  {% if dominated == false %}
    {% assign source_text = post.title | append: ' ' | append: post.excerpt | downcase %}
    {% for kw in ops_keywords %}
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
  {% if signal.category == "operations" %}
- [{{ signal.title }}](/signals/#{{ signal.id }})
  {% endif %}
{% endfor %}
