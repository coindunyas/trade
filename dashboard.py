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
    background: linear-gradient(135deg, #0f172a 0%, #111827 45%, #020617 100%);
    color: white;
}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.08);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
.card {
    background: rgba(255,255,255,0.08);
    padding: 24px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 12px 35px rgba(0,0,0,0.4);
    margin-bottom: 18px;
}
.coin-title {
    font-size: 28px;
    font-weight: 800;
    color: #38bdf8;
}
.score {
    font-size: 34px;
    font-weight: 900;
    color: #22c55e;
}
.small {
    color: #cbd5e1;
    font-size: 14px;
}
.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(34,197,94,0.18);
    color: #86efac;
    font-weight: 700;
}
h1, h2, h3 {
    color: white;
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


def price(v):
    try:
        v = float(v)
        if v >= 1:
            return f"{v:,.2f} TL"
        return f"{v:.6f} TL"
    except Exception:
        return str(v)


def volume(v):
    try:
        v = float(v)
        if v >= 1_000_000_000:
            return f"{v / 1_000_000_000:.2f}B TL"
        if v >= 1_000_000:
            return f"{v / 1_000_000:.2f}M TL"
        return f"{v:,.0f} TL"
    except Exception:
        return str(v)


st.markdown("# 🚀 AI Crypto Signal Dashboard")
st.markdown("### Premium kripto fırsat tarama paneli")
st.caption("CoinGecko TRY verileri ile çalışır. Yatırım tavsiyesi değildir.")

data = load_data()

if not data:
    st.warning("Veri bulunamadı.")
    st.stop()

df = pd.DataFrame(data).sort_values(by="score", ascending=False)

total = len(df)
signals = len(df[df["score"] >= 5])
best = int(df["score"].max())
avg_score = round(df["score"].mean(), 2)

m1, m2, m3, m4 = st.columns(4)

m1.metric("Taranan Coin", total)
m2.metric("Aktif Sinyal", signals)
m3.metric("En Yüksek Skor", f"{best}/8")
m4.metric("Ortalama Skor", avg_score)

st.divider()

st.markdown("## 🔥 En Verimli 3 Fırsat")

top3 = df.head(3)
cols = st.columns(3)

for i, row in enumerate(top3.itertuples(), start=0):
    with cols[i]:
        st.markdown(
            f"""
            <div class="card">
                <div class="coin-title">#{i+1} {row.symbol}</div>
                <div class="small">{getattr(row, "name", "")}</div>
                <br>
                <div class="score">{row.score}/8</div>
                <span class="badge">{row.risk}</span>
                <br><br>
                <b>💰 Fiyat:</b> {price(row.current_price)}<br>
                <b>📉 Günlük:</b> %{row.change_percent}<br><br>
                <b>🟢 Alış:</b> {price(row.entry_price)}<br>
                <b>🎯 Satış 1:</b> {price(row.sell_price_1)}<br>
                <b>🚀 Satış 2:</b> {price(row.sell_price_2)}<br>
                <b>🛑 Stop:</b> {price(row.stop_price)}<br><br>
                <b>📊 Hacim:</b> {volume(row.volume)}
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

st.markdown("## 📋 Profesyonel Sinyal Tablosu")

min_score = st.slider("Minimum skor", 0, 8, 5)

filtered = df[df["score"] >= min_score].copy()

st.dataframe(
    filtered[
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
    ],
    use_container_width=True,
    height=420,
)

st.divider()

c1, c2 = st.columns(2)

with c1:
    st.markdown("## 📊 Skor Liderleri")
    st.bar_chart(df.head(20).set_index("symbol")["score"])

with c2:
    st.markdown("## 💸 Hacim Liderleri")
    st.bar_chart(df.sort_values(by="volume", ascending=False).head(20).set_index("symbol")["volume"])

st.divider()

st.markdown("## 🧠 AI Piyasa Yorumu")

if signals == 0:
    st.info("Şu anda güçlü sinyal yok. Piyasa sakin veya kriterler oluşmamış.")
elif best >= 7:
    st.success("Güçlü fırsatlar mevcut. İlk 3 coin detaylı takip edilebilir.")
elif best >= 5:
    st.warning("Orta seviye fırsatlar var. Kademeli satış ve stop-loss önemli.")
else:
    st.info("Net fırsat sinyali zayıf.")

st.caption("⚠️ Bu sistem yatırım tavsiyesi değildir. Sadece karar destek amacıyla kullanılır.")
