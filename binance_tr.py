import time
import requests


class BinanceTRClient:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    def get_tickers(self):
        url = (
            f"{self.base_url}/coins/markets"
            "?vs_currency=try"
            "&order=volume_desc"
            "&per_page=250"
            "&page=1"
            "&sparkline=false"
            "&price_change_percentage=24h"
        )

        for attempt in range(3):
            try:
                response = requests.get(url, timeout=20)

                if response.status_code == 200:
                    data = response.json()
                    return self._normalize(data)

                print(f"CoinGecko API hatası: {response.status_code} - {response.text}")
                time.sleep(3)

            except requests.RequestException as e:
                print(f"API bağlantı hatası: {e}")
                time.sleep(3)

        raise Exception("CoinGecko verisi alınamadı.")

    def _normalize(self, data):
        tickers = []

        for coin in data:
            tickers.append({
                "id": coin.get("id"),
                "name": coin.get("name"),
                "symbol": f"{coin.get('symbol', '').upper()}TRY",
                "priceChangePercent": coin.get("price_change_percentage_24h", 0) or 0,
                "quoteVolume": coin.get("total_volume", 0) or 0,
                "lowPrice": coin.get("low_24h", 0) or 0,
                "highPrice": coin.get("high_24h", 0) or 0,
                "lastPrice": coin.get("current_price", 0) or 0,
                "marketCap": coin.get("market_cap", 0) or 0,
            })

        return tickers
