---
layout: page
title: Monthly Reports
permalink: /monthly-reports/
nav: true
nav_order: 2
---

## Monthly Reports

A curated monthly roundup of the biggest developments across translation, localization, and language technology.

{% assign monthly_posts = site.posts | where_exp: "post", "post.categories contains 'monthly-summary'" %}

{% if monthly_posts.size > 0 %}
  <section class="post-list">
  {% for post in monthly_posts %}
    <article class="post-preview">
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
