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
    <div class="search-content">
      <div class="search-box">
        <input type="text" id="search-input" class="search-input" placeholder="Search articles…" autocomplete="off" autofocus>
      </div>
      <p id="search-status" class="search-status">Loading search index…</p>
      <div id="search-results"></div>
    </div>
  </main>

  {% include sidebar.html %}
</div>

<script>
(function () {
  var index = null;
  var input = document.getElementById('search-input');
  var results = document.getElementById('search-results');
  var status = document.getElementById('search-status');
  var debounceTimer = null;

  fetch('/search.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      index = data;
      status.textContent = index.length + ' articles indexed — start typing to search.';
      var q = new URLSearchParams(window.location.search).get('q');
      if (q) {
        input.value = q;
        doSearch(q);
      }
    })
    .catch(function () {
      status.textContent = 'Could not load search index. Please try refreshing.';
    });

  input.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      doSearch(input.value);
    }, 200);
  });

  function doSearch(query) {
    if (!index) return;
    var q = query.trim().toLowerCase();

    if (q.length < 2) {
      results.innerHTML = '';
      status.textContent = index.length + ' articles indexed — start typing to search.';
      return;
    }

    var terms = q.split(/\s+/);
    var scored = [];

    for (var i = 0; i < index.length; i++) {
      var item = index[i];
      var title = (item.title || '').toLowerCase();
      var excerpt = (item.excerpt || '').toLowerCase();
      var publisher = (item.publisher || '').toLowerCase();
      var cats = (item.categories || []).join(' ').toLowerCase();
      var score = 0;

      for (var t = 0; t < terms.length; t++) {
        var term = terms[t];
        if (title.indexOf(term) !== -1) score += 10;
        if (excerpt.indexOf(term) !== -1) score += 3;
        if (publisher.indexOf(term) !== -1) score += 2;
        if (cats.indexOf(term) !== -1) score += 1;
      }

      if (score > 0) {
        scored.push({ item: item, score: score });
      }
    }

    scored.sort(function (a, b) { return b.score - a.score; });

    var MAX = 50;
    var shown = scored.slice(0, MAX);

    if (shown.length === 0) {
      results.innerHTML = '';
      status.textContent = 'No results for "' + query.trim() + '".';
      return;
    }

    status.textContent = scored.length + ' result' + (scored.length !== 1 ? 's' : '') + ' for "' + query.trim() + '"' + (scored.length > MAX ? ' (showing first ' + MAX + ')' : '');

    var html = '';
    for (var j = 0; j < shown.length; j++) {
      var r = shown[j].item;
      var highlightedTitle = highlightTerms(r.title, terms);
      var highlightedExcerpt = highlightTerms(r.excerpt, terms);
      html += '<a href="' + escapeAttr(r.url) + '" class="search-result">';
      html += '<h3 class="search-result-title">' + highlightedTitle + '</h3>';
      html += '<p class="search-result-meta">' + escapeHtml(r.date) + ' · ' + escapeHtml(r.publisher) + '</p>';
      html += '<p class="search-result-excerpt">' + highlightedExcerpt + '</p>';
      html += '</a>';
    }
    results.innerHTML = html;
  }

  function highlightTerms(text, terms) {
    var safe = escapeHtml(text);
    for (var i = 0; i < terms.length; i++) {
      if (terms[i].length < 2) continue;
      var escaped = terms[i].replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      safe = safe.replace(new RegExp('(' + escaped + ')', 'gi'), '<mark>$1</mark>');
    }
    return safe;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function escapeAttr(str) {
    return escapeHtml(str);
  }
})();
</script>
