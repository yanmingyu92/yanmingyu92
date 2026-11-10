"""Generate the "by the numbers" impact tiles (dark and light SVG).

Each tile shows one career metric, laid out as a 3 + 2 grid so the text
stays legible on mobile. Tiles fade in one after another on load (disabled
under prefers-reduced-motion). Edit TILES to update the numbers.

Usage:
    python scripts/generate_impact.py [--out dist]
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from pathlib import Path

SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif"
TILE_W, TILE_H, GAP = 200, 112, 20
PER_ROW = 3
WIDTH = PER_ROW * TILE_W + (PER_ROW - 1) * GAP


@dataclass(frozen=True)
class Tile:
    value: str
    label: str
    sub: str
    accent_dark: str
    accent_light: str  # >= 4.5:1 on the light card


TILES = (
    Tile("9+", "Years", "Phase 1–3 · CV & oncology", "#2dd4bf", "#0f766e"),
    Tile("NDA", "to FDA approval", "LIPFENDRA® · Merck", "#60a5fa", "#1d4ed8"),
    Tile("Org-wide", "SAS-to-R adoption", "GenAI tooling · Merck", "#a78bfa", "#6d28d9"),
    Tile("4 + 13", "Papers", "Journal · PhUSE/PharmaSUG", "#f472b6", "#be185d"),
    Tile("2", "Free books", "Clinical R · Modern R (EN/中文)", "#fbbf24", "#b45309"),
)


@dataclass(frozen=True)
class Palette:
    name: str
    card: str
    border: str
    value: str
    label: str
    sub: str


PALETTES = (
    Palette("dark", "#161b22", "#30363d", "#f0f6fc", "#c9d1d9", "#8b949e"),
    Palette("light", "#f6f8fa", "#d0d7de", "#1f2328", "#24292f", "#57606a"),
)


def tile_origin(i: int, count: int) -> tuple[float, float]:
    """Top-left corner of tile i; a short last row is centred."""
    row, col = divmod(i, PER_ROW)
    in_row = min(PER_ROW, count - row * PER_ROW)
    row_w = in_row * TILE_W + (in_row - 1) * GAP
    return (WIDTH - row_w) / 2 + col * (TILE_W + GAP), row * (TILE_H + GAP)


def tile_svg(i: int, tile: Tile, pal: Palette) -> str:
    x, y = tile_origin(i, len(TILES))
    cx = x + TILE_W / 2
    accent = tile.accent_dark if pal.name == "dark" else tile.accent_light
    return f"""<g class="t" style="animation-delay:{0.12 * i:.2f}s">
<rect x="{x + 0.5}" y="{y + 0.5}" width="{TILE_W - 1}" height="{TILE_H - 1}" rx="12" fill="{pal.card}" stroke="{pal.border}"/>
<rect x="{x + 18}" y="{y + 0.5}" width="{TILE_W - 36}" height="3" rx="1.5" fill="{accent}"/>
<text x="{cx}" y="{y + 46}" text-anchor="middle" font-size="32" font-weight="700" fill="{accent}">{escape(tile.value)}</text>
<text x="{cx}" y="{y + 74}" text-anchor="middle" font-size="16" font-weight="600" fill="{pal.label}">{escape(tile.label)}</text>
<text x="{cx}" y="{y + 96}" text-anchor="middle" font-size="13" fill="{pal.sub}">{escape(tile.sub)}</text>
</g>"""


def build(pal: Palette) -> str:
    rows = -(-len(TILES) // PER_ROW)
    width, height = WIDTH, rows * TILE_H + (rows - 1) * GAP
    tiles = "\n".join(tile_svg(i, t, pal) for i, t in enumerate(TILES))
    label = "; ".join(f"{t.value} {t.label} ({t.sub})" for t in TILES)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
<style>
.t{{opacity:0;animation:in .6s ease-out forwards}}
@keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.t{{animation:none;opacity:1}}}}
</style>
<g font-family="{SANS}">
{tiles}
</g>
</svg>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="dist")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for pal in PALETTES:
        path = out / f"impact-{pal.name}.svg"
        path.write_text(build(pal), encoding="utf-8")
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
