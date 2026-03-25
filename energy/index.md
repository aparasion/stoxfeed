---
layout: default
title: Energy Intelligence
permalink: /energy/
nav: true
nav_order: 5
description: "Real-time Energy Intelligence Dashboard — oil, natural gas, renewables, equities, and macro impact on global markets."
---

<section class="energy-hero">
  <div class="energy-hero-content">
    <span class="energy-hero-badge">Energy Intelligence</span>
    <h1>Energy Intelligence Dashboard</h1>
    <p class="energy-hero-sub">Track global energy markets, prices, equities, and macro impacts in real time.</p>
  </div>

  {% if site.data.energy %}
  <div class="energy-kpi-bar">
    {% if site.data.energy.commodities.wti %}
    <div class="energy-kpi">
      <span class="energy-kpi-label">WTI Crude</span>
      <span class="energy-kpi-val">${{ site.data.energy.commodities.wti.price }}</span>
      {% if site.data.energy.commodities.wti.change_pct >= 0 %}
      <span class="energy-kpi-change energy-up">+{{ site.data.energy.commodities.wti.change_pct }}%</span>
      {% else %}
      <span class="energy-kpi-change energy-down">{{ site.data.energy.commodities.wti.change_pct }}%</span>
      {% endif %}
    </div>
    {% endif %}
    {% if site.data.energy.commodities.brent %}
    <div class="energy-kpi">
      <span class="energy-kpi-label">Brent</span>
      <span class="energy-kpi-val">${{ site.data.energy.commodities.brent.price }}</span>
      {% if site.data.energy.commodities.brent.change_pct >= 0 %}
      <span class="energy-kpi-change energy-up">+{{ site.data.energy.commodities.brent.change_pct }}%</span>
      {% else %}
      <span class="energy-kpi-change energy-down">{{ site.data.energy.commodities.brent.change_pct }}%</span>
      {% endif %}
    </div>
    {% endif %}
    {% if site.data.energy.commodities.henry_hub %}
    <div class="energy-kpi">
      <span class="energy-kpi-label">Nat Gas</span>
      <span class="energy-kpi-val">${{ site.data.energy.commodities.henry_hub.price }}</span>
      {% if site.data.energy.commodities.henry_hub.change_pct >= 0 %}
      <span class="energy-kpi-change energy-up">+{{ site.data.energy.commodities.henry_hub.change_pct }}%</span>
      {% else %}
      <span class="energy-kpi-change energy-down">{{ site.data.energy.commodities.henry_hub.change_pct }}%</span>
      {% endif %}
    </div>
    {% endif %}
    {% if site.data.energy.equities.etfs.first %}
    {% assign xle = site.data.energy.equities.etfs.first %}
    <div class="energy-kpi">
      <span class="energy-kpi-label">{{ xle.symbol }}</span>
      <span class="energy-kpi-val">${{ xle.price }}</span>
      {% if xle.change_pct >= 0 %}
      <span class="energy-kpi-change energy-up">+{{ xle.change_pct }}%</span>
      {% else %}
      <span class="energy-kpi-change energy-down">{{ xle.change_pct }}%</span>
      {% endif %}
    </div>
    {% endif %}
  </div>
  {% endif %}
</section>

<!-- Module navigation -->
<nav class="energy-module-nav" aria-label="Dashboard modules">
  <button class="energy-tab active" data-module="overview">Overview</button>
  <button class="energy-tab" data-module="oil">Oil Markets</button>
  <button class="energy-tab" data-module="gas">Gas &amp; LNG</button>
  <button class="energy-tab" data-module="renewables">Renewables</button>
  <button class="energy-tab" data-module="equities">Equities</button>
  <button class="energy-tab" data-module="macro">Macro &amp; Geo</button>
  <button class="energy-tab" data-module="news">Energy News</button>
</nav>

{% if site.data.energy %}
{% assign ed = site.data.energy %}

