#!/usr/bin/env python3
"""
Image + byline policy for Neuro Council / Daily Neurosciences News.

Promotional homepage portraits stay as real/occasion media (1606, 1637, 1638).
Article featured images must be AI medical/neuroscience visuals — never doctor
personal photos. Each post ends with a mini author byline + small portrait.
"""

from __future__ import annotations

import base64
import os
import re
import time
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth

GROK_KEY = os.environ.get("GROK_API_KEY", "")
WP_URL = os.environ.get("WP_URL", "https://drwasifmalik.com").rstrip("/")
WP_USER = os.environ.get("WP_USERNAME", "")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")
GROK_IMAGE_MODEL = os.environ.get("GROK_IMAGE_MODEL", "grok-imagine-image")

# Real white-coat portrait — byline thumbnail ONLY (never post featured/cover)
AUTHOR_PHOTO_ID = int(os.environ.get("AUTHOR_PHOTO_ID", "1606"))
AUTHOR_PHOTO_URL = os.environ.get(
    "AUTHOR_PHOTO_URL",
    "https://drwasifmalik.com/wp-content/uploads/2026/06/WhatsAppImage2026-04-14at6.59.45PM2.jpeg",
)

# Doctor / occasion portraits — forbidden as article featured images
FORBIDDEN_FEATURED_IDS = {
    1604,
    1605,
    1606,
    1607,
    1627,
    1628,
    1637,
    1638,
}

BYLINE_MARKER = "<!-- neuro-author-byline -->"

IMAGE_STYLE = (
    "Realistic clinical/neuroscience editorial cover, ice-blue frosted medical aesthetic, "
    "accurate-looking clinical illustration style, soft hospital ambient light, "
    "NO identifiable doctor face, NO patient face, NO children, NO paediatric faces, "
    "NO gore, NO readable logos or device brand names, NO text overlays, "
    "horizontal 16:9 composition suitable as a WordPress featured image."
)


def author_byline_html(photo_url: Optional[str] = None) -> str:
    """Compact end-of-post author byline with small portrait."""
    url = photo_url or AUTHOR_PHOTO_URL
    return f"""{BYLINE_MARKER}
<div class="neuro-author-byline" style="margin:32px 0 8px;padding-top:20px;border-top:1px solid #c5d9e4;max-width:420px;font-family:inherit;color:#1a3a4a">
<p style="margin:0 0 4px;font-size:0.85rem;line-height:1.45"><strong>Published by:</strong> Dr. Wasif Rizwan Malik</p>
<p style="margin:0 0 12px;font-size:0.8rem;line-height:1.45;color:#2b6b8a">Credentials: MBBS, FCPS (Neurosurgery), PMDC 47983-P</p>
<img src="{url}" alt="Dr. Wasif Rizwan Malik" width="80" height="80" loading="lazy" style="width:80px;height:80px;object-fit:cover;border-radius:50%;border:1px solid #c5d9e4;display:block"/>
</div>
"""


def append_byline(html: str) -> str:
    if BYLINE_MARKER in html or "neuro-author-byline" in html:
        return html
    return html.rstrip() + "\n" + author_byline_html()


def build_featured_prompt(topic: str) -> str:
    topic_clean = re.sub(r"\s+", " ", (topic or "neurosurgery advances").strip())[:120]
    return (
        f"{IMAGE_STYLE} Subject theme inspired by: {topic_clean}. "
        "Prefer abstract anatomy, soft neural pathways, imaging motifs, or clinical atmosphere — "
        "never a portrait of a specific physician."
    )


def grok_generate_image_b64(prompt: str) -> Optional[str]:
    """Return base64 image data from xAI Grok Imagine, or None on failure."""
    if not GROK_KEY:
        print("image_policy: GROK_API_KEY missing — skip Grok imaging")
        return None
    try:
        r = requests.post(
            "https://api.x.ai/v1/images/generations",
            headers={
                "Authorization": f"Bearer {GROK_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROK_IMAGE_MODEL,
                "prompt": prompt,
                "n": 1,
                "aspect_ratio": "16:9",
                "response_format": "b64_json",
            },
            timeout=180,
        )
        if r.status_code != 200:
            print(f"image_policy: Grok image HTTP {r.status_code}: {r.text[:300]}")
            return None
        data = r.json().get("data") or []
        if not data:
            print("image_policy: Grok image empty data")
            return None
        item = data[0]
        b64 = item.get("b64_json")
        if b64:
            return b64
        url = item.get("url")
        if url:
            img = requests.get(url, timeout=90)
            if img.status_code == 200 and img.content:
                return base64.b64encode(img.content).decode("ascii")
        print("image_policy: Grok image response lacked b64/url")
        return None
    except Exception as exc:
        print(f"image_policy: Grok image exception: {exc}")
        return None


