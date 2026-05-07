import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

from binance_tr import BinanceTRClient


DB_FILE = "portfolio.db"

st.set_page_config(
    page_title="Portföy Takibi",
    page_icon="💼",
    layout="wide",
)

st.title("💼 Portföy / Kar-Zarar Takibi")
st.caption("Alış, satış, kalan coin, TRY kasa ve kar-zarar hesaplama paneli")


def connect_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def init_db():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        symbol TEXT,
        trade_type TEXT,
        price REAL,
        quantity REAL,
        note TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS manual_prices (
        symbol TEXT PRIMARY KEY,
        price REAL,
        updated_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cash_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        movement_type TEXT,
        amount REAL,
        note TEXT
    )
    """)

    cur.execute("""
    INSERT OR IGNORE INTO settings (key, value)
    VALUES ('initial_capital', 0)
    """)

    conn.commit()
    conn.close()


def get_initial_capital():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key='initial_capital'")
    row = cur.fetchone()
    conn.close()
    return float(row[0]) if row else 0.0


def set_initial_capital(value):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE settings SET value=? WHERE key='initial_capital'",
        (float(value),)
    )
    conn.commit()
    conn.close()


def add_trade(symbol, trade_type, price, quantity, note):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO trades (created_at, symbol, trade_type, price, quantity, note)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        symbol.upper().strip(),
        trade_type,
        float(price),
        float(quantity),
        note,
    ))

    conn.commit()
    conn.close()


def delete_trade(trade_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM trades WHERE id=?", (trade_id,))
    conn.commit()
    conn.close()


def load_trades():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM trades ORDER BY id DESC", conn)
    conn.close()
    return df


def save_manual_price(symbol, price):
    conn = connect_db()
    cur = conn.cursor()

    symbol = symbol.upper().strip()

    cur.execute("""
    INSERT INTO manual_prices (symbol, price, updated_at)
    VALUES (?, ?, ?)
    ON CONFLICT(symbol)
    DO UPDATE SET price=excluded.price, updated_at=excluded.updated_at
    """, (
        symbol,
        float(price),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))

    conn.commit()
    conn.close()


def delete_manual_price(symbol):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM manual_prices WHERE symbol=?",
        (symbol.upper().strip(),)
    )

    conn.commit()
    conn.close()


def load_manual_prices():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM manual_prices", conn)
    conn.close()

    prices = {}

    for _, row in df.iterrows():
        symbol = str(row["symbol"]).upper().strip()
        price = float(row["price"])

        prices[symbol] = price

        if symbol.endswith("TRY"):
            prices[symbol.replace("TRY", "")] = price

    return prices, df


def add_cash_movement(movement_type, amount, note):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO cash_movements (created_at, movement_type, amount, note)
    VALUES (?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        movement_type,
        float(amount),
        note,
    ))

    conn.commit()
    conn.close()


def delete_cash_movement(movement_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM cash_movements WHERE id=?",
        (movement_id,)
    )

    conn.commit()
    conn.close()


def load_cash_movements():
    conn = connect_db()
    df = pd.read_sql_query(
        "SELECT * FROM cash_movements ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def calculate_extra_cash(cash_df):
    if cash_df.empty:
        return 0.0

    total = 0.0

    for _, row in cash_df.iterrows():
        amount = float(row["amount"])

        if row["movement_type"] == "NAKİT EKLE":
            total += amount

        elif row["movement_type"] == "NAKİT ÇIKAR":
            total -= amount

    return total


@st.cache_data(ttl=300)
def load_live_prices():
    try:
        client = BinanceTRClient()
        tickers = client.get_tickers()

        prices = {}

        for item in tickers:
            symbol = str(item.get("symbol", "")).upper().strip()
            price = item.get("lastPrice")

            if symbol and price is not None:
                prices[symbol] = float(price)

                if symbol.endswith("TRY"):
                    prices[symbol.replace("TRY", "")] = float(price)

        return prices

    except Exception:
        return {}


def format_money(value):
    try:
        return f"{float(value):,.2f} TL"
    except Exception:
        return "-"


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


def calculate_portfolio(trades_df, prices):
    if trades_df.empty:
        return pd.DataFrame(), {
            "used_try": 0,
            "cash_from_sales": 0,
            "realized_pnl": 0,
            "unrealized_pnl": 0,
            "current_value": 0,
            "total_pnl": 0,
        }

    symbols = sorted(trades_df["symbol"].unique())

    rows = []

    total_used_try = 0
    total_cash_from_sales = 0
    total_realized_pnl = 0
    total_unrealized_pnl = 0
    total_current_value = 0

    for symbol in symbols:
        symbol_trades = trades_df[trades_df["symbol"] == symbol].copy()

        buys = symbol_trades[symbol_trades["trade_type"] == "ALIŞ"]
        sells = symbol_trades[symbol_trades["trade_type"] == "SATIŞ"]

        bought_qty = buys["quantity"].sum()
        buy_cost = (buys["price"] * buys["quantity"]).sum()

        sold_qty = sells["quantity"].sum()
        sell_revenue = (sells["price"] * sells["quantity"]).sum()

        remaining_qty = bought_qty - sold_qty

        avg_cost = buy_cost / bought_qty if bought_qty > 0 else 0
        realized_pnl = sell_revenue - (avg_cost * sold_qty)

        clean_symbol = str(symbol).upper().strip()

        current_price = prices.get(
            clean_symbol,
            prices.get(clean_symbol.replace("TRY", ""), 0)
        )

        current_value = remaining_qty * current_price
        remaining_cost = remaining_qty * avg_cost

        unrealized_pnl = current_value - remaining_cost if current_price > 0 else 0
        total_pnl = realized_pnl + unrealized_pnl

        total_used_try += buy_cost
        total_cash_from_sales += sell_revenue
        total_realized_pnl += realized_pnl
        total_unrealized_pnl += unrealized_pnl
        total_current_value += current_value

        rows.append({
            "Sembol": symbol,
            "Alınan Miktar": round(bought_qty, 8),
            "Satılan Miktar": round(sold_qty, 8),
            "Kalan Miktar": round(remaining_qty, 8),
            "Ortalama Maliyet": avg_cost,
            "Anlık Fiyat": current_price if current_price > 0 else None,
            "Alış Toplamı": buy_cost,
            "Satış Toplamı": sell_revenue,
            "Kalan Değer": current_value,
            "Gerçekleşen Kar/Zarar": realized_pnl,
            "Açık Pozisyon Kar/Zarar": unrealized_pnl,
            "Toplam Kar/Zarar": total_pnl,
        })

    summary = {
        "used_try": total_used_try,
        "cash_from_sales": total_cash_from_sales,
        "realized_pnl": total_realized_pnl,
        "unrealized_pnl": total_unrealized_pnl,
        "current_value": total_current_value,
        "total_pnl": total_realized_pnl + total_unrealized_pnl,
    }

    return pd.DataFrame(rows), summary


init_db()

live_prices = load_live_prices()
manual_prices, manual_prices_df = load_manual_prices()

prices = live_prices.copy()
prices.update(manual_prices)

if not live_prices:
    st.warning("Canlı fiyatlar geçici olarak alınamadı. Manuel fiyatlar varsa onlar kullanılacak.")

trades_df = load_trades()
cash_movements_df = load_cash_movements()

initial_capital = get_initial_capital()
extra_cash = calculate_extra_cash(cash_movements_df)

portfolio_df, summary = calculate_portfolio(trades_df, prices)

cash_balance = (
    initial_capital
    + extra_cash
    - summary["used_try"]
    + summary["cash_from_sales"]
)

total_assets = cash_balance + summary["current_value"]
total_profit = total_assets - initial_capital - extra_cash


st.subheader("💰 Genel Durum")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Başlangıç Sermayesi", format_money(initial_capital))
c2.metric("Ek Nakit", format_money(extra_cash))
c3.metric("Toplam Alış", format_money(summary["used_try"]))
c4.metric("Toplam Satış", format_money(summary["cash_from_sales"]))

c5, c6, c7, c8 = st.columns(4)

c5.metric("TRY Kasa", format_money(cash_balance))
c6.metric("Açık Pozisyon Değeri", format_money(summary["current_value"]))
c7.metric("Toplam Varlık", format_money(total_assets))
c8.metric("Toplam Kar/Zarar", format_money(total_profit))

c9, c10 = st.columns(2)

c9.metric("Gerçekleşen Kar/Zarar", format_money(summary["realized_pnl"]))
c10.metric("Açık Kar/Zarar", format_money(summary["unrealized_pnl"]))

st.divider()


st.subheader("⚙️ Başlangıç Sermayesi")

with st.form("capital_form"):
    new_capital = st.number_input(
        "Başlangıç TRY sermayesi",
        min_value=0.0,
        value=float(initial_capital),
        step=100.0
    )

    save_capital = st.form_submit_button("Sermayeyi Kaydet")

    if save_capital:
        set_initial_capital(new_capital)
        st.success("Başlangıç sermayesi kaydedildi.")
        st.rerun()


st.divider()


st.subheader("💵 Ek Nakit Girişi / Çıkışı")

st.caption("Sermaye dışında elde olan nakitleri buradan ekleyebilirsin. Örn: önceki kâr, dışarıdan eklenen para, kasadan çekilen para.")

with st.form("cash_form"):
    n1, n2, n3 = st.columns(3)

    with n1:
        cash_type = st.selectbox(
            "İşlem tipi",
            ["NAKİT EKLE", "NAKİT ÇIKAR"]
        )

    with n2:
        cash_amount = st.number_input(
            "Tutar",
            min_value=0.0,
            step=100.0
        )

    with n3:
        cash_note = st.text_input(
            "Not",
            placeholder="Örn: Önceki kâr, dışarıdan para, çekim"
        )

    save_cash = st.form_submit_button("Nakit İşlemini Kaydet")

    if save_cash:
        if cash_amount <= 0:
            st.error("Tutar sıfırdan büyük olmalı.")
        else:
            add_cash_movement(cash_type, cash_amount, cash_note)
            st.success("Nakit işlemi kaydedildi.")
            st.rerun()

if not cash_movements_df.empty:
    st.write("### 💵 Nakit Hareketleri")
    st.dataframe(cash_movements_df, use_container_width=True)

    cash_delete_id = st.number_input(
        "Silinecek nakit hareketi ID",
        min_value=0,
        step=1
    )

    if st.button("Nakit Hareketini Sil"):
        if cash_delete_id > 0:
            delete_cash_movement(cash_delete_id)
            st.success("Nakit hareketi silindi.")
            st.rerun()
        else:
            st.error("Geçerli ID gir.")


st.divider()


st.subheader("🟡 Manuel Anlık Fiyat Ekle / Sil")

st.caption("FOGO gibi CoinGecko’da çıkmayan coinler için manuel fiyat girebilirsin.")

with st.form("manual_price_form"):
    p1, p2 = st.columns(2)

    with p1:
        manual_symbol = st.text_input("Coin sembolü", placeholder="FOGOTRY")

    with p2:
        manual_price = st.number_input(
            "Anlık fiyat",
            min_value=0.0,
            step=0.000001,
            format="%.8f"
        )

    save_price = st.form_submit_button("Manuel Fiyatı Kaydet")

    if save_price:
        if not manual_symbol:
            st.error("Coin sembolü boş olamaz.")
        elif manual_price <= 0:
            st.error("Fiyat sıfırdan büyük olmalı.")
        else:
            save_manual_price(manual_symbol, manual_price)
            st.success("Manuel fiyat kaydedildi.")
            st.cache_data.clear()
            st.rerun()

if not manual_prices_df.empty:
    st.write("### 🟡 Kayıtlı Manuel Fiyatlar")
    st.dataframe(manual_prices_df, use_container_width=True)

    delete_symbol = st.text_input(
        "Silinecek manuel fiyat sembolü",
        placeholder="FOGOTRY"
    )

    if st.button("Manuel Fiyatı Sil"):
        if delete_symbol:
            delete_manual_price(delete_symbol)
            st.success("Manuel fiyat silindi.")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("Silmek için sembol gir.")


st.divider()


st.subheader("📥 İşlem Ekle")

with st.form("trade_form"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        symbol = st.text_input("Coin sembolü", placeholder="BTCTRY, SOLTRY, FOGOTRY")

    with col2:
        trade_type = st.selectbox("İşlem tipi", ["ALIŞ", "SATIŞ"])

    with col3:
        price = st.number_input(
            "Fiyat",
            min_value=0.0,
            step=0.000001,
            format="%.8f"
        )

    with col4:
        quantity = st.number_input(
            "Miktar",
            min_value=0.0,
            step=0.0001,
            format="%.8f"
        )

    note = st.text_input("Not", placeholder="Örn: ilk alış, satış 1, stop")

    submitted = st.form_submit_button("İşlemi Kaydet")

    if submitted:
        if not symbol:
            st.error("Coin sembolü boş olamaz.")
        elif price <= 0 or quantity <= 0:
            st.error("Fiyat ve miktar sıfırdan büyük olmalı.")
        else:
            add_trade(symbol, trade_type, price, quantity, note)
            st.success("İşlem kaydedildi.")
            st.rerun()


st.divider()


st.subheader("📊 Açık Pozisyonlar ve Kar/Zarar")

if portfolio_df.empty:
    st.info("Henüz işlem girmedin.")
else:
    display_portfolio = portfolio_df.copy()

    price_columns = [
        "Ortalama Maliyet",
        "Anlık Fiyat",
    ]

    money_columns = [
        "Alış Toplamı",
        "Satış Toplamı",
        "Kalan Değer",
        "Gerçekleşen Kar/Zarar",
        "Açık Pozisyon Kar/Zarar",
        "Toplam Kar/Zarar",
    ]

    for col in price_columns:
        display_portfolio[col] = display_portfolio[col].apply(
            lambda x: format_price(x) if pd.notna(x) else "Fiyat Yok"
        )

    for col in money_columns:
        display_portfolio[col] = display_portfolio[col].apply(format_money)

    st.dataframe(display_portfolio, use_container_width=True)


st.divider()


st.subheader("🧾 İşlem Geçmişi")

if trades_df.empty:
    st.info("İşlem geçmişi boş.")
else:
    st.dataframe(trades_df, use_container_width=True)

    st.warning("Silme işlemi geri alınamaz.")

    delete_id = st.number_input(
        "Silinecek işlem ID",
        min_value=0,
        step=1
    )

    if st.button("Seçili İşlemi Sil"):
        if delete_id > 0:
            delete_trade(delete_id)
            st.success("İşlem silindi.")
            st.rerun()
        else:
            st.error("Geçerli bir işlem ID gir.")
