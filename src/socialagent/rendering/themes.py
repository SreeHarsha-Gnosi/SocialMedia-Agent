"""Visual themes for Instagram slides (RGB tuples)."""
from __future__ import annotations

from dataclasses import dataclass

RGB = tuple[int, int, int]


@dataclass(frozen=True)
class Theme:
    name: str
    top: RGB
    bottom: RGB
    accent: RGB
    text: RGB
    muted: RGB


THEMES: dict[str, Theme] = {t.name: t for t in [
    Theme("Aurora", (30, 20, 80), (110, 40, 160), (255, 190, 90), (255, 255, 255), (214, 200, 240)),
    Theme("Sunset", (255, 110, 80), (175, 45, 30), (255, 235, 150), (255, 255, 255), (255, 225, 215)),
    Theme("Ocean", (8, 40, 80), (10, 120, 140), (120, 240, 210), (255, 255, 255), (200, 235, 240)),
    Theme("Midnight", (10, 10, 20), (35, 35, 60), (139, 92, 246), (245, 245, 250), (160, 160, 185)),
    Theme("Paper", (250, 246, 238), (235, 226, 208), (200, 70, 50), (30, 28, 26), (110, 104, 96)),
]}