<!-- ================================================================== -->
<!-- OVERVIEW MODULE                                                     -->
<!-- ================================================================== -->
<section class="energy-module" id="module-overview">

  <!-- Market Summary -->
  <div class="energy-card energy-summary-card">
    <h3 class="energy-card-title">Market Summary</h3>
    <p class="energy-summary-text">{{ ed.market_summary }}</p>
    <span class="energy-updated">Updated {{ ed.updated_at | date: "%b %d, %H:%M UTC" }}</span>
  </div>

  <!-- Signals -->
  {% if ed.signals.size > 0 %}
  <div class="energy-card">
    <h3 class="energy-card-title">AI Signals</h3>
    <div class="energy-signals-list">
      {% for sig in ed.signals %}
      <div class="energy-signal energy-signal--{{ sig.level }}">
        <span class="energy-signal-dot"></span>
        <div>
          <strong>{{ sig.label }}</strong>
          <span class="energy-signal-text">{{ sig.text }}</span>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  <!-- Key Events Calendar -->
  {% if ed.key_events.size > 0 %}
  <div class="energy-card">
    <h3 class="energy-card-title">Key Events</h3>
    <div class="energy-events">
      {% for ev in ed.key_events %}
      <div class="energy-event">
        <span class="energy-event-date">{{ ev.date | date: "%b %d" }}</span>
        <div class="energy-event-body">
          <span class="energy-event-badge energy-event-badge--{{ ev.impact }}">{{ ev.impact }}</span>
          <strong>{{ ev.title }}</strong>
          <p>{{ ev.description }}</p>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  <!-- Commodity Sparklines Overview -->
  <div class="energy-spark-grid">
    {% if ed.commodities.wti.history %}
    <div class="energy-card energy-spark-card">
      <div class="energy-spark-header">
        <span class="energy-spark-label">WTI Crude</span>
        <span class="energy-spark-price">${{ ed.commodities.wti.price }}/bbl</span>
        {% if ed.commodities.wti.change_pct >= 0 %}
        <span class="energy-kpi-change energy-up">+{{ ed.commodities.wti.change_pct }}%</span>
        {% else %}
        <span class="energy-kpi-change energy-down">{{ ed.commodities.wti.change_pct }}%</span>
        {% endif %}
      </div>
      <canvas class="energy-sparkline" id="spark-wti" width="280" height="80"></canvas>
    </div>
    {% endif %}
    {% if ed.commodities.brent.history %}
    <div class="energy-card energy-spark-card">
      <div class="energy-spark-header">
        <span class="energy-spark-label">Brent Crude</span>
        <span class="energy-spark-price">${{ ed.commodities.brent.price }}/bbl</span>
        {% if ed.commodities.brent.change_pct >= 0 %}
        <span class="energy-kpi-change energy-up">+{{ ed.commodities.brent.change_pct }}%</span>
        {% else %}
        <span class="energy-kpi-change energy-down">{{ ed.commodities.brent.change_pct }}%</span>
        {% endif %}
      </div>
      <canvas class="energy-sparkline" id="spark-brent" width="280" height="80"></canvas>
    </div>
    {% endif %}
    {% if ed.commodities.henry_hub.history %}
    <div class="energy-card energy-spark-card">
      <div class="energy-spark-header">
        <span class="energy-spark-label">Natural Gas (HH)</span>
        <span class="energy-spark-price">${{ ed.commodities.henry_hub.price }}/MMBtu</span>
        {% if ed.commodities.henry_hub.change_pct >= 0 %}
        <span class="energy-kpi-change energy-up">+{{ ed.commodities.henry_hub.change_pct }}%</span>
        {% else %}
        <span class="energy-kpi-change energy-down">{{ ed.commodities.henry_hub.change_pct }}%</span>
        {% endif %}
      </div>
      <canvas class="energy-sparkline" id="spark-ng" width="280" height="80"></canvas>
    </div>
    {% endif %}
  </div>
</section>

