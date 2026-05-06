from dataclasses import dataclass


@dataclass(frozen=True)
class Signal:
    symbol: str
    price: float
    price_change_pct: float
    quote_volume_try: float
    low_24h: float
    high_24h: float
    score: int
    target_price: float
    stop_loss_price: float
    risk_level: str
    reasons: list[str]


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def score_ticker(
    ticker: dict,
    *,
    min_volume_try: float,
    high_volume_try: float,
    target_profit_pct: float,
    stop_loss_pct: float,
) -> Signal | None:
    symbol = str(ticker.get("symbol", ""))
    price = safe_float(ticker.get("lastPrice"))
    change_pct = safe_float(ticker.get("priceChangePercent"))
    quote_volume = safe_float(ticker.get("quoteVolume"))
    low = safe_float(ticker.get("lowPrice"))
    high = safe_float(ticker.get("highPrice"))
    open_price = safe_float(ticker.get("openPrice"))

    if price <= 0 or low <= 0 or high <= 0:
        return None

    if quote_volume < min_volume_try:
        return None

    score = 0
    reasons: list[str] = []

    # 1) Fiyat analizi: 24 saatte %7+ dusus = dip firsati
    if change_pct <= -7:
        score += 3
        reasons.append("24s dusus %7 uzeri: dip firsati")
    elif change_pct <= -4:
        score += 2
        reasons.append("24s anlamli geri cekilme")
    elif change_pct <= -2:
        score += 1
        reasons.append("hafif geri cekilme")

    # 2) Hacim analizi: yuksek hacim + pozitif ivme
    positive_momentum = price > open_price if open_price > 0 else change_pct > 0
    if quote_volume >= high_volume_try and positive_momentum:
        score += 3
        reasons.append("20M TL+ hacim ve pozitif ivme: para girisi")
    elif quote_volume >= high_volume_try:
        score += 2
        reasons.append("20M TL+ hacim")
    elif quote_volume >= min_volume_try * 2:
        score += 1
        reasons.append("likidite yeterli")

    # 3) Dibe yakinlik: mevcut fiyat son 24s low seviyesine ne kadar yakin?
    daily_range = high - low
    low_distance_pct = ((price - low) / price) * 100 if price else 999

    if daily_range > 0:
        range_position = (price - low) / daily_range
        if range_position <= 0.20:
            score += 2
            reasons.append("24s dibine cok yakin")
        elif range_position <= 0.35:
            score += 1
            reasons.append("24s dibine yakin")
    elif low_distance_pct <= 2:
        score += 1
        reasons.append("low seviyesine yakin")

    score = min(score, 8)

    if score < 5:
        return None

    risk_level = "Dusuk Risk" if score >= 7 else "Orta Risk" if score == 6 else "Yuksek Risk"

    return Signal(
        symbol=symbol,
        price=price,
        price_change_pct=change_pct,
        quote_volume_try=quote_volume,
        low_24h=low,
        high_24h=high,
        score=score,
        target_price=price * (1 + target_profit_pct / 100),
        stop_loss_price=price * (1 - stop_loss_pct / 100),
        risk_level=risk_level,
        reasons=reasons,
    )
