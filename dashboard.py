import pandas as pd
import streamlit as st

from binance_tr import BinanceTRClient
from scoring import score_symbol


st.set_page_config(
    page_title="AI Crypto Signal Dashboard",
    page_icon="📊",
    layout="wide",
)


st.title("📊 AI Crypto Signal Dashboard")
st.caption("CoinGecko TRY verileriyle çalışan sinyal paneli")


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


data = load_data()

if not data:
    st.warning("Veri bulunamadı.")
    st.stop()

df = pd.DataFrame(data)
df = df.sort_values(by="score", ascending=False)

top3 = df.head(3)

col1, col2, col3 = st.columns(3)

for idx, row in enumerate(top3.itertuples(), start=1):
    with [col1, col2, col3][idx - 1]:
        st.metric(
            label=f"{idx}. {row.symbol}",
            value=f"{row.score}/8",
            delta=f"%{round(row.change_percent, 2)}"
        )
        st.write(f"💰 Fiyat: {row.current_price}")
        st.write(f"🎯 Hedef: {row.target_price}")
        st.write(f"🛑 Stop: {row.stop_price}")
        st.write(f"⚠️ Risk: {row.risk}")

st.divider()

st.subheader("🔥 En İyi Sinyaller")

filtered = df[df["score"] >= 5]

st.dataframe(
    filtered[
        [
            "symbol",
            "score",
            "risk",
            "current_price",
            "change_percent",
            "target_price",
            "stop_price",
            "volume",
        ]
    ],
    use_container_width=True,
)

st.divider()

st.subheader("📊 Skor Dağılımı")
st.bar_chart(df.set_index("symbol")["score"].head(20))

st.caption("Not: Bu panel yatırım tavsiyesi değildir. Sadece karar destek sistemidir.")
