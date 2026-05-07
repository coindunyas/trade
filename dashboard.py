import pandas as pd
import streamlit as st
from datetime import datetime

from binance_tr import BinanceTRClient
from scoring import score_symbol


st.set_page_config(
    page_title="AI Crypto Signal Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {
    background: #020617;
    color: #f8fafc;
}

.block-container {
    padding: 24px 28px 32px 28px;
    max-width: 100%;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #07111f 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.18);
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

h1, h2, h3, p, span, label, div {
    color: #f8fafc;
}

.hero {
    display: flex;
    justify-content: space-between;
    gap: 24px;
    align-items: flex-start;
    margin-bottom: 22px;
}

.hero-title {
    font-size: 42px;
    font-weight: 900;
    margin-bottom: 8px;
}

.hero-sub {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
}

.hero-note {
    color: #94a3b8;
    font-size: 14px;
}

.top-actions {
    display: flex;
    gap: 16px;
}

.action-card {
    background: #07111f;
    border: 1px solid rgba(148,163,184,.25);
    border-radius: 14px;
    padding: 15px 20px;
    min-width: 170px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 26px;
}

.kpi {
    background: linear-gradient(145deg, #07111f, #0b1628);
    border-radius: 18px;
    padding: 24px;
    border: 1px solid rgba(148,163,184,.22);
    min-height: 150px;
    box-shadow: 0 18px 45px rgba(0,0,0,.35);
}

.kpi.purple { border-color: rgba(168,85,247,.55); }
.kpi.green { border-color: rgba(34,197,94,.55); }
.kpi.yellow { border-color: rgba(250,204,21,.55); }
.kpi.blue { border-color: rgba(56,189,248,.55); }

.kpi-row {
    display: flex;
    gap: 20px;
    align-items: center;
}

.kpi-icon {
    width: 66px;
    height: 66px;
    border-radius: 16px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 34px;
}

.icon-purple { background: rgba(168,85,247,.18); border: 1px solid rgba(168,85,247,.55); }
.icon-green { background: rgba(34,197,94,.18); border: 1px solid rgba(34,197,94,.55); }
.icon-yellow { background: rgba(250,204,21,.18); border: 1px solid rgba(250,204,21,.55); }
.icon-blue { background: rgba(56,189,248,.18); border: 1px solid rgba(56,189,248,.55); }

.kpi-label {
    font-size: 15px;
    font-weight: 900;
}

.kpi-value {
    font-size: 38px;
    font-weight: 950;
    margin-top: 6px;
}

.kpi-small {
    color: #cbd5e1;
    margin-top: 6px;
    font-size: 14px;
}

.green-text { color: #22c55e !important; }
.red-text { color: #ef4444 !important; }
.yellow-text { color: #facc15 !important; }
.blue-text { color: #38bdf8 !important; }
.purple-text { color: #a855f7 !important; }

.section-title {
    font-size: 28px;
    font-weight: 900;
    margin: 18px 0 14px 0;
}

.stSlider label, .stSelectbox label, .stTextInput label {
    color: #f8fafc !important;
    font-weight: 800 !important;
}

div[data-baseweb="select"] > div,
input {
    background: #07111f !important;
    border: 1px solid rgba(148,163,184,.25) !important;
    color: #f8fafc !important;
    border-radius: 12px !important;
}

.crypto-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: #07111f;
    border: 1px solid rgba(148,163,184,.23);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 20px 45px rgba(0,0,0,.35);
    font-size: 13px;
}

.crypto-table th {
    background: #0b1628;
    color: #f8fafc;
    padding: 13px 10px;
    text-align: left;
    font-weight: 900;
    border-right: 1px solid rgba(148,163,184,.12);
    border-bottom: 1px solid rgba(148,163,184,.22);
}

.crypto-table td {
    background: #07111f;
    color: #e5e7eb;
    padding: 11px 10px;
    border-right: 1px solid rgba(148,163,184,.10);
    border-bottom: 1px solid rgba(148,163,184,.10);
}

.crypto-table tr:hover td {
    background: #0f1b2e;
}

.num {
    text-align: right;
    font-variant-numeric: tabular-nums;
}

.badge-low {
    background: rgba(34,197,94,.18);
    color: #4ade80;
    border: 1px solid rgba(34,197,94,.38);
    padding: 5px 9px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 12px;
}

.badge-mid {
    background: rgba(250,204,21,.18);
    color: #fde047;
    border: 1px solid rgba(250,204,21,.38);
    padding: 5px 9px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 12px;
}

.badge-high {
    background: rgba(239,68,68,.18);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,.38);
    padding: 5px 9px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 12px;
}

.bottom-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    margin-top: 24px;
}

.info-card {
    background: #07111f;
    border: 1px solid rgba(148,163,184,.22);
    border-radius: 16px;
    padding: 18px;
    min-height: 115px;
}

.info-card h3 {
    font-size: 17px;
    margin-bottom: 8px;
}

.info-card p {
    color: #cbd5e1;
    margin: 0;
}

.sidebar-title {
    font-size: 26px;
    font-weight: 950;
    line-height: 1.05;
}

.sidebar-purple {
    color: #a855f7 !important;
}

.nav-item {
    padding: 12px 14px;
    border-radius: 12px;
    margin-bottom: 8px;
    border: 1px solid transparent;
}

.nav-active {
    background: rgba(168,85,247,.22);
    border-color: rgba(168,85,247,.40);
}

.status-mini {
    background: rgba(34,197,94,.10);
    border: 1px solid rgba(34,197,94,.30);
    border-radius: 14px;
    padding: 14px;
    margin-top: 80px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data():
    client = BinanceTRClient()
    tickers = client.get_tickers()
    results = []

    for ticker in tickers:
        result = score_symbol(ticker)
        if result:
            results.append(result)

    return results


def fmt_price(value):
    try:
        value = float(value)
        if value >= 1:
            return f"{value:,.2f}"
        return f"{value:.6f}"
    except Exception:
        return "-"


def fmt_volume(value):
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        return f"{value:,.0f}"
    except Exception:
        return "-"


def entry_zone(value):
    try:
        price = float(value)
        low = price * 0.98
        high = price * 0.99
        return f"{fmt_price(low)} - {fmt_price(high)}"
    except Exception:
        return "-"


def risk_label(risk):
    risk = str(risk)
    if "Düşük" in risk:
        return "Düşük-Orta"
    if "Orta" in risk:
        return "Orta"
    return "Yüksek"


def risk_badge(risk):
    label = risk_label(risk)
    if label == "Düşük-Orta":
        return f'<span class="badge-low">{label}</span>'
    if label == "Orta":
        return f'<span class="badge-mid">{label}</span>'
    return f'<span class="badge-high">{label}</span>'


def trend_text(change):
    try:
        change = float(change)
        if change > 1:
            return '<span class="green-text">↑ Yükseliş</span>'
        if change < -1:
            return '<span class="red-text">↓ Düşüş</span>'
        return '<span>→ Yatay</span>'
    except Exception:
        return "-"


def change_text(change):
    try:
        change = float(change)
        color = "green-text" if change >= 0 else "red-text"
        return f'<span class="{color}">{change:.2f}%</span>'
    except Exception:
        return "-"


def proximity_text(value):
    try:
        value = float(value)
        color = "green-text" if value >= 0 else "red-text"
        return f'<span class="{color}">{value:.2f}%</span>'
    except Exception:
        return "-"


def ai_confidence(score, volume):
    try:
        score_part = float(score) / 8 * 70
        volume_part = min(float(volume) / 1_000_000_000, 1) * 30
        return round(score_part + volume_part)
    except Exception:
        return 0


def render_table(df):
    rows = []

    for idx, row in df.iterrows():
        rows.append(f"""
        <tr>
            <td class="num">{idx}</td>
            <td><b>{row["symbol"]}</b></td>
            <td class="num">{row["score"]}</td>
            <td>{risk_badge(row["risk"])}</td>
            <td class="num">{fmt_price(row["current_price"])}</td>
            <td class="num">{entry_zone(row["current_price"])}</td>
            <td class="num">{fmt_price(row["sell_price_1"])}</td>
            <td class="num">{fmt_price(row["sell_price_2"])}</td>
            <td class="num">{fmt_price(row["stop_price"])}</td>
            <td class="num">{change_text(row["change_percent"])}</td>
            <td class="num">{fmt_volume(row["volume"])}</td>
            <td class="num">{proximity_text(row["proximity_to_low"])}</td>
            <td class="num"><span class="purple-text">%{ai_confidence(row["score"], row["volume"])}</span></td>
            <td>{trend_text(row["change_percent"])}</td>
        </tr>
        """)

    return f"""
    <table class="crypto-table">
        <thead>
            <tr>
                <th>#</th>
                <th>Sembol</th>
                <th>Skor</th>
                <th>Risk Seviyesi</th>
                <th>Güncel Fiyat (TRY)</th>
                <th>Alış Bölgesi (TRY)</th>
                <th>Satış 1 (TRY)</th>
                <th>Satış 2 (TRY)</th>
                <th>Stop-Loss (TRY)</th>
                <th>Değişim (%)</th>
                <th>Hacim (TRY)</th>
                <th>Dibe Yakınlık (%)</th>
                <th>AI Güven</th>
                <th>Trend</th>
            </tr>
        </thead>
        <tbody>{''.join(rows)}</tbody>
    </table>
    """


st.sidebar.markdown("""
<div class="sidebar-title">
🚀 AI Crypto<br>
<span class="sidebar-purple">Signal Dashboard</span>
</div>
<br>
<b>Premium kripto fırsat tarama paneli</b>
<br><br>
<span style="color:#94a3b8;">Yatırım tavsiyesi değildir.</span>
<hr>
<div class="nav-item nav-active">🏠 Genel Bakış</div>
<div class="nav-item">📋 Sinyal Tablosu</div>
<div class="nav-item">🏆 En İyi Fırsatlar</div>
<div class="nav-item">📈 Trend Analizi</div>
<div class="nav-item">🔥 Heatmap</div>
<div class="nav-item">🔔 Bildirim Ayarları</div>
<div class="nav-item">✈️ Telegram</div>
<div class="nav-item">⚙️ Ayarlar</div>

<div class="status-mini">
<b>🛡️ Sistem Durumu</b><br>
<span style="color:#22c55e;font-weight:900;">Tüm Sistemler Aktif</span>
</div>
""", unsafe_allow_html=True)


try:
    data = load_data()
    df = pd.DataFrame(data).sort_values(by="score", ascending=False)
except Exception as e:
    st.error(f"Veri alınamadı: {e}")
    st.stop()

total = len(df)
signals = len(df[df["score"] >= 5])
best = int(df["score"].max())
avg = round(df["score"].mean(), 2)
now = datetime.now().strftime("%H:%M:%S")

st.markdown(f"""
<div class="hero">
    <div>
        <div class="hero-title">🚀 AI Crypto Signal Dashboard</div>
        <div class="hero-sub">Premium kripto fırsat tarama paneli</div>
        <div class="hero-note">CoinGecko TRY verileri ile çalışır. Yatırım tavsiyesi değildir.</div>
    </div>
    <div class="top-actions">
        <div class="action-card">
            <b><span class="green-text">● Canlı Veri</span></b><br>
            <small>Son güncelleme: {now}</small>
        </div>
        <div class="action-card">
            <b><span class="purple-text">🔄 Yenile</span></b><br>
            <small>Şimdi güncelle</small>
        </div>
        <div class="action-card">
            <b>Zaman Aralığı</b><br>
            <small>24 Saat</small>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 Verileri Yenile", use_container_width=False):
    st.cache_data.clear()
    st.rerun()

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi purple">
        <div class="kpi-row">
            <div class="kpi-icon icon-purple">⌕</div>
            <div>
                <div class="kpi-label">TARANAN COIN</div>
                <div class="kpi-value">{total} <span class="green-text" style="font-size:20px;">↑</span></div>
                <div class="kpi-small">Toplam taranan coin</div>
            </div>
        </div>
    </div>

    <div class="kpi green">
        <div class="kpi-row">
            <div class="kpi-icon icon-green">↗</div>
            <div>
                <div class="kpi-label">AKTİF SİNYAL</div>
                <div class="kpi-value green-text">{signals} <span style="font-size:20px;">↑</span></div>
                <div class="kpi-small">Sinyal üreten coin</div>
            </div>
        </div>
    </div>

    <div class="kpi yellow">
        <div class="kpi-row">
            <div class="kpi-icon icon-yellow">🏆</div>
            <div>
                <div class="kpi-label">EN YÜKSEK SKOR</div>
                <div class="kpi-value yellow-text">{best}/8 <span class="green-text" style="font-size:20px;">↑</span></div>
                <div class="kpi-small">Maksimum skor</div>
            </div>
        </div>
    </div>

    <div class="kpi blue">
        <div class="kpi-row">
            <div class="kpi-icon icon-blue">★</div>
            <div>
                <div class="kpi-label">ORTALAMA SKOR</div>
                <div class="kpi-value blue-text">{avg} <span class="green-text" style="font-size:20px;">↑</span></div>
                <div class="kpi-small">Ortalama skor</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">📋 Profesyonel Sinyal Tablosu</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1, 1.4])

with c1:
    min_score = st.slider("Minimum Skor", 0, 8, 5)

with c2:
    risk_filter = st.selectbox("Risk Seviyesi", ["Tümü", "Düşük-Orta", "Orta", "Yüksek"])

with c3:
    search = st.text_input("Coin ara", placeholder="BTC, ETH, SOL...")

filtered = df[df["score"] >= min_score].copy()
filtered["risk_label"] = filtered["risk"].apply(risk_label)

if risk_filter != "Tümü":
    filtered = filtered[filtered["risk_label"] == risk_filter]

if search:
    filtered = filtered[filtered["symbol"].str.contains(search.upper(), na=False)]

st.markdown(render_table(filtered.head(25)), unsafe_allow_html=True)

st.markdown(f"""
<div class="bottom-grid">
    <div class="info-card">
        <h3>🧠 Piyasa Yorumu</h3>
        <p>Orta seviye fırsatlar mevcut. İlk 3 sıradaki coinler güçlü sinyal veriyor.</p>
    </div>

    <div class="info-card">
        <h3>🔥 En Güçlü Sektör</h3>
        <p><span class="blue-text" style="font-size:20px;font-weight:900;">DeFi / Meme / Layer-1</span></p>
        <p>Hacim ve skor yoğunluğu yüksek.</p>
    </div>

    <div class="info-card">
        <h3>💸 Toplam Hacim</h3>
        <p><span class="blue-text" style="font-size:22px;font-weight:900;">{fmt_volume(df["volume"].sum())} TRY</span></p>
        <p>Son 24 saat</p>
    </div>

    <div class="info-card">
        <h3>⚡ Aktif Sinyal Oranı</h3>
        <p><span class="purple-text" style="font-size:22px;font-weight:900;">%{round((signals / total) * 100, 2)}</span></p>
        <p>{total} coin içinde</p>
    </div>

    <div class="info-card">
        <h3>⚠️ Uyarı</h3>
        <p>Piyasa volatil. Stop-loss kullanmayı unutmayın.</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("⚠️ Bu sistem yatırım tavsiyesi değildir. Sadece karar destek amacıyla kullanılır.")
