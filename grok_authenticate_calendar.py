#!/usr/bin/env python3
"""
Grok-authenticate the 365 neurosurgery calendar in resumable batches.

- Reads council_output/neurosurgery_365_calendar.seed.json (or checkpoint)
- Polishes topic wording / news_angle / keywords / practice_relevance for clinical authenticity
- Does NOT invent fake DOIs/PMIDs
- Writes checkpoint after each batch and final JSON when complete

Usage:
  set GROK_API_KEY=...   (or place key in .grok_key_tmp)
  python grok_authenticate_calendar.py
  python grok_authenticate_calendar.py --batch-size 40 --resume
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
SEED = ROOT / "council_output" / "neurosurgery_365_calendar.seed.json"
CHECKPOINT = ROOT / "council_output" / "neurosurgery_365_calendar.checkpoint.json"
FINAL = ROOT / "council_output" / "neurosurgery_365_calendar.json"
KEY_FILE = ROOT / ".grok_key_tmp"

MODEL = os.environ.get("GROK_CONTENT_MODEL", "grok-4.5")
API = "https://api.x.ai/v1/chat/completions"


def load_key() -> str:
    key = os.environ.get("GROK_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if len(key) < 8:
        raise SystemExit("GROK_API_KEY missing (env or .grok_key_tmp)")
    return key


def grok_chat(key: str, messages: list[dict], max_tokens: int = 6000) -> str:
    r = requests.post(
        API,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "temperature": 0.25,
            "max_tokens": max_tokens,
            "messages": messages,
        },
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Grok HTTP {r.status_code}: {r.text[:400]}")
    return r.json()["choices"][0]["message"]["content"].strip()


def extract_json_array(text: str) -> list:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    # Find outermost array
    start = text.find("[")
    end = text.rfind("]")
    if start < 0 or end < 0:
        raise ValueError("No JSON array in Grok response")
    return json.loads(text[start : end + 1])


SYSTEM = """You are a board-certified neurosurgeon-editor authenticating a daily practice-topic calendar.
Return ONLY a JSON array (no markdown). For each input item, return an object with the SAME day number and these fields:
day (int), topic (string), domain (string — keep unless clearly wrong), news_angle (1-2 sentences),
search_keywords (string), practice_relevance (1 sentence).

Rules:
- Keep clinically accurate neurosurgical/neurological practice language.
- Prefer real curriculum + research-frontier themes; no AI fluff, no sensational breakthroughs.
- news_angle must describe WHAT TO LOOK FOR / WRITE that day (research digest brief), NOT invent papers/DOIs/PMIDs/trial IDs.
- Keep uploads framing: exactly one daily topic.
- Tighten weak wording; fix any clinically dubious claims.
- Do not drop or renumber days. Return one object per input item, same order.
"""


def polish_batch(key: str, batch: list[dict]) -> list[dict]:
    slim = [
        {
            "day": e["day"],
            "topic": e["topic"],
            "domain": e["domain"],
            "news_angle": e["news_angle"],
            "search_keywords": e["search_keywords"],
            "practice_relevance": e["practice_relevance"],
        }
        for e in batch
    ]
    user = (
        "Authenticate and lightly polish these calendar entries for clinical authenticity.\n"
        + json.dumps(slim, ensure_ascii=False)
    )
    raw = grok_chat(
        key,
        [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
    )
    polished = extract_json_array(raw)
    by_day = {int(p["day"]): p for p in polished}
    out = []
    for e in batch:
        p = by_day.get(int(e["day"]))
        if not p:
            # keep original if missing
            e2 = dict(e)
            e2["grok_authenticated"] = False
            e2["grok_note"] = "missing_in_batch_response"
            out.append(e2)
            continue
        merged = dict(e)
        for field in ("topic", "domain", "news_angle", "search_keywords", "practice_relevance"):
            if p.get(field):
                merged[field] = str(p[field]).strip()
        merged["grok_authenticated"] = True
        merged["uploads_per_day"] = 1
        out.append(merged)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=40)
    ap.add_argument("--resume", action="store_true", default=True)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--max-batches", type=int, default=0, help="0 = all")
    args = ap.parse_args()
    resume = args.resume and not args.no_resume

    key = load_key()

    if resume and CHECKPOINT.exists():
        payload = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        print(f"Resuming from checkpoint ({CHECKPOINT})")
    else:
        if not SEED.exists():
            raise SystemExit(f"Missing seed: {SEED}")
        payload = json.loads(SEED.read_text(encoding="utf-8"))
        print(f"Loaded seed ({SEED})")

    topics = payload["topics"]
    assert len(topics) == 365, len(topics)

    # Find first unauthenticated index
    start = 0
    for i, t in enumerate(topics):
        if not t.get("grok_authenticated"):
            start = i
            break
    else:
        start = 365

    print(f"Authenticated so far: {start}/365 | model={MODEL}")
    if start >= 365:
        FINAL.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Already complete → {FINAL}")
        return

    batches_done = 0
    i = start
    while i < 365:
        batch = topics[i : i + args.batch_size]
        print(f"Polishing days {batch[0]['day']}-{batch[-1]['day']} ({len(batch)} items)...")
        try:
            polished = polish_batch(key, batch)
        except Exception as exc:
            print(f"Batch failed: {exc}")
            # save checkpoint and exit for resume
            CHECKPOINT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            raise SystemExit(f"Stopped at day {batch[0]['day']}; checkpoint saved. Re-run to resume.")

        topics[i : i + len(polished)] = polished
        payload["topics"] = topics
        payload["grok_auth"] = {
            "model": MODEL,
            "authenticated_count": sum(1 for t in topics if t.get("grok_authenticated")),
            "last_day_polished": polished[-1]["day"],
        }
        CHECKPOINT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  checkpoint OK ({payload['grok_auth']['authenticated_count']}/365)")
        i += len(polished)
        batches_done += 1
        if args.max_batches and batches_done >= args.max_batches:
            print("max-batches reached; exit for resume")
            return
        time.sleep(1.2)

    # Refresh domain counts after polish (domains may be lightly edited)
    counts: dict[str, int] = {}
    for t in topics:
        counts[t["domain"]] = counts.get(t["domain"], 0) + 1
    payload["counts_by_domain"] = dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
    payload["total_topics"] = 365
    payload["dating"]["uploads_per_day"] = 1
    FINAL.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"COMPLETE -> {FINAL}")
    print("Domain counts:", payload["counts_by_domain"])


if __name__ == "__main__":
    main()
