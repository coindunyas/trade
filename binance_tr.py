import time
from typing import Any
import requests


class BinanceTRClient:
    def __init__(self, base_url: str, timeout: int = 20) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        for attempt in range(4):
            response = self.session.get(url, params=params, timeout=self.timeout)

            if response.status_code in (418, 429):
                retry_after = int(response.headers.get("Retry-After", "5"))
                time.sleep(retry_after)
                continue

            if 500 <= response.status_code < 600:
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            return response.json()

        response.raise_for_status()
        return response.json()

    def exchange_info(self) -> dict[str, Any]:
        return self._get("/api/v3/exchangeInfo")

    def ticker_24hr(self) -> list[dict[str, Any]]:
        data = self._get("/api/v3/ticker/24hr")
        if isinstance(data, list):
            return data
        return [data]
