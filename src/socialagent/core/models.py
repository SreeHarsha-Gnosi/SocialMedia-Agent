"""Domain models shared across layers (no I/O, no framework imports)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SlideKind = Literal["cover", "content", "stat", "quote", "cta"]


@dataclass
class Attachment:
    """An uploaded file or fetched link normalised for the LLM: text, or a binary block (pdf/image)."""

    name: str
    kind: Literal["text", "pdf", "image"]
    text: str = ""
    media_type: str = ""
    data_b64: str = ""


@dataclass
class Slide:
    kind: SlideKind
    headline: str
    body: str = ""
    stat: str = ""


@dataclass
class CaptionVariant:
    label: str
    text: str


@dataclass
class InstagramPost:
    caption: str
    hashtags: list[str]
    slides: list[Slide]
    caption_variants: list[CaptionVariant] = field(default_factory=list)


@dataclass
class CampaignContent:
    summary: str
    instagram: InstagramPost
    telegram: str
    whatsapp: str


@dataclass
class BrandKit:
    name: str = "My Brand"
    handle: str = "@mybrand"
    theme: str = "Aurora"
    tone: str = "Friendly & energetic"
    language: str = "English"
    audience: str = ""


@dataclass
class PublishResult:
    platform: str
    ok: bool
    detail: str = ""
    extra: dict = field(default_factory=dict)


@dataclass
class Campaign:
    """A saved generation (history entry)."""

    id: int
    created_at: str
    title: str
    brief: str
    brand: BrandKit
    content: CampaignContent
    parent_id: int | None = None


@dataclass
class ScheduledPost:
    id: int
    run_at: str  # naive local ISO timestamp
    platforms: list[str]
    telegram_text: str
    whatsapp_text: str
    image_paths: list[str]
    send_images: bool
    status: Literal["pending", "running", "sent", "partial", "failed", "cancelled"]
    note: str = ""
    campaign_id: int | None = None
