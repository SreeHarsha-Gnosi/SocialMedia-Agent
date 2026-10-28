"""Single-piece regeneration ("make it punchier").

Buttons only *request* a refinement (callback). The work runs at the top of the next script run,
before the text widgets exist, so their values can be overwritten and a spinner can be shown.
"""
from __future__ import annotations

import streamlit as st

from socialagent.agent.generator import GenerationError
from socialagent.ui import keys, state


def request(kind: str, i: int = 0) -> None:
    st.session_state["_pending_refine"] = (kind, i)


def process_pending() -> None:
    pending = st.session_state.pop("_pending_refine", None)
    content = state.content()
    if not pending or content is None:
        return
    kind, i = pending
    ss, gid, ig = st.session_state, st.session_state["gen_id"], content.instagram
    instruction = (ss.get(keys.instr(gid, kind, i)) or "").strip()
    if not instruction:
        st.toast("Type an instruction first, e.g. “make it punchier”.", icon="⚠️")
        return
    try:
        gen = state.generator()
        with st.spinner("Rewriting…"):
            if kind == "slide":
                s = gen.refine_slide(ig.slides[i], instruction, content, state.brand())
                ig.slides[i] = s
                ss[keys.slide_h(gid, i)], ss[keys.slide_b(gid, i)], ss[keys.slide_s(gid, i)] = (
                    s.headline, s.body, s.stat)
            elif kind == "caption":
                ig.caption = gen.refine_text("Instagram caption", ig.caption, instruction, content, state.brand())
                ss[keys.cap(gid)] = ig.caption
            elif kind == "telegram":
                content.telegram = gen.refine_text("Telegram message (HTML)", content.telegram,
                                                   instruction, content, state.brand())
                ss[keys.telegram(gid)] = content.telegram
            elif kind == "whatsapp":
                content.whatsapp = gen.refine_text("WhatsApp message", content.whatsapp,
                                                   instruction, content, state.brand())
                ss[keys.whatsapp(gid)] = content.whatsapp
    except GenerationError as e:
        st.error(str(e))
        return
    ss[keys.instr(gid, kind, i)] = ""
    st.toast("Updated ✨")


def pick_variant() -> None:
    """Radio callback: copy the chosen caption variant into the caption editor."""
    content, gid = state.content(), st.session_state["gen_id"]
    if content is None:
        return
    idx = st.session_state.get(keys.variant(gid), 0)
    text = content.instagram.caption_variants[idx].text
    content.instagram.caption = text
    st.session_state[keys.cap(gid)] = text
