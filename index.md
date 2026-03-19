---
layout: default
title: Home
nav: true
nav_order: 1
---

{% include source-logos-bar.html %}

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
      {% assign is_brief = false %}{% if post.categories contains "daily-brief" %}{% assign is_brief = true %}{% endif %}
      <article class="timeline-item{% if is_brief %} timeline-item--daily-brief{% endif %}">
        <span class="timeline-time">{{ post.date | date: "%H:%M" }}</span>
        <div class="timeline-body">
          {% if is_brief %}<span class="daily-brief-pill">DAILY BRIEF &middot; {{ post.date | date: "%b %d" }}</span>{% endif %}
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
      {% assign is_brief = false %}{% if post.categories contains "daily-brief" %}{% assign is_brief = true %}{% endif %}
      <article class="timeline-item{% if is_brief %} timeline-item--daily-brief{% endif %}">
        <span class="timeline-time">{{ post.date | date: "%H:%M" }}</span>
        <div class="timeline-body">
          {% if is_brief %}<span class="daily-brief-pill">DAILY BRIEF &middot; {{ post.date | date: "%b %d" }}</span>{% endif %}
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
      {% assign is_brief = false %}{% if post.categories contains "daily-brief" %}{% assign is_brief = true %}{% endif %}
      <article class="timeline-item{% if is_brief %} timeline-item--daily-brief{% endif %}">
        <span class="timeline-time">{{ post.date | date: "%H:%M" }}</span>
        <div class="timeline-body">
          {% if is_brief %}<span class="daily-brief-pill">DAILY BRIEF &middot; {{ post.date | date: "%b %d" }}</span>{% endif %}
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

  {% include sidebar.html %}
</div>
