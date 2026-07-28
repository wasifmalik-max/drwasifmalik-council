#!/usr/bin/env python3
"""
Daily Neurosciences News — lightweight Grok-powered posts.
SEPARATE from Monday Neuro Council Weekly Pipeline.
Dr. Wasif Rizwan Malik | drwasifmalik.com
"""

import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
from requests.auth import HTTPBasicAuth

GROK_KEY = os.environ.get("GROK_API_KEY", "")
WP_URL = os.environ.get("WP_URL", "https://drwasifmalik.com").rstrip("/")
WP_USER = os.environ.get("WP_USERNAME", "")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")
GROK_MODEL = os.environ.get("GROK_CONTENT_MODEL", "grok-4.5")
PUBLISH_MODE = os.environ.get("PUBLISH_MODE", "publish").lower()  # live by default; set draft to stage
DRY_RUN = "--dry-run" in sys.argv or os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")
CATEGORY_SLUG = os.environ.get("DAILY_NEWS_CATEGORY", "neurosciences-advances")

AUTHOR = (
    "Dr. Wasif Rizwan Malik | MBBS, FCPS (Neurosurgery) | PMDC 47983-P | "
    "Consultant Neurosurgeon, Faraz Hospital, Bahawalpur"
)
CTA = "Book consultation: https://rx.drwasifmalik.com | WhatsApp +923458254232"


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


def pick_topic():
    """Ask Grok for one hot/trendy brain/spine/nerve/mind topic for today."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prompt = f"""Today is {today} UTC.
Propose ONE hot, trendy, clinically relevant neurosciences topic for a short daily news brief
covering brain, spine, nerves, or mind/neuropsychiatry advances.
Return ONLY this format (no markdown fences):
TOPIC: <concise title under 70 chars>
ANGLE: <one sentence hook for patients/clinicians in Pakistan context>
KEYWORDS: <3 comma-separated SEO keywords>
Avoid sensationalism and fake breakthroughs. Prefer real guideline/device/trial themes."""
    text = grok_chat([{"role": "user", "content": prompt}], max_tokens=250, temperature=0.5)
    topic = re.search(r"TOPIC:\s*(.+)", text)
    angle = re.search(r"ANGLE:\s*(.+)", text)
    keys = re.search(r"KEYWORDS:\s*(.+)", text)
    return {
        "topic": (topic.group(1).strip() if topic else text.splitlines()[0][:70]),
        "angle": (angle.group(1).strip() if angle else ""),
        "keywords": (keys.group(1).strip() if keys else "neurosurgery, brain, spine"),
        "raw": text,
    }


def write_brief(meta):
    prompt = f"""Write a SHORT daily neurosciences advances post (350–500 words) as {AUTHOR}.

Title: {meta['topic']}
Angle: {meta['angle']}
Keywords: {meta['keywords']}

Rules:
- Educational only; no diagnosis of individuals; no fabricated PMIDs or trial IDs.
- Structure: H1 title, 1-paragraph hook, What changed / Why it matters, Patient takeaway, Disclaimer, CTA.
- CTA must include: {CTA}
- Clear, professional English; optional one Urdu sentence for accessibility.
- Do NOT claim unpublished personal surgical outcomes.
Return full HTML-ready Markdown starting with # title."""
    return grok_chat(
        [
            {"role": "system", "content": "You write concise, accurate neurosciences news for a consultant neurosurgeon website."},
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


def publish(title: str, html: str, cat_id):
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
    os.makedirs("council_output", exist_ok=True)

    meta = pick_topic()
    print("TOPIC:", meta["topic"])
    print("ANGLE:", meta["angle"])

    md = write_brief(meta)
    title = extract_title(md, meta["topic"])
    html = md_to_html(md)
    html += (
        "\n<p><em>Educational only — not a substitute for clinical consultation. "
        f'This daily brief is separate from the weekly Neuro Council deep-dive.</em></p>\n'
        f'<p><a href="https://rx.drwasifmalik.com">Book a consultation</a></p>'
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = f"council_output/daily_news_{stamp}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print("Wrote", out_path, f"({len(md.split())}w)")

    cat_id = None if DRY_RUN else ensure_category()
    result = publish(title, html, cat_id)
    print("DONE", result.get("status"), result.get("link"))


if __name__ == "__main__":
    main()
