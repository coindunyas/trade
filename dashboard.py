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
    background: radial-gradient(circle at top left, #0b1220 0%, #020617 45%, #030712 100%);
    color: #f8fafc;
}

.block-container {
    padding-top: 1.2rem;
    padding-left: 1.4rem;
    padding-right: 1.4rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
    border-right: 1px solid rgba(148,163,184,.18);
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

h1, h2, h3, p, span, label, div {
    color: #f8fafc;
}

.hero-title {
    font-size: 48px;
    font-weight: 950;
    line-height: 1.05;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 22px;
    font-weight: 800;
    color: #e5e7eb;
}

.hero-caption {
    color: #94a3b8;
    font-size: 14px;
}

.status-box {
    background: rgba(15,23,42,.88);
    border: 1px solid rgba(148,163,184,.22);
    border-radius: 16px;
    padding: 18px 22px;
    box-shadow: 0 14px 40px rgba(0,0,0,.35);
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-top: 24px;
    margin-bottom: 28px;
}

.kpi-card {
    position: relative;
    min-height: 145px;
    border-radius: 20px;
    padding: 24px;
    overflow: hidden;
    background: linear-gradient(145deg, rgba(15,23,42,.96), rgba(2,6,23,.92));
    border: 1px solid rgba(148,163,184,.23);
    box-shadow: 0 18px 55px rgba(0,0,0,.36);
}

.kpi-card.purple { border-color: rgba(168,85,247,.45); box-shadow: 0 0 28px rgba(168,85,247,.12); }
.kpi-card.green { border-color: rgba(34,197,94,.42); box-shadow: 0 0 28px rgba(34,197,94,.10); }
.kpi-card.yellow { border-color: rgba(250,204,21,.42); box-shadow: 0 0 28px rgba(250,204,21,.10); }
.kpi-card.blue { border-color: rgba(56,189,248,.42); box-shadow: 0 0 28px rgba(56,189,248,.10); }

.kpi-icon {
    float: left;
    width: 64px;
    height: 64px;
    border-radius: 16px;
    margin-right: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
}

.icon-purple { background: rgba(168,85,247,.18); color: #c084fc; border: 1px solid rgba(168,85,247,.45); }
.icon-green { background: rgba(34,197,94,.18); color: #86efac; border: 1px solid rgba(34,197,94,.45); }
.icon-yellow { background: rgba(250,204,21,.18); color: #fde047; border: 1px solid rgba(250,204,21,.45); }
.icon-blue { background: rgba(56,189,248,.18); color: #7dd3fc; border: 1px solid rgba(56,189,248,.45); }

.kpi-label {
    font-size: 15px;
    font-weight: 900;
    letter-spacing: .3px;
    color: #f8fafc;
}

.kpi-value {
    font-size: 44px;
    font-weight: 950;
    margin-top: 8px;
    line-height: 1;
}

.value-green { color: #4ade80; }
.value-yellow { color: #facc15; }
.value-blue { color: #38bdf8; }
.value-white { color: #ffffff; }

.kpi-small {
    margin-top: 12px;
    font-size: 14px;
    color: #cbd5e1;
}

.section-title {
    font-size: 30px;
    font-weight: 950;
    margin-top: 20px;
    margin-bottom: 18px;
}

.filter-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1.4fr;
    gap: 16px;
    margin-bottom: 16px;
}

div[data-baseweb="select"] > div {
    background: rgba(15,23,42,.92) !important;
    border: 1px solid rgba(148,163,184,.28) !important;
    color: white !important;
    border-radius: 12px !important;
}

input {
    background: rgba(15,23,42,.92) !important;
    color: white !important;
    border-radius: 12px !important;
}

.stSlider label, .stSelectbox label, .stTextInput label {
    color: white !important;
    font-weight: 800 !important;
}

.crypto-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: rgba(15,23,42,.80);
    border: 1px solid rgba(148,163,184,.25);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 20px 55px rgba(0,0,0,.38);
    font-size: 14px;
}

.crypto-table th {
    background: rgba(15,23,42,.98);
    color: #f8fafc;
    padding: 14px 12px;
    text-align: left;
    font-weight: 900;
    border-bottom: 1px solid rgba(148,163,184,.25);
    border-right: 1px solid rgba(148,163,184,.12);
}

.crypto-table td {
    color: #e5e7eb;
    padding: 12px 12px;
    border-bottom: 1px solid rgba(148,163,184,.12);
    border-right: 1px solid rgba(148,163,184,.08);
    background: rgba(2,6,23,.45);
}

.crypto-table tr:hover td {
    background: rgba(30,41,59,.85);
}

.num {
    text-align: right !important;
    font-variant-numeric: tabular-nums;
}

.badge-low {
    background: rgba(34,197,94,.18);
    color: #4ade80;
    border: 1px solid rgba(34,197,94,.35);
    padding: 5px 9px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 12px;
}

.badge-mid {
    background: rgba(250,204,21,.18);
    color: #fde047;
    border: 1px solid rgba(250,204,21,.35);
    padding: 5px 9px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 12px;
}

.badge-high {
    background: rgba(239,68,68,.18);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,.35);
    padding: 5px 9px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 12px;
}

.negative { color: #ef4444 !important; font-weight: 900; }
.positive { color: #22c55e !important; font-weight: 900; }
.confidence { color: #c084fc !important; font-weight: 900; }
.trend-down { color: #ef4444 !important; font-weight: 900; }
.trend-up { color: #22c55e !important; font-weight: 900; }

.bottom-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: 24px;
}

.info-card {
    background: rgba(15,23,42,.88);
    border: 1px solid rgba(148,163,184,.22);
    border-radius: 18px;
    padding: 18px;
    min-height: 110px;
    box-shadow: 0 14px 40px rgba(0,0,0,.30);
}

.info-card h3 {
    font-size: 18px;
    margin-bottom: 8px;
}

.info-card p {
    color: #cbd5e1;
    margin: 0;
}

hr {
    border-color: rgba(148,163,184,.15);
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


def entry_zone(current_price):
    price = float(current_price)
    low = price * 0.98
    high = price * 0.99
    return f"{fmt_price(low)} - {fmt_price(high)}"


def trend_text(change):
    change = float(change)
    if change > 1:
        return "Yükseliş"
    if change < -1:
        return "Düşüş"
    return "Yatay"


def confidence(score, volume):
    score_part = float(score) / 8 * 70
    volume_part = min(float(volume) / 1_000_000_000, 1) * 30
    return round(score_part + volume_part)


def risk_label(risk):
    risk = str(risk)
    if "Düşük" in risk:
        return "Düşük-Orta"
    if "Orta" in risk:
        return "Orta"
    return "Yüksek"


def risk_html(risk):
    label = risk_label(risk)
    if label == "Düşük-Orta":
        return f'<span class="badge-low">{label}</span>'
    if label == "Orta":
        return f'<span class="badge-mid">{label}</span>'
    return f'<span class="badge-high">{label}</span>'


def change_html(value):
    value = float(value)
    css = "positive" if value >= 0 else "negative"
    return f'<span class="{css}">{value:.2f}%</span>'


def proximity_html(value):
    try:
        value = float(value)
        css = "positive" if value >= 0 else "negative"
        return f'<span class="{css}">{value:.2f}%</span>'
    except Exception:
        return "-"


def trend_html(value):
    if value == "Yükseliş":
        return '<span class="trend-up">↑ Yükseliş</span>'
    if value == "Düşüş":
        return '<span class="trend-down">↓ Düşüş</span>'
    return '<span>→ Yatay</span>'


def render_table(df):
    rows = []
    for idx, row in df.iterrows():
        rows.append(f"""
        <tr>
            <td class="num">{idx}</td>
            <td><b>{row["symbol"]}</b></td>
            <td class="num">{row["score"]}</td>
            <td>{risk_html(row["risk"])}</td>
            <td class="num">{fmt_price(row["current_price"])}</td>
            <td class="num">{entry_zone(row["current_price"])}</td>
            <td class="num">{fmt_price(row["sell_price_1"])}</td>
            <td class="num">{fmt_price(row["sell_price_2"])}</td>
            <td class="num">{fmt_price(row["stop_price"])}</td>
            <td class="num">{change_html(row["change_percent"])}</td>
            <td class="num">{fmt_volume(row["volume"])}</td>
            <td class="num">{proximity_html(row["proximity_to_low"])}</td>
            <td class="num"><span class="confidence">%{confidence(row["score"], row["volume"])}</span></td>
            <td>{trend_html(trend_text(row["change_percent"]))}</td>
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
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """


st.sidebar.markdown("# 🚀 AI Crypto")
st.sidebar.markdown("## Signal Dashboard")
st.sidebar.caption("Premium kripto fırsat tarama paneli")
st.sidebar.divider()
st.sidebar.markdown("🏠 Genel Bakış")
st.sidebar.markdown("📋 Sinyal Tablosu")
st.sidebar.markdown("🏆 En İyi Fırsatlar")
st.sidebar.markdown("📈 Trend Analizi")
st.sidebar.markdown("🔥 Heatmap")
st.sidebar.markdown("🔔 Bildirim Ayarları")
st.sidebar.markdown("✈️ Telegram")
st.sidebar.divider()
st.sidebar.success("🛡️ Tüm Sistemler Aktif")


data = load_data()
df = pd.DataFrame(data).sort_values(by="score", ascending=False)

total = len(df)
signals = len(df[df["score"] >= 5])
best = int(df["score"].max())
avg = round(df["score"].mean(), 2)
now = datetime.now().strftime("%H:%M:%S")

left, right = st.columns([2.5, 1])

with left:
    st.markdown("""
    <div class="hero-title">🚀 AI Crypto Signal Dashboard</div>
    <div class="hero-subtitle">Premium kripto fırsat tarama paneli</div>
    <div class="hero-caption">CoinGecko TRY verileri ile çalışır. Yatırım tavsiyesi değildir.</div>
    """, unsafe_allow_html=True)

with right:
    st.markdown(f"""
    <div class="status-box">
        <b><span style="color:#22c55e;">● Canlı Veri</span></b><br>
        <small>Son güncelleme: {now}</small>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 Yenile", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card purple">
        <div class="kpi-icon icon-purple">⌕</div>
        <div class="kpi-label">TARANAN COIN</div>
        <div class="kpi-value value-white">{total}</div>
        <div class="kpi-small">Toplam taranan coin</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon icon-green">↗</div>
        <div class="kpi-label">AKTİF SİNYAL</div>
        <div class="kpi-value value-green">{signals}</div>
        <div class="kpi-small">Sinyal üreten coin</div>
    </div>
    <div class="kpi-card yellow">
        <div class="kpi-icon icon-yellow">🏆</div>
        <div class="kpi-label">EN YÜKSEK SKOR</div>
        <div class="kpi-value value-yellow">{best}/8</div>
        <div class="kpi-small">Maksimum skor</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon icon-blue">★</div>
        <div class="kpi-label">ORTALAMA SKOR</div>
        <div class="kpi-value value-blue">{avg}</div>
        <div class="kpi-small">Ortalama skor</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">📋 Profesyonel Sinyal Tablosu</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns([1, 1, 1.4])

with f1:
    min_score = st.slider("Minimum Skor", 0, 8, 5)

with f2:
    risk_filter = st.selectbox("Risk Seviyesi", ["Tümü", "Düşük-Orta", "Orta", "Yüksek"])

with f3:
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
        <p>Orta seviye fırsatlar mevcut. İlk sıralardaki coinler güçlü sinyal veriyor.</p>
    </div>
    <div class="info-card">
        <h3>🔥 En Güçlü Bölge</h3>
        <p><span style="color:#22c55e;font-weight:900;">DeFi / Meme / Layer-1</span></p>
    </div>
    <div class="info-card">
        <h3>💸 Toplam Hacim</h3>
        <p><span style="color:#38bdf8;font-weight:900;">{fmt_volume(df["volume"].sum())} TRY</span></p>
    </div>
    <div class="info-card">
        <h3>⚠️ Uyarı</h3>
        <p>Piyasa volatil. Stop-loss kullanmayı unutmayın.</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("⚠️ Bu sistem yatırım tavsiyesi değildir. Sadece karar destek amacıyla kullanılır.")
