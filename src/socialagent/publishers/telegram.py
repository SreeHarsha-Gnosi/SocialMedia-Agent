from __future__ import annotations

import json

import requests

from socialagent.core.models import PublishResult
from socialagent.publishers.base import Publisher

API = "https://api.telegram.org/bot{token}/{method}"
CAPTION_LIMIT = 1024


class TelegramPublisher(Publisher):
    platform = "Telegram"

    def __init__(self, bot_token: str, chat_id: str):
        self._token, self._chat = bot_token, chat_id

    def _call(self, method: str, **kwargs) -> dict:
        r = requests.post(API.format(token=self._token, method=method), timeout=60, **kwargs)
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("description", f"HTTP {r.status_code}"))
        return data

    def publish(self, text: str, images: list[bytes] | None = None) -> PublishResult:
        try:
            if images:
                # Telegram albums allow 2-10 photos; the caption sits on the first.
                chunk = images[:10]
                if len(chunk) == 1:
                    self._call("sendPhoto", data={"chat_id": self._chat}, files={"photo": chunk[0]})
                else:
                    media = [{"type": "photo", "media": f"attach://p{i}"} for i in range(len(chunk))]
                    self._call("sendMediaGroup", data={"chat_id": self._chat, "media": json.dumps(media)},
                               files={f"p{i}": b for i, b in enumerate(chunk)})
            # Full text goes as a separate message so it is never cut by the caption limit.
            self._call("sendMessage", data={"chat_id": self._chat, "text": text,
                                            "parse_mode": "HTML", "disable_web_page_preview": True})
            return PublishResult(self.platform, True, "Sent")
        except (RuntimeError, requests.RequestException) as e:
            return PublishResult(self.platform, False, str(e))
