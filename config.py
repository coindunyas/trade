from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    binance_base_url: str = os.getenv("BINANCE_TR_BASE_URL", "https://www.binance.tr")
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    min_volume_try: float = float(os.getenv("MIN_VOLUME_TRY", "3000000"))
    high_volume_try: float = float(os.getenv("HIGH_VOLUME_TRY", "20000000"))
    max_results: int = int(os.getenv("MAX_RESULTS", "3"))
    target_profit_pct: float = float(os.getenv("TARGET_PROFIT_PCT", "18"))
    stop_loss_pct: float = float(os.getenv("STOP_LOSS_PCT", "5"))
    signal_cooldown_hours: int = int(os.getenv("SIGNAL_COOLDOWN_HOURS", "2"))
    state_file: str = os.getenv("STATE_FILE", ".signal_state.json")


def get_settings() -> Settings:
    return Settings()
