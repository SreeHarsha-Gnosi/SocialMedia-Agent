"""Past campaigns: reopen/repost, or write a follow-up with new information."""
from __future__ import annotations

import streamlit as st

from socialagent.agent.generator import GenerationError
from socialagent.core.models import Campaign
from socialagent.storage import history
from socialagent.ui import sources, state


def render_history() -> None:
    campaigns = history.list_all()
    if not campaigns:
        st.info("Nothing here yet — generate a post and it will be saved automatically.")
        return
    for c in campaigns:
        _card(c)


def _card(c: Campaign) -> None:
    with st.container(border=True):
        head, actions = st.columns([4, 2])
        origin = f" · ↳ follow-up of #{c.parent_id}" if c.parent_id else ""
        head.markdown(f"**{c.title}**  \n<small>#{c.id} · {c.created_at.replace('T', ' ')} · "
                      f"{c.brand.name}{origin}</small>", unsafe_allow_html=True)
        head.caption(c.content.summary)
        open_col, del_col = actions.columns(2)
        if open_col.button("📂 Open / repost", key=f"open{c.id}", width="stretch"):
            state.load_campaign(c)
            state.goto(state.CREATE)
            st.rerun()
        if del_col.button("🗑 Delete", key=f"del{c.id}", width="stretch"):
            history.delete(c.id)
            st.rerun()

        with st.expander("🔔 Follow-up / reminder with new info"):
            new_info = st.text_area("What's new?", key=f"fu{c.id}", height=90,
                                    placeholder="e.g. Registrations close Friday, 20 seats left, early-bird ends tonight")
            links = st.text_area("Extra links (optional, one per line)", key=f"fl{c.id}", height=60)
            if st.button("Generate follow-up", key=f"fg{c.id}", type="primary"):
                try:
                    gen = state.generator()
                    with st.spinner("Writing the follow-up…"):
                        content = gen.followup(c.content, new_info, c.brand, sources.collect([], links))
                except GenerationError as e:
                    st.error(str(e))
                    return
                st.session_state["brand"] = c.brand
                state.set_content(content, history.save(content, c.brand, new_info, parent_id=c.id), new_info)
                state.goto(state.CREATE)
                st.rerun()
