"""WhatsApp Business Cloud API.

Note: free-form text only reaches users inside the 24h customer-service window;
otherwise Meta requires an approved template message.
"""
from __future__ import annotations

import requests

from socialagent.core.models import PublishResult
from socialagent.publishers.base import Publisher

URL = "https://graph.facebook.com/v21.0/{phone_id}/messages"


class WhatsAppPublisher(Publisher):
    platform = "WhatsApp"

    def __init__(self, access_token: str, phone_number_id: str, recipients: str):
        self._token = access_token
        self._phone_id = phone_number_id
        self._recipients = [r.strip().lstrip("+") for r in recipients.split(",") if r.strip()]

    def publish(self, text: str, images: list[bytes] | None = None) -> PublishResult:
        failures: list[str] = []
        for to in self._recipients:
            try:
                r = requests.post(
                    URL.format(phone_id=self._phone_id),
                    headers={"Authorization": f"Bearer {self._token}"},
                    json={"messaging_product": "whatsapp", "to": to, "type": "text",
                          "text": {"body": text, "preview_url": False}},
                    timeout=30,
                )
                if not r.ok:
                    failures.append(f"{to}: {r.json().get('error', {}).get('message', r.status_code)}")
            except requests.RequestException as e:
                failures.append(f"{to}: {e}")
        sent = len(self._recipients) - len(failures)
        return PublishResult(self.platform, not failures,
                             f"Sent to {sent}/{len(self._recipients)}" + (f" — {'; '.join(failures)}" if failures else ""))
