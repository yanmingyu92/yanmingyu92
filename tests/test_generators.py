"""Unit tests for the SVG generators (no network)."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import generate_banner as gb  # noqa: E402
import generate_card as gc  # noqa: E402
import generate_impact as gi  # noqa: E402

DARK, LIGHT = gc.THEMES


def _cfg(**overrides):
    cfg = {
        "username": "u",
        "title": "a&b<c@host",
        "prompt": "x@y:~$ neofetch",
        "sections": [{"fields": [["Key", "R & <Python>"]]}],
        "stats": {"fields": ["repos"]},
    }
    cfg.update(overrides)
    return cfg


def _tiny_portrait():
    img = Image.new("RGB", (4, 3), (120, 90, 80))
    return img, [[False] * 4 for _ in range(3)]


def test_background_detection():
    assert gc._is_background((200, 210, 230))
    assert not gc._is_background((250, 250, 250))  # white shirt
    assert not gc._is_background((20, 15, 15))  # hair


def test_flood_fill_does_not_seed_from_bottom_edge():
    img = Image.new("RGB", (3, 3), (240, 240, 240))
    img.putpixel((1, 2), (200, 210, 235))  # backdrop-coloured pixel on bottom edge only
    mask = gc._background_mask(img)
    assert mask[2][1] is False


def test_dark_theme_keeps_black_pixels_visible():
    char, colour = gc._cell((0, 0, 0), DARK)
    assert char != " "
    assert colour != "#000000"


def test_ascii_rows_merge_same_colour_runs():
    img, mask = _tiny_portrait()
    rows = gc.ascii_rows(img, mask, DARK)
    assert all(len(r) == 1 for r in rows)


def test_card_svg_is_well_formed_and_escaped():
    img, mask = _tiny_portrait()
    svg = gc.render_svg(_cfg(), img, mask, {"repos": "3"}, LIGHT)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert "R &amp; &lt;Python&gt;" in svg


def test_missing_prompt_falls_back_and_keeps_width():
    img, mask = _tiny_portrait()
    svg = gc.render_svg(_cfg(prompt=""), img, mask, {}, DARK)
    assert gc.DEFAULT_PROMPT.replace("$", "$") in svg
    assert 'textLength="0.0"' not in svg


def test_fetch_owned_repos_paginates(monkeypatch):
    pages = {1: [{"stargazers_count": 1}] * 100, 2: [{"stargazers_count": 2}] * 5 + [{"fork": True}]}

    def fake_request(url, token, body=None):
        return pages[int(url.rsplit("page=", 1)[1])]

    monkeypatch.setattr(gc, "_request", fake_request)
    repos = gc.fetch_owned_repos("u", None)
    assert len(repos) == 105
    assert sum(r["stargazers_count"] for r in repos) == 110


def test_banner_is_deterministic_and_well_formed():
    assert gb.build() == gb.build()
    ET.fromstring(gb.build())
    ET.fromstring(gb.build_footer())


def test_impact_tiles_fit_grid_and_parse():
    for pal in gi.PALETTES:
        ET.fromstring(gi.build(pal))
    for i in range(len(gi.TILES)):
        x, _ = gi.tile_origin(i, len(gi.TILES))
        assert 0 <= x and x + gi.TILE_W <= gi.WIDTH
