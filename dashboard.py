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
    background: linear-gradient(135deg, #020617 0%, #0f172a 55%, #020617 100%);
    color: white;
}

section[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #1e293b;
}

h1, h2, h3, p, div, span, label {
    color: #f8fafc !important;
}

[data-testid="stMetric"] {
    background: #0f172a;
    border: 1px solid #334155;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 12px 32px rgba(0,0,0,.35);
}

[data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 900 !important;
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
    font-weight: 800 !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

.stSelectbox, .stTextInput, .stSlider {
    background: transparent;
}

.card {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 20px;
    min-height: 300px;
    box-shadow: 0 12px 32px rgba(0,0,0,.35);
}

.card-title {
    font-size: 24px;
    font-weight: 900;
    color: #38bdf8 !important;
}

.good {
    color: #22c55e !important;
    font-weight: 800;
}

.bad {
    color: #ef4444 !important;
    font-weight: 800;
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


def format_price(value):
    try:
        value = float(value)
        if value >= 1:
            return f"{value:,.2f} TL"
        return f"{value:.6f} TL"
    except Exception:
        return value


def format_volume(value):
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B TL"
        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M TL"
        return f"{value:,.0f} TL"
    except Exception:
        return value


def entry_zone(value):
    try:
        price = float(value)
        low = price * 0.98
        high = price * 0.99
        return f"{format_price(low)} - {format_price(high)}"
    except Exception:
        return "-"


def risk_label(value):
    value = str(value)
    if "Düşük" in value:
        return "Düşük-Orta"
    if "Orta" in value:
        return "Orta"
    return "Yüksek"


def ai_confidence(score, volume):
    try:
        score_part = float(score) / 8 * 70
        volume_part = min(float(volume) / 1_000_000_000, 1) * 30
        return round(score_part + volume_part)
    except Exception:
        return 0


def trend_label(change):
    try:
        change = float(change)
        if change > 1:
            return "Yükseliş"
        if change < -1:
            return "Düşüş"
        return "Yatay"
    except Exception:
        return "Yatay"


st.sidebar.title("🚀 AI Crypto")
st.sidebar.subheader("Signal Dashboard")
st.sidebar.caption("Premium kripto fırsat tarama paneli")
st.sidebar.divider()
st.sidebar.markdown("🏠 Genel Bakış")
st.sidebar.markdown("📋 Sinyal Tablosu")
st.sidebar.markdown("🏆 En İyi Fırsatlar")
st.sidebar.markdown("📈 Trend Analizi")
st.sidebar.markdown("🔔 Bildirim Ayarları")
st.sidebar.markdown("✈️ Telegram")
st.sidebar.divider()
st.sidebar.success("🛡️ Sistem Aktif")


data = load_data()

if not data:
    st.warning("Veri bulunamadı.")
    st.stop()

df = pd.DataFrame(data).sort_values(by="score", ascending=False)

df["Alış Bölgesi"] = df["current_price"].apply(entry_zone)
df["Risk Seviyesi"] = df["risk"].apply(risk_label)
df["AI Güven"] = df.apply(lambda x: f"%{ai_confidence(x['score'], x['volume'])}", axis=1)
df["Trend"] = df["change_percent"].apply(trend_label)

total = len(df)
signals = len(df[df["score"] >= 5])
best = int(df["score"].max())
avg = round(df["score"].mean(), 1)
now = datetime.now().strftime("%H:%M:%S")

top_left, top_right = st.columns([3, 1])

with top_left:
    st.title("🚀 AI Crypto Signal Dashboard")
    st.subheader("Premium kripto fırsat tarama paneli")
    st.caption("CoinGecko TRY verileri ile çalışır. Yatırım tavsiyesi değildir.")

with top_right:
    st.success(f"● Canlı Veri\n\nSon güncelleme: {now}")
    if st.button("🔄 Verileri Yenile", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

c1, c2, c3, c4 = st.columns(4)

c1.metric("TARANAN COIN", total)
c2.metric("AKTİF SİNYAL", signals)
c3.metric("EN YÜKSEK SKOR", f"{best}/8")
c4.metric("ORTALAMA SKOR", avg)

st.divider()

st.subheader("🔥 En Verimli 3 Fırsat")

top3 = df.head(3)
cols = st.columns(3)

for i, row in enumerate(top3.itertuples(), start=1):
    with cols[i - 1]:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">#{i} {row.symbol}</div>
                <h2>{row.score}/8</h2>
                <p><b>Risk:</b> {row._asdict()["Risk Seviyesi"]}</p>
                <p><b>💰 Güncel:</b> {format_price(row.current_price)}</p>
                <p><b>🟢 Alış:</b> {row._asdict()["Alış Bölgesi"]}</p>
                <p><b>🎯 Satış 1:</b> <span class="good">{format_price(row.sell_price_1)}</span></p>
                <p><b>🚀 Satış 2:</b> <span class="good">{format_price(row.sell_price_2)}</span></p>
                <p><b>🛑 Stop:</b> <span class="bad">{format_price(row.stop_price)}</span></p>
                <p><b>📉 Değişim:</b> %{row.change_percent}</p>
                <p><b>📊 Hacim:</b> {format_volume(row.volume)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

st.subheader("📋 Profesyonel Sinyal Tablosu")

f1, f2, f3 = st.columns([1, 1, 2])

with f1:
    min_score = st.slider("Minimum Skor", 0, 8, 5)

with f2:
    selected_risk = st.selectbox(
        "Risk Seviyesi",
        ["Tümü", "Düşük-Orta", "Orta", "Yüksek"]
    )

with f3:
    search = st.text_input("Coin ara", placeholder="BTC, ETH, SOL...")

filtered = df[df["score"] >= min_score].copy()

if selected_risk != "Tümü":
    filtered = filtered[filtered["Risk Seviyesi"] == selected_risk]

if search:
    filtered = filtered[filtered["symbol"].str.contains(search.upper(), na=False)]

table = filtered[
    [
        "symbol",
        "score",
        "Risk Seviyesi",
        "current_price",
        "Alış Bölgesi",
        "sell_price_1",
        "sell_price_2",
        "stop_price",
        "change_percent",
        "volume",
        "proximity_to_low",
        "AI Güven",
        "Trend",
    ]
].rename(columns={
    "symbol": "Sembol",
    "score": "Skor",
    "current_price": "Güncel Fiyat",
    "sell_price_1": "Satış 1",
    "sell_price_2": "Satış 2",
    "stop_price": "Stop-Loss",
    "change_percent": "Değişim %",
    "volume": "Hacim",
    "proximity_to_low": "Dibe Yakınlık %",
})

st.dataframe(table, use_container_width=True, height=520)

st.caption(f"Toplam {len(filtered)} coin gösteriliyor.")

st.divider()

g1, g2 = st.columns(2)

with g1:
    st.subheader("📊 Skor Liderleri")
    st.bar_chart(df.head(20).set_index("symbol")["score"])

with g2:
    st.subheader("💸 Hacim Liderleri")
    st.bar_chart(df.sort_values(by="volume", ascending=False).head(20).set_index("symbol")["volume"])

st.divider()

st.subheader("🧠 Sistem Yorumu")

if signals == 0:
    st.info("Şu anda güçlü sinyal yok. Piyasa sakin veya kriterler oluşmamış.")
elif best >= 7:
    st.success("Güçlü fırsatlar mevcut. İlk 3 coin detaylı incelenebilir.")
elif best >= 5:
    st.warning("Orta seviye fırsatlar var. Kademeli satış ve stop-loss önemli.")
else:
    st.info("Net fırsat sinyali zayıf.")

st.caption("⚠️ Bu sistem yatırım tavsiyesi değildir. Sadece karar destek amacıyla kullanılır.")
