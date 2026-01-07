from datetime import datetime, timedelta, timezone

from daily_digest_bot.feeds import NewsItem
from daily_digest_bot.ranker import rank_items


def _item(title: str, hours_ago: int) -> NewsItem:
    now = datetime(2024, 1, 2, tzinfo=timezone.utc)
    return NewsItem(
        title=title,
        link="https://example.com",
        published_at=now - timedelta(hours=hours_ago),
        source="Test",
        summary="",
        date_missing=False,
    )


def test_ranker_prefers_recent_items() -> None:
    now = datetime(2024, 1, 2, tzinfo=timezone.utc)
    items = [_item("Older story", 24), _item("Newer story", 2)]
    ranked = rank_items(items, {"Test": 1.0}, [], now=now)
    assert ranked[0].title == "Newer story"


def test_ranker_deterministic_ordering() -> None:
    now = datetime(2024, 1, 2, tzinfo=timezone.utc)
    item_a = _item("Alpha headline", 5)
    item_b = _item("Beta headline", 5)
    ranked = rank_items([item_b, item_a], {"Test": 1.0}, [], now=now)
    assert [item.title for item in ranked] == ["Alpha headline", "Beta headline"]
