"""Generate the "by the numbers" impact tiles (dark and light SVG).

Each tile shows one career metric. Tiles fade in one after another on load
(disabled under prefers-reduced-motion). Edit TILES to update the numbers.

Usage:
    python scripts/generate_impact.py [--out dist]
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from pathlib import Path

SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif"
TILE_W, TILE_H, GAP = 188, 112, 14


@dataclass(frozen=True)
class Tile:
    value: str
    label: str
    sub: str
    accent: str


TILES = (
    Tile("9+", "Years", "Phase 1–3 · CV & oncology", "#2dd4bf"),
    Tile("NDA", "to FDA approval", "LIPFENDRA® · Merck", "#60a5fa"),
    Tile("Org-wide", "SAS-to-R adoption", "GenAI tooling · Merck", "#a78bfa"),
    Tile("4 + 13", "Papers", "Journal · PhUSE/PharmaSUG", "#f472b6"),
    Tile("2", "Free books", "Clinical R · Modern R (EN/中文)", "#fbbf24"),
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


def tile_svg(i: int, tile: Tile, pal: Palette) -> str:
    x = i * (TILE_W + GAP)
    cx = x + TILE_W / 2
    return f"""<g class="t" style="animation-delay:{0.12 * i:.2f}s">
<rect x="{x + 0.5}" y="0.5" width="{TILE_W - 1}" height="{TILE_H - 1}" rx="12" fill="{pal.card}" stroke="{pal.border}"/>
<rect x="{x + 18}" y="0.5" width="{TILE_W - 36}" height="3" rx="1.5" fill="{tile.accent}"/>
<text x="{cx}" y="50" text-anchor="middle" font-size="34" font-weight="700" fill="{tile.accent}">{escape(tile.value)}</text>
<text x="{cx}" y="76" text-anchor="middle" font-size="14" font-weight="600" fill="{pal.label}">{escape(tile.label)}</text>
<text x="{cx}" y="96" text-anchor="middle" font-size="11.5" fill="{pal.sub}">{escape(tile.sub)}</text>
</g>"""


def build(pal: Palette) -> str:
    width = len(TILES) * TILE_W + (len(TILES) - 1) * GAP
    tiles = "\n".join(tile_svg(i, t, pal) for i, t in enumerate(TILES))
    label = "; ".join(f"{t.value} {t.label} ({t.sub})" for t in TILES)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{TILE_H}" viewBox="0 0 {width} {TILE_H}" role="img" aria-label="{escape(label)}">
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
