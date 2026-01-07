from __future__ import annotations

import difflib
import re
from typing import List

from daily_digest_bot.feeds import NewsItem


def _tokenize(title: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", title.lower()) if len(t) > 2}


def _similarity(a: NewsItem, b: NewsItem) -> float:
    tokens_a = _tokenize(a.title)
    tokens_b = _tokenize(b.title)
    if tokens_a and tokens_b:
        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b
        return len(intersection) / max(len(union), 1)
    return difflib.SequenceMatcher(a=a.title.lower(), b=b.title.lower()).ratio()


def dedupe_items(items: List[NewsItem], threshold: float = 0.6) -> List[NewsItem]:
    kept: List[NewsItem] = []
    for item in items:
        match_index = None
        for idx, existing in enumerate(kept):
            if _similarity(item, existing) >= threshold:
                match_index = idx
                break
        if match_index is None:
            kept.append(item)
        else:
            if item.score > kept[match_index].score:
                kept[match_index] = item
    kept.sort(
        key=lambda i: (-i.score, -i.published_at.timestamp(), i.title.lower(), i.source.lower())
    )
    return kept
