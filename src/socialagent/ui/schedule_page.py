"""Queue of scheduled posts (auto-refreshing)."""
from __future__ import annotations

import streamlit as st

from socialagent.storage import schedule

_BADGE = {"pending": "⏳ Pending", "running": "🔄 Sending", "sent": "✅ Sent", "partial": "⚠️ Partial",
          "failed": "❌ Failed", "cancelled": "🚫 Cancelled"}


@st.fragment(run_every="30s")
def render_schedule() -> None:
    posts = schedule.list_all()
    st.caption("Posts are sent by a background thread of this app — keep it running. Auto-refreshes every 30s.")
    if not posts:
        st.info("No scheduled posts. Use “Schedule for later” on the Create page.")
        return
    for p in posts:
        with st.container(border=True):
            info, btns = st.columns([5, 1])
            info.markdown(f"**{p.run_at.replace('T', ' ')}** · {', '.join(p.platforms)} · {_BADGE[p.status]}")
            info.caption((p.telegram_text or p.whatsapp_text)[:140].replace("\n", " "))
            if p.note:
                info.caption(p.note)
            if p.status == "pending" and btns.button("Cancel", key=f"sc{p.id}"):
                schedule.cancel(p.id)
                st.rerun(scope="fragment")
            elif p.status != "pending" and p.status != "running" and btns.button("Delete", key=f"sd{p.id}"):
                schedule.delete(p.id)
                st.rerun(scope="fragment")
