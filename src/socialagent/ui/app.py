from __future__ import annotations

import streamlit as st

from socialagent.scheduling.runner import Scheduler
from socialagent.ui import state
from socialagent.ui.history_page import render_history
from socialagent.ui.results import render_results
from socialagent.ui.schedule_page import render_schedule
from socialagent.ui.sidebar import render_sidebar
from socialagent.ui.styles import CSS
from socialagent.ui.workspace import render_workspace


@st.cache_resource
def _scheduler() -> Scheduler:
    """One background publisher thread per server process."""
    s = Scheduler()
    s.start()
    return s


def _chip(label: str, ok: bool) -> str:
    return f'<span class="chip {"ok" if ok else ""}">{"●" if ok else "○"} {label}</span>'


def run() -> None:
    st.set_page_config(page_title="Social Agent", page_icon="🪄", layout="wide")
    state.init_state()
    _scheduler().credentials = state.creds()
    st.markdown(CSS, unsafe_allow_html=True)
    render_sidebar()

    c = state.creds()
    st.markdown(
        f"""<div class="hero"><h1>🪄 Social Agent</h1>
        <p>Drop in any document, spreadsheet, image, web page or YouTube link — Claude turns it into
        Instagram carousels, Telegram and WhatsApp posts, ready to publish or schedule.</p>
        <div class="chips">{_chip("Claude", bool(c.anthropic_api_key))}{_chip("Telegram", c.telegram_ready)}
        {_chip("WhatsApp", c.whatsapp_ready)}{_chip("Instagram · download", True)}</div></div>""",
        unsafe_allow_html=True,
    )

    page = st.radio("Page", state.PAGES, key="page", horizontal=True, label_visibility="collapsed")
    if page == state.PAGES[0]:
        render_workspace()
        render_results()
    elif page == state.PAGES[1]:
        render_history()
    else:
        render_schedule()
