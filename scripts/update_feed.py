"""Refresh the "Latest writing" list in README.md from the jaimeyan.com RSS feed.

The list lives between the markers
    <!-- FEED:START -->  and  <!-- FEED:END -->
This is the same pattern as gautamkrishnar/blog-post-workflow, implemented
with the standard library only so it runs locally or in GitHub Actions.

Usage:
    python scripts/update_feed.py [--readme README.md] [--limit 5]
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

FEED_URL = "https://jaimeyan.com/rss.xml"
START, END = "<!-- FEED:START -->", "<!-- FEED:END -->"


def fetch_items(url: str) -> list[dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": "profile-feed"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        root = ET.fromstring(resp.read())
    items = []
    for node in root.iter("item"):
        link = (node.findtext("link") or "").strip()
        title = (node.findtext("title") or "").strip()
        if not link or not title:
            continue
        date = parsedate_to_datetime(node.findtext("pubDate")).strftime("%b %d, %Y")
        kind = "paper" if "/papers/" in link else "article"
        items.append({"title": title, "link": link, "date": date, "kind": kind})
    return items


def _escape_md(text: str) -> str:
    return text.replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def render(items: list[dict[str, str]], limit: int) -> str:
    articles = [i for i in items if i["kind"] == "article"][:limit]
    return "\n".join(f"- [{_escape_md(i['title'])}]({i['link']}) <sub>· {i['date']}</sub>" for i in articles)


def splice(readme: str, block: str) -> str:
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(readme):
        raise ValueError(f"markers {START} / {END} not found in README")
    return pattern.sub(f"{START}\n{block}\n{END}", readme)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    path = Path(args.readme)
    try:
        items = fetch_items(FEED_URL)
    except Exception as exc:  # network or XML problems should not wipe the list
        print(f"error: could not read feed ({exc}); README left unchanged", file=sys.stderr)
        return 1
    new = splice(path.read_text(encoding="utf-8"), render(items, args.limit))
    path.write_text(new, encoding="utf-8")
    print(f"updated {path} with {min(args.limit, len(items))} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
