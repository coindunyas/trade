from dotenv import load_dotenv

from binance_tr import BinanceTRClient
from config import Settings
from scoring import score_symbol
from state import SignalState
from telegram import TelegramNotifier


def active_try_symbols(exchange_info: dict) -> set[str]:
    symbols: set[str] = set()
    for item in exchange_info.get("symbols", []):
        symbol = str(item.get("symbol", ""))
        status = str(item.get("status", ""))
        quote_asset = str(item.get("quoteAsset", ""))

        if status == "TRADING" and (quote_asset == "TRY" or symbol.endswith("TRY")):
            symbols.add(symbol)
    return symbols


def run() -> None:
    load_dotenv()
    settings = get_settings()

    client = BinanceTRClient(settings.binance_base_url)
    state = SignalState(settings.state_file, settings.signal_cooldown_hours)

    symbols = active_try_symbols(client.exchange_info())
    tickers = [t for t in client.ticker_24hr() if t.get("symbol") in symbols]

    signals = []
    for ticker in tickers:
        signal = score_ticker(
            ticker,
            min_volume_try=settings.min_volume_try,
            high_volume_try=settings.high_volume_try,
            target_profit_pct=settings.target_profit_pct,
            stop_loss_pct=settings.stop_loss_pct,
        )
        if signal and state.can_send(signal.symbol):
            signals.append(signal)

    signals.sort(key=lambda s: (s.score, s.quote_volume_try), reverse=True)
    top_signals = signals[: settings.max_results]

    message = build_message(top_signals)
    send_telegram_message(settings.telegram_bot_token, settings.telegram_chat_id, message)

    for signal in top_signals:
        state.mark_sent(signal.symbol)
    state.save()

    print(f"Taranan TRY parite: {len(tickers)} | Gonderilen sinyal: {len(top_signals)}")


if __name__ == "__main__":
    run()