<!-- ================================================================== -->
<!-- OIL MODULE                                                          -->
<!-- ================================================================== -->
<section class="energy-module energy-module--hidden" id="module-oil">
  <div class="energy-section-header">
    <h2>Oil Market Intelligence</h2>
    <p>Live benchmarks, product prices, and major producer equities.</p>
  </div>

  <div class="energy-commodity-grid">
    {% for pair in ed.commodities %}
    {% assign key = pair[0] %}
    {% assign c = pair[1] %}
    {% if c.sector == "oil" %}
    <div class="energy-card energy-commodity-card">
      <span class="energy-commodity-name">{{ c.name }}</span>
      <span class="energy-commodity-symbol">{{ c.symbol }}</span>
      <div class="energy-commodity-price-row">
        <span class="energy-commodity-price">${{ c.price }}</span>
        <span class="energy-commodity-unit">{{ c.unit }}</span>
      </div>
      {% if c.change_pct >= 0 %}
      <span class="energy-kpi-change energy-up">+{{ c.change_pct }}%</span>
      {% else %}
      <span class="energy-kpi-change energy-down">{{ c.change_pct }}%</span>
      {% endif %}
      {% if c.history %}
      <canvas class="energy-sparkline" id="spark-oil-{{ key }}" width="220" height="60" data-series="{{ c.history | jsonify | escape }}"></canvas>
      {% endif %}
    </div>
    {% endif %}
    {% endfor %}
  </div>

  <!-- Oil Majors -->
  <div class="energy-card">
    <h3 class="energy-card-title">Oil Majors &amp; Oilfield Services</h3>
    <div class="ticker-rows">
      {% for e in ed.equities.majors %}
      {% if e.change_pct >= 0 %}{% assign dir = "up" %}{% assign sign = "+" %}{% else %}{% assign dir = "down" %}{% assign sign = "" %}{% endif %}
      <div class="ticker-row" title="{{ e.name }}">
        <span class="ticker-symbol">{{ e.symbol }}</span>
        <span class="ticker-price">${{ e.price }}</span>
        <span class="ticker-val ticker-{{ dir }}">{{ sign }}{{ e.change_pct }}%</span>
      </div>
      {% endfor %}
      {% for e in ed.equities.oilfield %}
      {% if e.change_pct >= 0 %}{% assign dir = "up" %}{% assign sign = "+" %}{% else %}{% assign dir = "down" %}{% assign sign = "" %}{% endif %}
      <div class="ticker-row" title="{{ e.name }}">
        <span class="ticker-symbol">{{ e.symbol }}</span>
        <span class="ticker-price">${{ e.price }}</span>
        <span class="ticker-val ticker-{{ dir }}">{{ sign }}{{ e.change_pct }}%</span>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Supply & Demand Context -->
  <div class="energy-card">
    <h3 class="energy-card-title">Supply &amp; Demand Context</h3>
    <div class="energy-context-grid">
      <div class="energy-context-item">
        <span class="energy-context-label">OPEC+ Output Target</span>
        <span class="energy-context-val">~41.5 mb/d</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">Global Demand Est.</span>
        <span class="energy-context-val">~103.5 mb/d</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">US SPR Level</span>
        <span class="energy-context-val">~370M bbl</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">Brent-WTI Spread</span>
        {% assign spread = ed.commodities.brent.price | minus: ed.commodities.wti.price %}
        <span class="energy-context-val">${{ spread | round: 2 }}</span>
      </div>
    </div>
    <p class="energy-context-note">Key chokepoints: Strait of Hormuz (~21 mb/d), Suez Canal (~5 mb/d), Panama Canal (~0.9 mb/d)</p>
  </div>
</section>

