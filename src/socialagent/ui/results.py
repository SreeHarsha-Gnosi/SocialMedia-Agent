"""Step 2 – review/edit/regenerate generated content; Step 3 – publish, schedule or export."""
from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from socialagent.core.models import CampaignContent
from socialagent.publishers import build_publishers
from socialagent.rendering.slides import build_zip, render_deck
from socialagent.storage import history, schedule
from socialagent.ui import actions, keys, state

PLATFORMS = ["Telegram", "WhatsApp"]


def _refine_row(gid: int, kind: str, i: int = 0) -> None:
    """Instruction box + button that asks Claude to rewrite just this piece."""
    c1, c2 = st.columns([4, 1])
    c1.text_input("Ask Claude to change this", key=keys.instr(gid, kind, i),
                  placeholder="e.g. make it punchier / shorter / add urgency",
                  label_visibility="collapsed")
    c2.button("🪄 Rewrite", key=f"rw{gid}_{kind}_{i}", on_click=actions.request, args=(kind, i),
              width="stretch")


def render_results() -> None:
    content = state.content()
    if content is None:
        return
    actions.process_pending()
    gid = st.session_state["gen_id"]
    brand = state.brand()

    st.markdown('<div class="step">Step 2 · Review &amp; edit</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary">{content.summary}</div>', unsafe_allow_html=True)

    tab_ig, tab_tg, tab_wa = st.tabs(["📸 Instagram", "✈️ Telegram", "💬 WhatsApp"])

    with tab_ig:
        ig = content.instagram
        left, right = st.columns([2, 3])
        with left:
            if ig.caption_variants:
                st.radio("Caption style", range(len(ig.caption_variants)), key=keys.variant(gid),
                         format_func=lambda n: f"{ig.caption_variants[n].label} — "
                                               f"{ig.caption_variants[n].text[:55]}…",
                         on_change=actions.pick_variant)
            ig.caption = st.text_area("Caption", ig.caption, height=220, key=keys.cap(gid))
            _refine_row(gid, "caption")
            tag_text = st.text_area("Hashtags", " ".join(f"#{h}" for h in ig.hashtags), key=keys.tags(gid))
            ig.hashtags = [t.lstrip("#") for t in tag_text.split() if t.strip("#")]
        with right:
            for i, s in enumerate(ig.slides):
                with st.expander(f"Slide {i + 1} · {s.kind} · {s.headline[:40]}", expanded=False):
                    s.headline = st.text_input("Headline", s.headline, key=keys.slide_h(gid, i))
                    s.body = st.text_area("Body", s.body, key=keys.slide_b(gid, i), height=80)
                    if s.kind == "stat":
                        s.stat = st.text_input("Stat", s.stat, key=keys.slide_s(gid, i))
                    _refine_row(gid, "slide", i)
        pngs = render_deck(ig.slides, brand)
        cols = st.columns(min(3, len(pngs)))
        for i, png in enumerate(pngs):
            cols[i % len(cols)].image(png, width="stretch", caption=f"Slide {i + 1}")

    with tab_tg:
        content.telegram = st.text_area("Telegram message (HTML)", content.telegram, height=280,
                                        key=keys.telegram(gid))
        _refine_row(gid, "telegram")
    with tab_wa:
        content.whatsapp = st.text_area("WhatsApp message", content.whatsapp, height=280,
                                        key=keys.whatsapp(gid))
        _refine_row(gid, "whatsapp")
        st.markdown(f'<div class="phone">{content.whatsapp}</div>', unsafe_allow_html=True)

    _render_publish(content, pngs)


def _persist(content: CampaignContent) -> None:
    if (cid := st.session_state.get("campaign_id")) is not None:
        history.update(cid, content)


def _render_publish(content: CampaignContent, pngs: list[bytes]) -> None:
    st.markdown('<div class="step">Step 3 · Publish</div>', unsafe_allow_html=True)
    publishers = build_publishers(state.creds())

    a, b = st.columns(2)
    a.download_button("⬇️ Download everything (ZIP)", type="primary", width="stretch",
                      data=build_zip(pngs, content.instagram.caption, content.instagram.hashtags,
                                     content.telegram, content.whatsapp),
                      file_name="social_pack.zip", mime="application/zip")
    if b.button("💾 Save changes to history", width="stretch"):
        _persist(content)
        st.toast("Saved")

    send_images = st.checkbox("Also send carousel images to Telegram", value=True)

    now_tab, later_tab = st.tabs(["🚀 Publish now", "🗓 Schedule for later"])
    with now_tab:
        if not publishers:
            st.info("Add Telegram / WhatsApp credentials in the sidebar to enable one-click publishing.")
        else:
            targets = st.multiselect("Publish to", list(publishers), default=list(publishers))
            if st.button("🚀 Publish now", width="stretch") and targets:
                _persist(content)
                for name in targets:
                    text = content.telegram if name == "Telegram" else content.whatsapp
                    res = publishers[name].publish(text, pngs if send_images and name == "Telegram" else None)
                    (st.success if res.ok else st.error)(f"{res.platform}: {res.detail}")
    with later_tab:
        default = datetime.now() + timedelta(hours=1)
        c1, c2 = st.columns(2)
        day = c1.date_input("Date", value=default.date(), min_value=datetime.now().date(), key="sched_date")
        at = c2.time_input("Time", value=default.time().replace(second=0, microsecond=0), key="sched_time")
        targets = st.multiselect("Send to", PLATFORMS, default=PLATFORMS, key="sched_targets")
        st.caption("Posts go out while this app is running; anything overdue is sent when it next starts. "
                   "Credentials are kept in memory only, so re-enter them (or use .env) after a restart.")
        if st.button("🗓 Schedule", width="stretch", key="sched_btn") and targets:
            run_at = datetime.combine(day, at)
            if run_at <= datetime.now():
                st.error("Pick a time in the future.")
            else:
                _persist(content)
                schedule.add(run_at, targets, content.telegram, content.whatsapp, pngs, send_images,
                             st.session_state.get("campaign_id"))
                st.success(f"Scheduled for {run_at:%d %b %Y, %H:%M}. See the 🗓 Scheduled tab.")
