from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Iterable

from zoneinfo import ZoneInfo

from daily_digest_bot.feeds import NewsItem


def _format_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def _truncate(text: str, limit: int = 360) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _render_section(title: str, items: Iterable[NewsItem]) -> str:
    rows = []
    for item in items:
        summary = _truncate(item.summary) if item.summary else ""
        summary_html = (
            f"<div class=\"summary\">{escape(summary)}</div>" if summary else ""
        )
        if item.link:
            title_html = f"<a class=\"title\" href=\"{escape(item.link)}\">{escape(item.title)}</a>"
        else:
            title_html = f"<span class=\"title\">{escape(item.title)}</span>"
        rows.append(
            "\n".join(
                [
                    "<div class=\"item\">",
                    f"  {title_html}",
                    f"  <div class=\"meta\">{escape(item.source)} · {_format_time(item.published_at)}</div>",
                    f"  {summary_html}",
                    "</div>",
                ]
            )
        )
    if not rows:
        rows.append("<div class=\"empty\">No stories found.</div>")
    return "\n".join(
        [
            f"<h2>{escape(title)}</h2>",
            "<div class=\"section\">",
            *rows,
            "</div>",
        ]
    )


def render_email(
    world_items: Iterable[NewsItem],
    india_items: Iterable[NewsItem],
    generated_at: datetime,
) -> str:
    local_date = generated_at.astimezone(ZoneInfo("Asia/Kolkata")).strftime(
        "%Y-%m-%d"
    )
    world_section = _render_section("World Top Stories", world_items)
    india_section = _render_section("India Top Stories", india_items)

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Daily Digest {local_date}</title>
    <style>
      :root {{
        color-scheme: light;
      }}
      body {{
        margin: 0;
        background: #f4f4f0;
        color: #1f2933;
        font-family: "Georgia", "Times New Roman", serif;
      }}
      .container {{
        max-width: 760px;
        margin: 0 auto;
        padding: 28px 22px 40px;
      }}
      .header {{
        background: linear-gradient(120deg, #1f2933, #3e4c59);
        color: #f5f7fa;
        padding: 20px 24px;
        border-radius: 14px;
      }}
      .header h1 {{
        margin: 0 0 8px;
        font-size: 26px;
        letter-spacing: 0.4px;
      }}
      .header .meta {{
        font-size: 13px;
        opacity: 0.85;
      }}
      h2 {{
        margin: 28px 0 12px;
        font-size: 20px;
        color: #1f2933;
      }}
      .section {{
        display: block;
        background: #ffffff;
        border-radius: 12px;
        padding: 8px 18px;
        box-shadow: 0 8px 20px rgba(20, 20, 20, 0.08);
      }}
      .item {{
        display: block;
        padding: 14px 0;
        border-bottom: 1px solid #e4e7eb;
      }}
      .item:last-child {{
        border-bottom: none;
      }}
      .title {{
        font-size: 16px;
        color: #102a43;
        text-decoration: none;
        font-weight: 600;
      }}
      .meta {{
        margin-top: 6px;
        font-size: 12px;
        color: #52606d;
      }}
      .summary {{
        margin-top: 8px;
        font-size: 14px;
        color: #334e68;
      }}
      .empty {{
        font-size: 14px;
        color: #52606d;
        padding: 10px 0;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>Daily Digest</h1>
        <div class="meta">Local date: {local_date} · Generated at {_format_time(generated_at)}</div>
      </div>
      {world_section}
      {india_section}
    </div>
  </body>
</html>
"""
