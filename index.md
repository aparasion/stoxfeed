---
layout: default
title: Home
nav: true
nav_order: 1
---

<section class="hero">
  <h1>{% include brand-word.html %}</h1>
  <p>{{ site.description }}</p>
</section>

<section class="post-list">
{% for post in site.posts %}

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
