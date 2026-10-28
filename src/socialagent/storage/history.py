"""Persistence for generated campaigns."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime

from socialagent.agent.schema import parse_content
from socialagent.core.models import BrandKit, Campaign, CampaignContent
from socialagent.storage.db import connect


def _title(content: CampaignContent) -> str:
    slides = content.instagram.slides
    text = slides[0].headline if slides else content.summary
    return text[:80] or "Untitled"


def _row_to_campaign(r) -> Campaign:
    return Campaign(
        id=r["id"], created_at=r["created_at"], title=r["title"], brief=r["brief"],
        brand=BrandKit(**json.loads(r["brand_json"])),
        content=parse_content(json.loads(r["content_json"])),
        parent_id=r["parent_id"],
    )


def save(content: CampaignContent, brand: BrandKit, brief: str, parent_id: int | None = None) -> int:
    with connect() as db:
        cur = db.execute(
            "INSERT INTO campaigns (created_at, title, brief, brand_json, content_json, parent_id)"
            " VALUES (?,?,?,?,?,?)",
            (datetime.now().isoformat(timespec="seconds"), _title(content), brief,
             json.dumps(asdict(brand)), json.dumps(asdict(content)), parent_id),
        )
        return cur.lastrowid


def update(campaign_id: int, content: CampaignContent) -> None:
    with connect() as db:
        db.execute("UPDATE campaigns SET content_json=?, title=? WHERE id=?",
                   (json.dumps(asdict(content)), _title(content), campaign_id))


def list_all() -> list[Campaign]:
    with connect() as db:
        return [_row_to_campaign(r) for r in db.execute("SELECT * FROM campaigns ORDER BY id DESC")]


def get(campaign_id: int) -> Campaign | None:
    with connect() as db:
        r = db.execute("SELECT * FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
    return _row_to_campaign(r) if r else None


def delete(campaign_id: int) -> None:
    with connect() as db:
        db.execute("DELETE FROM campaigns WHERE id=?", (campaign_id,))
