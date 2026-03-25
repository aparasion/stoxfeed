---
layout: page
title: "The Long Game"
nav: true
nav_order: 6
---

<div class="the-long-game-list">
  {% assign sorted_articles = site.articles | sort: 'date' | reverse %}
  {% for article in sorted_articles %}
  <div class="long-game-card">
    <p class="long-game-meta">{{ article.date | date: "%B %d, %Y" }}{% if article.issue_line %} &nbsp;·&nbsp; {{ article.issue_line }}{% endif %}</p>
    <h2><a href="{{ article.url | relative_url }}">{{ article.title }}</a></h2>
    {% if article.subtitle %}<p class="long-game-subtitle">{{ article.subtitle }}</p>{% endif %}
    <a href="{{ article.url | relative_url }}" class="read-more">Read article →</a>
  </div>
  {% else %}
  <p class="muted">No articles published yet.</p>
  {% endfor %}
</div>
