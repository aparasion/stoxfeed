---
layout: page
title: "Insights"
nav: true
nav_order: 4
---

<div class="insights-list">
  {% assign sorted_articles = site.articles | sort: 'date' | reverse %}
  {% for article in sorted_articles %}
  <div class="insight-card">
    <p class="insight-meta">{{ article.date | date: "%B %d, %Y" }}{% if article.issue_line %} &nbsp;·&nbsp; {{ article.issue_line }}{% endif %}</p>
    <h2><a href="{{ article.url | relative_url }}">{{ article.title }}</a></h2>
    {% if article.subtitle %}<p class="insight-subtitle">{{ article.subtitle }}</p>{% endif %}
    <a href="{{ article.url | relative_url }}" class="read-more">Read article →</a>
  </div>
  {% else %}
  <p class="muted">No articles published yet.</p>
  {% endfor %}
</div>
