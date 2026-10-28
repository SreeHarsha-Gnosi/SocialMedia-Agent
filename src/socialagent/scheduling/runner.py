"""Background thread that publishes scheduled posts when they fall due.

Runs inside the app process, so posts only go out while the app is running; anything overdue
is published on the next start. Credentials are held in memory only (never written to the DB).
"""
from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path

from socialagent.core.settings import Credentials
from socialagent.publishers import build_publishers
from socialagent.storage import schedule

POLL_SECONDS = 20


class Scheduler:
    def __init__(self) -> None:
        self.credentials = Credentials()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="post-scheduler", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _loop(self) -> None:
        while not self._stop.wait(POLL_SECONDS):
            try:
                self.run_due()
            except Exception:  # keep the loop alive no matter what
                pass

    def run_due(self, now: datetime | None = None) -> None:
        publishers = build_publishers(self.credentials)
        for post in schedule.due(now or datetime.now()):
            missing = [p for p in post.platforms if p not in publishers]
            if missing:
                schedule.set_note(post.id, f"Waiting for credentials: {', '.join(missing)}")
                continue
            if not schedule.claim(post.id):
                continue
            results = []
            try:
                images = [Path(p).read_bytes() for p in post.image_paths] if post.send_images else None
                for name in post.platforms:
                    text = post.telegram_text if name == "Telegram" else post.whatsapp_text
                    results.append(publishers[name].publish(text, images if name == "Telegram" else None))
            except OSError as e:
                schedule.finish(post.id, "failed", f"Could not read images: {e}")
                continue
            ok = [r for r in results if r.ok]
            status = "sent" if len(ok) == len(results) else "partial" if ok else "failed"
            schedule.finish(post.id, status, "; ".join(f"{r.platform}: {r.detail}" for r in results))
