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

        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            raise Exception(
                f"CoinGecko API hatası: {response.status_code}"
            )

        data = response.json()

        tickers = []

        for coin in data:
            tickers.append({
                "symbol": f"{coin['symbol'].upper()}TRY",
                "priceChangePercent": coin.get("price_change_percentage_24h", 0) or 0,
                "quoteVolume": coin.get("total_volume", 0) or 0,
                "lowPrice": coin.get("low_24h", 0) or 0,
                "lastPrice": coin.get("current_price", 0) or 0,
            })

        return tickers
