#!/usr/bin/env python3
"""Fetches latest news from Google News RSS feeds and writes news-data.json."""
import feedparser
import json
import datetime
import re
import html as html_mod

FEEDS = {
    "Microsoft": (
        "https://news.google.com/rss/search?"
        "q=microsoft&hl=es-419&gl=AR&ceid=AR:es-419"
    ),
    "Marketing": (
        "https://news.google.com/rss/search?"
        "q=marketing+digital&hl=es-419&gl=AR&ceid=AR:es-419"
    ),
    "IA": (
        "https://news.google.com/rss/search?"
        "q=inteligencia+artificial&hl=es-419&gl=AR&ceid=AR:es-419"
    ),
    "Vaca Muerta": (
        "https://news.google.com/rss/search?"
        "q=%22vaca+muerta%22&hl=es-419&gl=AR&ceid=AR:es-419"
    ),
}

MAX_ITEMS = 7


def clean(text, max_len=300):
    """Strip HTML tags, decode entities, normalise whitespace."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html_mod.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        text = text[:max_len].rsplit(" ", 1)[0] + "…"
    return text


def clean_title(title):
    """Remove the trailing source attribution added by Google News (e.g. ' - Infobae')."""
    title = clean(title)
    title = re.sub(r"\s+-\s+[^-]{3,60}$", "", title).strip()
    return title


def parse_date(date_str):
    if not date_str:
        return ""
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str).isoformat()
    except Exception:
        return date_str[:25]


def fetch(name, url):
    print(f"  {name}…", end=" ", flush=True)
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:MAX_ITEMS]:
            title = clean_title(entry.get("title", ""))
            if not title:
                continue
            source = getattr(getattr(entry, "source", None), "title", "") or ""
            items.append({
                "title": title,
                "description": clean(entry.get("summary", ""), 280),
                "link": entry.get("link", "#"),
                "date": parse_date(entry.get("published", "")),
                "source": source,
            })
        print(f"✓ {len(items)} items")
        return items
    except Exception as exc:
        print(f"✗ {exc}")
        return []


if __name__ == "__main__":
    print("Fetching news…\n")
    output = {
        "updated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "categories": {name: fetch(name, url) for name, url in FEEDS.items()},
    }
    with open("news-data.json", "w", encoding="utf-8") as fh:
        json.dump(output, fh, ensure_ascii=False, indent=2)
    total = sum(len(v) for v in output["categories"].values())
    print(f"\nGuardado news-data.json — {total} noticias — {output['updated_at']}")
