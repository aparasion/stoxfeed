---
layout: page
title: Monthly Reports
permalink: /monthly-reports/
nav: true
nav_order: 4
---

A curated monthly roundup of the biggest developments across translation, localization, and language technology.
<br />
{% assign monthly_posts = site.posts | where_exp: "post", "post.categories contains 'monthly-summary'" %}
{% if monthly_posts.size > 0 %}
  <section class="post-list">
  {% for post in monthly_posts %}
    {% assign source_text = post.title | append: ' ' | append: post.excerpt | append: ' ' | append: post.content | downcase %}
    {% assign topics = '' %}
    {% if source_text contains 'ai' or source_text contains 'llm' or source_text contains 'machine learning' or source_text contains 'neural' %}
      {% assign topics = topics | append: 'ai,' %}
    {% endif %}
    {% if source_text contains 'lsp' or source_text contains 'language service' or source_text contains 'vendor' or source_text contains 'provider' %}
      {% assign topics = topics | append: 'lsp,' %}
    {% endif %}
    {% if source_text contains 'platform' or source_text contains 'api' or source_text contains 'tool' or source_text contains 'workflow' or source_text contains 'software' %}
      {% assign topics = topics | append: 'tooling,' %}
    {% endif %}
    {% if source_text contains 'regulation' or source_text contains 'law' or source_text contains 'compliance' or source_text contains 'government' or source_text contains 'commission' or source_text contains 'policy' %}
      {% assign topics = topics | append: 'policy,' %}
    {% endif %}
    {% if topics == '' %}
      {% assign topics = 'tooling' %}
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
