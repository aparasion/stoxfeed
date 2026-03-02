---
layout: default
title: Home
nav: true
---

<section class="hero">
  <h1>Translation and localization news</h1>
  <p>Articles and information digest delivered in on place.</p>
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
