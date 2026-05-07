import pandas as pd
import streamlit as st
from datetime import datetime

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
    background: #0f172a;
    color: white;
}

h1, h2, h3, p, div, span, label {
    color: white !important;
}

[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 16px;
}

[data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 900 !important;
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
    font-weight: 800 !important;
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

.stButton > button {
    background: #2563eb;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 700;
}

.stSelectbox div[data-baseweb="select"] > div {
    color: black !important;
    background-color: white !important;
    border-radius: 10px !important;
}

div[role="listbox"] div {
    color: black !important;
    background-color: white !important;
}

.stTextInput input {
    color: black !important;
    background-color: white !important;
    border-radius: 10px !important;
}

.stTextInput input::placeholder {
    color: #666 !important;
}

.stSelectbox svg {
    fill: black !important;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data():
    try:
        client = BinanceTRClient()
        tickers = client.get_tickers()
        results = []

        for ticker in tickers:
            result = score_symbol(ticker)
            if result:
                results.append(result)

        return results

    except Exception:
        return []


def format_price(value):
    try:
        value = float(value)

        if value == 0:
            return "0.00 TL"

        if value < 1:
            return f"{value:.8f} TL"

        return f"{value:,.2f} TL"

    except Exception:
        return "-"


def format_volume(value):
    try:
        value = float(value)

        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B TL"

        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M TL"

        return f"{value:,.0f} TL"

    except Exception:
        return "-"


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
        return f"%{round(score_part + volume_part)}"

    except Exception:
        return "%0"


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


st.title("🚀 AI Crypto Signal Dashboard")
st.subheader("Premium kripto fırsat tarama paneli")
st.caption("CoinGecko TRY verileri ile çalışır. Yatırım tavsiyesi değildir.")

col_live, col_btn = st.columns([3, 1])

with col_live:
    st.success(
        f"● Canlı Veri | Son güncelleme: {datetime.now().strftime('%H:%M:%S')}"
    )

with col_btn:
    if st.button("🔄 Verileri Yenile", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


data = load_data()

if not data:
    st.warning(
        "CoinGecko verisi şu anda alınamadı. Birkaç dakika sonra tekrar deneyin."
    )
    st.stop()


df = pd.DataFrame(data).sort_values(by="score", ascending=False)

df["alis_bolgesi"] = df["current_price"].apply(entry_zone)
df["risk_seviyesi"] = df["risk"].apply(risk_label)
df["ai_guven"] = df.apply(
    lambda x: ai_confidence(x["score"], x["volume"]),
    axis=1
)
df["trend"] = df["change_percent"].apply(trend_label)

total = len(df)
signals = len(df[df["score"] >= 5])
best = int(df["score"].max())
avg = round(df["score"].mean(), 1)


c1, c2, c3, c4 = st.columns(4)

c1.metric("TARANAN COIN", total)
c2.metric("AKTİF SİNYAL", signals)
c3.metric("EN YÜKSEK SKOR", f"{best}/8")
c4.metric("ORTALAMA SKOR", avg)

st.divider()

st.subheader("🔥 En Verimli 3 Fırsat")

top3 = df.head(3)

cols = st.columns(3)

for i in range(len(top3)):
    row = top3.iloc[i]

    with cols[i]:
        with st.container(border=True):
            st.markdown(f"### #{i + 1} {row['symbol']}")
            st.metric(
                "AI Skor",
                f"{row['score']}/8",
                f"%{row['change_percent']}"
            )

            st.write(f"⚠️ **Risk:** {row['risk_seviyesi']}")
            st.write(f"💰 **Güncel Fiyat:** {format_price(row['current_price'])}")
            st.write(f"🟢 **Alış Bölgesi:** {row['alis_bolgesi']}")
            st.write(f"🎯 **Satış 1:** {format_price(row['sell_price_1'])}")
            st.write(f"🚀 **Satış 2:** {format_price(row['sell_price_2'])}")
            st.write(f"🛑 **Stop-Loss:** {format_price(row['stop_price'])}")
            st.write(f"📊 **Hacim:** {format_volume(row['volume'])}")
            st.write(f"🧠 **AI Güven:** {row['ai_guven']}")
            st.write(f"📈 **Trend:** {row['trend']}")

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
    search = st.text_input(
        "Coin ara",
        placeholder="BTC, ETH, SOL..."
    )

filtered = df[df["score"] >= min_score].copy()

if selected_risk != "Tümü":
    filtered = filtered[
        filtered["risk_seviyesi"] == selected_risk
    ]

if search:
    filtered = filtered[
        filtered["symbol"].str.contains(search.upper(), na=False)
    ]

table = pd.DataFrame({
    "Sembol": filtered["symbol"],
    "Skor": filtered["score"],
    "Risk Seviyesi": filtered["risk_seviyesi"],
    "Güncel Fiyat": filtered["current_price"].apply(format_price),
    "Alış Bölgesi": filtered["alis_bolgesi"],
    "Satış 1": filtered["sell_price_1"].apply(format_price),
    "Satış 2": filtered["sell_price_2"].apply(format_price),
    "Stop-Loss": filtered["stop_price"].apply(format_price),
    "Değişim %": filtered["change_percent"],
    "Hacim": filtered["volume"].apply(format_volume),
    "Dibe Yakınlık %": filtered["proximity_to_low"],
    "AI Güven": filtered["ai_guven"],
    "Trend": filtered["trend"],
})

st.dataframe(
    table,
    use_container_width=True,
    height=520
)

st.caption(f"Toplam {len(filtered)} coin gösteriliyor.")

st.divider()

g1, g2 = st.columns(2)

with g1:
    st.subheader("📊 Skor Liderleri")
    st.bar_chart(
        df.head(20).set_index("symbol")["score"]
    )

with g2:
    st.subheader("💸 Hacim Liderleri")
    st.bar_chart(
        df.sort_values(
            by="volume",
            ascending=False
        ).head(20).set_index("symbol")["volume"]
    )

st.divider()

st.subheader("🧠 Sistem Yorumu")

if signals == 0:
    st.info(
        "Şu anda güçlü sinyal yok. Piyasa sakin veya kriterler oluşmamış."
    )

elif best >= 7:
    st.success(
        "Güçlü fırsatlar mevcut. İlk 3 coin detaylı incelenebilir."
    )

elif best >= 5:
    st.warning(
        "Orta seviye fırsatlar var. Kademeli satış ve stop-loss önemli."
    )

else:
    st.info(
        "Net fırsat sinyali zayıf."
    )

st.caption(
    "⚠️ Bu sistem yatırım tavsiyesi değildir. Sadece karar destek amacıyla kullanılır."
)
