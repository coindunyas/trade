import os
import requests

from binance_tr import BinanceTRClient
from scoring import score_symbol
from telegram import TelegramNotifier


def get_settings():
    return {
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
    }


def format_message(results):
    message = "🚀 <b>EN VERİMLİ 3 FIRSAT (AI ANALİZ)</b>\n\n"

    for item in results:
        message += (
            f"📊 <b>{item['symbol']}</b> (Skor: {item['score']}/8)\n"
            f"💰 Fiyat: {item['current_price']}\n"
            f"📉 Değişim: %{item['change_percent']}\n"
            f"🎯 Hedef: {item['target_price']}\n"
            f"🛑 Stop: {item['stop_price']}\n"
            f"⚠️ Risk: {item['risk']}\n\n"
        )

    return message


def run():
    settings = get_settings()

    notifier = TelegramNotifier(
        settings["bot_token"],
        settings["chat_id"]
    )

    client = BinanceTRClient()

    tickers = client.get_tickers()

    scored = []

    for ticker in tickers:
        try:
            symbol = ticker.get("symbol", "")

            if not symbol.endswith("TRY"):
                continue

            result = score_symbol(ticker)

            if result and result["score"] >= 5:
                scored.append(result)

        except Exception as e:
            print(f"Hata: {e}")

    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    top3 = scored[:3]

    if not top3:
        notifier.send_message("⚠️ Uygun sinyal bulunamadı.")
        return

    message = format_message(top3)

    notifier.send_message(message)


if __name__ == "__main__":
    run()
