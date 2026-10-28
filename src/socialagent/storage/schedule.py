"""Persistence for scheduled posts. Image bytes are written to disk, paths stored in the row."""
from __future__ import annotations

import json
import uuid
from datetime import datetime

from socialagent.core.models import ScheduledPost
from socialagent.core.settings import DATA_DIR
from socialagent.storage.db import connect


def _row(r) -> ScheduledPost:
    return ScheduledPost(
        id=r["id"], run_at=r["run_at"], platforms=json.loads(r["platforms_json"]),
        telegram_text=r["telegram_text"], whatsapp_text=r["whatsapp_text"],
        image_paths=json.loads(r["image_paths_json"]), send_images=bool(r["send_images"]),
        status=r["status"], note=r["note"], campaign_id=r["campaign_id"],
    )


def add(run_at: datetime, platforms: list[str], telegram_text: str, whatsapp_text: str,
        images: list[bytes], send_images: bool, campaign_id: int | None = None) -> int:
    media_dir = DATA_DIR / "media" / uuid.uuid4().hex
    media_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, png in enumerate(images, 1):
        p = media_dir / f"slide_{i:02d}.png"
        p.write_bytes(png)
        paths.append(str(p))
    with connect() as db:
        cur = db.execute(
            "INSERT INTO scheduled_posts (run_at, platforms_json, telegram_text, whatsapp_text,"
            " image_paths_json, send_images, campaign_id) VALUES (?,?,?,?,?,?,?)",
            (run_at.isoformat(timespec="minutes"), json.dumps(platforms), telegram_text,
             whatsapp_text, json.dumps(paths), int(send_images), campaign_id),
        )
        return cur.lastrowid


def list_all() -> list[ScheduledPost]:
    with connect() as db:
        return [_row(r) for r in db.execute("SELECT * FROM scheduled_posts ORDER BY run_at DESC")]


def due(now: datetime) -> list[ScheduledPost]:
    with connect() as db:
        rows = db.execute("SELECT * FROM scheduled_posts WHERE status='pending' AND run_at<=? ORDER BY run_at",
                          (now.isoformat(timespec="minutes"),)).fetchall()
    return [_row(r) for r in rows]


def claim(post_id: int) -> bool:
    """Atomically move pending -> running; False if someone else got it (or it was cancelled)."""
    with connect() as db:
        return db.execute("UPDATE scheduled_posts SET status='running' WHERE id=? AND status='pending'",
                          (post_id,)).rowcount == 1


def finish(post_id: int, status: str, note: str = "") -> None:
    with connect() as db:
        db.execute("UPDATE scheduled_posts SET status=?, note=? WHERE id=?", (status, note, post_id))


def set_note(post_id: int, note: str) -> None:
    with connect() as db:
        db.execute("UPDATE scheduled_posts SET note=? WHERE id=?", (note, post_id))


def cancel(post_id: int) -> None:
    with connect() as db:
        db.execute("UPDATE scheduled_posts SET status='cancelled' WHERE id=? AND status='pending'", (post_id,))


def delete(post_id: int) -> None:
    with connect() as db:
        db.execute("DELETE FROM scheduled_posts WHERE id=? AND status!='running'", (post_id,))
