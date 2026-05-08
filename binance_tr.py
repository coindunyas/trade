import requests


class BinanceTRClient:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"

    def get_tickers(self):
        url = f"{self.base_url}/ticker/24hr"

        response = requests.get(
            url,
            timeout=25,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
            }
        )

        if response.status_code != 200:
            raise Exception(f"Binance API hatası: {response.status_code}")

        data = response.json()

        tickers = []

        for item in data:
            symbol = str(item.get("symbol", "")).upper().strip()

            if not symbol.endswith("TRY"):
                continue

            last_price = float(item.get("lastPrice", 0) or 0)

            if last_price <= 0:
                continue

            tickers.append({
                "id": symbol.lower(),
                "name": symbol.replace("TRY", ""),
                "symbol": symbol,
                "priceChangePercent": float(item.get("priceChangePercent", 0) or 0),
                "quoteVolume": float(item.get("quoteVolume", 0) or 0),
                "lowPrice": float(item.get("lowPrice", 0) or 0),
                "highPrice": float(item.get("highPrice", 0) or 0),
                "lastPrice": last_price,
                "marketCap": 0,
                "source": "binance_global_try",
            })

        if not tickers:
            raise Exception("Binance TRY pariteleri alınamadı.")

        return sorted(
            tickers,
            key=lambda x: x["quoteVolume"],
            reverse=True
        )
