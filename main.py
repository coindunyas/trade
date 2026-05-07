import os
from datetime import datetime

from binance_tr import BinanceTRClient
from scoring import score_symbol
from telegram import TelegramNotifier


MIN_SCORE_TO_NOTIFY = int(os.getenv("MIN_SCORE_TO_NOTIFY", "5"))


def format_price(value):
    try:
        value = float(value)
        if value >= 1:
            return f"{value:,.2f} TL"
        return f"{value:.6f} TL"
    except Exception:
        return str(value)


def format_volume(value):
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B TL"
        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M TL"
        return f"{value:,.0f} TL"
    except Exception:
        return str(value)


def format_message(results):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    message = f"🚀 <b>EN VERİMLİ 3 FIRSAT</b>\n"
    message += f"⏰ Son Tarama: {now}\n\n"

    for item in results:
        reasons = ", ".join(item.get("reasons", [])) or "Standart sinyal"

        message += (
            f"📊 <b>#{item['symbol']}</b> "
            f"(Skor: {item['score']}/8)\n"
            f"💰 Fiyat: {format_price(item['current_price'])}\n"
            f"📉 Günlük Değişim: %{item['change_percent']}\n\n"
            f"🟢 Alış Bölgesi: {format_price(item['entry_price'])}\n"
            f"🎯 Satış 1: {format_price(item['sell_price_1'])} | Pozisyonun %50'si\n"
            f"🚀 Satış 2: {format_price(item['sell_price_2'])} | Kalan %50\n"
            f"🛑 Stop-Loss: {format_price(item['stop_price'])}\n\n"
            f"⚠️ Risk: {item['risk']}\n"
            f"📊 Hacim: {format_volume(item['volume'])}\n"
            f"🧠 Sebep: {reasons}\n\n"
        )

    message += "⚠️ Bu sistem yatırım tavsiyesi değildir. Karar destek amaçlıdır."

    return message


def format_no_signal_message(total_scanned):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    return (
        f"⏰ <b>Sistem Aktif</b>\n\n"
        f"Son Tarama: {now}\n"
        f"Taranan Coin: {total_scanned}\n"
        f"Durum: Şu anda güçlü sinyal bulunamadı.\n\n"
        f"Bot çalışıyor, piyasa takipte."
    )


def run():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    notifier = TelegramNotifier(bot_token, chat_id)
    client = BinanceTRClient()

    tickers = client.get_tickers()

    scored = []

    for ticker in tickers:
        result = score_symbol(ticker)

        if result:
            scored.append(result)

    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    top_signals = [item for item in scored if item["score"] >= MIN_SCORE_TO_NOTIFY][:3]

    if top_signals:
        message = format_message(top_signals)
    else:
        message = format_no_signal_message(len(scored))

    notifier.send_message(message)


if __name__ == "__main__":
    run()