<!-- ================================================================== -->
<!-- GAS & LNG MODULE                                                    -->
<!-- ================================================================== -->
<section class="energy-module energy-module--hidden" id="module-gas">
  <div class="energy-section-header">
    <h2>Natural Gas &amp; LNG Markets</h2>
    <p>Regional benchmarks, LNG flows, and gas-focused equities.</p>
  </div>

  <div class="energy-commodity-grid">
    {% if ed.commodities.henry_hub %}
    {% assign ng = ed.commodities.henry_hub %}
    <div class="energy-card energy-commodity-card">
      <span class="energy-commodity-name">{{ ng.name }}</span>
      <span class="energy-commodity-symbol">{{ ng.symbol }} &middot; US Benchmark</span>
      <div class="energy-commodity-price-row">
        <span class="energy-commodity-price">${{ ng.price }}</span>
        <span class="energy-commodity-unit">{{ ng.unit }}</span>
      </div>
      {% if ng.change_pct >= 0 %}
      <span class="energy-kpi-change energy-up">+{{ ng.change_pct }}%</span>
      {% else %}
      <span class="energy-kpi-change energy-down">{{ ng.change_pct }}%</span>
      {% endif %}
      {% if ng.history %}
      <canvas class="energy-sparkline" id="spark-gas-hh" width="220" height="60" data-series="{{ ng.history | jsonify | escape }}"></canvas>
      {% endif %}
    </div>
    {% endif %}

    <!-- TTF and JKM placeholders (no Yahoo Finance ticker — added via script expansion) -->
    <div class="energy-card energy-commodity-card energy-card--placeholder">
      <span class="energy-commodity-name">EU TTF Natural Gas</span>
      <span class="energy-commodity-symbol">TTF &middot; Europe Benchmark</span>
      <div class="energy-commodity-price-row">
        <span class="energy-commodity-price">--</span>
        <span class="energy-commodity-unit">EUR/MWh</span>
      </div>
      <span class="energy-kpi-change energy-muted">via Refinitiv / ICE</span>
    </div>
    <div class="energy-card energy-commodity-card energy-card--placeholder">
      <span class="energy-commodity-name">JKM LNG</span>
      <span class="energy-commodity-symbol">JKM &middot; Asia-Pacific Benchmark</span>
      <div class="energy-commodity-price-row">
        <span class="energy-commodity-price">--</span>
        <span class="energy-commodity-unit">$/MMBtu</span>
      </div>
      <span class="energy-kpi-change energy-muted">via Platts / ICE</span>
    </div>
  </div>

  <!-- Gas Equities -->
  <div class="energy-card">
    <h3 class="energy-card-title">Gas &amp; LNG Equities</h3>
    <div class="ticker-rows">
      {% for e in ed.equities.gas %}
      {% if e.change_pct >= 0 %}{% assign dir = "up" %}{% assign sign = "+" %}{% else %}{% assign dir = "down" %}{% assign sign = "" %}{% endif %}
      <div class="ticker-row" title="{{ e.name }}">
        <span class="ticker-symbol">{{ e.symbol }}</span>
        <span class="ticker-price">${{ e.price }}</span>
        <span class="ticker-val ticker-{{ dir }}">{{ sign }}{{ e.change_pct }}%</span>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Storage & Infrastructure -->
  <div class="energy-card">
    <h3 class="energy-card-title">Storage &amp; Infrastructure</h3>
    <div class="energy-context-grid">
      <div class="energy-context-item">
        <span class="energy-context-label">EU Gas Storage</span>
        <span class="energy-context-val">~42%</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">US Inventory (EIA)</span>
        <span class="energy-context-val">Watch weekly</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">Global LNG Capacity</span>
        <span class="energy-context-val">~470 MTPA</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">US LNG Export Capacity</span>
        <span class="energy-context-val">~14 Bcf/d</span>
      </div>
    </div>
  </div>
</section>

