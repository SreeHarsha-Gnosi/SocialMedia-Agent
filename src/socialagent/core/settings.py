"""Runtime configuration: environment first, UI-provided values override."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "claude-opus-5-5"
AVAILABLE_MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]

# SQLite database + rendered slide images for scheduled posts live here.
DATA_DIR = Path(os.getenv("SOCIALAGENT_DATA_DIR", "data")).resolve()


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


@dataclass
class Credentials:
    anthropic_api_key: str = field(default_factory=lambda: _env("ANTHROPIC_API_KEY"))
    telegram_bot_token: str = field(default_factory=lambda: _env("TELEGRAM_BOT_TOKEN"))
    telegram_chat_id: str = field(default_factory=lambda: _env("TELEGRAM_CHAT_ID"))
    whatsapp_access_token: str = field(default_factory=lambda: _env("WHATSAPP_ACCESS_TOKEN"))
    whatsapp_phone_number_id: str = field(default_factory=lambda: _env("WHATSAPP_PHONE_NUMBER_ID"))
    # Comma-separated E.164 numbers without "+", e.g. "919999999999,14155550123"
    whatsapp_recipients: str = field(default_factory=lambda: _env("WHATSAPP_RECIPIENTS"))

    @property
    def telegram_ready(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def whatsapp_ready(self) -> bool:
        return bool(
            self.whatsapp_access_token and self.whatsapp_phone_number_id and self.whatsapp_recipients
        )
