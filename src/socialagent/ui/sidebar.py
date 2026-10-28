from __future__ import annotations

import streamlit as st

from socialagent.core.settings import AVAILABLE_MODELS
from socialagent.rendering.themes import THEMES
from socialagent.ui import state

TONES = ["Friendly & energetic", "Professional", "Witty & playful", "Inspirational",
         "Educational", "Bold & punchy", "Calm & minimal"]
LANGUAGES = ["English", "Hindi", "Telugu", "Tamil", "Spanish", "French", "German", "Arabic", "Portuguese"]


def render_sidebar() -> None:
    c, b = state.creds(), state.brand()
    with st.sidebar:
        st.markdown("### 🎨 Brand kit")
        b.name = st.text_input("Brand name", b.name)
        b.handle = st.text_input("Handle", b.handle)
        b.theme = st.selectbox("Slide theme", list(THEMES), index=list(THEMES).index(b.theme))
        b.tone = st.selectbox("Tone", TONES, index=TONES.index(b.tone))
        b.language = st.selectbox("Language", LANGUAGES, index=LANGUAGES.index(b.language))
        b.audience = st.text_input("Target audience", b.audience, placeholder="e.g. startup founders")

        st.markdown("### 🔑 Connections")
        with st.expander("Claude (Anthropic)", expanded=not c.anthropic_api_key):
            c.anthropic_api_key = st.text_input("API key", c.anthropic_api_key, type="password")
            st.session_state["model"] = st.selectbox("Model", AVAILABLE_MODELS,
                                                     index=AVAILABLE_MODELS.index(st.session_state["model"]))
        with st.expander("Telegram"):
            c.telegram_bot_token = st.text_input("Bot token", c.telegram_bot_token, type="password")
            c.telegram_chat_id = st.text_input("Chat / channel ID", c.telegram_chat_id,
                                               placeholder="@mychannel or -100123…")
        with st.expander("WhatsApp Business"):
            c.whatsapp_access_token = st.text_input("Access token", c.whatsapp_access_token, type="password")
            c.whatsapp_phone_number_id = st.text_input("Phone number ID", c.whatsapp_phone_number_id)
            c.whatsapp_recipients = st.text_input("Recipients", c.whatsapp_recipients,
                                                  help="Comma-separated numbers with country code")
        with st.expander("Instagram"):
            st.caption("Auto-posting arrives once credentials are added. For now, download the "
                       "slides + caption and post from your phone.")