<!-- ================================================================== -->
<!-- RENEWABLES MODULE                                                   -->
<!-- ================================================================== -->
<section class="energy-module energy-module--hidden" id="module-renewables">
  <div class="energy-section-header">
    <h2>Renewable Energy &amp; Transition</h2>
    <p>Clean energy equities, carbon markets, and global capacity trends.</p>
  </div>

  <!-- Renewable Equities -->
  <div class="energy-card">
    <h3 class="energy-card-title">Clean Energy Equities</h3>
    <div class="ticker-rows">
      {% for e in ed.equities.renewables %}
      {% if e.change_pct >= 0 %}{% assign dir = "up" %}{% assign sign = "+" %}{% else %}{% assign dir = "down" %}{% assign sign = "" %}{% endif %}
      <div class="ticker-row" title="{{ e.name }}">
        <span class="ticker-symbol">{{ e.symbol }}</span>
        <span class="ticker-price">${{ e.price }}</span>
        <span class="ticker-val ticker-{{ dir }}">{{ sign }}{{ e.change_pct }}%</span>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Carbon Markets & Capacity -->
  <div class="energy-dual-grid">
    <div class="energy-card">
      <h3 class="energy-card-title">Carbon Markets</h3>
      <div class="energy-context-grid energy-context-grid--2col">
        <div class="energy-context-item">
          <span class="energy-context-label">EU ETS (EUA)</span>
          <span class="energy-context-val">~64 EUR/t</span>
        </div>
        <div class="energy-context-item">
          <span class="energy-context-label">CA Cap-and-Trade</span>
          <span class="energy-context-val">~38 USD/t</span>
        </div>
      </div>
      <p class="energy-context-note">EU ETS Phase IV in effect; voluntary carbon credits market growing but fragmented.</p>
    </div>
    <div class="energy-card">
      <h3 class="energy-card-title">Global Renewable Capacity</h3>
      <div class="energy-context-grid energy-context-grid--2col">
        <div class="energy-context-item">
          <span class="energy-context-label">Solar</span>
          <span class="energy-context-val">~1,800 GW</span>
        </div>
        <div class="energy-context-item">
          <span class="energy-context-label">Wind</span>
          <span class="energy-context-val">~1,050 GW</span>
        </div>
        <div class="energy-context-item">
          <span class="energy-context-label">Hydro</span>
          <span class="energy-context-val">~1,400 GW</span>
        </div>
        <div class="energy-context-item">
          <span class="energy-context-label">Green H2 Pipeline</span>
          <span class="energy-context-val">~45 GW</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Index Tracking -->
  <div class="energy-card">
    <h3 class="energy-card-title">Index Tracking</h3>
    <div class="energy-context-grid">
      <div class="energy-context-item">
        <span class="energy-context-label">RENIXX World</span>
        <span class="energy-context-val">Top 30 renewables</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">S&amp;P Global Clean Energy</span>
        <span class="energy-context-val">ICLN ETF tracks</span>
      </div>
    </div>
  </div>
</section>

