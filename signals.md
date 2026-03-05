---
layout: page
title: Signal Tracker
permalink: /signals/
nav: true
nav_order: 3
---

A living tracker of high-impact claims in localization and AI, with linked evidence from published coverage.

{% for signal in site.data.signals %}
  {% assign evidence_posts = site.posts | where_exp: "post", "post.signal_ids contains signal.id" %}
  <article class="signal-card">
    <h2>{{ signal.title }}</h2>
    <p class="post-meta">Category: {{ signal.category }} · Status: <strong>{{ signal.current_status }}</strong> · First seen: {{ signal.first_seen }}</p>
    <p>{{ signal.description }}</p>

    {% if evidence_posts.size > 0 %}
      <ul class="signal-evidence-list">
        {% for post in evidence_posts limit: 8 %}
          <li>
            <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
            <span class="signal-evidence-meta">({{ post.date | date: "%Y-%m-%d" }}{% if post.signal_stance %}, {{ post.signal_stance }}{% endif %})</span>
          </li>
        {% endfor %}
      </ul>
    {% else %}
      <p>No linked evidence yet.</p>
    {% endif %}
  </article>
{% endfor %}
