---
layout: default
title: Daily Briefs
permalink: /daily-briefs/
nav: true
nav_order: 2
description: "End-of-day market briefs synthesizing each day's financial news into actionable summaries."
---

<section class="topics-hero">
  <h1>Daily Briefs</h1>
  <p class="topics-subtitle">End-of-day market summaries — what happened and what to expect next.</p>
</section>

<div class="feed-layout">
  <main class="feed-main">
    <section class="articles-section">
      <div class="post-grid">
        {% for post in site.posts %}
          {% if post.categories contains "daily-brief" %}
            <article class="post-card post-card--daily-brief">
              <span class="daily-brief-pill">DAILY BRIEF &middot; {{ post.date | date: "%b %d, %Y" }}</span>
              <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}</p>
              <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
              <p>{{ post.excerpt | strip_html | truncate: 140 }}</p>
              <span class="read-more">Read more &rarr;</span>
            </article>
          {% endif %}
        {% endfor %}
      </div>
    </section>
  </main>

  {% include sidebar.html %}
</div>
