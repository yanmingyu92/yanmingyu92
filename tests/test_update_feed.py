"""Unit tests for scripts/update_feed.py (no network)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import update_feed as uf  # noqa: E402

README = f"intro\n{uf.START}\nold\n{uf.END}\noutro\n"

RSS = b"""<?xml version="1.0"?><rss><channel>
<item><title>Paper one</title><link>https://jaimeyan.com/papers/p1.html</link>
<pubDate>Wed, 04 Nov 2026 00:00:00 GMT</pubDate></item>
<item><title>Article
  with <b>html</b> [and] | pipes</title><link>https://jaimeyan.com/blog/a (1).html</link>
<pubDate>Tue, 03 Nov 2026 00:00:00 GMT</pubDate></item>
<item><title>No date</title><link>https://jaimeyan.com/blog/b.html</link></item>
<item><title>Off-site</title><link>javascript:alert(1)</link></item>
</channel></rss>"""


def test_splice_inserts_block_literally_with_backslashes():
    lines = [r"- C:\temp \1 \g<0>"]
    out = uf.splice(README, lines)
    assert r"- C:\temp \1 \g<0>" in out


def test_splice_only_touches_text_between_markers():
    out = uf.splice(README, ["- new"])
    assert out.startswith("intro\n") and out.endswith("\noutro\n")
    assert "old" not in out


def test_splice_raises_when_markers_missing():
    with pytest.raises(ValueError):
        uf.splice("no markers here", ["- x"])


def test_parse_items_escapes_titles_and_filters_links():
    items = uf.parse_items(RSS)
    titles = [i.title for i in items]
    assert len(items) == 3  # javascript: link dropped
    article = items[1]
    assert "\n" not in article.title
    assert "<" not in article.title.replace("\\<", "")
    assert article.link == "https://jaimeyan.com/blog/a%20%281%29.html"
    assert "Off-site" not in " ".join(titles)


def test_item_without_pubdate_is_kept_with_empty_date():
    items = uf.parse_items(RSS)
    no_date = [i for i in items if i.title.startswith("No date")][0]
    assert no_date.date == ""


def test_render_excludes_papers_and_respects_limit():
    items = uf.parse_items(RSS)
    lines = uf.render(items, limit=1)
    assert len(lines) == 1
    assert "papers" not in lines[0]


def test_render_returns_empty_list_when_only_papers():
    items = [uf.Item("P", "https://jaimeyan.com/papers/x.html", "", True)]
    assert uf.render(items, limit=5) == []


def test_rendered_output_resplices_idempotently():
    lines = uf.render(uf.parse_items(RSS), limit=5)
    once = uf.splice(README, lines)
    assert uf.splice(once, lines) == once
