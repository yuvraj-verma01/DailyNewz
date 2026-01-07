from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Iterable, List, Optional

import feedparser
import requests

from daily_digest_bot.config import FeedConfig


@dataclass
class NewsItem:
    title: str
    link: str
    published_at: datetime
    source: str
    summary: str
    date_missing: bool = False
    score: float = field(default=0.0)


def _parse_entry_datetime(entry: dict) -> Optional[datetime]:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    try:
        return datetime(
            parsed.tm_year,
            parsed.tm_mon,
            parsed.tm_mday,
            parsed.tm_hour,
            parsed.tm_min,
            parsed.tm_sec,
            tzinfo=timezone.utc,
        )
    except Exception:
        return None


def _coerce_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def _summarize_text(text: str, max_chars: int = 320, max_sentences: int = 2) -> str:
    cleaned = _strip_html(text)
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    summary = " ".join(sentences[:max_sentences]).strip()
    if not summary:
        summary = cleaned
    if len(summary) > max_chars:
        summary = summary[: max_chars - 3].rstrip() + "..."
    return summary


def fetch_feeds(feeds: Iterable[FeedConfig], timeout: int = 12) -> List[NewsItem]:
    items: List[NewsItem] = []
    now = datetime.now(timezone.utc)
    headers = {
        "User-Agent": "daily-digest-bot/0.1 (+https://example.com)",
        "Accept": "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.5",
    }
    for feed in feeds:
        try:
            response = requests.get(feed.url, timeout=timeout, headers=headers)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"[warn] Failed to fetch {feed.name}: {exc}")
            continue

        parsed = feedparser.parse(response.content)
        if parsed.bozo:
            print(f"[warn] RSS parse issue for {feed.name}: {parsed.bozo_exception}")

        for entry in parsed.entries:
            title = _coerce_text(entry.get("title"))
            link = _coerce_text(entry.get("link"))
            raw_summary = _coerce_text(entry.get("summary") or entry.get("description"))
            if not raw_summary:
                content = entry.get("content")
                if isinstance(content, list) and content:
                    raw_summary = _coerce_text(content[0].get("value"))
            summary = _summarize_text(raw_summary)
            if not summary and title:
                summary = title
            published_at = _parse_entry_datetime(entry)
            date_missing = False
            if published_at is None:
                published_at = now
                date_missing = True
            items.append(
                NewsItem(
                    title=title,
                    link=link,
                    published_at=published_at,
                    source=feed.name,
                    summary=summary,
                    date_missing=date_missing,
                )
            )
    return items
