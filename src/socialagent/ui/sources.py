"""Collect attachments from uploaded files and pasted links, surfacing problems as warnings."""
from __future__ import annotations

import streamlit as st

from socialagent.core.models import Attachment
from socialagent.ingestion.extractors import UnsupportedFileError, extract
from socialagent.ingestion.web import UrlFetchError, fetch_url


def collect(files, links_text: str) -> list[Attachment]:
    out: list[Attachment] = []
    for f in files or []:
        try:
            out.append(extract(f.name, f.getvalue()))
        except UnsupportedFileError as e:
            st.warning(str(e))
        except Exception as e:  # a corrupt file must not kill the run
            st.warning(f"Could not read {f.name}: {e}")
    for url in (u.strip() for u in links_text.splitlines()):
        if not url:
            continue
        try:
            out.append(fetch_url(url))
        except UrlFetchError as e:
            st.warning(str(e))
        except Exception as e:
            st.warning(f"Could not read {url}: {e}")
    return out
