import json
import time
from pathlib import Path


class SignalState:
    def __init__(self, path: str, cooldown_hours: int) -> None:
        self.path = Path(path)
        self.cooldown_seconds = cooldown_hours * 3600
        self.data = self._load()

    def _load(self) -> dict[str, float]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def can_send(self, symbol: str) -> bool:
        last_sent = float(self.data.get(symbol, 0))
        return time.time() - last_sent >= self.cooldown_seconds

    def mark_sent(self, symbol: str) -> None:
        self.data[symbol] = time.time()

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
