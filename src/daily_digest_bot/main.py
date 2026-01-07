from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from zoneinfo import ZoneInfo

from daily_digest_bot.config import AppConfig, load_config
from daily_digest_bot.dedupe import dedupe_items
from daily_digest_bot.emailer import send_email
from daily_digest_bot.feeds import fetch_feeds
from daily_digest_bot.ranker import rank_items
from daily_digest_bot.render import render_email


def _resolve_output_dir(config: AppConfig, root: Path) -> Path:
    output_dir = Path(config.output_dir)
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _apply_email_overrides(config: AppConfig) -> tuple[str, str]:
    from_email = os.getenv("DIGEST_FROM_EMAIL", "").strip() or config.email.from_email
    to_email = os.getenv("DIGEST_TO_EMAIL", "").strip() or config.email.to_email
    return from_email, to_email


def _print_summary(label: str, items) -> None:
    print(f"[info] {label}: {len(items)} stories")
    for item in items:
        print(f"  - {item.title} ({item.source})")


def run(
    config_path: str,
    dry_run: bool,
    limit_world: int,
    limit_india: int,
) -> int:
    config = load_config(config_path)
    root = Path(__file__).resolve().parents[2]
    now_utc = datetime.now(timezone.utc)
    output_dir = _resolve_output_dir(config, root)

    world_items = fetch_feeds(config.world_feeds)
    india_items = fetch_feeds(config.india_feeds)

    world_ranked = rank_items(
        world_items, config.source_weights, config.keywords, now=now_utc
    )
    india_ranked = rank_items(
        india_items, config.source_weights, config.keywords, now=now_utc
    )

    world_deduped = dedupe_items(world_ranked)[:limit_world]
    india_deduped = dedupe_items(india_ranked)[:limit_india]

    html = render_email(world_deduped, india_deduped, now_utc)

    local_date = now_utc.astimezone(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
    output_path = output_dir / f"{local_date}.html"
    output_path.write_text(html, encoding="utf-8")

    _print_summary("World", world_deduped)
    _print_summary("India", india_deduped)
    print(f"[info] HTML written to {output_path}")

    if dry_run:
        print("[info] Dry run enabled; skipping email send.")
        return 0

    from_email, to_email = _apply_email_overrides(config)
    subject = f"{config.email.subject_prefix} {local_date}"
    send_email(
        html=html,
        subject=subject,
        from_email=from_email,
        to_email=to_email,
        smtp_host=config.email.smtp_host,
        smtp_port=config.email.smtp_port,
    )
    print("[info] Email sent.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Daily news digest bot")
    parser.add_argument(
        "--config", default="config.yaml", help="Path to config YAML"
    )
    parser.add_argument("--dry-run", action="store_true", help="Skip sending email")
    parser.add_argument(
        "--limit-world", type=int, default=5, help="Number of world stories"
    )
    parser.add_argument(
        "--limit-india", type=int, default=5, help="Number of India stories"
    )
    args = parser.parse_args()

    try:
        return run(
            config_path=args.config,
            dry_run=args.dry_run,
            limit_world=args.limit_world,
            limit_india=args.limit_india,
        )
    except Exception as exc:
        print(f"[error] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
