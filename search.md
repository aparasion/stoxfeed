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
    <div class="search-content" data-pagefind-ignore="all">
      <link href="/pagefind/pagefind-ui.css" rel="stylesheet">
      <div id="search-container"></div>
      <script>
        (function () {
          var script = document.createElement('script');
          script.src = '/pagefind/pagefind-ui.js';
          script.onload = function () {
            var ui = new PagefindUI({
              element: '#search-container',
              showSubResults: true,
              showImages: false,
              excerptLength: 30
            });
            var q = new URLSearchParams(window.location.search).get('q');
            if (q) {
              var observer = new MutationObserver(function () {
                var input = document.querySelector('.pagefind-ui__search-input');
                if (input) {
                  observer.disconnect();
                  input.value = q;
                  input.dispatchEvent(new Event('input', { bubbles: true }));
                }
              });
              observer.observe(document.getElementById('search-container'), { subtree: true, childList: true });
            }
          };
          document.head.appendChild(script);
        })();
      </script>
    </div>
  </main>

  {% include sidebar.html %}
</div>
