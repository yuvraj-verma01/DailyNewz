from __future__ import annotations

from datetime import datetime, timezone
from math import exp, log
from typing import Iterable, List, Mapping, Sequence

from daily_digest_bot.feeds import NewsItem

HALF_LIFE_HOURS = 18.0
KEYWORD_BOOST_PER = 0.12
KEYWORD_BOOST_CAP = 0.5


def _recency_score(published_at: datetime, now: datetime, half_life_hours: float) -> float:
    age_seconds = max((now - published_at).total_seconds(), 0.0)
    age_hours = age_seconds / 3600.0
    if half_life_hours <= 0:
        return 1.0
    return exp(-log(2) * (age_hours / half_life_hours))


def _keyword_boost(text: str, keywords: Sequence[str]) -> float:
    if not keywords:
        return 1.0
    lowered = text.lower()
    hits = sum(1 for kw in keywords if kw and kw.lower() in lowered)
    boost = min(hits * KEYWORD_BOOST_PER, KEYWORD_BOOST_CAP)
    return 1.0 + boost


def _completeness_factor(item: NewsItem) -> float:
    factor = 1.0
    if not item.title:
        factor *= 0.5
    if not item.link:
        factor *= 0.7
    if item.date_missing:
        factor *= 0.6
    return factor


def score_item(
    item: NewsItem,
    source_weights: Mapping[str, float],
    keywords: Sequence[str],
    now: datetime | None = None,
    half_life_hours: float = HALF_LIFE_HOURS,
) -> float:
    current = now or datetime.now(timezone.utc)
    source_weight = source_weights.get(item.source, 1.0)
    recency = _recency_score(item.published_at, current, half_life_hours)
    keyword_boost = _keyword_boost(f"{item.title} {item.summary}", keywords)
    completeness = _completeness_factor(item)
    return source_weight * recency * keyword_boost * completeness


def rank_items(
    items: Iterable[NewsItem],
    source_weights: Mapping[str, float],
    keywords: Sequence[str],
    now: datetime | None = None,
    half_life_hours: float = HALF_LIFE_HOURS,
) -> List[NewsItem]:
    current = now or datetime.now(timezone.utc)
    ranked: List[NewsItem] = []
    for item in items:
        item.score = score_item(
            item,
            source_weights=source_weights,
            keywords=keywords,
            now=current,
            half_life_hours=half_life_hours,
        )
        ranked.append(item)
    ranked.sort(
        key=lambda i: (
            -i.score,
            -i.published_at.timestamp(),
            i.title.lower(),
            i.source.lower(),
        )
    )
    return ranked
