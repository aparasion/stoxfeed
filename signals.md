---
layout: page
title: Signal Tracker
permalink: /signals/
nav: true
nav_order: 2
---

A living tracker of high-impact claims in localization and AI, with linked evidence from published coverage.

<div class="signal-accordion-list">
  {% for signal in site.data.signals %}
    {% assign evidence_posts = site.posts | where_exp: "post", "post.signal_ids contains signal.id" %}
    <details class="signal-accordion" id="{{ signal.id }}">
      <summary class="signal-accordion__summary">
        <span class="signal-tile__category">{{ signal.category }}</span>
        <span class="signal-accordion__title">{{ signal.title }}</span>
        <span class="signal-accordion__meta">
          <span class="status-badge status-badge--{{ signal.current_status }}">{{ signal.current_status }}</span>
          <span class="signal-tile__count">{{ evidence_posts.size }} post{% if evidence_posts.size != 1 %}s{% endif %}</span>
          <span class="signal-accordion__chevron">▾</span>
        </span>
      </summary>
      <div class="signal-accordion__body">
        <p class="post-meta">Category: {{ signal.category }} · First seen: {{ signal.first_seen }}</p>
        <p>{{ signal.description }}</p>
        {% if evidence_posts.size > 0 %}
          <ul class="signal-evidence-list">
            {% for post in evidence_posts limit: 8 %}
              <li>
                <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
                <span class="signal-evidence-meta">({{ post.date | date: "%Y-%m-%d" }}{% if post.signal_stance %}, <span class="stance-badge stance-badge--{{ post.signal_stance }}">{{ post.signal_stance }}</span>{% endif %})</span>
              </li>
            {% endfor %}
          </ul>
        {% else %}
          <p class="signal-card__empty">No linked evidence yet.</p>
        {% endif %}
      </div>
    </details>
  {% endfor %}
</div>
