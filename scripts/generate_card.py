"""Generate a neofetch-style profile card as dark and light SVGs.

The card shows a coloured ASCII portrait built from a local photo next to
profile facts from ``neofetch.json`` and live public stats from the GitHub
API. The output is static SVG, so the profile does not depend on a hosted
rendering service.

Usage:
    python scripts/generate_card.py [--config neofetch.json] [--out dist] [--offline]

Environment:
    GITHUB_TOKEN  optional; enables the contributions count (GraphQL) and
                  raises the REST rate limit.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from html import escape
from pathlib import Path

from PIL import Image

API = "https://api.github.com"
RAMP = ".:-=+*#%@"  # light -> dense; background pixels become spaces
CHAR_ASPECT = 0.5  # monospace glyph width / line height
FONT_SIZE = 14
CHAR_W = 8.4
LINE_H = 18
PAD = 28
ASCII_GAP = 34
INFO_COLS = 56
COLOR_STEP = 24  # colour quantisation keeps the SVG small

DEFAULT_PROMPT = "~$ neofetch"
FONT_STACK = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    border: str
    text: str
    muted: str
    key: str
    title: str
    prompt: str
    ascii_dense_is_bright: bool
    ascii_floor: float  # min brightness kept for ASCII glyphs (dark theme)
    ascii_ceil: float  # max brightness kept for ASCII glyphs (light theme)
    swatches: tuple[str, ...]


# Accents match the banner (teal / violet) and keep >= 4.5:1 contrast.
THEMES = (
    Theme("dark", "#0d1117", "#30363d", "#c9d1d9", "#8b949e",
          "#5eead4", "#a78bfa", "#c4b5fd", True, 0.45, 1.0,
          ("#484f58", "#ff7b72", "#3fb950", "#d29922",
           "#58a6ff", "#bc8cff", "#39c5cf", "#b1bac4")),
    Theme("light", "#ffffff", "#d0d7de", "#24292f", "#57606a",
          "#0f766e", "#6d28d9", "#6d28d9", False, 0.0, 0.48,
          ("#6e7781", "#cf222e", "#1a7f37", "#9a6700",
           "#0969da", "#8250df", "#1b7c83", "#424a53")),
)


# --------------------------------------------------------------------------
# ASCII portrait
# --------------------------------------------------------------------------

def _is_background(rgb: tuple[int, int, int]) -> bool:
    """Studio backdrop: bright and bluer than it is red (incl. the light halo)."""
    r, g, b = rgb
    return (b - r) >= 6 and (r + g + b) / 3 > 165


def _background_mask(img: Image.Image) -> list[list[bool]]:
    """Flood-fill backdrop cells reachable from the top and side edges.

    The bottom edge is not a seed, so a white shirt touching it survives.
    """
    w, h = img.size
    px = img.load()
    candidate = [[_is_background(px[x, y]) for x in range(w)] for y in range(h)]
    mask = [[False] * w for _ in range(h)]
    stack = [(x, 0) for x in range(w)]
    stack += [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if not (0 <= x < w and 0 <= y < h) or mask[y][x] or not candidate[y][x]:
            continue
        mask[y][x] = True
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return mask


def load_portrait(cfg: dict, root: Path) -> tuple[Image.Image, list[list[bool]]]:
    img = Image.open(root / cfg["path"]).convert("RGB")
    if cfg.get("crop"):
        img = img.crop(tuple(cfg["crop"]))
    cols = int(cfg.get("cols", 44))
    rows = max(1, round(img.height / img.width * cols * CHAR_ASPECT))
    small = img.resize((cols, rows), Image.LANCZOS)
    if cfg.get("remove_background", True):
        mask = _background_mask(small)
    else:
        mask = [[False] * cols for _ in range(rows)]
    return small, mask


def _quantise(c: int) -> int:
    return min(255, round(c / COLOR_STEP) * COLOR_STEP)


def _cell(rgb: tuple[int, int, int], theme: Theme) -> tuple[str, str]:
    """Pick a glyph and colour for one foreground pixel."""
    lum = (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255
    level = lum if theme.ascii_dense_is_bright else 1 - lum
    char = RAMP[min(len(RAMP) - 1, int(level * len(RAMP)))]
    # Keep very dark (or very light) pixels visible against the card. A
    # uniform shift (not a multiplicative scale) also lifts pure black.
    target = max(theme.ascii_floor, min(theme.ascii_ceil, lum))
    shift = (target - lum) * 255
    r, g, b = (_quantise(max(0, min(255, int(c + shift)))) for c in rgb)
    return char, f"#{r:02x}{g:02x}{b:02x}"


def ascii_rows(img: Image.Image, mask: list[list[bool]], theme: Theme) -> list[list[tuple[str, str]]]:
    """Return rows of (text-run, colour) segments; colour '' means blank."""
    px = img.load()
    rows = []
    for y in range(img.height):
        runs: list[tuple[str, str]] = []
        for x in range(img.width):
            char, colour = (" ", "") if mask[y][x] else _cell(px[x, y], theme)
            if runs and runs[-1][1] == colour:
                runs[-1] = (runs[-1][0] + char, colour)
            else:
                runs.append((char, colour))
        rows.append(runs)
    return rows


# --------------------------------------------------------------------------
# GitHub stats
# --------------------------------------------------------------------------

def _request(url: str, token: str | None, body: dict | None = None) -> object:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "neofetch-card"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


API_ERRORS = (OSError, urllib.error.URLError, ValueError, KeyError, TypeError, AttributeError)
PER_PAGE = 100


def fetch_owned_repos(username: str, token: str | None) -> list[dict]:
    """All public repos owned by the user (paginated), forks excluded."""
    repos: list[dict] = []
    page = 1
    while True:
        batch = _request(f"{API}/users/{username}/repos?per_page={PER_PAGE}&type=owner&page={page}", token)
        repos.extend(batch)
        if len(batch) < PER_PAGE:
            return [r for r in repos if not r.get("fork")]
        page += 1


def fetch_stats(username: str, token: str | None) -> dict[str, str]:
    stats: dict[str, str] = {}
    try:
        user = _request(f"{API}/users/{username}", token)
        repos = fetch_owned_repos(username, token)
        stats["repos"] = str(len(repos))
        stats["stars"] = str(sum(r.get("stargazers_count", 0) for r in repos))
        stats["followers"] = str(user.get("followers", 0))
    except API_ERRORS as exc:
        print(f"warning: REST stats unavailable ({exc})", file=sys.stderr)
    if token:
        query = ("query($u:String!){user(login:$u){contributionsCollection"
                 "{contributionCalendar{totalContributions}}}}")
        try:
            res = _request(f"{API}/graphql", token, {"query": query, "variables": {"u": username}})
            total = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
            stats["contributions"] = f"{total:,} (last 12 months)"
        except API_ERRORS as exc:
            print(f"warning: contributions unavailable ({exc})", file=sys.stderr)
    return stats


STAT_LABELS = {"repos": "Public repos", "stars": "Stars",
               "followers": "Followers", "contributions": "Contributions"}


# --------------------------------------------------------------------------
# SVG rendering
# --------------------------------------------------------------------------

def info_lines(cfg: dict, stats: dict[str, str]) -> list[tuple[str, ...]]:
    """Build typed lines: ('title', s) | ('rule', n) | ('field', k, v) | ('blank',) | ('palette',)."""
    lines: list[tuple[str, ...]] = [("title", cfg["title"]), ("rule", str(len(cfg["title"])))]
    for i, section in enumerate(cfg["sections"]):
        if i:
            lines.append(("blank",))
        if section.get("title"):
            lines.append(("header", section["title"]))
        lines.extend(("field", k, v) for k, v in section["fields"])
    stat_fields = [(STAT_LABELS[k], stats[k]) for k in cfg["stats"]["fields"] if k in stats]
    if stat_fields:
        lines += [("blank",), ("header", cfg["stats"].get("title", "GitHub"))]
        lines.extend(("field", k, v) for k, v in stat_fields)
    lines += [("blank",), ("palette",)]
    return lines


def _render_info(lines, x: float, y0: float, theme: Theme) -> list[str]:
    out = []
    for i, line in enumerate(lines):
        y = y0 + i * LINE_H
        kind = line[0]
        if kind == "title":
            user, _, host = line[1].partition("@")
            out.append(f'<text x="{x}" y="{y}"><tspan fill="{theme.title}" font-weight="700">{escape(user)}</tspan>'
                       f'<tspan fill="{theme.text}">@</tspan><tspan fill="{theme.title}" font-weight="700">{escape(host)}</tspan></text>')
        elif kind == "rule":
            out.append(f'<text x="{x}" y="{y}" fill="{theme.muted}">{"-" * int(line[1])}</text>')
        elif kind == "header":
            label = f"- {line[1]} "
            fill = "-" * max(4, INFO_COLS - len(label) - 8)
            out.append(f'<text x="{x}" y="{y}"><tspan fill="{theme.title}" font-weight="700">{escape(label)}</tspan>'
                       f'<tspan fill="{theme.muted}">{fill}</tspan></text>')
        elif kind == "field":
            out.append(f'<text x="{x}" y="{y}"><tspan fill="{theme.key}" font-weight="700">{escape(line[1])}</tspan>'
                       f'<tspan fill="{theme.text}">: {escape(line[2])}</tspan></text>')
        elif kind == "palette":
            for j, colour in enumerate(theme.swatches):
                out.append(f'<rect x="{x + j * 26}" y="{y - 12}" width="24" height="14" rx="2" fill="{colour}"/>')
    return out


def _render_ascii(rows, x: float, y0: float, cols: int) -> list[str]:
    out = []
    width = cols * CHAR_W
    for i, runs in enumerate(rows):
        spans = "".join(
            f'<tspan fill="{c}">{escape(t)}</tspan>' if c else escape(t) for t, c in runs
        )
        out.append(f'<text x="{x}" y="{y0 + i * LINE_H}" textLength="{width:.1f}" '
                   f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{spans}</text>')
    return out


def render_svg(cfg: dict, img, mask, stats: dict[str, str], theme: Theme) -> str:
    cols = img.width
    lines = info_lines(cfg, stats)
    body_rows = max(img.height, len(lines))
    prompt_y = PAD + FONT_SIZE
    body_y = prompt_y + LINE_H * 2
    info_x = PAD + cols * CHAR_W + ASCII_GAP
    width = round(info_x + INFO_COLS * CHAR_W + PAD)
    height = round(body_y + body_rows * LINE_H + PAD - LINE_H / 2)
    ascii_y = body_y + (body_rows - img.height) * LINE_H / 2
    info_y = body_y + (body_rows - len(lines)) * LINE_H / 2
    prompt_raw = cfg.get("prompt") or DEFAULT_PROMPT
    prompt = escape(prompt_raw)
    cursor_x = PAD + (len(prompt_raw) + 1) * CHAR_W

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Neofetch-style profile card for {escape(cfg["title"])}">',
        "<style>.c{animation:b 1.1s steps(1) 6}@keyframes b{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.c{animation:none}}</style>",
        f"<title>Neofetch-style profile card for {escape(cfg['title'])}</title>",
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{theme.bg}" stroke="{theme.border}"/>',
        f'<g font-family="{FONT_STACK}" font-size="{FONT_SIZE}">',
        f'<text x="{PAD}" y="{prompt_y}" fill="{theme.prompt}" textLength="{len(prompt_raw) * CHAR_W:.1f}" '
        f'lengthAdjust="spacingAndGlyphs">{prompt}</text>',
        f'<rect class="c" x="{cursor_x:.1f}" y="{prompt_y - 12}" width="8" height="15" fill="{theme.text}"/>',
        *_render_ascii(ascii_rows(img, mask, theme), PAD, ascii_y, cols),
        *_render_info(lines, info_x, info_y, theme),
        "</g></svg>",
    ]
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default="neofetch.json")
    parser.add_argument("--out", default="dist")
    parser.add_argument("--offline", action="store_true", help="skip GitHub API calls")
    parser.add_argument("--require-stats", action="store_true",
                        help="fail (exit 1) instead of rendering a card with missing stats")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    root = config_path.parent
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    img, mask = load_portrait(cfg["image"], root)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    stats = {} if args.offline else fetch_stats(cfg["username"], token)
    missing = [k for k in cfg["stats"]["fields"] if k not in stats]
    if args.require_stats and missing:
        print(f"error: missing stats {missing}; existing cards left unchanged", file=sys.stderr)
        return 1

    out_dir = root / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        path = out_dir / f"neofetch-{theme.name}.svg"
        path.write_text(render_svg(cfg, img, mask, stats, theme), encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(root)} ({path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
