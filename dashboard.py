import html
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from binance_tr import BinanceTRClient
from scoring import score_symbol


st.set_page_config(
    page_title="AI Crypto Signal Dashboard",
    page_icon="🚀",
    layout="wide",
)


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
        return f"{fmt_price(price * 0.98)} - {fmt_price(price * 0.99)}"
    except Exception:
        return "-"


def risk_label(risk):
    risk = str(risk)
    if "Düşük" in risk:
        return "Düşük-Orta"
    if "Orta" in risk:
        return "Orta"
    return "Yüksek"


def confidence(score, volume):
    try:
        score_part = float(score) / 8 * 70
        volume_part = min(float(volume) / 1_000_000_000, 1) * 30
        return round(score_part + volume_part)
    except Exception:
        return 0


def trend(change):
    try:
        change = float(change)
        if change > 1:
            return '<span class="up">↑ Yükseliş</span>'
        if change < -1:
            return '<span class="down">↓ Düşüş</span>'
        return '<span class="flat">→ Yatay</span>'
    except Exception:
        return "-"


data = load_data()

if not data:
    st.error("Veri bulunamadı.")
    st.stop()

df = pd.DataFrame(data).sort_values(by="score", ascending=False)

total = len(df)
signals = len(df[df["score"] >= 5])
best_score = int(df["score"].max())
avg_score = round(df["score"].mean(), 1)
total_volume = fmt_volume(df["volume"].sum())
active_ratio = round((signals / total) * 100, 1) if total else 0
now = datetime.now().strftime("%H:%M:%S")

rows = ""

for idx, row in df.head(25).iterrows():
    change = float(row["change_percent"])
    change_class = "up" if change >= 0 else "down"

    proximity = row.get("proximity_to_low", "-")
    try:
        proximity_text = f"{float(proximity):.2f}%"
    except Exception:
        proximity_text = "-"

    rows += f"""
    <tr>
        <td>{idx}</td>
        <td><b>{html.escape(str(row["symbol"]))}</b></td>
        <td>{row["score"]}</td>
        <td><span class="risk">{risk_label(row["risk"])}</span></td>
        <td>{fmt_price(row["current_price"])}</td>
        <td>{entry_zone(row["current_price"])}</td>
        <td>{fmt_price(row["sell_price_1"])}</td>
        <td>{fmt_price(row["sell_price_2"])}</td>
        <td>{fmt_price(row["stop_price"])}</td>
        <td><span class="{change_class}">{change:.2f}%</span></td>
        <td>{fmt_volume(row["volume"])}</td>
        <td><span class="up">{proximity_text}</span></td>
        <td><span class="ai">%{confidence(row["score"], row["volume"])}</span></td>
        <td>{trend(row["change_percent"])}</td>
    </tr>
    """

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Inter, Arial, sans-serif;
    background: #020617;
    color: #f8fafc;
}}

.page {{
    display: grid;
    grid-template-columns: 240px 1fr;
    min-height: 100vh;
    background:
        radial-gradient(circle at top left, rgba(124,58,237,.18), transparent 28%),
        radial-gradient(circle at top right, rgba(14,165,233,.13), transparent 30%),
        #020617;
}}

.sidebar {{
    padding: 24px 18px;
    border-right: 1px solid rgba(148,163,184,.18);
    background: linear-gradient(180deg, #020617, #07111f);
}}

.logo {{
    font-size: 25px;
    font-weight: 900;
    line-height: 1.15;
    margin-bottom: 30px;
}}

.logo span {{
    color: #a855f7;
}}

.side-text {{
    font-size: 15px;
    color: #cbd5e1;
    line-height: 1.6;
    margin-bottom: 25px;
}}

.nav {{
    margin-top: 20px;
}}

.nav-item {{
    padding: 13px 14px;
    border-radius: 12px;
    color: #dbeafe;
    margin-bottom: 8px;
    font-weight: 700;
}}

.nav-item.active {{
    background: linear-gradient(90deg, rgba(124,58,237,.42), rgba(88,28,135,.18));
    border: 1px solid rgba(168,85,247,.45);
}}

.system {{
    position: absolute;
    bottom: 24px;
    left: 18px;
    width: 200px;
    padding: 15px;
    border-radius: 14px;
    border: 1px solid rgba(34,197,94,.35);
    background: rgba(34,197,94,.08);
    color: #86efac;
    font-weight: 800;
}}

.content {{
    padding: 24px 32px 36px;
}}

.header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 22px;
}}

.title {{
    font-size: 42px;
    font-weight: 950;
    margin-bottom: 8px;
}}

.subtitle {{
    font-size: 19px;
    font-weight: 800;
    color: #e5e7eb;
    margin-bottom: 7px;
}}

.note {{
    color: #94a3b8;
    font-size: 14px;
}}

.actions {{
    display: flex;
    gap: 16px;
}}

