---
layout: default
title: Home
nav: true
nav_order: 1
---

<section class="hero">
  <div class="hero-content">
    <h1>Longevity science, decoded daily</h1>
    <p class="hero-subtitle">Curated coverage of healthspan research, longevity therapeutics, and the science of living longer — tracked through the signals that matter.</p>
    <div class="hero-stats">
      <div class="hero-stat">
        <span class="hero-stat-number">{{ site.posts.size }}</span>
        <span class="hero-stat-label">Articles</span>
      </div>
      <div class="hero-stat">
        <span class="hero-stat-number">{{ site.data.signals.size }}</span>
        <span class="hero-stat-label">Signals</span>
      </div>
      <div class="hero-stat">
        <span class="hero-stat-number">5</span>
        <span class="hero-stat-label">Topics</span>
      </div>
    </div>
  </div>
</section>

{% comment %}
  Collect the last 3 unique days that have published content.
  Posts are already sorted newest-first by Jekyll.
{% endcomment %}
{% assign day_count = 0 %}
{% assign current_day = "" %}
{% assign day1 = "" %}
{% assign day2 = "" %}
{% assign day3 = "" %}

{% for post in site.posts %}
  {% assign post_day = post.date | date: "%Y-%m-%d" %}
  {% if post_day != current_day %}
    {% assign current_day = post_day %}
    {% assign day_count = day_count | plus: 1 %}
    {% if day_count == 1 %}
      {% assign day1 = post_day %}
    {% elsif day_count == 2 %}
      {% assign day2 = post_day %}
    {% elsif day_count == 3 %}
      {% assign day3 = post_day %}
    {% endif %}
  {% endif %}
  {% if day_count > 3 %}{% break %}{% endif %}
{% endfor %}

{% comment %} Day 1: Most recent — featured first article + grid of remaining {% endcomment %}
{% assign day1_first = true %}
<section class="day-section">
  <h2 class="day-header">{{ site.posts.first.date | date: "%B %d, %Y" }}</h2>

  {% for post in site.posts %}
    {% assign post_day = post.date | date: "%Y-%m-%d" %}
    {% if post_day != day1 %}{% continue %}{% endif %}

    {% if day1_first %}
      {% assign day1_first = false %}
      <article class="featured-article reveal">
        <span class="featured-badge">Latest</span>
        <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
        <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}</p>
        <p>{{ post.excerpt | strip_html | truncate: 200 }}</p>
      </article>

      <div class="post-grid reveal-stagger">
    {% else %}
      <article class="post-card">
        <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}<span class="new-badge">NEW</span></p>
        <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
        <p>{{ post.excerpt | strip_html | truncate: 140 }}</p>
        <span class="read-more">Read more &rarr;</span>
      </article>
    {% endif %}
  {% endfor %}
      </div>
</section>

{% comment %} Day 2 {% endcomment %}
{% if day2 != "" %}
<section class="day-section">
  {% for post in site.posts %}
    {% assign post_day = post.date | date: "%Y-%m-%d" %}
    {% if post_day == day2 %}
      {% assign day2_display = post.date | date: "%B %d, %Y" %}
      {% break %}
    {% endif %}
  {% endfor %}
  <h2 class="day-header">{{ day2_display }}</h2>
  <div class="post-grid reveal-stagger">
    {% for post in site.posts %}
      {% assign post_day = post.date | date: "%Y-%m-%d" %}
      {% if post_day != day2 %}{% continue %}{% endif %}
      <article class="post-card">
        <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}</p>
        <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
        <p>{{ post.excerpt | strip_html | truncate: 140 }}</p>
        <span class="read-more">Read more &rarr;</span>
      </article>
    {% endfor %}
  </div>
</section>
{% endif %}

{% comment %} Day 3 {% endcomment %}
{% if day3 != "" %}
<section class="day-section">
  {% for post in site.posts %}
    {% assign post_day = post.date | date: "%Y-%m-%d" %}
    {% if post_day == day3 %}
      {% assign day3_display = post.date | date: "%B %d, %Y" %}
      {% break %}
    {% endif %}
  {% endfor %}
  <h2 class="day-header">{{ day3_display }}</h2>
  <div class="post-grid reveal-stagger">
    {% for post in site.posts %}
      {% assign post_day = post.date | date: "%Y-%m-%d" %}
      {% if post_day != day3 %}{% continue %}{% endif %}
      <article class="post-card">
        <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}</p>
        <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
        <p>{{ post.excerpt | strip_html | truncate: 140 }}</p>
        <span class="read-more">Read more &rarr;</span>
      </article>
    {% endfor %}
  </div>
</section>
{% endif %}

<div class="view-all-cta">
  <a href="/topics/" class="view-all-link">View all articles &rarr;</a>
</div>
