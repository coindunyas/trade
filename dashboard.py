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
    background: radial-gradient(circle at top left, #111827 0%, #020617 42%, #030712 100%);
    color: #f8fafc;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
    border-right: 1px solid rgba(148,163,184,.18);
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 800 !important;
}

p, span, label, div {
    color: #e5e7eb;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(15,23,42,.95), rgba(30,41,59,.72));
    border: 1px solid rgba(148,163,184,.22);
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 18px 50px rgba(0,0,0,.35);
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
    font-size: 15px !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 42px !important;
    font-weight: 900 !important;
}

.premium-card {
    background: linear-gradient(145deg, rgba(15,23,42,.92), rgba(2,6,23,.9));
    border: 1px solid rgba(148,163,184,.22);
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 18px 50px rgba(0,0,0,.36);
}

.status-card {
    background: rgba(15,23,42,.82);
    border: 1px solid rgba(148,163,184,.22);
    border-radius: 18px;
    padding: 18px 22px;
}

.green { color: #22c55e !important; font-weight: 800; }
.red { color: #ef4444 !important; font-weight: 800; }
.yellow { color: #facc15 !important; font-weight: 800; }
.blue { color: #38bdf8 !important; font-weight: 800; }
.purple { color: #a855f7 !important; font-weight: 800; }

.badge-green {
    background: rgba(34,197,94,.16);
    color: #86efac;
    border: 1px solid rgba(34,197,94,.35);
    padding: 5px 10px;
    border-radius: 999px;
    font-weight: 800;
}

.badge-yellow {
    background: rgba(250,204,21,.16);
    color: #fde68a;
    border: 1px solid rgba(250,204,21,.35);
    padding: 5px 10px;
    border-radius: 999px;
    font-weight: 800;
}

.badge-red {
    background: rgba(239,68,68,.16);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,.35);
    padding: 5px 10px;
    border-radius: 999px;
    font-weight: 800;
}

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(148,163,184,.18);
}

hr {
    border-color: rgba(148,163,184,.18);
}

.stSlider label {
    color: #f8fafc !important;
    font-weight: 700 !important;
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
        return value


def fmt_volume(value):
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        return f"{value:,.0f}"
    except Exception:
        return value


def risk_badge(risk):
    risk_text = str(risk)
    if "Düşük" in risk_text:
        return "Düşük-Orta"
    if "Orta" in risk_text:
        return "Orta"
    return "Yüksek"


def trend_text(change):
    try:
        change = float(change)
        if change > 1:
            return "Yükseliş"
        if change < -1:
            return "Düşüş"
        return "Yatay"
    except Exception:
        return "Yatay"


def ai_confidence(score, volume):
    try:
        score_part = float(score) / 8 * 70
        volume_part = min(float(volume) / 1_000_000_000, 1) * 30
        return round(score_part + volume_part)
    except Exception:
        return 0


def entry_zone(current_price):
    try:
        price = float(current_price)
        low = price * 0.98
        high = price * 0.99
        return f"{fmt_price(low)} - {fmt_price(high)}"
    except Exception:
        return "-"


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
st.sidebar.success("🛡️ Sistem Durumu: Aktif")


data = load_data()

if not data:
    st.warning("Veri bulunamadı.")
    st.stop()

df = pd.DataFrame(data).sort_values(by="score", ascending=False)

df["Alış Bölgesi (TRY)"] = df["current_price"].apply(entry_zone)
df["AI Güven"] = df.apply(lambda x: f"%{ai_confidence(x['score'], x['volume'])}", axis=1)
df["Trend"] = df["change_percent"].apply(trend_text)

total = len(df)
signals = len(df[df["score"] >= 5])
best = int(df["score"].max())
avg = round(df["score"].mean(), 2)
now = datetime.now().strftime("%H:%M:%S")

top_left, top_right = st.columns([2.2, 1])

with top_left:
    st.markdown("# 🚀 AI Crypto Signal Dashboard")
    st.markdown("### Premium kripto fırsat tarama paneli")
    st.caption("CoinGecko TRY verileri ile çalışır. Yatırım tavsiyesi değildir.")

with top_right:
    a, b = st.columns(2)
    with a:
        st.markdown(
            f"""
            <div class="status-card">
            <span class="green">● Canlı Veri</span><br>
            <small>Son güncelleme: {now}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b:
        if st.button("🔄 Yenile", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

st.divider()

m1, m2, m3, m4 = st.columns(4)
m1.metric("TARANAN COIN", total, "Toplam taranan coin")
m2.metric("AKTİF SİNYAL", signals, "Sinyal üreten coin")
m3.metric("EN YÜKSEK SKOR", f"{best}/8", "Maksimum skor")
m4.metric("ORTALAMA SKOR", avg, "Ortalama skor")

st.divider()

st.markdown("## 📋 Profesyonel Sinyal Tablosu")

f1, f2, f3 = st.columns([1.2, 1, 1.4])

with f1:
    min_score = st.slider("Minimum Skor", 0, 8, 5)

with f2:
    risk_filter = st.selectbox("Risk Seviyesi", ["Tümü", "Düşük-Orta", "Orta", "Yüksek"])

with f3:
    search = st.text_input("Coin ara", placeholder="BTC, ETH, SOL...")

filtered = df[df["score"] >= min_score].copy()

filtered["Risk Seviyesi"] = filtered["risk"].apply(risk_badge)

if risk_filter != "Tümü":
    filtered = filtered[filtered["Risk Seviyesi"] == risk_filter]

if search:
    filtered = filtered[filtered["symbol"].str.contains(search.upper(), na=False)]

table = pd.DataFrame({
    "Sembol": filtered["symbol"],
    "Skor": filtered["score"],
    "Risk Seviyesi": filtered["Risk Seviyesi"],
    "Güncel Fiyat (TRY)": filtered["current_price"].apply(fmt_price),
    "Alış Bölgesi (TRY)": filtered["Alış Bölgesi (TRY)"],
    "Satış 1 (TRY)": filtered["sell_price_1"].apply(fmt_price),
    "Satış 2 (TRY)": filtered["sell_price_2"].apply(fmt_price),
    "Stop-Loss (TRY)": filtered["stop_price"].apply(fmt_price),
    "Değişim (%)": filtered["change_percent"],
    "Hacim (TRY)": filtered["volume"].apply(fmt_volume),
    "Dibe Yakınlık (%)": filtered["proximity_to_low"],
    "AI Güven": filtered["AI Güven"],
    "Trend": filtered["Trend"],
})

st.dataframe(table, use_container_width=True, height=460)

st.divider()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="premium-card">
        <h3>🧠 Piyasa Yorumu</h3>
        <p>Orta seviye fırsatlar mevcut. İlk 3 sıradaki coinler güçlü sinyal veriyor.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="premium-card">
        <h3>🔥 En Güçlü Bölge</h3>
        <p><span class="green">DeFi / Meme / Layer-1</span></p>
        <small>Hacim ve skor yoğunluğu yüksek.</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="premium-card">
        <h3>💸 Toplam Hacim</h3>
        <p><span class="blue">{fmt_volume(df["volume"].sum())} TRY</span></p>
        <small>Son 24 saat</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    active_ratio = round((signals / total) * 100, 2) if total else 0
    st.markdown(
        f"""
        <div class="premium-card">
        <h3>⚡ Aktif Sinyal Oranı</h3>
        <p><span class="purple">%{active_ratio}</span></p>
        <small>{total} coin içinde</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

g1, g2 = st.columns(2)

with g1:
    st.markdown("## 📊 Skor Liderleri")
    st.bar_chart(df.head(20).set_index("symbol")["score"])

with g2:
    st.markdown("## 💸 Hacim Liderleri")
    st.bar_chart(df.sort_values(by="volume", ascending=False).head(20).set_index("symbol")["volume"])

st.caption("⚠️ Bu sistem yatırım tavsiyesi değildir. Sadece karar destek amacıyla kullanılır.")
