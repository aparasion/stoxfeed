---
layout: default
title: Search
permalink: /search/
nav: true
nav_order: 2
description: Search all StoxFeed articles, daily briefs, and market intelligence.
---

<section class="hero-slim">
  <h1>Search StoxFeed</h1>
  <p class="hero-subtitle">Full-text search across all articles, daily briefs, and market intelligence.</p>
</section>

<div class="feed-layout">
  <main class="feed-main">
    <div class="page-content" data-pagefind-ignore="all">
      <link href="/pagefind/pagefind-ui.css" rel="stylesheet">
      <div id="search-container"></div>
      <script>
        (function () {
          var script = document.createElement('script');
          script.src = '/pagefind/pagefind-ui.js';
          script.onload = function () {
            new PagefindUI({
              element: '#search-container',
              showSubResults: true,
              showImages: false,
              excerptLength: 30
            });
          };
          document.head.appendChild(script);
        })();
      </script>
    </div>
  </main>

  {% include sidebar.html %}
</div>
