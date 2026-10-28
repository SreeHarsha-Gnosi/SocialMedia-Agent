"""Step 1 – inputs (files, links, brief), and the Generate action."""
from __future__ import annotations

import streamlit as st

from socialagent.agent.generator import GenerationError
from socialagent.ingestion.extractors import SUPPORTED_EXTENSIONS
from socialagent.storage import history
from socialagent.ui import sources, state


def render_workspace() -> None:
    st.markdown('<div class="step">Step 1 · Feed the agent</div>', unsafe_allow_html=True)
    files = st.file_uploader(
        "Drop PDFs, images, CSV/Excel, Word or text files", accept_multiple_files=True,
        type=SUPPORTED_EXTENSIONS, label_visibility="collapsed",
    )
    links = st.text_area("Links — web pages or YouTube videos (one per line)", height=80,
                         placeholder="https://example.com/blog-post\nhttps://youtu.be/…")
    col1, col2 = st.columns([3, 1])
    brief = col1.text_area("What should the post focus on? (optional)", height=110,
                           placeholder="e.g. Announce our Q3 results and highlight the growth numbers")
    slides = col2.slider("Carousel slides", 3, 10, 6)

    if st.button("✨ Generate posts", type="primary", width="stretch"):
        _generate(files, links, brief, slides)


def _generate(files, links: str, brief: str, slide_count: int) -> None:
    try:
        gen = state.generator()
        with st.status("Claude is analysing your material and writing posts…", expanded=True) as status:
            attachments = sources.collect(files, links)
            st.write(f"Read {len(attachments)} source(s)")
            content = gen.generate(attachments, state.brand(), brief, slide_count)
            status.update(label="Done!", state="complete", expanded=False)
    except GenerationError as e:
        st.error(str(e))
        return
    state.set_content(content, history.save(content, state.brand(), brief), brief)
