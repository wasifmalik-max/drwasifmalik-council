#!/usr/bin/env python3
"""
Daily Neurosciences News — lightweight Grok-powered posts.
SEPARATE from Monday Neuro Council Weekly Pipeline.
Dr. Wasif Rizwan Malik | drwasifmalik.com

HARD RULE: exactly ONE calendar topic → ONE research digest upload per day.
Topic source: neurosurgery_365_calendar.json via topic_of_the_day.py
(Day 1 = 2026-10-02 PKT). Optional RSS hinting may enrich the brief, but
never publishes a second post or a different calendar day.
"""

import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth

from image_policy import (
    append_byline,
    append_contact_footer,
    create_ai_featured_media,
    resolve_author_photo_url,
    author_byline_html,
    scrub_forbidden_featured,
)
from topic_of_the_day import format_topic_brief, get_today_topic

GROK_KEY = os.environ.get("GROK_API_KEY", "")
WP_URL = os.environ.get("WP_URL", "https://drwasifmalik.com").rstrip("/")
WP_USER = os.environ.get("WP_USERNAME", "")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")
GROK_MODEL = os.environ.get("GROK_CONTENT_MODEL", "grok-4.5")
PUBLISH_MODE = os.environ.get("PUBLISH_MODE", "publish").lower()  # live by default; set draft to stage
DRY_RUN = "--dry-run" in sys.argv or os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")
CATEGORY_SLUG = os.environ.get("DAILY_NEWS_CATEGORY", "neurosciences-advances")
# Soft RSS enrichment around today's single calendar topic (never multi-post)
USE_FEED_HINT = os.environ.get("DAILY_FEED_HINT", "1").lower() in ("1", "true", "yes")
MAX_UPLOADS_PER_DAY = 1

AUTHOR = (
    "Dr. Wasif Rizwan Malik | MBBS, FCPS (Neurosurgery) | PMDC 47983-P | "
    "Consultant Neurosurgeon, Faraz Hospital, Bahawalpur"
)
# Authoritative contact roles (do not collapse into one WhatsApp number):
# 0300 087 4232 = AI WhatsApp (booking & PA). 0345 825 4232 = emergency direct only.
CTA = (
    "Book online: https://rx.drwasifmalik.com | "
    "AI WhatsApp (booking & PA, no diagnosis, no imaging brief): "
    "https://wa.me/923000874232 (0300 087 4232) | "
    "Emergency direct Dr Wasif (not routine booking): tel:+923458254232 (0345 825 4232)"
)


FEED_URLS = [
    "https://www.sciencedaily.com/rss/mind_brain/neuroscience.xml",
    "https://www.sciencedaily.com/rss/health_medicine/stroke.xml",
    "https://www.sciencedaily.com/rss/health_medicine/nervous_system.xml",
    "https://www.sciencedaily.com/rss/mind_brain/brain_injury.xml",
]


def die(msg, code=1):
    print(f"ERROR: {msg}")
    sys.exit(code)


def grok_chat(messages, max_tokens=1200, temperature=0.4):
    if not GROK_KEY:
        die("GROK_API_KEY required")
    r = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROK_KEY}", "Content-Type": "application/json"},
        json={
            "model": GROK_MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        },
        timeout=120,
    )
    if r.status_code != 200:
        die(f"Grok HTTP {r.status_code}: {r.text[:300]}")
    return r.json()["choices"][0]["message"]["content"].strip()


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(t) > 3}


def fetch_feed_items(limit_per_feed: int = 12) -> list[dict]:
    items = []
    for url in FEED_URLS:
        try:
            r = requests.get(url, timeout=25, headers={"User-Agent": "NeuroCouncilDaily/1.0"})
            if r.status_code != 200:
                continue
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:limit_per_feed]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                desc = (item.findtext("description") or "").strip()
                desc = re.sub(r"<[^>]+>", " ", desc)
                desc = re.sub(r"\s+", " ", desc).strip()[:400]
                if title:
                    items.append({"title": title, "link": link, "summary": desc, "source": url})
        except Exception as exc:
            print(f"Feed warn {urlparse(url).netloc}: {exc}")
    return items


def best_feed_match(calendar_topic: dict, items: list[dict]) -> dict | None:
    """Pick at most ONE best RSS item matching today's calendar topic; else None."""
    if not items:
        return None
    keys = _tokenize(calendar_topic.get("search_keywords", "")) | _tokenize(
        calendar_topic.get("topic", "")
    )
    scored = []
    for it in items:
        blob = _tokenize(it["title"]) | _tokenize(it.get("summary", ""))
        score = len(keys & blob)
        if score:
            scored.append((score, it))
    if not scored:
        return None
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best = scored[0]
    if best_score < 2:
        return None
    best = dict(best)
    best["match_score"] = best_score
    return best


