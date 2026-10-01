#!/usr/bin/env python3
"""
Topic-of-the-day loader for the neurosurgery 365 calendar.

Rule: exactly ONE topic per calendar day → exactly ONE daily upload.

Dating: Day 1 = 2026-10-02 (civil date Asia/Karachi / PKT).
  day_index = (today - 2026-10-02).days + 1
  If outside 1..365, wraps with modulo across the 365-topic cycle
  (so the calendar remains usable after year 1).

Usage:
  from topic_of_the_day import get_topic_for_date, get_today_topic
  t = get_today_topic()
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
DEFAULT_CALENDAR = ROOT / "council_output" / "neurosurgery_365_calendar.json"
FALLBACK_SEED = ROOT / "council_output" / "neurosurgery_365_calendar.seed.json"
ANCHOR = date(2026, 10, 2)
PKT = ZoneInfo("Asia/Karachi")


def _calendar_path() -> Path:
    override = os.environ.get("NEURO_365_CALENDAR", "").strip()
    if override:
        return Path(override)
    if DEFAULT_CALENDAR.exists():
        return DEFAULT_CALENDAR
    return FALLBACK_SEED


@lru_cache(maxsize=2)
def load_calendar(path_str: str = "") -> dict[str, Any]:
    path = Path(path_str) if path_str else _calendar_path()
    if not path.exists():
        raise FileNotFoundError(f"Calendar not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("topics") or len(data["topics"]) != 365:
        raise ValueError(f"Calendar must contain exactly 365 topics: {path}")
    return data


def clear_calendar_cache() -> None:
    load_calendar.cache_clear()


def pkt_today(now: Optional[datetime] = None) -> date:
    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(PKT).date()


def day_index_for_date(d: date, wrap: bool = True) -> int:
    """1-based day index. If wrap=True, cycles every 365 days after the first year."""
    delta = (d - ANCHOR).days
    if delta < 0:
        if not wrap:
            raise ValueError(f"Date {d} is before calendar anchor {ANCHOR}")
        # wrap backward
        return (delta % 365) + 1
    idx = delta + 1
    if idx <= 365:
        return idx
    if not wrap:
        raise ValueError(f"Date {d} is past day 365")
    return ((idx - 1) % 365) + 1


def get_topic_for_date(d: date, wrap: bool = True, calendar_path: str = "") -> dict[str, Any]:
    data = load_calendar(calendar_path)
    idx = day_index_for_date(d, wrap=wrap)
    topic = dict(data["topics"][idx - 1])
    topic["day"] = idx
    topic["date"] = d.isoformat()
    topic["calendar_date_mapped"] = (ANCHOR + timedelta(days=idx - 1)).isoformat()
    topic["uploads_per_day"] = 1
    topic["selection_rule"] = "exactly_one_topic_one_upload_per_day"
    return topic


def get_today_topic(now: Optional[datetime] = None, wrap: bool = True) -> dict[str, Any]:
    return get_topic_for_date(pkt_today(now), wrap=wrap)


def format_topic_brief(topic: dict[str, Any]) -> str:
    return (
        f"Day {topic['day']} ({topic.get('date', '')}) | {topic['domain']}\n"
        f"TOPIC: {topic['topic']}\n"
        f"ANGLE: {topic['news_angle']}\n"
        f"KEYWORDS: {topic['search_keywords']}\n"
        f"WHY: {topic['practice_relevance']}\n"
        f"UPLOADS_TODAY: 1 (hard limit)"
    )


if __name__ == "__main__":
    t = get_today_topic()
    print(format_topic_brief(t))
