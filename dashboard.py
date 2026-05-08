import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="AI Crypto Signal Dashboard",
    page_icon="🚀",
    layout="wide",
)

html_code = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8" />
<style>
body {
  margin:0;
  font-family:Arial, sans-serif;
  background:#0f172a;
  color:white;
}
.wrap { padding:28px; }
h1 { font-size:40px; margin-bottom:8px; }
.sub { color:#cbd5e1; margin-bottom:24px; }
.top {
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:16px;
  margin-bottom:28px;
}
.card {
  background:#111827;
  border:1px solid #334155;
  border-radius:16px;
  padding:20px;
}
.metric-title { color:#cbd5e1; font-weight:bold; }
.metric-value { font-size:34px; font-weight:900; margin-top:10px; }
.controls {
  display:grid;
  grid-template-columns:1fr 1fr 2fr;
  gap:16px;
  margin-bottom:20px;
}
input, select {
  width:100%;
  padding:13px;
  border-radius:10px;
  border:1px solid #334155;
  font-size:15px;
}
button {
  background:#2563eb;
  color:white;
  border:none;
  border-radius:10px;
  padding:13px 20px;
  font-weight:900;
  cursor:pointer;
}
.grid {
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:16px;
  margin-bottom:28px;
}
.coin-card {
  background:#111827;
  border:1px solid #334155;
  border-radius:18px;
  padding:20px;
}
.coin-title {
  color:#38bdf8;
  font-size:24px;
  font-weight:900;
}
.score {
  color:#22c55e;
  font-size:32px;
  font-weight:900;
  margin:12px 0;
}
.row {
  display:flex;
  justify-content:space-between;
  border-bottom:1px solid #334155;
  padding:8px 0;
}
.green { color:#22c55e; font-weight:900; }
.red { color:#ef4444; font-weight:900; }
table {
  width:100%;
  border-collapse:collapse;
  background:white;
  color:#111827;
  border-radius:14px;
  overflow:hidden;
}
th, td {
  padding:10px;
  border:1px solid #e5e7eb;
  font-size:14px;
}
th { background:#f8fafc; }
.status {
  background:#064e3b;
  padding:14px;
  border-radius:12px;
  margin-bottom:16px;
}
.warn {
  background:#7f1d1d;
  padding:14px;
  border-radius:12px;
  margin-bottom:16px;
  display:none;
}
</style>
</head>
<body>
<div class="wrap">
  <h1>🚀 AI Crypto Signal Dashboard</h1>
  <div class="sub">Binance TRY pariteleri tarayıcı üzerinden canlı çekilir. Yatırım tavsiyesi değildir.</div>

  <div class="status" id="status">● Canlı veri hazırlanıyor...</div>
  <div class="warn" id="errorBox"></div>

  <div class="top">
    <div class="card"><div class="metric-title">TARANAN COIN</div><div class="metric-value" id="totalCoins">-</div></div>
    <div class="card"><div class="metric-title">AKTİF SİNYAL</div><div class="metric-value" id="activeSignals">-</div></div>
    <div class="card"><div class="metric-title">EN YÜKSEK SKOR</div><div class="metric-value" id="bestScore">-</div></div>
    <div class="card"><div class="metric-title">ORTALAMA SKOR</div><div class="metric-value" id="avgScore">-</div></div>
  </div>

  <button onclick="loadData()">🔄 Verileri Yenile</button>

  <h2>🔥 En Verimli 3 Fırsat</h2>
  <div class="grid" id="topCards"></div>

  <h2>📋 Profesyonel Sinyal Tablosu</h2>
  <div class="controls">
    <div>
      <label>Minimum Skor</label>
      <select id="minScore" onchange="render()">
        <option value="0">0</option>
        <option value="3">3</option>
        <option value="5" selected>5</option>
        <option value="7">7</option>
        <option value="8">8</option>
      </select>
    </div>
    <div>
      <label>Risk Seviyesi</label>
      <select id="riskFilter" onchange="render()">
        <option value="Tümü">Tümü</option>
        <option value="Düşük-Orta">Düşük-Orta</option>
        <option value="Orta">Orta</option>
        <option value="Yüksek">Yüksek</option>
      </select>
    </div>
    <div>
      <label>Coin ara</label>
      <input id="searchBox" placeholder="BTC, ETH, SOL..." oninput="render()" />
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Sembol</th>
        <th>Skor</th>
        <th>Risk</th>
        <th>Güncel Fiyat</th>
        <th>Alış Bölgesi</th>
        <th>Satış 1</th>
        <th>Satış 2</th>
        <th>Stop</th>
        <th>Değişim %</th>
        <th>Hacim</th>
        <th>Trend</th>
      </tr>
    </thead>
    <tbody id="tableBody"></tbody>
  </table>
</div>

<script>
const API_URL = "https://api.binance.com/api/v3/ticker/24hr";
let coins = [];

function fmtPrice(v) {
  v = Number(v);
  if (!isFinite(v)) return "-";
  if (v >= 1) return v.toLocaleString("tr-TR", {maximumFractionDigits:2}) + " TL";
  return v.toFixed(8) + " TL";
}

function fmtVolume(v) {
  v = Number(v);
  if (v >= 1_000_000_000) return (v/1_000_000_000).toFixed(2) + "B TL";
  if (v >= 1_000_000) return (v/1_000_000).toFixed(2) + "M TL";
  return v.toLocaleString("tr-TR", {maximumFractionDigits:0}) + " TL";
}

function scoreCoin(c) {
  const change = Number(c.priceChangePercent);
  const volume = Number(c.quoteVolume);
  const last = Number(c.lastPrice);
  const low = Number(c.lowPrice);
  const high = Number(c.highPrice);

  let score = 0;

  if (change <= -7) score += 3;
  else if (change <= -4) score += 2;

  if (volume >= 20000000) score += 3;
  else if (volume >= 10000000) score += 2;
  else if (volume >= 3000000) score += 1;

  if (low > 0) {
    const nearLow = (last - low) / low;
    if (nearLow <= 0.03) score += 2;
    else if (nearLow <= 0.07) score += 1;
  }

  if (high > low && last > low && change < 0) {
    const recovery = (last - low) / (high - low);
    if (recovery >= 0.15 && recovery <= 0.55) score += 1;
  }

  return Math.min(score, 8);
}

function risk(score) {
  if (score >= 7) return "Düşük-Orta";
  if (score >= 5) return "Orta";
  return "Yüksek";
}

function trend(change) {
  change = Number(change);
  if (change > 1) return "Yükseliş";
  if (change < -1) return "Düşüş";
  return "Yatay";
}

function enrich(c) {
  const last = Number(c.lastPrice);
  const score = scoreCoin(c);

  return {
    symbol: c.symbol,
    score,
    risk: risk(score),
    price: last,
    entryLow: last * 0.98,
    entryHigh: last * 0.99,
    sell1: last * 1.10,
    sell2: last * 1.18,
    stop: last * 0.95,
    change: Number(c.priceChangePercent),
    volume: Number(c.quoteVolume),
    trend: trend(c.priceChangePercent)
  };
}

async function loadData() {
  const status = document.getElementById("status");
  const errorBox = document.getElementById("errorBox");

  status.innerText = "● Binance verisi çekiliyor...";
  errorBox.style.display = "none";

  try {
    const res = await fetch(API_URL);

    if (!res.ok) {
      throw new Error("Binance API hata kodu: " + res.status);
    }

    const data = await res.json();

    coins = data
      .filter(x => x.symbol && x.symbol.endsWith("TRY"))
      .filter(x => Number(x.lastPrice) > 0)
      .map(enrich)
      .sort((a,b) => b.score - a.score || b.volume - a.volume);

    status.innerText = "● Canlı Veri | Son güncelleme: " + new Date().toLocaleTimeString("tr-TR");

    render();

  } catch (err) {
    errorBox.innerText = "Veri çekme hatası: " + err.message;
    errorBox.style.display = "block";
    status.innerText = "● Veri alınamadı";
  }
}

function renderCards(list) {
  const topCards = document.getElementById("topCards");
  const top3 = list.slice(0,3);

  topCards.innerHTML = top3.map((c, i) => `
    <div class="coin-card">
      <div class="coin-title">#${i+1} ${c.symbol}</div>
      <div class="score">${c.score}/8</div>
      <div class="row"><span>Risk</span><b>${c.risk}</b></div>
      <div class="row"><span>Güncel</span><b>${fmtPrice(c.price)}</b></div>
      <div class="row"><span>Alış Bölgesi</span><b>${fmtPrice(c.entryLow)} - ${fmtPrice(c.entryHigh)}</b></div>
      <div class="row"><span>Satış 1</span><b class="green">${fmtPrice(c.sell1)}</b></div>
      <div class="row"><span>Satış 2</span><b class="green">${fmtPrice(c.sell2)}</b></div>
      <div class="row"><span>Stop</span><b class="red">${fmtPrice(c.stop)}</b></div>
      <div class="row"><span>Değişim</span><b>${c.change.toFixed(2)}%</b></div>
      <div class="row"><span>Hacim</span><b>${fmtVolume(c.volume)}</b></div>
    </div>
  `).join("");
}

function render() {
  const minScore = Number(document.getElementById("minScore").value);
  const riskFilter = document.getElementById("riskFilter").value;
  const search = document.getElementById("searchBox").value.toUpperCase();

  let list = coins.filter(c => c.score >= minScore);

  if (riskFilter !== "Tümü") {
    list = list.filter(c => c.risk === riskFilter);
  }

  if (search) {
    list = list.filter(c => c.symbol.includes(search));
  }

  document.getElementById("totalCoins").innerText = coins.length;
  document.getElementById("activeSignals").innerText = coins.filter(c => c.score >= 5).length;
  document.getElementById("bestScore").innerText = coins.length ? Math.max(...coins.map(c => c.score)) + "/8" : "-";
  document.getElementById("avgScore").innerText = coins.length ? (coins.reduce((a,b)=>a+b.score,0)/coins.length).toFixed(1) : "-";

  renderCards(list);

  document.getElementById("tableBody").innerHTML = list.map(c => `
    <tr>
      <td><b>${c.symbol}</b></td>
      <td>${c.score}</td>
      <td>${c.risk}</td>
      <td>${fmtPrice(c.price)}</td>
      <td>${fmtPrice(c.entryLow)} - ${fmtPrice(c.entryHigh)}</td>
      <td>${fmtPrice(c.sell1)}</td>
      <td>${fmtPrice(c.sell2)}</td>
      <td>${fmtPrice(c.stop)}</td>
      <td>${c.change.toFixed(2)}%</td>
      <td>${fmtVolume(c.volume)}</td>
      <td>${c.trend}</td>
    </tr>
  `).join("");
}

loadData();
setInterval(loadData, 30000);
</script>
</body>
</html>
"""

components.html(html_code, height=1250, scrolling=True)
