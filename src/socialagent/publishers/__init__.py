from socialagent.core.settings import Credentials
from socialagent.publishers.base import Publisher
from socialagent.publishers.telegram import TelegramPublisher
from socialagent.publishers.whatsapp import WhatsAppPublisher


def build_publishers(c: Credentials) -> dict[str, Publisher]:
    """Only publishers whose credentials are present are returned."""
    out: dict[str, Publisher] = {}
    if c.telegram_ready:
        out["Telegram"] = TelegramPublisher(c.telegram_bot_token, c.telegram_chat_id)
    if c.whatsapp_ready:
        out["WhatsApp"] = WhatsAppPublisher(c.whatsapp_access_token, c.whatsapp_phone_number_id,
                                            c.whatsapp_recipients)
    return out
