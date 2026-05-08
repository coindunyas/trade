import time
import requests


class BinanceTRClient:
    def __init__(self):
        self.binance_tr_urls = [
            "https://api.binance.me/api/v3/ticker/24hr",
            "https://www.binance.tr/api/v3/ticker/24hr",
        ]
        self.binance_global_url = "https://api.binance.com/api/v3"
        self.coingecko_url = "https://api.coingecko.com/api/v3"

    def get_tickers(self):
        try:
            data = self.get_binance_tr_tickers()
            if data:
                return data
        except Exception as e:
            print(f"Binance TR veri alınamadı: {e}")

        try:
            data = self.get_binance_global_tickers()
            if data:
                return data
        except Exception as e:
            print(f"Binance Global veri alınamadı: {e}")

        return self.get_coingecko_tickers()

    def fetch_json(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers, timeout=25)

        if response.status_code != 200:
            raise Exception(f"{response.status_code} - {response.text[:200]}")

        return response.json()

    def extract_list(self, data):
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            if isinstance(data.get("data"), list):
                return data["data"]

            if isinstance(data.get("data"), dict):
                inner = data["data"]

                for key in ["list", "items", "tickers", "symbols"]:
                    if isinstance(inner.get(key), list):
                        return inner[key]

            for key in ["list", "items", "tickers", "symbols"]:
                if isinstance(data.get(key), list):
                    return data[key]

        return []

    def normalize_symbol(self, symbol):
        return str(symbol).upper().replace("_", "").replace("-", "").strip()

    def get_binance_tr_tickers(self):
        all_items = []

        for url in self.binance_tr_urls:
            try:
                data = self.fetch_json(url)
                items = self.extract_list(data)

                if items:
                    all_items.extend(items)
            except Exception as e:
                print(f"Binance TR endpoint başarısız: {url} | {e}")

        if not all_items:
            raise Exception("Binance TR ticker listesi boş.")

        usdt_try = 0

        for item in all_items:
            symbol = self.normalize_symbol(item.get("symbol", ""))
            if symbol == "USDTTRY":
                usdt_try = float(item.get("lastPrice", item.get("last", item.get("price", 0))) or 0)

        if usdt_try <= 0:
            usdt_try = self.get_usdt_try_rate()

        tickers = []

        for item in all_items:
            raw_symbol = item.get("symbol", "")
            symbol = self.normalize_symbol(raw_symbol)

            last_price = float(item.get("lastPrice", item.get("last", item.get("price", 0))) or 0)
            low_price = float(item.get("lowPrice", item.get("low", 0)) or 0)
            high_price = float(item.get("highPrice", item.get("high", 0)) or 0)
            quote_volume = float(item.get("quoteVolume", item.get("volume", 0)) or 0)
            change_percent = float(item.get("priceChangePercent", item.get("change", 0)) or 0)

            if last_price <= 0:
                continue

            if symbol.endswith("TRY"):
                final_symbol = symbol
                multiplier = 1

            elif symbol.endswith("USDT"):
                base = symbol.replace("USDT", "")
                final_symbol = f"{base}TRY"
                multiplier = usdt_try

            else:
                continue

            tickers.append({
                "id": final_symbol.lower(),
                "name": final_symbol.replace("TRY", ""),
                "symbol": final_symbol,
                "priceChangePercent": change_percent,
                "quoteVolume": quote_volume * multiplier,
                "lowPrice": low_price * multiplier,
                "highPrice": high_price * multiplier,
                "lastPrice": last_price * multiplier,
                "marketCap": 0,
                "source": "binance_tr",
            })

        if not tickers:
            raise Exception("Binance TR normalize sonrası boş.")

        return tickers

    def get_usdt_try_rate(self):
        try:
            url = f"{self.binance_global_url}/ticker/price?symbol=USDTTRY"
            data = self.fetch_json(url)
            return float(data["price"])
        except Exception:
            pass

        try:
            url = "https://api.frankfurter.app/latest?from=USD&to=TRY"
            data = self.fetch_json(url)
            return float(data["rates"]["TRY"])
        except Exception:
            pass

        return 40.0

    def get_binance_global_tickers(self):
        usdt_try = self.get_usdt_try_rate()

        url = f"{self.binance_global_url}/ticker/24hr"
        data = self.fetch_json(url)

        if not isinstance(data, list):
            raise Exception("Binance Global beklenmeyen veri.")

        tickers = []

        for item in data:
            symbol = self.normalize_symbol(item.get("symbol", ""))

            if not symbol.endswith("USDT"):
                continue

            base_symbol = symbol.replace("USDT", "")

            if base_symbol in ["USDT", "USDC", "FDUSD", "TUSD", "DAI", "BUSD"]:
                continue

            last_price = float(item.get("lastPrice", 0) or 0)
            low_price = float(item.get("lowPrice", 0) or 0)
            high_price = float(item.get("highPrice", 0) or 0)
            quote_volume = float(item.get("quoteVolume", 0) or 0)

            if last_price <= 0:
                continue

            tickers.append({
                "id": base_symbol.lower(),
                "name": base_symbol,
                "symbol": f"{base_symbol}TRY",
                "priceChangePercent": float(item.get("priceChangePercent", 0) or 0),
                "quoteVolume": quote_volume * usdt_try,
                "lowPrice": low_price * usdt_try,
                "highPrice": high_price * usdt_try,
                "lastPrice": last_price * usdt_try,
                "marketCap": 0,
                "source": "binance_global_usdt_try",
            })

        if not tickers:
            raise Exception("Binance Global ticker boş.")

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

            try:
                response = requests.get(url, timeout=25)

                if response.status_code == 200:
                    all_data.extend(response.json())
                    time.sleep(1)
            except Exception:
                pass

        if not all_data:
            raise Exception("CoinGecko verisi alınamadı.")

        return self.normalize_coingecko(all_data)

    def normalize_coingecko(self, data):
        tickers = []

        for coin in data:
            symbol = str(coin.get("symbol", "")).upper().strip()

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
