---
layout: default
title: Home
nav: true
nav_order: 1
---

<section class="hero-slim">
  <h1>Stock market intelligence, decoded daily</h1>
</section>

<div class="feed-layout">
  <main class="feed-main">

{% comment %}
  Collect the last 3 unique days that have published content.
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

{% comment %} Day 1 {% endcomment %}
<section class="timeline-section">
  <h2 class="timeline-date">{{ site.posts.first.date | date: "%B %d, %Y" }}</h2>
  <div class="timeline-items">
    {% for post in site.posts %}
      {% assign post_day = post.date | date: "%Y-%m-%d" %}
      {% if post_day != day1 %}{% continue %}{% endif %}
      <article class="timeline-item">
        <span class="timeline-time">{{ post.date | date: "%H:%M" }}</span>
        <div class="timeline-body">
          <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
          <p>{{ post.excerpt | strip_html | truncate: 120 }}</p>
        </div>
      </article>
    {% endfor %}
  </div>
</section>

{% comment %} Day 2 {% endcomment %}
{% if day2 != "" %}
<section class="timeline-section">
  {% for post in site.posts %}
    {% assign post_day = post.date | date: "%Y-%m-%d" %}
    {% if post_day == day2 %}
      {% assign day2_display = post.date | date: "%B %d, %Y" %}
      {% break %}
    {% endif %}
  {% endfor %}
  <h2 class="timeline-date">{{ day2_display }}</h2>
  <div class="timeline-items">
    {% for post in site.posts %}
      {% assign post_day = post.date | date: "%Y-%m-%d" %}
      {% if post_day != day2 %}{% continue %}{% endif %}
      <article class="timeline-item">
        <span class="timeline-time">{{ post.date | date: "%H:%M" }}</span>
        <div class="timeline-body">
          <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
          <p>{{ post.excerpt | strip_html | truncate: 120 }}</p>
        </div>
      </article>
    {% endfor %}
  </div>
</section>
{% endif %}

{% comment %} Day 3 {% endcomment %}
{% if day3 != "" %}
<section class="timeline-section">
  {% for post in site.posts %}
    {% assign post_day = post.date | date: "%Y-%m-%d" %}
    {% if post_day == day3 %}
      {% assign day3_display = post.date | date: "%B %d, %Y" %}
      {% break %}
    {% endif %}
  {% endfor %}
  <h2 class="timeline-date">{{ day3_display }}</h2>
  <div class="timeline-items">
    {% for post in site.posts %}
      {% assign post_day = post.date | date: "%Y-%m-%d" %}
      {% if post_day != day3 %}{% continue %}{% endif %}
      <article class="timeline-item">
        <span class="timeline-time">{{ post.date | date: "%H:%M" }}</span>
        <div class="timeline-body">
          <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
          <p>{{ post.excerpt | strip_html | truncate: 120 }}</p>
        </div>
      </article>
    {% endfor %}
  </div>
</section>
{% endif %}

<div class="view-all-cta">
  <a href="/topics/" class="view-all-link">View all articles &rarr;</a>
</div>

  </main>

  <aside class="feed-sidebar">

    <div class="sidebar-widget sidebar-banner">
      <span class="sidebar-label">Sponsored</span>
      <div class="banner-placeholder">
        <span>Ad Space</span>
      </div>
    </div>

    <div class="sidebar-widget sidebar-featured">
      <h4 class="sidebar-title">Featured Analysis</h4>
      <ul class="sidebar-links">
        {% for post in site.posts limit:5 %}
        <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a></li>
        {% endfor %}
      </ul>
    </div>

    <div class="sidebar-widget sidebar-ticker">
      <h4 class="sidebar-title">Market Pulse</h4>
      <div class="ticker-rows">
        <div class="ticker-row"><span class="ticker-symbol">SPY</span><span class="ticker-val ticker-up">+0.42%</span></div>
        <div class="ticker-row"><span class="ticker-symbol">QQQ</span><span class="ticker-val ticker-up">+0.67%</span></div>
        <div class="ticker-row"><span class="ticker-symbol">DIA</span><span class="ticker-val ticker-down">-0.13%</span></div>
        <div class="ticker-row"><span class="ticker-symbol">IWM</span><span class="ticker-val ticker-up">+0.31%</span></div>
        <div class="ticker-row"><span class="ticker-symbol">VIX</span><span class="ticker-val ticker-down">-2.10%</span></div>
      </div>
    </div>

    <div class="sidebar-widget sidebar-newsletter">
      <h4 class="sidebar-title">Stay Informed</h4>
      <p class="sidebar-desc">Get daily market intelligence straight to your inbox.</p>
      <form class="newsletter-form" action="https://buttondown.com/api/emails/embed-subscribe/stoxfeed" method="post">
        <input type="email" name="email" placeholder="you@email.com" required>
        <button type="submit">Subscribe</button>
      </form>
    </div>

    <div class="sidebar-widget sidebar-banner">
      <span class="sidebar-label">Sponsored</span>
      <div class="banner-placeholder banner-tall">
        <span>Ad Space</span>
      </div>
    </div>

  </aside>
</div>
