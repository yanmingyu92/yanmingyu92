"""Refresh the "Latest writing" list in README.md from the jaimeyan.com RSS feed.

The list lives between the markers
    <!-- FEED:START -->  and  <!-- FEED:END -->
This is the same pattern as gautamkrishnar/blog-post-workflow, implemented
with the standard library only so it runs locally or in GitHub Actions.

Safety rules (the feed is treated as untrusted input):
- titles are collapsed to one line and Markdown/HTML-escaped;
- only https://jaimeyan.com/ links are accepted;
- if no usable article is found, the README is left unchanged.

Usage:
    python scripts/update_feed.py [--readme README.md] [--limit 5]
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from pathlib import Path

FEED_URL = "https://jaimeyan.com/rss.xml"
ALLOWED_PREFIX = "https://jaimeyan.com/"
START, END = "<!-- FEED:START -->", "<!-- FEED:END -->"
MAX_FEED_BYTES = 2_000_000
_MD_SPECIALS = re.compile(r"([\\`*_{}\[\]()<>#+!|&-])")


@dataclass(frozen=True)
class Item:
    title: str
    link: str
    date: str
    is_paper: bool


def clean_title(raw: str) -> str:
    """One line, Markdown/HTML characters backslash-escaped."""
    return _MD_SPECIALS.sub(r"\\\1", " ".join(raw.split()))


def clean_link(raw: str) -> str | None:
    """Accept only site links; percent-encode characters that break Markdown."""
    link = raw.strip()
    if not link.startswith(ALLOWED_PREFIX):
        return None
    return urllib.parse.quote(link, safe=":/?#=&%.~-_")


def format_date(raw: str | None) -> str:
    try:
        return parsedate_to_datetime(raw).strftime("%b %d, %Y") if raw else ""
    except (TypeError, ValueError):
        return ""


def parse_items(xml_bytes: bytes) -> list[Item]:
    items = []
    for node in ET.fromstring(xml_bytes).iter("item"):
        link = clean_link(node.findtext("link") or "")
        title = (node.findtext("title") or "").strip()
        if not link or not title:
            continue
        items.append(Item(clean_title(title), link, format_date(node.findtext("pubDate")), "/papers/" in link))
    return items


def fetch_feed(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "profile-feed"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read(MAX_FEED_BYTES)


def render(items: list[Item], limit: int) -> list[str]:
    articles = [i for i in items if not i.is_paper][:limit]
    return [
        f"- [{i.title}]({i.link})" + (f" <sub>· {i.date}</sub>" if i.date else "")
        for i in articles
    ]


def splice(readme: str, lines: list[str]) -> str:
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(readme):
        raise ValueError(f"markers {START} / {END} not found in README")
    block = "\n".join([START, *lines, END])
    # A callable replacement is inserted literally (no backslash templates).
    return pattern.sub(lambda _: block, readme, count=1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    path = Path(args.readme)
    try:
        lines = render(parse_items(fetch_feed(FEED_URL)), args.limit)
    except (OSError, urllib.error.URLError, ET.ParseError) as exc:
        print(f"error: could not read feed ({exc}); README left unchanged", file=sys.stderr)
        return 1
    if not lines:
        print("error: feed had no usable articles; README left unchanged", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    path.write_text(splice(text, lines), encoding="utf-8", newline="\n")
    print(f"updated {path} with {len(lines)} articles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