<!-- ================================================================== -->
<!-- EQUITIES MODULE                                                     -->
<!-- ================================================================== -->
<section class="energy-module energy-module--hidden" id="module-equities">
  <div class="energy-section-header">
    <h2>Energy Equities &amp; ETFs</h2>
    <p>Complete sector performance — ETFs, majors, gas producers, renewables, and oilfield services.</p>
  </div>

  <div class="energy-card">
    <h3 class="energy-card-title">All Energy Equities</h3>
    <div class="energy-equities-table-wrap">
      <table class="energy-equities-table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Name</th>
            <th>Category</th>
            <th class="num">Price</th>
            <th class="num">Chg %</th>
          </tr>
        </thead>
        <tbody>
          {% for e in ed.equities.all %}
          <tr>
            <td class="energy-eq-sym">{{ e.symbol }}</td>
            <td>{{ e.name }}</td>
            <td><span class="energy-cat-badge energy-cat-badge--{{ e.category }}">{{ e.category }}</span></td>
            <td class="num">${{ e.price }}</td>
            {% if e.change_pct >= 0 %}
            <td class="num energy-up">+{{ e.change_pct }}%</td>
            {% else %}
            <td class="num energy-down">{{ e.change_pct }}%</td>
            {% endif %}
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Sector Heatmap -->
  <div class="energy-card">
    <h3 class="energy-card-title">Sector Heatmap</h3>
    <div class="energy-heatmap" id="energy-heatmap">
      {% for e in ed.equities.all %}
      <div class="energy-heatmap-cell {% if e.change_pct >= 1 %}hm-strong-up{% elsif e.change_pct >= 0 %}hm-up{% elsif e.change_pct >= -1 %}hm-down{% else %}hm-strong-down{% endif %}" title="{{ e.name }}: {{ e.change_pct }}%">
        <span class="hm-sym">{{ e.symbol }}</span>
        <span class="hm-pct">{% if e.change_pct >= 0 %}+{% endif %}{{ e.change_pct }}%</span>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Index References -->
  <div class="energy-card">
    <h3 class="energy-card-title">Key Energy Indices</h3>
    <div class="energy-context-grid">
      <div class="energy-context-item">
        <span class="energy-context-label">Energy Select Sector (XLE)</span>
        <span class="energy-context-val">${{ ed.equities.etfs.first.price }}</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">S&amp;P Global 1200 Energy</span>
        <span class="energy-context-val">Index</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">DJ Global Oil &amp; Gas (W1ENE)</span>
        <span class="energy-context-val">Index</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">Midstream (AMLP)</span>
        <span class="energy-context-val">Pipelines &amp; Storage</span>
      </div>
    </div>
  </div>
</section>

<!-- ================================================================== -->
<!-- MACRO & GEOPOLITICAL MODULE                                         -->
<!-- ================================================================== -->
<section class="energy-module energy-module--hidden" id="module-macro">
  <div class="energy-section-header">
    <h2>Macroeconomic &amp; Geopolitical Layer</h2>
    <p>How energy markets connect to inflation, interest rates, GDP, and geopolitical risk.</p>
  </div>

  {% if ed.macro_context %}
  <div class="energy-card">
    <h3 class="energy-card-title">Macro Indicators</h3>
    <div class="energy-context-grid">
      <div class="energy-context-item">
        <span class="energy-context-label">US CPI Energy (YoY)</span>
        <span class="energy-context-val">{{ ed.macro_context.us_cpi_energy_pct }}%</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">Fed Funds Rate</span>
        <span class="energy-context-val">{{ ed.macro_context.fed_funds_rate }}%</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">Brent vs S&amp;P 500 (30d r)</span>
        <span class="energy-context-val">{{ ed.macro_context.brent_vs_sp500_30d_corr }}</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">USD Index (DXY)</span>
        <span class="energy-context-val">{{ ed.macro_context.usd_index }}</span>
      </div>
    </div>
    <p class="energy-context-note">{{ ed.macro_context.note }}</p>
  </div>
  {% endif %}

  <div class="energy-dual-grid">
    <div class="energy-card">
      <h3 class="energy-card-title">Geopolitical Risk Factors</h3>
      <ul class="energy-risk-list">
        <li><strong>Middle East tensions</strong> — Hormuz Strait transit risk remains elevated</li>
        <li><strong>Russia-Ukraine</strong> — EU pipeline gas flows near zero; LNG dependence</li>
        <li><strong>OPEC+ unity</strong> — Compliance and quota allocation under pressure</li>
        <li><strong>China demand</strong> — Economic recovery pace uncertain</li>
        <li><strong>US shale</strong> — Capital discipline holding; rig count stable</li>
      </ul>
    </div>
    <div class="energy-card">
      <h3 class="energy-card-title">Scenario Analysis</h3>
      <ul class="energy-risk-list">
        <li><strong>Geopolitical shock</strong> — Brent to $95+ if Hormuz disrupted</li>
        <li><strong>Global recession</strong> — WTI could test $55 on demand destruction</li>
        <li><strong>Renewable acceleration</strong> — Peak oil demand debate intensifies</li>
        <li><strong>OPEC+ unwinding</strong> — Output increase could add $5-10 downside</li>
      </ul>
    </div>
  </div>

  <div class="energy-card">
    <h3 class="energy-card-title">Correlation Matrix Insights</h3>
    <div class="energy-context-grid energy-context-grid--2col">
      <div class="energy-context-item">
        <span class="energy-context-label">Energy vs S&amp;P 500</span>
        <span class="energy-context-val">Moderate negative</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">Energy vs USD</span>
        <span class="energy-context-val">Inverse</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">Oil vs Inflation expectations</span>
        <span class="energy-context-val">Positive</span>
      </div>
      <div class="energy-context-item">
        <span class="energy-context-label">NG vs Weather (HDD/CDD)</span>
        <span class="energy-context-val">Strong positive</span>
      </div>
    </div>
  </div>