def upload_wp_media(
    image_bytes: bytes,
    filename: str,
    title: str,
    alt: str,
) -> Optional[int]:
    """Upload binary image to WP Media Library; return attachment ID."""
    if not all([WP_URL, WP_USER, WP_PASS]):
        print("image_policy: WP credentials missing — skip media upload")
        return None
    auth = HTTPBasicAuth(WP_USER, WP_PASS)
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "image/png",
    }
    for attempt in range(1, 4):
        try:
            r = requests.post(
                f"{WP_URL}/wp-json/wp/v2/media",
                auth=auth,
                headers=headers,
                data=image_bytes,
                timeout=120,
            )
            if r.status_code in (200, 201):
                mid = int(r.json()["id"])
                # Set alt + title
                requests.post(
                    f"{WP_URL}/wp-json/wp/v2/media/{mid}",
                    auth=auth,
                    json={"alt_text": alt, "title": title},
                    timeout=45,
                )
                print(f"image_policy: uploaded media id={mid} ({filename})")
                return mid
            print(f"image_policy: media upload attempt {attempt} HTTP {r.status_code}: {r.text[:250]}")
        except Exception as exc:
            print(f"image_policy: media upload attempt {attempt} exception: {exc}")
        time.sleep(5 * attempt)
    return None


def create_ai_featured_media(topic: str, slug_hint: str = "neuro") -> Optional[int]:
    """
    Generate an AI medical visual via Grok Imagine and upload to WP.
    Returns media ID or None (caller should not fall back to doctor portraits).
    """
    prompt = build_featured_prompt(topic)
    print(f"image_policy: generating featured visual for: {topic[:80]}")
    b64 = grok_generate_image_b64(prompt)
    if not b64:
        return None
    try:
        raw = base64.b64decode(b64)
    except Exception as exc:
        print(f"image_policy: b64 decode failed: {exc}")
        return None
    safe = re.sub(r"[^a-z0-9]+", "-", (slug_hint or "neuro").lower()).strip("-")[:40] or "neuro"
    filename = f"ai-featured-{safe}-{int(time.time())}.png"
    title = f"AI medical visual — {topic[:80]}"
    alt = (
        f"Atmospheric clinical neuroscience illustration related to {topic[:100]}. "
        "No patient or physician identity depicted."
    )
    mid = upload_wp_media(raw, filename, title, alt)
    if mid and mid in FORBIDDEN_FEATURED_IDS:
        print(f"image_policy: refusing forbidden featured id {mid}")
        return None
    return mid


def resolve_author_photo_url() -> str:
    """Prefer live attachment URL for 1606 when WP creds available."""
    if not all([WP_URL, WP_USER, WP_PASS]):
        return AUTHOR_PHOTO_URL
    try:
        r = requests.get(
            f"{WP_URL}/wp-json/wp/v2/media/{AUTHOR_PHOTO_ID}",
            auth=HTTPBasicAuth(WP_USER, WP_PASS),
            timeout=30,
        )
        if r.status_code == 200:
            src = (r.json().get("source_url") or "").strip()
            if src:
                return src
    except Exception as exc:
        print(f"image_policy: author photo lookup failed: {exc}")
    return AUTHOR_PHOTO_URL


def scrub_forbidden_featured(post_id: int) -> None:
    """If a post somehow got a doctor portrait as featured image, clear it."""
    if not post_id or not all([WP_URL, WP_USER, WP_PASS]):
        return
    auth = HTTPBasicAuth(WP_USER, WP_PASS)
    try:
        r = requests.get(
            f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
            auth=auth,
            params={"context": "edit"},
            timeout=45,
        )
        if r.status_code != 200:
            return
        featured = int(r.json().get("featured_media") or 0)
        if featured in FORBIDDEN_FEATURED_IDS:
            print(f"image_policy: clearing forbidden featured_media={featured} on post {post_id}")
            requests.post(
                f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
                auth=auth,
                json={"featured_media": 0},
                timeout=45,
            )
    except Exception as exc:
        print(f"image_policy: scrub_forbidden_featured failed: {exc}")
