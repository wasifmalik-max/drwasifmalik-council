#!/usr/bin/env python3
"""Compile neurosurgery_365_topics.md from the authenticated (or seed) calendar JSON."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "council_output" / "neurosurgery_365_calendar.json"
SEED = ROOT / "council_output" / "neurosurgery_365_calendar.seed.json"
CHECKPOINT = ROOT / "council_output" / "neurosurgery_365_calendar.checkpoint.json"
MD_OUT = ROOT / "neurosurgery_365_topics.md"


def load() -> dict:
    for p in (FINAL, CHECKPOINT, SEED):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8")), p
    raise SystemExit("No calendar JSON found")


def main():
    data, src = load()
    topics = data["topics"]
    dating = data.get("dating", {})
    counts = data.get("counts_by_domain", {})
    auth_n = sum(1 for t in topics if t.get("grok_authenticated"))

    by_domain = defaultdict(list)
    for t in topics:
        by_domain[t["domain"]].append(t)

    lines = []
    lines.append("# Neurosurgery / Neurology Practice Topic Calendar (365)")
    lines.append("")
    lines.append("**One topic per day → one research digest upload. Never batch-upload multiple calendar topics on the same day.**")
    lines.append("")
    lines.append(f"- **Source of truth:** `council_output/neurosurgery_365_calendar.json`")
    lines.append(f"- **Compiled from:** `{src.name}`")
    lines.append(f"- **Day 1:** `{dating.get('day_1', '2026-10-02')}` (Asia/Karachi civil date)")
    lines.append(f"- **Day 365:** `{dating.get('day_365', '2027-10-01')}`")
    lines.append(f"- **Grok-authenticated entries:** {auth_n}/365")
    lines.append(f"- **Uploads per day:** `{dating.get('uploads_per_day', 1)}`")
    lines.append("")
    lines.append("## Dating rule")
    lines.append("")
    lines.append(dating.get("rule", ""))
    lines.append("")
    lines.append(dating.get("selection_rule", ""))
    lines.append("")
    lines.append("```text")
    lines.append("day_index = (PKT_today - 2026-10-02).days + 1")
    lines.append("topic     = calendar.topics[day_index - 1]   # exactly one")
    lines.append("publish   = ONE WordPress post / ONE council_output/daily_news_YYYYMMDD.md")
    lines.append("```")
    lines.append("")
    lines.append("## Domain counts")
    lines.append("")
    lines.append("| Domain | Topics |")
    lines.append("|---|---:|")
    for k, v in counts.items():
        lines.append(f"| {k} | {v} |")
    lines.append(f"| **Total** | **{len(topics)}** |")
    lines.append("")
    lines.append("## How the daily job uses this")
    lines.append("")
    lines.append("1. GitHub Action `neuro-daily-news.yml` runs `daily_neuro_news.py` once per day.")
    lines.append("2. `topic_of_the_day.get_today_topic()` resolves **exactly one** calendar entry for today's PKT date.")
    lines.append("3. Optional RSS feeds may supply a **single** best-match hint; if weak, Grok writes a research brief on the calendar topic alone.")
    lines.append("4. Pipeline publishes **one** post only (`MAX_UPLOADS_PER_DAY = 1`).")
    lines.append("")
    lines.append("Regenerate / re-authenticate:")
    lines.append("")
    lines.append("```bash")
    lines.append("python build_365_seed_calendar.py")
    lines.append("python grok_authenticate_calendar.py --batch-size 35   # resumable")
    lines.append("python compile_365_markdown.py")
    lines.append("python topic_of_the_day.py   # prints today's single topic")
    lines.append("```")
    lines.append("")
    lines.append("## Sample week 1 (days 1–7)")
    lines.append("")
    lines.append("| Day | Date | Domain | Topic |")
    lines.append("|---:|---|---|---|")
    for t in topics[:7]:
        lines.append(f"| {t['day']} | {t['date']} | {t['domain']} | {t['topic']} |")
    lines.append("")
    lines.append("### Day 1 detail")
    lines.append("")
    t0 = topics[0]
    lines.append(f"- **News angle:** {t0['news_angle']}")
    lines.append(f"- **Keywords:** `{t0['search_keywords']}`")
    lines.append(f"- **Practice relevance:** {t0['practice_relevance']}")
    lines.append("")
    lines.append("## Sample mid-year (days 180–186)")
    lines.append("")
    lines.append("| Day | Date | Domain | Topic |")
    lines.append("|---:|---|---|---|")
    for t in topics[179:186]:
        lines.append(f"| {t['day']} | {t['date']} | {t['domain']} | {t['topic']} |")
    lines.append("")
    lines.append("## Final week (days 359–365)")
    lines.append("")
    lines.append("| Day | Date | Domain | Topic |")
    lines.append("|---:|---|---|---|")
    for t in topics[358:]:
        lines.append(f"| {t['day']} | {t['date']} | {t['domain']} | {t['topic']} |")
    lines.append("")
    lines.append("## Domain overview (titles only)")
    lines.append("")
    for domain, items in sorted(by_domain.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        lines.append(f"### {domain} ({len(items)})")
        lines.append("")
        for t in items:
            lines.append(f"- D{t['day']:03d} ({t['date']}): {t['topic']}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Dr. Wasif Rizwan Malik | The Neuro Council | drwasifmalik.com*")
    lines.append("")

    MD_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {MD_OUT} from {src} (auth {auth_n}/365)")


if __name__ == "__main__":
    main()
