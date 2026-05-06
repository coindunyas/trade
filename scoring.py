from typing import Dict


def score_symbol(symbol_data: Dict):
    score = 0
    reasons = []

    try:
        price_change = float(symbol_data.get("priceChangePercent", 0))
        volume = float(symbol_data.get("quoteVolume", 0))
        low_price = float(symbol_data.get("lowPrice", 0))
        last_price = float(symbol_data.get("lastPrice", 0))

        # 1. Dip fırsatı
        if price_change <= -7:
            score += 3
            reasons.append("Dip fırsatı")

        # 2. Güçlü hacim
        if volume >= 20000000:
            score += 3
            reasons.append("Yüksek hacim")

        # 3. Dibe yakınlık
        if low_price > 0:
            proximity = (last_price - low_price) / low_price

            if proximity <= 0.05:
                score += 2
                reasons.append("Dibe yakın")

        # Risk seviyesi
        if score >= 7:
            risk = "Düşük Risk"
        elif score >= 5:
            risk = "Orta Risk"
        else:
            risk = "Yüksek Risk"

        # Hedef ve stop
        target_price = round(last_price * 1.18, 4)
        stop_price = round(last_price * 0.95, 4)

        return {
            "symbol": symbol_data.get("symbol"),
            "score": score,
            "reasons": reasons,
            "risk": risk,
            "current_price": last_price,
            "change_percent": price_change,
            "target_price": target_price,
            "stop_price": stop_price,
            "volume": volume,
        }

    except Exception as e:
        print(f"Scoring error: {e}")
        return None
