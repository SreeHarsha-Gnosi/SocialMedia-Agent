from __future__ import annotations

import json
from dataclasses import asdict

from socialagent.core.models import BrandKit, CampaignContent

SYSTEM_PROMPT = """You are a senior social media strategist and copywriter.
You receive source material (documents, spreadsheets, images, web pages, video transcripts) and a brief,
and produce ready-to-post content for Instagram (carousel), Telegram and WhatsApp.

Rules:
- Use only facts present in the source material. Never invent numbers, quotes or claims.
- Instagram carousel: slide 1 is a "cover" with a scroll-stopping hook; the last slide is a "cta".
  Use "stat" slides for a single striking number (put it in `stat`, short, e.g. "42%"),
  "quote" for a notable quote, "content" for key points. Headlines max ~8 words; body max ~35 words.
  Leave `stat` and `body` as empty strings when unused.
- Instagram captions: write exactly 3 distinct variants in `caption_variants`, each with a short `label`
  (e.g. "Punchy", "Storytelling", "Professional"). Each has a hook line, a short value-adding body and a call to action.
- Hashtags: 8-15, without the leading hash sign.
- Telegram: an informative message with a title line, concise bullets, and a closing line.
  Use Telegram HTML only (<b>, <i>, <a>).
- WhatsApp: conversational and compact. Use WhatsApp formatting (*bold*, _italic_) and a few emojis.
- Write in the requested language and tone, for the stated audience.
- `summary` is a 1-2 sentence description of what the source material says (for the user, not for posting)."""

REFINE_SYSTEM_PROMPT = """You are a senior social media copywriter editing one piece of an existing campaign.
Apply the user's instruction to the piece and return only the revised piece.
Keep facts consistent with the campaign; do not invent new numbers or claims.
Keep the same language and platform formatting (Telegram: HTML tags <b>,<i>,<a> only;
WhatsApp: *bold*, _italic_; Instagram slides: headline max ~8 words, body max ~35 words)."""


def build_brief(brand: BrandKit, brief: str, slide_count: int) -> str:
    return (
        f"Brand: {brand.name} ({brand.handle})\n"
        f"Tone: {brand.tone}\n"
        f"Language: {brand.language}\n"
        f"Target audience: {brand.audience or 'general social media audience'}\n"
        f"Instagram carousel length: exactly {slide_count} slides\n\n"
        f"User brief:\n{brief.strip() or '(none - decide the best angle from the source material)'}"
    )


def build_followup(previous: CampaignContent, new_info: str) -> str:
    return (
        "This is a FOLLOW-UP campaign. Below is the earlier campaign that was already posted, "
        "followed by new information. Write fresh posts that remind the audience of the earlier "
        "post in one line, then lead with the new information. Do not repeat the earlier copy.\n\n"
        f"Earlier campaign (JSON):\n{json.dumps(asdict(previous), ensure_ascii=False)}\n\n"
        f"New information / angle:\n{new_info.strip()}"
    )


def build_refine(piece_label: str, current: str, instruction: str,
                 content: CampaignContent, brand: BrandKit) -> str:
    return (
        f"Brand: {brand.name}; tone: {brand.tone}; language: {brand.language}.\n"
        f"Campaign summary: {content.summary}\n\n"
        f"Piece to revise ({piece_label}):\n{current}\n\n"
        f"Instruction: {instruction.strip()}"
    )
