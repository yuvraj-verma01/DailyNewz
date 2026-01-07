from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass(frozen=True)
class FeedConfig:
    name: str
    url: str


@dataclass(frozen=True)
class EmailConfig:
    from_email: str
    to_email: str
    subject_prefix: str
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465


@dataclass(frozen=True)
class AppConfig:
    world_feeds: List[FeedConfig]
    india_feeds: List[FeedConfig]
    source_weights: Dict[str, float]
    keywords: List[str]
    email: EmailConfig
    output_dir: str = "out"


def _parse_feeds(raw: Any, label: str) -> List[FeedConfig]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError(f"{label} must be a list of feeds")
    feeds: List[FeedConfig] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"{label}[{idx}] must be a mapping")
        name = str(item.get("name", "")).strip()
        url = str(item.get("url", "")).strip()
        if not name or not url:
            raise ValueError(f"{label}[{idx}] requires name and url")
        feeds.append(FeedConfig(name=name, url=url))
    return feeds


def _parse_email(raw: Any) -> EmailConfig:
    if not isinstance(raw, dict):
        raise ValueError("email must be a mapping")
    from_email = str(raw.get("from_email", "")).strip()
    to_email = str(raw.get("to_email", "")).strip()
    subject_prefix = str(raw.get("subject_prefix", "Daily Digest")).strip()
    smtp_host = str(raw.get("smtp_host", "smtp.gmail.com")).strip()
    smtp_port = int(raw.get("smtp_port", 465))
    if not from_email or not to_email:
        raise ValueError("email.from_email and email.to_email are required")
    return EmailConfig(
        from_email=from_email,
        to_email=to_email,
        subject_prefix=subject_prefix,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
    )


def load_config(path: str) -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    world_feeds = _parse_feeds(data.get("world_feeds"), "world_feeds")
    india_feeds = _parse_feeds(data.get("india_feeds"), "india_feeds")
    source_weights = {
        str(k): float(v) for k, v in (data.get("source_weights") or {}).items()
    }
    keywords = [str(k).strip() for k in (data.get("keywords") or []) if str(k).strip()]
    email = _parse_email(data.get("email") or {})
    output_dir = str(data.get("output_dir", "out")).strip() or "out"
    return AppConfig(
        world_feeds=world_feeds,
        india_feeds=india_feeds,
        source_weights=source_weights,
        keywords=keywords,
        email=email,
        output_dir=output_dir,
    )
