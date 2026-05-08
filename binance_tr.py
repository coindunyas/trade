import time
import requests


class BinanceTRClient:
    def __init__(self):
        self.binance_url = "https://api.binance.com/api/v3"
        self.coingecko_url = "https://api.coingecko.com/api/v3"

    def get_usdt_try_rate(self):
        # 1. Binance USDTTRY dene
        try:
            url = f"{self.binance_url}/ticker/price?symbol=USDTTRY"
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                return float(data["price"])
        except Exception:
            pass

        # 2. Frankfurter USDTRY dene
        try:
            url = "https://api.frankfurter.app/latest?from=USD&to=TRY"
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                return float(data["rates"]["TRY"])
        except Exception:
            pass

        # 3. Güvenli fallback
        return 40.0

    def get_tickers(self):
        try:
            return self.get_binance_global_tickers()
        except Exception as e:
            print(f"Binance Global veri alınamadı, CoinGecko fallback çalışıyor: {e}")
            return self.get_coingecko_tickers()

    def get_binance_global_tickers(self):
        usdt_try = self.get_usdt_try_rate()

        url = f"{self.binance_url}/ticker/24hr"
        response = requests.get(url, timeout=25)

        if response.status_code != 200:
            raise Exception(f"Binance API hatası: {response.status_code} - {response.text}")

        data = response.json()

        tickers = []

        for item in data:
            symbol = item.get("symbol", "")

            if not symbol.endswith("USDT"):
                continue

            base_symbol = symbol.replace("USDT", "")

            # Gereksiz stable coinleri ele
            if base_symbol in ["USDT", "USDC", "FDUSD", "TUSD", "DAI", "BUSD"]:
                continue

            last_price_usdt = float(item.get("lastPrice", 0) or 0)
            low_price_usdt = float(item.get("lowPrice", 0) or 0)
            high_price_usdt = float(item.get("highPrice", 0) or 0)
            quote_volume_usdt = float(item.get("quoteVolume", 0) or 0)

            if last_price_usdt <= 0:
                continue

            tickers.append({
                "id": base_symbol.lower(),
                "name": base_symbol,
                "symbol": f"{base_symbol}TRY",
                "priceChangePercent": float(item.get("priceChangePercent", 0) or 0),
                "quoteVolume": quote_volume_usdt * usdt_try,
                "lowPrice": low_price_usdt * usdt_try,
                "highPrice": high_price_usdt * usdt_try,
                "lastPrice": last_price_usdt * usdt_try,
                "marketCap": 0,
                "source": "binance_global_usdt_try",
            })
print("FOGO TEST:", [x for x in tickers if "FOGO" in x.get("symbol", "")])
print("TOPLAM BINANCE TICKER:", len(tickers))
        if not tickers:
            raise Exception("Binance Global ticker boş geldi.")

        return tickers

    def get_coingecko_tickers(self):
        all_data = []

        for page in range(1, 5):
            url = (
                f"{self.coingecko_url}/coins/markets"
                "?vs_currency=try"
                "&order=volume_desc"
                "&per_page=250"
                f"&page={page}"
                "&sparkline=false"
                "&price_change_percentage=24h"
            )

            response = requests.get(url, timeout=25)

            if response.status_code == 200:
                all_data.extend(response.json())
                time.sleep(1)
            else:
                print(f"CoinGecko API hatası: {response.status_code}")

        if not all_data:
            raise Exception("CoinGecko verisi alınamadı.")

        return self._normalize_coingecko(all_data)

    def _normalize_coingecko(self, data):
        tickers = []

        for coin in data:
            symbol = coin.get("symbol", "").upper()

            if not symbol:
                continue

            tickers.append({
                "id": coin.get("id"),
                "name": coin.get("name"),
                "symbol": f"{symbol}TRY",
                "priceChangePercent": coin.get("price_change_percentage_24h", 0) or 0,
                "quoteVolume": coin.get("total_volume", 0) or 0,
                "lowPrice": coin.get("low_24h", 0) or 0,
                "highPrice": coin.get("high_24h", 0) or 0,
                "lastPrice": coin.get("current_price", 0) or 0,
                "marketCap": coin.get("market_cap", 0) or 0,
                "source": "coingecko",
            })

        return tickers
