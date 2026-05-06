import requests


class BinanceTRClient:
    def __init__(self):
        self.base_url = "https://api.binance.me/api/v3"

    def get_tickers(self):
        url = f"{self.base_url}/ticker/24hr"

        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            raise Exception(
                f"Binance API hatası: {response.status_code}"
            )

        data = response.json()

        if not isinstance(data, list):
            raise Exception("Beklenmeyen API cevabı")

        return data