.action-card {{
    min-width: 170px;
    padding: 16px 18px;
    border-radius: 14px;
    background: rgba(15,23,42,.8);
    border: 1px solid rgba(148,163,184,.22);
}}

.action-title {{
    font-weight: 900;
    margin-bottom: 5px;
}}

.action-small {{
    color: #cbd5e1;
    font-size: 13px;
}}

.kpis {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 28px;
}}

.kpi {{
    border-radius: 18px;
    padding: 24px;
    min-height: 160px;
    background: linear-gradient(145deg, rgba(15,23,42,.95), rgba(2,6,23,.95));
    border: 1px solid rgba(148,163,184,.22);
    box-shadow: 0 18px 50px rgba(0,0,0,.35);
}}

.kpi.purple {{ border-color: rgba(168,85,247,.52); }}
.kpi.green {{ border-color: rgba(34,197,94,.52); }}
.kpi.yellow {{ border-color: rgba(250,204,21,.52); }}
.kpi.blue {{ border-color: rgba(56,189,248,.52); }}

.kpi-inner {{
    display: flex;
    align-items: center;
    gap: 20px;
}}

.icon {{
    width: 66px;
    height: 66px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
}}

.icon.purple {{ background: rgba(168,85,247,.18); color: #c084fc; }}
.icon.green {{ background: rgba(34,197,94,.18); color: #4ade80; }}
.icon.yellow {{ background: rgba(250,204,21,.18); color: #facc15; }}
.icon.blue {{ background: rgba(56,189,248,.18); color: #38bdf8; }}

.kpi-label {{
    font-size: 14px;
    font-weight: 950;
    color: #f8fafc;
}}

.kpi-value {{
    font-size: 38px;
    font-weight: 950;
    margin-top: 6px;
}}

.kpi-small {{
    color: #cbd5e1;
    margin-top: 6px;
    font-size: 14px;
}}

.section-title {{
    font-size: 28px;
    font-weight: 950;
    margin: 8px 0 18px;
}}

.filters {{
    display: grid;
    grid-template-columns: 1fr 1fr 1.4fr;
    gap: 28px;
    margin-bottom: 16px;
    align-items: end;
}}

.filter label {{
    display: block;
    color: #e5e7eb;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 8px;
}}

.fake-input {{
    height: 43px;
    background: #07111f;
    border: 1px solid rgba(148,163,184,.23);
    border-radius: 10px;
    padding: 12px 14px;
    color: #cbd5e1;
}}

.slider {{
    height: 4px;
    background: linear-gradient(90deg, #a855f7 0%, #a855f7 50%, #1e293b 50%);
    border-radius: 999px;
    margin-top: 22px;
    position: relative;
}}

.slider::after {{
    content: "5";
    position: absolute;
    left: 49%;
    top: -25px;
    background: #a855f7;
    color: white;
    padding: 2px 7px;
    border-radius: 7px;
    font-size: 13px;
    font-weight: 900;
}}

.table-wrap {{
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(148,163,184,.25);
    background: #07111f;
    box-shadow: 0 18px 50px rgba(0,0,0,.35);
}}

table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}}

th {{
    background: #0b1628;
    color: white;
    padding: 13px 10px;
    text-align: left;
    font-weight: 950;
    border-right: 1px solid rgba(148,163,184,.13);
}}

td {{
    padding: 11px 10px;
    color: #e5e7eb;
    border-top: 1px solid rgba(148,163,184,.10);
    border-right: 1px solid rgba(148,163,184,.08);
}}

tr:hover td {{
    background: rgba(30,41,59,.72);
}}

.risk {{
    background: rgba(34,197,94,.18);
    color: #4ade80;
    border: 1px solid rgba(34,197,94,.35);
    padding: 5px 8px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 12px;
}}

.up {{
    color: #22c55e;
    font-weight: 900;
}}

.down {{
    color: #ef4444;
    font-weight: 900;
}}

.flat {{
    color: #cbd5e1;
    font-weight: 900;
}}

.ai {{
    color: #c084fc;
    font-weight: 900;
}}

.bottom {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    margin-top: 24px;
}}

.info {{
    background: rgba(15,23,42,.82);
    border: 1px solid rgba(148,163,184,.22);
    border-radius: 16px;
    padding: 18px;
    min-height: 115px;
}}

.info h3 {{
    margin: 0 0 8px;
    font-size: 17px;
}}

.info p {{
    color: #cbd5e1;
    margin: 0;
    line-height: 1.5;
}}
</style>
</head>

<body>
<div class="page">

    <aside class="sidebar">
        <div class="logo">🚀 AI Crypto<br><span>Signal Dashboard</span></div>
        <div class="side-text">
            <b>Premium kripto fırsat tarama paneli</b><br><br>
            Yatırım tavsiyesi değildir.
        </div>

        <div class="nav">
            <div class="nav-item active">🏠 Genel Bakış</div>
            <div class="nav-item">📋 Sinyal Tablosu</div>
            <div class="nav-item">🏆 En İyi Fırsatlar</div>
            <div class="nav-item">📈 Trend Analizi</div>
            <div class="nav-item">🔥 Heatmap</div>
            <div class="nav-item">🔔 Bildirim Ayarları</div>
            <div class="nav-item">✈️ Telegram</div>
            <div class="nav-item">⚙️ Ayarlar</div>
        </div>

        <div class="system">
            🛡️ Sistem Durumu<br>
            Tüm Sistemler Aktif
        </div>
    </aside>

    <main class="content">

        <div class="header">
            <div>
                <div class="title">🚀 AI Crypto Signal Dashboard</div>
                <div class="subtitle">Premium kripto fırsat tarama paneli</div>
                <div class="note">CoinGecko TRY verileri ile çalışır. Yatırım tavsiyesi değildir.</div>
            </div>

            <div class="actions">
                <div class="action-card">
                    <div class="action-title"><span class="up">● Canlı Veri</span></div>
                    <div class="action-small">Son güncelleme: {now}</div>
                </div>
                <div class="action-card">
                    <div class="action-title"><span class="ai">🔄 Yenile</span></div>
                    <div class="action-small">Şimdi güncelle</div>
                </div>
                <div class="action-card">
                    <div class="action-title">Zaman Aralığı</div>
                    <div class="action-small">24 Saat</div>
                </div>
            </div>
        </div>

        <section class="kpis">
            <div class="kpi purple">
                <div class="kpi-inner">
                    <div class="icon purple">⌕</div>
                    <div>
                        <div class="kpi-label">TARANAN COIN</div>
                        <div class="kpi-value">{total} <span class="up">↑</span></div>
                        <div class="kpi-small">Toplam taranan coin</div>
                    </div>
                </div>
            </div>

            <div class="kpi green">
                <div class="kpi-inner">
                    <div class="icon green">↗</div>
                    <div>
                        <div class="kpi-label">AKTİF SİNYAL</div>
                        <div class="kpi-value"><span class="up">{signals}</span> <span class="up">↑</span></div>
                        <div class="kpi-small">Sinyal üreten coin</div>
                    </div>
                </div>
            </div>

            <div class="kpi yellow">
                <div class="kpi-inner">
                    <div class="icon yellow">🏆</div>
                    <div>
                        <div class="kpi-label">EN YÜKSEK SKOR</div>
                        <div class="kpi-value" style="color:#facc15;">{best_score}/8 <span class="up">↑</span></div>
                        <div class="kpi-small">Maksimum skor</div>
                    </div>
                </div>
            </div>

            <div class="kpi blue">
                <div class="kpi-inner">
                    <div class="icon blue">★</div>
                    <div>
                        <div class="kpi-label">ORTALAMA SKOR</div>
                        <div class="kpi-value" style="color:#38bdf8;">{avg_score} <span class="up">↑</span></div>
                        <div class="kpi-small">Ortalama skor</div>
                    </div>
                </div>
            </div>
        </section>

        <div class="section-title">📋 Profesyonel Sinyal Tablosu</div>

        <div class="filters">
            <div class="filter">
                <label>Minimum Skor</label>
                <div class="slider"></div>
            </div>
            <div class="filter">
                <label>Risk Seviyesi</label>
                <div class="fake-input">Tümü</div>
            </div>
            <div class="filter">
                <label>Coin ara</label>
                <div class="fake-input">BTC, ETH, SOL...</div>
            </div>
        </div>

        <div class="table-wrap">
            <table>
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
                    {rows}
                </tbody>
            </table>
        </div>

        <div class="bottom">
            <div class="info">
                <h3>🧠 Piyasa Yorumu</h3>
                <p>Orta seviye fırsatlar mevcut. İlk sıralardaki coinler güçlü sinyal veriyor.</p>
            </div>
            <div class="info">
                <h3>🔥 En Güçlü Sektör</h3>
                <p><b style="color:#38bdf8;">DeFi / Meme / Layer-1</b><br>Hacim ve skor yoğunluğu yüksek.</p>
            </div>
            <div class="info">
                <h3>💸 Toplam Hacim</h3>
                <p><b style="color:#38bdf8;font-size:22px;">{total_volume} TRY</b><br>Son 24 saat</p>
            </div>
            <div class="info">
                <h3>⚡ Aktif Sinyal Oranı</h3>
                <p><b style="color:#a855f7;font-size:22px;">%{active_ratio}</b><br>{total} coin içinde</p>
            </div>
            <div class="info">
                <h3>⚠️ Uyarı</h3>
                <p>Piyasa volatil. Stop-loss kullanmayı unutma.</p>
            </div>
        </div>

    </main>
</div>
</body>
</html>
"""

components.html(html_code, height=1150, scrolling=True)
