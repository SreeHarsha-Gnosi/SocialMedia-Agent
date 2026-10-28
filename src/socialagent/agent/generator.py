"""Calls Claude and returns structured content."""
from __future__ import annotations

import json
from dataclasses import asdict

import anthropic

from socialagent.agent.prompts import (REFINE_SYSTEM_PROMPT, SYSTEM_PROMPT, build_brief,
                                       build_followup, build_refine)
from socialagent.agent.schema import CONTENT_SCHEMA, SLIDE_SCHEMA, TEXT_SCHEMA, parse_content
from socialagent.core.models import Attachment, BrandKit, CampaignContent, Slide


class GenerationError(RuntimeError):
    pass


def _content_blocks(attachments: list[Attachment], brief_text: str) -> list[dict]:
    blocks: list[dict] = []
    for a in attachments:
        if a.kind == "pdf":
            blocks.append({"type": "text", "text": f"[File: {a.name}]"})
            blocks.append({"type": "document", "source": {
                "type": "base64", "media_type": a.media_type, "data": a.data_b64}})
        elif a.kind == "image":
            blocks.append({"type": "text", "text": f"[Image: {a.name}]"})
            blocks.append({"type": "image", "source": {
                "type": "base64", "media_type": a.media_type, "data": a.data_b64}})
        else:
            blocks.append({"type": "text", "text": f"[Source: {a.name}]\n{a.text}"})
    blocks.append({"type": "text", "text": brief_text})
    return blocks


class ContentGenerator:
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise GenerationError("Anthropic API key is missing.")
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    # -- low level -------------------------------------------------------------------------
    def _run(self, system: str, content: list[dict] | str, schema: dict,
             effort: str = "medium", max_tokens: int = 16000) -> dict:
        try:
            # Streaming avoids HTTP timeouts on long, high-max_tokens requests.
            with self._client.messages.stream(
                model=self._model,
                max_tokens=max_tokens,
                system=system,
                output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
                messages=[{"role": "user", "content": content}],
            ) as stream:
                response = stream.get_final_message()
        except anthropic.AuthenticationError as e:
            raise GenerationError("Invalid Anthropic API key.") from e
        except anthropic.RateLimitError as e:
            raise GenerationError("Rate limited by Anthropic. Try again shortly.") from e
        except anthropic.APIConnectionError as e:
            raise GenerationError("Network error reaching Anthropic.") from e
        except anthropic.APIStatusError as e:
            raise GenerationError(f"Anthropic API error ({e.status_code}): {e.message}") from e

        if response.stop_reason == "refusal":
            raise GenerationError("Claude declined this request.")
        if response.stop_reason == "max_tokens":
            raise GenerationError("Response was cut off; try fewer slides or less material.")
        text = next((b.text for b in response.content if b.type == "text"), "")
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise GenerationError(f"Could not parse model output: {e}") from e

    def _content(self, system: str, blocks: list[dict]) -> CampaignContent:
        data = self._run(system, blocks, CONTENT_SCHEMA)
        try:
            return parse_content(data)
        except (KeyError, TypeError) as e:
            raise GenerationError(f"Unexpected model output shape: {e}") from e

    # -- campaigns ---------------------------------------------------------------------------
    def generate(self, attachments: list[Attachment], brand: BrandKit,
                 brief: str, slide_count: int = 6) -> CampaignContent:
        if not attachments and not brief.strip():
            raise GenerationError("Provide a file, link or brief to work from.")
        return self._content(SYSTEM_PROMPT,
                             _content_blocks(attachments, build_brief(brand, brief, slide_count)))

    def followup(self, previous: CampaignContent, new_info: str, brand: BrandKit,
                 attachments: list[Attachment] | None = None, slide_count: int = 5) -> CampaignContent:
        if not new_info.strip() and not attachments:
            raise GenerationError("Describe the new information for the follow-up.")
        brief = build_brief(brand, "", slide_count) + "\n\n" + build_followup(previous, new_info)
        return self._content(SYSTEM_PROMPT, _content_blocks(attachments or [], brief))

    # -- single-piece regeneration -----------------------------------------------------------
    def refine_slide(self, slide: Slide, instruction: str, content: CampaignContent,
                     brand: BrandKit) -> Slide:
        prompt = build_refine("Instagram slide, JSON", json.dumps(asdict(slide), ensure_ascii=False),
                              instruction, content, brand)
        data = self._run(REFINE_SYSTEM_PROMPT, prompt, SLIDE_SCHEMA, effort="low", max_tokens=2000)
        return Slide(**data)

    def refine_text(self, label: str, current: str, instruction: str, content: CampaignContent,
                    brand: BrandKit) -> str:
        prompt = build_refine(label, current, instruction, content, brand)
        return self._run(REFINE_SYSTEM_PROMPT, prompt, TEXT_SCHEMA, effort="low", max_tokens=4000)["text"]
