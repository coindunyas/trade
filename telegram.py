import requests


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_message(self, message: str) -> bool:
        if not self.bot_token or not self.chat_id:
            print("Telegram bilgileri eksik: TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID yok.")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=20)

            if response.status_code != 200:
                print(f"Telegram mesaj gönderme hatası: {response.status_code} - {response.text}")
                return False

            print("Telegram mesajı başarıyla gönderildi.")
            return True

        except requests.RequestException as e:
            print(f"Telegram bağlantı hatası: {e}")
            return False
