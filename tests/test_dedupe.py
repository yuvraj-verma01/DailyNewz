from datetime import datetime, timezone

from daily_digest_bot.dedupe import dedupe_items
from daily_digest_bot.feeds import NewsItem


def test_dedupe_keeps_highest_score() -> None:
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    item_a = NewsItem(
        title="India election results announced",
        link="https://a.example.com",
        published_at=now,
        source="A",
        summary="",
        score=0.9,
    )
    item_b = NewsItem(
        title="Election results announced in India",
        link="https://b.example.com",
        published_at=now,
        source="B",
        summary="",
        score=0.8,
    )
    deduped = dedupe_items([item_b, item_a])
    assert len(deduped) == 1
    assert deduped[0].link == "https://a.example.com"


def test_dedupe_preserves_distinct_items() -> None:
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    item_a = NewsItem(
        title="Global markets rally on tech earnings",
        link="https://a.example.com",
        published_at=now,
        source="A",
        summary="",
        score=0.7,
    )
    item_b = NewsItem(
        title="Monsoon forecast updated by weather office",
        link="https://b.example.com",
        published_at=now,
        source="B",
        summary="",
        score=0.6,
    )
    deduped = dedupe_items([item_a, item_b])
    assert len(deduped) == 2
