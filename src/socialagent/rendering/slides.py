"""Renders `Slide`s to 1080x1350 (4:5) PNGs with Pillow."""
from __future__ import annotations

import io
import zipfile
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

from socialagent.core.models import BrandKit, Slide
from socialagent.rendering.themes import THEMES, Theme

W, H = 1080, 1350
MARGIN = 100

_FONT_CANDIDATES = {
    True: ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "Helvetica-Bold.ttc"],
    False: ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf", "Helvetica.ttc"],
}


@lru_cache(maxsize=64)
def _font(size: int, bold: bool) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in _FONT_CANDIDATES[bold]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def _gradient(theme: Theme) -> Image.Image:
    strip = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1)
        strip.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip(theme.top, theme.bottom)))
    return strip.resize((W, H))


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = f"{line} {word}".strip()
            if draw.textlength(trial, font=font) <= max_w:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
    return lines


def _fit(draw, text: str, bold: bool, start: int, min_size: int, max_w: int, max_h: int):
    """Largest font size at which the wrapped text fits the box."""
    size = start
    while True:
        font = _font(size, bold)
        lines = _wrap(draw, text, font, max_w)
        height = len(lines) * int(size * 1.22)
        if (height <= max_h and all(draw.textlength(l, font=font) <= max_w for l in lines)) or size <= min_size:
            return font, lines, size
        size -= 4


def _draw_block(draw, xy, lines, font, size, fill, align="left", max_w=W - 2 * MARGIN) -> int:
    x, y = xy
    for line in lines:
        lx = x if align == "left" else x + (max_w - draw.textlength(line, font=font)) / 2
        draw.text((lx, y), line, font=font, fill=fill)
        y += int(size * 1.22)
    return y


def render_slide(slide: Slide, index: int, total: int, brand: BrandKit) -> Image.Image:
    theme = THEMES.get(brand.theme, THEMES["Aurora"])
    img = _gradient(theme)
    d = ImageDraw.Draw(img)
    box_w = W - 2 * MARGIN

    # Decorative accent circle
    d.ellipse((W - 380, -200, W + 120, 300), fill=tuple(int(c * 0.08 + b * 0.92) + 12 for c, b in zip(theme.accent, theme.top)))

    # Top bar: brand + page counter
    d.text((MARGIN, 80), brand.name.upper(), font=_font(30, True), fill=theme.accent)
    counter = f"{index + 1}/{total}"
    d.text((W - MARGIN - d.textlength(counter, font=_font(30, False)), 80), counter,
           font=_font(30, False), fill=theme.muted)

    kind = slide.kind
    if kind == "stat" and slide.stat:
        font, lines, size = _fit(d, slide.stat, True, 300, 120, box_w, 360)
        y = _draw_block(d, (MARGIN, 330), lines, font, size, theme.accent)
        hf, hl, hs = _fit(d, slide.headline, True, 64, 40, box_w, 260)
        y = _draw_block(d, (MARGIN, y + 30), hl, hf, hs, theme.text)
        if slide.body:
            bf, bl, bs = _fit(d, slide.body, False, 40, 28, box_w, 300)
            _draw_block(d, (MARGIN, y + 20), bl, bf, bs, theme.muted)
    elif kind == "cover":
        hf, hl, hs = _fit(d, slide.headline, True, 108, 56, box_w, 620)
        y = _draw_block(d, (MARGIN, 380), hl, hf, hs, theme.text)
        d.rounded_rectangle((MARGIN, y + 30, MARGIN + 140, y + 42), 6, fill=theme.accent)
        if slide.body:
            bf, bl, bs = _fit(d, slide.body, False, 44, 30, box_w, 260)
            _draw_block(d, (MARGIN, y + 80), bl, bf, bs, theme.muted)
        d.text((MARGIN, H - 190), "Swipe  →", font=_font(34, True), fill=theme.accent)
    elif kind == "quote":
        d.text((MARGIN - 10, 230), "“", font=_font(300, True), fill=theme.accent)
        hf, hl, hs = _fit(d, slide.headline, True, 70, 38, box_w, 560)
        y = _draw_block(d, (MARGIN, 470), hl, hf, hs, theme.text)
        if slide.body:
            bf, bl, bs = _fit(d, "— " + slide.body, False, 36, 26, box_w, 120)
            _draw_block(d, (MARGIN, y + 30), bl, bf, bs, theme.muted)
    elif kind == "cta":
        hf, hl, hs = _fit(d, slide.headline, True, 92, 50, box_w, 520)
        y = _draw_block(d, (MARGIN, 360), hl, hf, hs, theme.text)
        if slide.body:
            bf, bl, bs = _fit(d, slide.body, False, 42, 28, box_w, 260)
            y = _draw_block(d, (MARGIN, y + 30), bl, bf, bs, theme.muted)
        label = brand.handle or brand.name
        pw = int(d.textlength(label, font=_font(44, True))) + 100
        d.rounded_rectangle((MARGIN, y + 60, MARGIN + pw, y + 160), 50, fill=theme.accent)
        d.text((MARGIN + 50, y + 85), label, font=_font(44, True), fill=theme.top)
    else:  # content
        hf, hl, hs = _fit(d, slide.headline, True, 80, 44, box_w, 320)
        y = _draw_block(d, (MARGIN, 240), hl, hf, hs, theme.text)
        d.rounded_rectangle((MARGIN, y + 20, MARGIN + 100, y + 30), 5, fill=theme.accent)
        if slide.body:
            bf, bl, bs = _fit(d, slide.body, False, 48, 30, box_w, H - y - 400)
            _draw_block(d, (MARGIN, y + 70), bl, bf, bs, theme.muted)

    # Footer
    d.text((MARGIN, H - 110), brand.handle, font=_font(30, False), fill=theme.muted)
    return img


def render_deck(slides: list[Slide], brand: BrandKit) -> list[bytes]:
    out = []
    for i, s in enumerate(slides):
        buf = io.BytesIO()
        render_slide(s, i, len(slides), brand).save(buf, "PNG")
        out.append(buf.getvalue())
    return out


def build_zip(pngs: list[bytes], caption: str, hashtags: list[str],
              telegram: str, whatsapp: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for i, png in enumerate(pngs, 1):
            z.writestr(f"instagram/slide_{i:02d}.png", png)
        z.writestr("instagram/caption.txt", caption + "\n\n" + " ".join(f"#{h}" for h in hashtags))
        z.writestr("telegram.txt", telegram)
        z.writestr("whatsapp.txt", whatsapp)
    return buf.getvalue()
