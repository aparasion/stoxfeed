---
layout: page
title: Monthly Reports
permalink: /monthly-reports/
nav: true
nav_order: 4
---

A curated monthly roundup of the biggest developments across equities, earnings, crypto, macro policy, and the forces shaping global financial markets.
<br />
{% assign monthly_posts = site.posts | where_exp: "post", "post.categories contains 'monthly-summary'" %}
{% if monthly_posts.size > 0 %}
  <section class="post-list">
  {% for post in monthly_posts %}
    {% assign source_text = post.title | append: ' ' | append: post.excerpt | append: ' ' | append: post.content | downcase %}
    {% assign topics = '' %}
    {% if source_text contains 'earnings' or source_text contains 'revenue' or source_text contains 'profit' or source_text contains 'eps' or source_text contains 'quarterly' %}
      {% assign topics = topics | append: 'earnings,' %}
    {% endif %}
    {% if source_text contains 'bitcoin' or source_text contains 'ethereum' or source_text contains 'crypto' or source_text contains 'token' or source_text contains 'blockchain' or source_text contains 'defi' %}
      {% assign topics = topics | append: 'crypto,' %}
    {% endif %}
    {% if source_text contains 'fed' or source_text contains 'federal reserve' or source_text contains 'interest rate' or source_text contains 'inflation' or source_text contains 'ecb' or source_text contains 'central bank' or source_text contains 'monetary' %}
      {% assign topics = topics | append: 'macro,' %}
    {% endif %}
    {% if source_text contains 'ipo' or source_text contains 'acquisition' or source_text contains 'merger' or source_text contains 'deal' or source_text contains 'buyout' or source_text contains 'spinoff' %}
      {% assign topics = topics | append: 'dealflow,' %}
    {% endif %}
    {% if topics == '' %}
      {% assign topics = 'equities' %}
    {% endif %}

    <article class="post-preview" data-topics="{{ topics | strip }}">
      <h2>
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      </h2>

      <p class="post-meta">
        {{ post.date | date: "%B %d, %Y" }}
      </p>

      <p>{{ post.excerpt }}</p>
    </article>
  {% endfor %}
  </section>
{% else %}
  <p>No monthly reports have been published yet.</p>
{% endif %}
