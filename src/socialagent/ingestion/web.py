"""Turn web pages and YouTube links into `Attachment`s."""
from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

from socialagent.core.models import Attachment
from socialagent.ingestion.extractors import MAX_TEXT_CHARS, extract

MAX_BYTES = 8_000_000
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SocialAgent/1.0)"}
_YT_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "music.youtube.com"}
_TRANSCRIPT_LANGS = ["en", "hi", "te", "ta", "es", "fr", "de", "pt", "ar"]


class UrlFetchError(RuntimeError):
    pass


def youtube_video_id(url: str) -> str | None:
    u = urlparse(url)
    if u.netloc.lower() not in _YT_HOSTS:
        return None
    if u.netloc.lower() == "youtu.be":
        vid = u.path.lstrip("/").split("/")[0]
    elif u.path == "/watch":
        vid = parse_qs(u.query).get("v", [""])[0]
    else:
        m = re.match(r"^/(?:shorts|embed|live)/([\w-]+)", u.path)
        vid = m.group(1) if m else ""
    return vid if re.fullmatch(r"[\w-]{11}", vid or "") else None


def _youtube(url: str, video_id: str) -> Attachment:
    from youtube_transcript_api import YouTubeTranscriptApi, YouTubeTranscriptApiException

    api = YouTubeTranscriptApi()
    try:
        try:
            transcript = api.fetch(video_id, languages=_TRANSCRIPT_LANGS)
        except YouTubeTranscriptApiException:
            transcript = next(iter(api.list(video_id))).fetch()  # any available language
    except (YouTubeTranscriptApiException, StopIteration) as e:
        raise UrlFetchError(f"No transcript available for this video ({type(e).__name__}).") from e
    except requests.RequestException as e:
        raise UrlFetchError(f"Could not reach YouTube: {e}") from e

    title = ""
    try:
        r = requests.get("https://www.youtube.com/oembed", params={"url": url, "format": "json"},
                         headers=HEADERS, timeout=10)
        if r.ok:
            title = r.json().get("title", "")
    except (requests.RequestException, ValueError):
        pass
    text = " ".join(s.text.replace("\n", " ") for s in transcript)[:MAX_TEXT_CHARS]
    return Attachment(f"YouTube: {title or video_id}", "text", text=f"Video: {title}\nURL: {url}\n\nTranscript:\n{text}")


def _html_to_text(html: str, url: str) -> Attachment:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "aside", "form", "svg"]):
        tag.decompose()
    title = soup.title.get_text(strip=True) if soup.title else url
    root = soup.find("article") or soup.find("main") or soup.body or soup
    lines = [ln.strip() for ln in root.get_text("\n").splitlines()]
    text = "\n".join(ln for ln in lines if ln)[:MAX_TEXT_CHARS]
    if len(text) < 80:
        raise UrlFetchError("The page has almost no readable text (it may need JavaScript or a login).")
    return Attachment(f"Web: {title}", "text", text=f"Title: {title}\nURL: {url}\n\n{text}")


def fetch_url(url: str) -> Attachment:
    url = url.strip()
    if urlparse(url).scheme not in ("http", "https"):
        raise UrlFetchError(f"Not an http(s) link: {url}")
    if vid := youtube_video_id(url):
        return _youtube(url, vid)
    try:
        with requests.get(url, headers=HEADERS, timeout=20, stream=True) as r:
            r.raise_for_status()
            data = r.raw.read(MAX_BYTES + 1, decode_content=True)
            ctype = r.headers.get("content-type", "").split(";")[0].strip().lower()
            encoding = r.encoding or "utf-8"
    except requests.RequestException as e:
        raise UrlFetchError(f"Could not fetch {url}: {e}") from e
    if len(data) > MAX_BYTES:
        raise UrlFetchError(f"{url} is larger than {MAX_BYTES // 1_000_000} MB.")
    if ctype == "application/pdf":
        return extract(urlparse(url).path.rsplit("/", 1)[-1] or "document.pdf", data)
    if ctype.startswith("image/"):
        return extract(urlparse(url).path.rsplit("/", 1)[-1] or "image.png", data)
    return _html_to_text(data.decode(encoding, errors="replace"), url)
