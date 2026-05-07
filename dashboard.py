import pandas as pd
import streamlit as st

from binance_tr import BinanceTRClient
from scoring import score_symbol

st.set_page_config(
    page_title="AI Crypto Signal Dashboard",
    page_icon="🚀",
    layout="wide",
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617 0%, #0f172a 50%, #020617 100%);
    color: #f8fafc;
}

h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 800 !important;
}

p, span, label, div {
    color: #e5e7eb;
}

[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(148, 163, 184, 0.25);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.35);
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 900 !important;
}

[data-testid="stDataFrame"] {
    background: #0f172a;
    border-radius: 16px;
}

.stAlert {
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 AI Crypto Signal Dashboard")
st.caption("TRY bazlı kripto fırsat tarama paneli | CoinGecko API")

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

data = load_data()

if not data:
    st.warning("Veri bulunamadı.")
    st.stop()

df = pd.DataFrame(data).sort_values(by="score", ascending=False)

df["entry_zone"] = df["current_price"].apply(entry_zone)

total_coins = len(df)
signal_count = len(df[df["score"] >= 5])
best_score = int(df["score"].max())

col_a, col_b, col_c = st.columns(3)

col_a.metric("Taranan Coin", total_coins)
col_b.metric("Sinyal Adayı", signal_count)
col_c.metric("En Yüksek Skor", f"{best_score}/8")

st.divider()

st.subheader("🔥 En Verimli 3 Fırsat")

top3 = df.head(3)
cols = st.columns(3)

for index, row in enumerate(top3.itertuples(), start=0):
    with cols[index]:
        st.markdown(f"### #{index + 1} {row.symbol}")
        st.metric(
            label="AI Skor",
            value=f"{row.score}/8",
            delta=f"%{row.change_percent}"
        )
        st.write(f"💰 **Fiyat:** {format_price(row.current_price)}")
        st.write(f"🟢 **Alış Bölgesi:** {row.entry_zone}")
        st.write(f"🎯 **Satış 1:** {format_price(row.sell_price_1)}")
        st.write(f"🚀 **Satış 2:** {format_price(row.sell_price_2)}")
        st.write(f"🛑 **Stop:** {format_price(row.stop_price)}")
        st.write(f"⚠️ **Risk:** {row.risk}")
        st.write(f"📊 **Hacim:** {format_volume(row.volume)}")

st.divider()

st.subheader("📋 Sinyal Tablosu")

min_score = st.slider(
    "Minimum skor filtresi",
    min_value=0,
    max_value=8,
    value=5
)

filtered_df = df[df["score"] >= min_score].copy()

display_df = filtered_df[
    [
        "symbol",
        "score",
        "risk",
        "current_price",
        "entry_zone",
        "sell_price_1",
        "sell_price_2",
        "stop_price",
        "change_percent",
        "volume",
        "proximity_to_low",
    ]
].rename(columns={
    "symbol": "Sembol",
    "score": "Skor",
    "risk": "Risk",
    "current_price": "Güncel Fiyat",
    "entry_zone": "Alış Bölgesi",
    "sell_price_1": "Satış 1",
    "sell_price_2": "Satış 2",
    "stop_price": "Stop-Loss",
    "change_percent": "Değişim %",
    "volume": "Hacim",
    "proximity_to_low": "Dibe Yakınlık %",
})

st.dataframe(display_df, use_container_width=True)

st.divider()

st.subheader("📊 En Yüksek Skorlu Coinler")
st.bar_chart(df.head(20).set_index("symbol")["score"])

st.divider()

st.subheader("🧠 Sistem Yorumu")

if signal_count == 0:
    st.info("Şu anda güçlü sinyal yok. Piyasa sakin veya kriterler oluşmamış.")
elif best_score >= 7:
    st.success("Güçlü fırsatlar mevcut. İlk 3 coin detaylı incelenebilir.")
elif best_score >= 5:
    st.warning("Orta seviye fırsatlar var. Stop-loss disiplini önemli.")
else:
    st.info("Net fırsat sinyali zayıf.")

st.caption("⚠️ Bu sistem yatırım tavsiyesi değildir. Sadece karar destek amacıyla kullanılır.")
