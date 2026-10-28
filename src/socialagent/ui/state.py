"""Typed access to Streamlit session state."""
from __future__ import annotations

import streamlit as st

from socialagent.agent.generator import ContentGenerator
from socialagent.core.models import BrandKit, Campaign, CampaignContent
from socialagent.core.settings import DEFAULT_MODEL, Credentials

PAGES = ["✨ Create", "🗂 History", "🗓 Scheduled"]
CREATE = PAGES[0]


def init_state() -> None:
    st.session_state.setdefault("creds", Credentials())
    st.session_state.setdefault("brand", BrandKit())
    st.session_state.setdefault("model", DEFAULT_MODEL)
    st.session_state.setdefault("content", None)
    st.session_state.setdefault("campaign_id", None)
    st.session_state.setdefault("brief", "")
    st.session_state.setdefault("gen_id", 0)
    st.session_state.setdefault("page", CREATE)
    # A page switch requested mid-run is applied before the nav widget is created next run.
    if goto := st.session_state.pop("_goto", None):
        st.session_state["page"] = goto


def creds() -> Credentials:
    return st.session_state["creds"]


def brand() -> BrandKit:
    return st.session_state["brand"]


def content() -> CampaignContent | None:
    return st.session_state["content"]


def generator() -> ContentGenerator:
    return ContentGenerator(creds().anthropic_api_key, st.session_state["model"])


def set_content(content: CampaignContent, campaign_id: int | None, brief: str = "") -> None:
    st.session_state.update(content=content, campaign_id=campaign_id, brief=brief)
    st.session_state["gen_id"] += 1


def load_campaign(c: Campaign) -> None:
    st.session_state["brand"] = c.brand
    set_content(c.content, c.id, c.brief)


def goto(page: str) -> None:
    st.session_state["_goto"] = page
