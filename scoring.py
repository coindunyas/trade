from typing import Dict


MIN_VOLUME_TRY = 3_000_000
STRONG_VOLUME_TRY = 20_000_000


def score_symbol(symbol_data: Dict):
    try:
        symbol = symbol_data.get("symbol")
        name = symbol_data.get("name", "")
        price_change = float(symbol_data.get("priceChangePercent", 0))
        volume = float(symbol_data.get("quoteVolume", 0))
        low_price = float(symbol_data.get("lowPrice", 0))
        high_price = float(symbol_data.get("highPrice", 0))
        last_price = float(symbol_data.get("lastPrice", 0))
        market_cap = float(symbol_data.get("marketCap", 0))

        if last_price <= 0:
            return None

        if volume < MIN_VOLUME_TRY:
            return None

        score = 0
        reasons = []

        # 1. Dip fırsatı
        if price_change <= -7:
            score += 3
            reasons.append("24 saatte %7+ düşüş")

        elif price_change <= -4:
            score += 2
            reasons.append("24 saatte orta düşüş")

        # 2. Hacim analizi
        if volume >= STRONG_VOLUME_TRY:
            score += 3
            reasons.append("Güçlü hacim")

        elif volume >= 10_000_000:
            score += 2
            reasons.append("Orta hacim")

        elif volume >= MIN_VOLUME_TRY:
            score += 1
            reasons.append("Minimum hacim yeterli")

        # 3. Dibe yakınlık
        proximity_to_low = None

        if low_price > 0:
            proximity_to_low = (last_price - low_price) / low_price

            if proximity_to_low <= 0.03:
                score += 2
                reasons.append("24s dibine çok yakın")

            elif proximity_to_low <= 0.07:
                score += 1
                reasons.append("24s dibine yakın")

        # 4. Pozitif toparlanma bonusu
        if high_price > low_price and last_price > low_price:
            recovery_ratio = (last_price - low_price) / (high_price - low_price)

            if 0.15 <= recovery_ratio <= 0.55 and price_change < 0:
                score += 1
                reasons.append("Dipten toparlanma başlangıcı")
        else:
            recovery_ratio = 0

        score = min(score, 8)

        if score >= 7:
            risk = "Düşük-Orta Risk"
        elif score >= 5:
            risk = "Orta Risk"
        else:
            risk = "Yüksek Risk"

        entry_price = round(last_price, 6)
        sell_price_1 = round(last_price * 1.10, 6)
        sell_price_2 = round(last_price * 1.18, 6)
        stop_price = round(last_price * 0.95, 6)

        return {
            "symbol": symbol,
            "name": name,
            "score": score,
            "reasons": reasons,
            "risk": risk,
            "current_price": round(last_price, 6),
            "entry_price": entry_price,
            "sell_price_1": sell_price_1,
            "sell_price_2": sell_price_2,
            "stop_price": stop_price,
            "change_percent": round(price_change, 2),
            "volume": round(volume, 2),
            "market_cap": round(market_cap, 2),
            "proximity_to_low": round(proximity_to_low * 100, 2) if proximity_to_low is not None else None,
        }

    except Exception as e:
        print(f"Scoring error: {e}")
        return None