</section>

<!-- ================================================================== -->
<!-- ENERGY NEWS MODULE                                                  -->
<!-- ================================================================== -->
<section class="energy-module energy-module--hidden" id="module-news">
  <div class="energy-section-header">
    <h2>Latest Energy News</h2>
    <p>Recent coverage from StoxFeed related to energy markets.</p>
  </div>

  {% assign energy_signals = "oil-price-trajectory,renewable-energy-shift" | split: "," %}
  {% assign energy_keywords = "oil,natural gas,energy,solar,wind,renewable,exxon,chevron,opec,crude,pipeline,utility,clean energy,lng,brent,wti" | split: "," %}
  {% assign energy_posts_arr = "" | split: "" %}

  {% for post in site.posts %}
    {% assign found = false %}
    {% assign signal_ids_str = post.signal_ids | join: ',' | downcase %}
    {% for sid in energy_signals %}
      {% if signal_ids_str contains sid %}{% assign found = true %}{% endif %}
    {% endfor %}
    {% if found == false %}
      {% assign source_text = post.title | append: ' ' | append: post.excerpt | downcase %}
      {% for kw in energy_keywords %}
        {% if source_text contains kw %}{% assign found = true %}{% endif %}
      {% endfor %}
    {% endif %}
    {% if found %}
      {% if energy_posts_arr.size < 15 %}
        {% assign energy_posts_arr = energy_posts_arr | push: post %}
      {% endif %}
    {% endif %}
  {% endfor %}

  {% if energy_posts_arr.size > 0 %}
  <div class="energy-news-list">
    {% for post in energy_posts_arr %}
    <article class="energy-news-item">
      <span class="energy-news-date">{{ post.date | date: "%b %d" }}</span>
      <div class="energy-news-body">
        <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
        <p>{{ post.excerpt | strip_html | truncate: 140 }}</p>
      </div>
    </article>
    {% endfor %}
  </div>
  {% else %}
  <div class="energy-card">
    <p class="energy-empty">No energy-related articles published yet. Check back soon for coverage of oil, gas, and renewable energy markets.</p>
  </div>
  {% endif %}

  <!-- Signal Tracker for Energy -->
  {% assign energy_signal_data = site.data.signals | where_exp: "s", "s.category == 'energy'" %}
  {% if energy_signal_data.size > 0 %}
  <div class="energy-card" style="margin-top: var(--space-5);">
    <h3 class="energy-card-title">Energy Signal Tracker</h3>
    {% for signal in energy_signal_data %}
    {% assign evidence_posts = site.posts | where_exp: "post", "post.signal_ids contains signal.id" %}
    <div class="energy-signal-tracker-item">
      <div class="energy-signal-tracker-header">
        <strong>{{ signal.title }}</strong>
        <span class="status-badge status-badge--{{ signal.current_status }}">{{ signal.current_status }}</span>
      </div>
      <p>{{ signal.description }}</p>
      <span class="energy-signal-evidence">{{ evidence_posts.size }} linked article{% if evidence_posts.size != 1 %}s{% endif %}</span>
    </div>
    {% endfor %}
  </div>
  {% endif %}
</section>

{% endif %}

