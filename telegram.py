import requests
from .scoring import Signal


def fmt_money(value: float) -> str:
    if value >= 1:
        return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{value:.6f}".replace(".", ",")


def build_message(signals: list[Signal]) -> str:
    if not signals:
        return "📊 AI ANALIZ: Su an kriterlere uyan guclu TRY firsati bulunamadi."

    lines = ["📊 EN VERIMLI 3 FIRSAT (AI ANALIZ)", ""]
    for idx, signal in enumerate(signals, start=1):
        reasons = "; ".join(signal.reasons[:3])
        lines.extend([
            f"{idx}) #{signal.symbol} (Skor: {signal.score}/8)",
            f"💰 Fiyat: {fmt_money(signal.price)} TL | Degisim: %{signal.price_change_pct:.2f}",
            f"📈 Hacim: {fmt_money(signal.quote_volume_try)} TL | Risk: {signal.risk_level}",
            f"🟢 Alis Referansi: {fmt_money(signal.price)} TL",
            f"🚀 Hedef Satis: {fmt_money(signal.target_price)} TL",
            f"🛑 Stop-Loss: {fmt_money(signal.stop_loss_price)} TL",
            f"🧠 Neden: {reasons}",
            "",
        ])

    lines.append("⚠️ Bu mesaj yatirim tavsiyesi degildir. Nihai karar kullaniciya aittir.")
    return "\n".join(lines)


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    if not bot_token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID zorunludur.")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
        timeout=20,
    )
    response.raise_for_status()
