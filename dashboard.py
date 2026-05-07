import pandas as pd
import streamlit as st

from binance_tr import BinanceTRClient
from scoring import score_symbol


st.set_page_config(
    page_title="AI Crypto Signal Dashboard",
    page_icon="🚀",
    layout="wide",
)


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


data = load_data()

if not data:
    st.warning("Veri bulunamadı.")
    st.stop()

df = pd.DataFrame(data)
df = df.sort_values(by="score", ascending=False)

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
        st.write(f"🟢 **Alış:** {format_price(row.entry_price)}")
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
        "entry_price",
        "sell_price_1",
        "sell_price_2",
        "stop_price",
        "change_percent",
        "volume",
        "proximity_to_low",
    ]
]

st.dataframe(display_df, use_container_width=True)

st.divider()

st.subheader("📊 En Yüksek Skorlu Coinler")

chart_df = df.head(20).set_index("symbol")
st.bar_chart(chart_df["score"])

st.divider()

st.subheader("💸 Hacim Liderleri")

volume_df = df.sort_values(by="volume", ascending=False).head(20).set_index("symbol")
st.bar_chart(volume_df["volume"])

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
