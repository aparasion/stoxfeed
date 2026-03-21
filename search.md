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
  <p class="hero-subtitle">Search across signals, long-form articles, daily briefs, and market intelligence.</p>
</section>

<div class="feed-layout">
  <main class="feed-main">
    <div class="search-content">
      <div class="search-box">
        <input type="text" id="search-input" class="search-input" placeholder="Search articles, signals…" autocomplete="off" autofocus>
      </div>
      <p id="search-status" class="search-status">Loading search index…</p>
      <div id="search-results"></div>
    </div>
  </main>

  {% include sidebar.html %}
</div>

<script>
(function () {
  var data = null;
  var input = document.getElementById('search-input');
  var resultsEl = document.getElementById('search-results');
  var status = document.getElementById('search-status');
  var debounceTimer = null;

  fetch('/search.json')
    .then(function (r) { return r.json(); })
    .then(function (d) {
      data = d;
      var total = (d.posts ? d.posts.length : 0) + (d.articles ? d.articles.length : 0) + (d.signals ? d.signals.length : 0);
      status.textContent = total + ' items indexed — start typing to search.';
      var q = new URLSearchParams(window.location.search).get('q');
      if (q) { input.value = q; doSearch(q); }
    })
    .catch(function () {
      status.textContent = 'Could not load search index. Please try refreshing.';
    });

  input.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () { doSearch(input.value); }, 200);
  });

  function scoreItem(item, terms, fields) {
    var total = 0;
    for (var t = 0; t < terms.length; t++) {
      var term = terms[t];
      for (var f = 0; f < fields.length; f++) {
        var val = fields[f].val;
        if (val && val.indexOf(term) !== -1) total += fields[f].weight;
      }
    }
    return total;
  }

  function doSearch(query) {
    if (!data) return;
    var q = query.trim().toLowerCase();

    if (q.length < 2) {
      resultsEl.innerHTML = '';
      var total = data.posts.length + data.articles.length + data.signals.length;
      status.textContent = total + ' items indexed — start typing to search.';
      return;
    }

    var terms = q.split(/\s+/);

    // Score signals
    var signals = [];
    for (var s = 0; s < data.signals.length; s++) {
      var sig = data.signals[s];
      var sc = scoreItem(sig, terms, [
        { val: (sig.title || '').toLowerCase(), weight: 10 },
        { val: (sig.description || '').toLowerCase(), weight: 5 },
        { val: (sig.category || '').toLowerCase(), weight: 2 }
      ]);
      if (sc > 0) signals.push({ item: sig, score: sc });
    }
    signals.sort(function (a, b) { return b.score - a.score; });

    // Score Long Game articles
    var articles = [];
    for (var a = 0; a < data.articles.length; a++) {
      var art = data.articles[a];
      var sa = scoreItem(art, terms, [
        { val: (art.title || '').toLowerCase(), weight: 10 },
        { val: (art.subtitle || '').toLowerCase(), weight: 5 }
      ]);
      if (sa > 0) articles.push({ item: art, score: sa });
    }
    articles.sort(function (a2, b2) { return b2.score - a2.score; });

    // Score posts
    var posts = [];
    for (var p = 0; p < data.posts.length; p++) {
      var post = data.posts[p];
      var sp = scoreItem(post, terms, [
        { val: (post.title || '').toLowerCase(), weight: 10 },
        { val: (post.excerpt || '').toLowerCase(), weight: 3 },
        { val: (post.publisher || '').toLowerCase(), weight: 2 },
        { val: (post.categories || []).join(' ').toLowerCase(), weight: 1 }
      ]);
      if (sp > 0) posts.push({ item: post, score: sp });
    }
    posts.sort(function (a3, b3) { return b3.score - a3.score; });

    var totalResults = signals.length + articles.length + posts.length;
    if (totalResults === 0) {
      resultsEl.innerHTML = '';
      status.textContent = 'No results for \u201c' + query.trim() + '\u201d.';
      return;
    }

    status.textContent = totalResults + ' result' + (totalResults !== 1 ? 's' : '') + ' for \u201c' + query.trim() + '\u201d';

    var html = '';

    // Signals section
    if (signals.length > 0) {
      html += '<div class="search-section">';
      html += '<h2 class="search-section-title">Signals</h2>';
      for (var i = 0; i < signals.length; i++) {
        var r = signals[i].item;
        html += '<a href="/signals/#' + escapeAttr(r.id) + '" class="search-result">';
        html += '<div class="search-result-header">';
        html += '<h3 class="search-result-title">' + highlightTerms(r.title, terms) + '</h3>';
        html += '<span class="search-pill search-pill--' + escapeAttr(r.category) + '">' + escapeHtml(r.category) + '</span>';
        html += '<span class="search-pill search-pill--status">' + escapeHtml(r.status) + '</span>';
        html += '</div>';
        html += '<p class="search-result-excerpt">' + highlightTerms(r.description, terms) + '</p>';
        html += '</a>';
      }
      html += '</div>';
    }

    // The Long Game section
    if (articles.length > 0) {
      html += '<div class="search-section">';
      html += '<h2 class="search-section-title">The Long Game</h2>';
      for (var j = 0; j < articles.length; j++) {
        var ra = articles[j].item;
        html += '<a href="' + escapeAttr(ra.url) + '" class="search-result">';
        html += '<div class="search-result-header">';
        html += '<h3 class="search-result-title">' + highlightTerms(ra.title, terms) + '</h3>';
        html += '</div>';
        if (ra.subtitle) html += '<p class="search-result-excerpt">' + highlightTerms(ra.subtitle, terms) + '</p>';
        if (ra.date) html += '<p class="search-result-meta">' + escapeHtml(ra.date) + '</p>';
        html += '</a>';
      }
      html += '</div>';
    }

    // Articles section
    if (posts.length > 0) {
      var MAX = 50;
      var shown = posts.slice(0, MAX);
      html += '<div class="search-section">';
      html += '<h2 class="search-section-title">Articles' + (posts.length > MAX ? ' <span class="search-section-count">(showing ' + MAX + ' of ' + posts.length + ')</span>' : '') + '</h2>';
      for (var k = 0; k < shown.length; k++) {
        var rp = shown[k].item;
        html += '<a href="' + escapeAttr(rp.url) + '" class="search-result">';
        html += '<div class="search-result-header">';
        html += '<h3 class="search-result-title">' + highlightTerms(rp.title, terms) + '</h3>';
        html += '<span class="search-pill search-pill--source">' + escapeHtml(rp.publisher) + '</span>';
        html += '</div>';
        html += '<p class="search-result-meta">' + escapeHtml(rp.date) + '</p>';
        html += '<p class="search-result-excerpt">' + highlightTerms(rp.excerpt, terms) + '</p>';
        html += '</a>';
      }
      html += '</div>';
    }

    resultsEl.innerHTML = html;
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

  function escapeAttr(str) { return escapeHtml(str); }
})();
</script>