def pick_topic():
    """
    Exactly ONE topic for today from the 365 calendar (PKT date).
    Soft-optional: attach a single best RSS hint if feeds align; otherwise
    Grok writes a research-oriented brief on the calendar topic alone.
    """
    cal = get_today_topic()
    print(format_topic_brief(cal))
    feed_hint = None
    if USE_FEED_HINT:
        try:
            feed_hint = best_feed_match(cal, fetch_feed_items())
            if feed_hint:
                print(
                    f"FEED_HINT (single): score={feed_hint['match_score']} | {feed_hint['title'][:80]}"
                )
            else:
                print("FEED_HINT: none strong enough — Grok research brief on calendar topic")
        except Exception as exc:
            print(f"FEED_HINT skipped: {exc}")

    return {
        "topic": cal["topic"],
        "angle": cal["news_angle"],
        "keywords": cal["search_keywords"],
        "domain": cal["domain"],
        "day": cal["day"],
        "date": cal["date"],
        "practice_relevance": cal["practice_relevance"],
        "feed_hint": feed_hint,
        "uploads_per_day": MAX_UPLOADS_PER_DAY,
        "raw": format_topic_brief(cal),
    }


def write_brief(meta):
    feed_block = ""
    if meta.get("feed_hint"):
        fh = meta["feed_hint"]
        feed_block = (
            f"\nOptional real-world news hint (use only if clinically coherent with the topic; "
            f"do not invent citations beyond this headline):\n"
            f"- Headline: {fh['title']}\n"
            f"- Link: {fh.get('link', '')}\n"
            f"- Summary: {fh.get('summary', '')}\n"
            f"If the hint is weak or off-topic, ignore it and write a research-oriented practice brief.\n"
        )
    prompt = f"""Write a SHORT daily neurosciences advances post (350–500 words) as {AUTHOR}.

HARD CONSTRAINTS:
- This is the SINGLE daily upload for calendar day {meta.get('day')} ({meta.get('date')}).
- Domain: {meta.get('domain')}
- Stay tightly on this ONE topic (do not cover multiple unrelated stories).
- Educational research-digest style; no clickbait; no fabricated PMIDs/DOIs/trial IDs.
- Practice relevance: {meta.get('practice_relevance', '')}

Title: {meta['topic']}
Angle: {meta['angle']}
Keywords: {meta['keywords']}
{feed_block}
Rules:
- Structure: H1 title, 1-paragraph hook, What changed / Why it matters, Patient takeaway, Disclaimer, CTA.
- CTA must include: {CTA}
- Clear, professional English; optional one Urdu sentence for accessibility.
- Do NOT claim unpublished personal surgical outcomes.
Return full HTML-ready Markdown starting with # title."""
    return grok_chat(
        [
            {
                "role": "system",
                "content": (
                    "You write concise, accurate neurosciences news for a consultant neurosurgeon website. "
                    "One topic only. Prefer guideline/trial/device themes that are real; never invent citations."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=1400,
        temperature=0.35,
    )


def md_to_html(md: str) -> str:
    # Minimal conversion for WP content
    lines = md.splitlines()
    html = []
    para = []

    def flush():
        nonlocal para
        if para:
            html.append("<p>" + " ".join(para) + "</p>")
            para = []

    for line in lines:
        s = line.strip()
        if not s:
            flush()
            continue
        if s.startswith("# "):
            flush()
            html.append(f"<h1>{s[2:].strip()}</h1>")
        elif s.startswith("## "):
            flush()
            html.append(f"<h2>{s[3:].strip()}</h2>")
        elif s.startswith("### "):
            flush()
            html.append(f"<h3>{s[4:].strip()}</h3>")
        elif s.startswith("- "):
            flush()
            html.append(f"<ul><li>{s[2:].strip()}</li></ul>")
        else:
            # bold
            s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
            para.append(s)
    flush()
    return "\n".join(html)


def ensure_category():
    if not all([WP_URL, WP_USER, WP_PASS]):
        return None
    auth = HTTPBasicAuth(WP_USER, WP_PASS)
    for attempt in range(1, 5):
        try:
            r = requests.get(
                f"{WP_URL}/wp-json/wp/v2/categories",
                params={"slug": CATEGORY_SLUG},
                auth=auth,
                timeout=45,
            )
            if r.status_code == 200 and r.json():
                return r.json()[0]["id"]
            r = requests.post(
                f"{WP_URL}/wp-json/wp/v2/categories",
                auth=auth,
                json={
                    "name": "Neurosciences Advances",
                    "slug": CATEGORY_SLUG,
                    "description": "Daily short updates on brain, spine, nerve, and mind advances.",
                },
                timeout=45,
            )
            if r.status_code in (200, 201):
                return r.json()["id"]
            print(f"Category attempt {attempt} warn: {r.status_code} {r.text[:200]}")
        except Exception as exc:
            print(f"Category attempt {attempt} exception: {exc}")
        time.sleep(8 * attempt)
    print("Category ensure failed after retries — publishing without category")
    return None


def tag_frontline_meta(post_id: int) -> None:
    """Mark council daily posts so homepage Frontline Neuroscience can surface them."""
    if not post_id or DRY_RUN:
        return
    auth = HTTPBasicAuth(WP_USER, WP_PASS)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "meta": {
            "_dwf_nn_generated": stamp,
            "_dwf_nn_source": "neuro-council-daily-calendar",
            "_dwf_nn_model": GROK_MODEL,
            "_dwf_nn_image_model": os.environ.get("GROK_IMAGE_MODEL", "grok-imagine-image"),
        }
    }
    try:
        r = requests.post(
            f"{WP_URL}/wp-json/wp/v2/posts/{int(post_id)}",
            auth=auth,
            json=payload,
            timeout=45,
        )
        if r.status_code in (200, 201):
            print(f"frontline_meta: tagged post {post_id}")
        else:
            print(f"frontline_meta warn: HTTP {r.status_code} {r.text[:180]}")
    except Exception as exc:
        print(f"frontline_meta warn: {exc}")


def publish(title: str, html: str, cat_id, featured_media=None):
    if DRY_RUN:
        print("DRY_RUN — skip WP publish")
        return {"id": 0, "link": "(dry-run)", "status": "dry-run"}
    if not all([WP_URL, WP_USER, WP_PASS]):
        die("WP credentials required for publish")
    status = "publish" if PUBLISH_MODE == "publish" else "draft"
    payload = {
        "title": title,
        "content": html,
        "status": status,
        "excerpt": "Daily neurosciences advances brief from The Neuro Council desk.",
    }
    if cat_id:
        payload["categories"] = [cat_id]
    if featured_media:
        payload["featured_media"] = int(featured_media)
    for attempt in range(1, 4):
        try:
            r = requests.post(
                f"{WP_URL}/wp-json/wp/v2/posts",
                auth=HTTPBasicAuth(WP_USER, WP_PASS),
                json=payload,
                timeout=60,
            )
            if r.status_code in (200, 201):
                data = r.json()
                print(f"WP {status}: id={data.get('id')} link={data.get('link')}")
                if data.get("id"):
                    scrub_forbidden_featured(int(data["id"]))
                    # Homepage frontline queries meta_key=_dwf_nn_generated
                    tag_frontline_meta(int(data["id"]))
                return data
            print(f"WP attempt {attempt} failed: {r.status_code} {r.text[:250]}")
        except Exception as exc:
            print(f"WP attempt {attempt} exception: {exc}")
        time.sleep(6)
    die("WP publish failed")


def extract_title(md: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", md, re.M)
    return (m.group(1).strip() if m else fallback)[:120]


def main():
    print("=== Daily Neurosciences News ===")
    print(f"Dry run: {DRY_RUN} | Publish mode: {PUBLISH_MODE} | Model: {GROK_MODEL}")
    print(f"UPLOAD RULE: exactly {MAX_UPLOADS_PER_DAY} post/day from 365 calendar (PKT date)")
    os.makedirs("council_output", exist_ok=True)

    meta = pick_topic()
    assert meta.get("uploads_per_day", 1) == 1
    print("TOPIC:", meta["topic"])
    print("ANGLE:", meta["angle"])
    print(f"CALENDAR: day={meta.get('day')} date={meta.get('date')} domain={meta.get('domain')}")

    md = write_brief(meta)
    title = extract_title(md, meta["topic"])
    html = md_to_html(md)
    html += (
        "\n<p><em>Educational only — not a substitute for clinical consultation. "
        f'This daily brief is separate from the weekly Neuro Council deep-dive. '
        f"Calendar day {meta.get('day')} — one topic, one upload.</em></p>\n"
        f'<p><a href="https://rx.drwasifmalik.com">Book a consultation</a></p>\n'
    )
    # Mini author byline (small photo + credentials) — not used as featured image
    if DRY_RUN:
        html = append_byline(html)
    else:
        html = html.rstrip() + "\n" + author_byline_html(resolve_author_photo_url())
    html = append_contact_footer(html)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = f"council_output/daily_news_{stamp}.md"
    header = (
        f"<!-- calendar_day={meta.get('day')} date={meta.get('date')} "
        f"domain={meta.get('domain')} uploads=1 -->\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + md)
    print("Wrote", out_path, f"({len(md.split())}w) | single daily upload")

    # ONE WordPress post only — never batch-publish calendar topics
    featured_id = None
    if not DRY_RUN:
        featured_id = create_ai_featured_media(title, slug_hint=title)
        if not featured_id:
            print("WARN: AI featured image unavailable — publishing without doctor-face fallback")

    cat_id = None if DRY_RUN else ensure_category()
    result = publish(title, html, cat_id, featured_media=featured_id)
    print(
        "DONE",
        result.get("status"),
        result.get("link"),
        "featured=",
        featured_id,
        "| uploads_today=1",
    )


if __name__ == "__main__":
    main()