<!-- Sparkline + Tab JS -->
<script>
(function(){
  // ── Tab switching ──
  var tabs = document.querySelectorAll('.energy-tab');
  var modules = document.querySelectorAll('.energy-module');
  tabs.forEach(function(tab){
    tab.addEventListener('click', function(){
      tabs.forEach(function(t){ t.classList.remove('active'); });
      tab.classList.add('active');
      var target = tab.getAttribute('data-module');
      modules.forEach(function(m){
        if(m.id === 'module-' + target){
          m.classList.remove('energy-module--hidden');
        } else {
          m.classList.add('energy-module--hidden');
        }
      });
      history.replaceState(null, '', '#' + target);
    });
  });
  // Handle initial hash
  var hash = window.location.hash.replace('#','');
  if(hash){
    var matchTab = document.querySelector('.energy-tab[data-module="'+hash+'"]');
    if(matchTab) matchTab.click();
  }

  // ── Sparkline renderer ──
  function drawSparkline(canvasId, data, color){
    var c = document.getElementById(canvasId);
    if(!c || !data || data.length < 2) return;
    var ctx = c.getContext('2d'), W = c.width, H = c.height;
    var padL=30, padR=4, padT=4, padB=14;
    var mn = Math.min.apply(null, data), mx = Math.max.apply(null, data), rng = mx - mn || 1;
    var chartW = W - padL - padR, chartH = H - padT - padB;
    var sx = chartW / (data.length - 1);
    function X(i){ return padL + i * sx; }
    function Y(v){ return padT + (1 - (v - mn) / rng) * chartH; }
    // gradient fill
    var g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, color.replace(')', ',0.25)').replace('rgb', 'rgba'));
    g.addColorStop(1, color.replace(')', ',0)').replace('rgb', 'rgba'));
    ctx.beginPath();
    data.forEach(function(v,i){ i ? ctx.lineTo(X(i),Y(v)) : ctx.moveTo(X(i),Y(v)); });
    ctx.lineTo(X(data.length-1), padT+chartH);
    ctx.lineTo(padL, padT+chartH);
    ctx.closePath();
    ctx.fillStyle = g; ctx.fill();
    // line
    ctx.beginPath();
    data.forEach(function(v,i){ i ? ctx.lineTo(X(i),Y(v)) : ctx.moveTo(X(i),Y(v)); });
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.lineJoin = 'round'; ctx.stroke();
    // labels
    ctx.fillStyle = '#9ca3af'; ctx.font = '9px system-ui,sans-serif';
    ctx.textBaseline = 'top'; ctx.textAlign = 'left';
    ctx.fillText('$'+mn.toFixed(1), 2, padT);
    ctx.textBaseline = 'bottom';
    ctx.fillText('$'+mx.toFixed(1), 2, padT+chartH);
    ctx.textBaseline = 'bottom'; ctx.textAlign = 'left';
    ctx.fillText('30d ago', padL, H);
    ctx.textAlign = 'right';
    ctx.fillText('Today', W - padR, H);
  }

  // Overview sparklines
  {% if site.data.energy.commodities.wti.history %}
  drawSparkline('spark-wti', {{ site.data.energy.commodities.wti.history | jsonify }}, 'rgb(239,68,68)');
  {% endif %}
  {% if site.data.energy.commodities.brent.history %}
  drawSparkline('spark-brent', {{ site.data.energy.commodities.brent.history | jsonify }}, 'rgb(59,130,246)');
  {% endif %}
  {% if site.data.energy.commodities.henry_hub.history %}
  drawSparkline('spark-ng', {{ site.data.energy.commodities.henry_hub.history | jsonify }}, 'rgb(245,158,11)');
  {% endif %}

  // Oil module sparklines (from data attributes)
  document.querySelectorAll('.energy-sparkline[data-series]').forEach(function(canvas){
    try {
      var data = JSON.parse(canvas.getAttribute('data-series'));
      var color = 'rgb(239,68,68)';
      drawSparkline(canvas.id, data, color);
    } catch(e){}
  });
})();
</script>
