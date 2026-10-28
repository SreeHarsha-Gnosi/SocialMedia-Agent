"""JSON schemas for Claude's structured output + parsers into domain models."""
from __future__ import annotations

from socialagent.core.models import CampaignContent, CaptionVariant, InstagramPost, Slide

_str = {"type": "string"}

SLIDE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["kind", "headline", "body", "stat"],
    "properties": {
        "kind": {"type": "string", "enum": ["cover", "content", "stat", "quote", "cta"]},
        "headline": _str,
        "body": _str,
        "stat": _str,
    },
}

TEXT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["text"],
    "properties": {"text": _str},
}

CONTENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "instagram", "telegram", "whatsapp"],
    "properties": {
        "summary": _str,
        "instagram": {
            "type": "object",
            "additionalProperties": False,
            "required": ["caption_variants", "hashtags", "slides"],
            "properties": {
                "caption_variants": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["label", "text"],
                        "properties": {"label": _str, "text": _str},
                    },
                },
                "hashtags": {"type": "array", "items": _str},
                "slides": {"type": "array", "items": SLIDE_SCHEMA},
            },
        },
        "telegram": _str,
        "whatsapp": _str,
    },
}


def parse_content(data: dict) -> CampaignContent:
    """Accepts both model output (caption_variants only) and stored dicts (with `caption`)."""
    ig = data["instagram"]
    variants = [CaptionVariant(**v) for v in ig.get("caption_variants", [])]
    caption = ig.get("caption") or (variants[0].text if variants else "")
    return CampaignContent(
        summary=data["summary"],
        instagram=InstagramPost(
            caption=caption,
            hashtags=[h.lstrip("#") for h in ig["hashtags"]],
            slides=[Slide(**s) for s in ig["slides"]],
            caption_variants=variants,
        ),
        telegram=data["telegram"],
        whatsapp=data["whatsapp"],
    )
