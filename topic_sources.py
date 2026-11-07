#!/usr/bin/env python3
"""
Topic citations + further-reading + monolingual source HTML for daily neuro-news.

Never invent PMIDs/DOIs. Prefer open-access links. Section labels are monolingual
per lang; URLs stay Latin/ASCII.
"""

from __future__ import annotations

import html as html_lib
import json
import os
import re
from typing import Any, Optional
from urllib.parse import urlparse

import requests

GROK_KEY = os.environ.get("GROK_API_KEY", "")
GROK_MODEL = os.environ.get("GROK_CONTENT_MODEL", "grok-4.5")

LABELS = {
    "en": {
        "primary": "Primary source",
        "further": "Further reading — study & management",
        "fulltext": "Full text / PubMed / DOI →",
        "image_oa": "Featured image: clinical figure from the cited open-access source (attributed below).",
        "image_ai": "Featured image: AI-generated conceptual editorial image — not a clinical photograph from the cited study.",
    },
    "ur": {
        "primary": "اصل ماخذ",
        "further": "مزید مطالعہ — مطالعہ اور نظم و نسق",
        "fulltext": "مکمل متن / PubMed / DOI ←",
        "image_oa": "تصویر: حوالہ شدہ اوپن ایکسیس ماخذ سے کلینیکل شکل (ذیل میں انتساب).",
        "image_ai": "تصویر: مصنوعی ذہانت سے تیار کردہ تصویری اداریہ — حوالہ شدہ تحقیق کی کلینیکل فوٹو نہیں۔",
    },
    "ar": {
        "primary": "المصدر الأساسي",
        "further": "قراءات إضافية — الدراسة والإدارة",
        "fulltext": "النص الكامل / PubMed / DOI ←",
        "image_oa": "الصورة: شكل سريري من المصدر المفتوح المذكور (الإسناد أدناه).",
        "image_ai": "الصورة: صورة تحريرية مفاهيمية بالذكاء الاصطناعي — ليست صورة سريرية من الدراسة المذكورة.",
    },
}

_ALLOWED_HOST_HINTS = (
    "nih.gov",
    "ncbi.nlm.nih.gov",
    "pubmed.ncbi.nlm.nih.gov",
    "pmc.ncbi.nlm.nih.gov",
    "doi.org",
    "thejns.org",
    "aans.org",
    "cns.org",
    "who.int",
    "nice.org.uk",
    "cochranelibrary.com",
    "nejm.org",
    "thelancet.com",
    "jamanetwork.com",
    "nature.com",
    "springer.com",
    "wiley.com",
    "oup.com",
    "bmj.com",
    "frontiersin.org",
    "mdpi.com",
    "plos.org",
    "hindawi.com",
    "lww.com",
    "medscape.com",
    "statnews.com",
    "reuters.com",
    "bbc.com",
    "bbc.co.uk",
    "nih.gov",
    "clinicaltrials.gov",
    "europepmc.org",
    "ebi.ac.uk",
)


def _esc(s: str) -> str:
    return html_lib.escape(s or "", quote=True)


def _looks_like_url(u: str) -> bool:
    try:
        p = urlparse((u or "").strip())
        return p.scheme in ("http", "https") and bool(p.netloc) and "." in p.netloc
    except Exception:
        return False


def _host_ok(u: str) -> bool:
    host = (urlparse(u).netloc or "").lower()
    if not host:
        return False
    return any(h in host for h in _ALLOWED_HOST_HINTS) or host.endswith(".edu") or host.endswith(".gov")


def extract_pmcid(url_or_id: str) -> Optional[str]:
    s = (url_or_id or "").strip()
    m = re.search(r"PMC(\d+)", s, re.I)
    if m:
        return m.group(1)
    if s.isdigit():
        return s
    return None


def normalize_sources(raw: Any) -> dict:
    """Validate and clamp a sources dict. Drops invented-looking empty links."""
    if not isinstance(raw, dict):
        return {}
    primary = raw.get("primary") if isinstance(raw.get("primary"), dict) else {}
    title = str(primary.get("title") or "").strip()[:300]
    authors = str(primary.get("authors") or "").strip()[:200]
    journal = str(primary.get("journal") or "").strip()[:160]
    year = str(primary.get("year") or "").strip()[:12]
    url = str(primary.get("url") or primary.get("link") or "").strip()
    pmcid = extract_pmcid(str(primary.get("pmcid") or url or ""))
    license_note = str(primary.get("license") or "").strip()[:200]
    if url and not _looks_like_url(url):
        url = ""
    if url and not _host_ok(url):
        # Keep DOI/PubMed-like only; drop random hosts from hallucinated links
        url = ""

    further = []
    for item in raw.get("further_reading") or raw.get("further") or []:
        if not isinstance(item, dict):
            continue
        fu = str(item.get("url") or item.get("link") or "").strip()
        ft = str(item.get("title") or item.get("label") or "").strip()[:240]
        note = str(item.get("note") or item.get("why") or "").strip()[:200]
        if not fu or not _looks_like_url(fu) or not _host_ok(fu):
            continue
        if not ft:
            ft = fu
        further.append({"title": ft, "url": fu, "note": note})
        if len(further) >= 5:
            break

    fig = raw.get("oa_figure") if isinstance(raw.get("oa_figure"), dict) else {}
    fig_out = {}
    if fig:
        f_pmc = extract_pmcid(str(fig.get("pmcid") or pmcid or ""))
        f_label = str(fig.get("figure") or fig.get("figure_id") or "F1").strip()[:12] or "F1"
        f_cap = str(fig.get("caption") or "").strip()[:400]
        f_lic = str(fig.get("license") or license_note or "").strip()[:200]
        if f_pmc:
            fig_out = {
                "pmcid": f_pmc,
                "figure": f_label,
                "caption": f_cap,
                "license": f_lic,
                "article_url": f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{f_pmc}/",
            }

    out: dict[str, Any] = {
        "primary": {
            "title": title,
            "authors": authors,
            "journal": journal,
            "year": year,
            "url": url,
            "pmcid": pmcid or "",
            "license": license_note,
        },
        "further_reading": further,
        "oa_figure": fig_out,
    }
    return out


def grok_resolve_sources(topic: str, angle: str = "", keywords: str = "", feed_hint: Optional[dict] = None) -> dict:
    """
    Ask Grok for real primary + 3–5 further-reading links. Returns normalized dict
    (may be empty on failure — caller should still try curated fallbacks).
    """
    key = GROK_KEY or os.environ.get("GROK_API_KEY", "")
    if not key:
        return {}
    hint = ""
    if feed_hint:
        hint = (
            f"\nOptional feed hint (use only if it is the real primary story):\n"
            f"- {feed_hint.get('title','')}\n- {feed_hint.get('link','')}\n"
        )
    system = (
        "You are a neurosurgery librarian. Return STRICT JSON only. "
        "NEVER invent PMIDs, PMCIDs, DOIs, or URLs. Only cite sources you are confident exist. "
        "Prefer PubMed/PMC/DOI/open-access journal links. "
        "If unsure of an exact URL, omit that item rather than guess."
    )
    user = {
        "topic": topic,
        "angle": angle,
        "keywords": keywords,
        "feed_hint": hint,
        "schema": {
            "primary": {
                "title": "paper or guideline title",
                "authors": "short author string",
                "journal": "journal or site",
                "year": "YYYY",
                "url": "https://...",
                "pmcid": "digits only if PMC OA exists, else empty",
                "license": "e.g. CC BY-NC-SA 4.0 if known",
            },
            "further_reading": [
                {
                    "title": "label",
                    "url": "https://...",
                    "note": "why useful for patients or doctors (short)",
                }
            ],
            "oa_figure": {
                "pmcid": "same as primary when an OA radiology/clinical figure exists",
                "figure": "F1",
                "caption": "short clinical caption",
                "license": "CC license if known",
            },
        },
        "rules": [
            "Provide exactly one primary source tightly on topic.",
            "Provide 3 to 5 further_reading links for study and management.",
            "Mix peer-reviewed + at least one patient-friendly reputable page when possible.",
            "If primary has PMC OA imaging figures, fill oa_figure; else leave oa_figure empty object.",
        ],
    }
    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": GROK_MODEL,
                "temperature": 0.1,
                "max_tokens": 1800,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
                ],
            },
            timeout=90,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        if "```" in text:
            m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
            if m:
                text = m.group(1).strip()
        raw = json.loads(text[text.find("{") : text.rfind("}") + 1])
        return normalize_sources(raw)
    except Exception as exc:  # noqa: BLE001
        print(f"topic_sources: grok_resolve_sources warn: {exc}")
        return {}


def render_sources_html(sources: dict, lang: str = "en", image_mode: str = "ai") -> str:
    """Monolingual HTML block: primary citation + further reading + image note."""
    lang = lang if lang in LABELS else "en"
    L = LABELS[lang]
    sources = normalize_sources(sources or {})
    primary = sources.get("primary") or {}
    further = sources.get("further_reading") or []
    parts: list[str] = ['<!-- dwf-topic-sources-v1 -->']

    if primary.get("title") or primary.get("url"):
        parts.append(
            '<div class="dwf-primary-source" style="background:#faf8f5;border:1px solid #c9c6c0;'
            'border-radius:10px;padding:12px 14px;margin:18px 0 16px;font-size:0.92rem;color:#3a342c">'
            f'<strong style="color:#1a1510">{_esc(L["primary"])}</strong>'
        )
        if primary.get("title"):
            parts.append(f'<p style="margin:6px 0 0"><em>{_esc(primary["title"])}</em></p>')
        meta_bits = [b for b in (primary.get("authors"), primary.get("journal"), primary.get("year")) if b]
        if meta_bits:
            parts.append(
                f'<p style="margin:4px 0 0;color:#5a7084">{_esc(" · ".join(meta_bits))}</p>'
            )
        if primary.get("url"):
            parts.append(
                f'<p style="margin:6px 0 0"><a style="color:#8a6520;font-weight:700" '
                f'href="{_esc(primary["url"])}" target="_blank" rel="noopener noreferrer">'
                f'{_esc(L["fulltext"])}</a></p>'
            )
        parts.append("</div>")

    if further:
        parts.append(
            '<div class="dwf-further-reading" style="background:#fff;border:1px solid #c9c6c0;'
            'border-radius:10px;padding:12px 14px;margin:0 0 16px;font-size:0.92rem;color:#3a342c">'
            f'<strong style="color:#1a1510">{_esc(L["further"])}</strong><ol style="margin:8px 0 0;padding-inline-start:1.25rem">'
        )
        for item in further:
            note = f' — {_esc(item["note"])}' if item.get("note") else ""
            parts.append(
                f'<li style="margin:0 0 6px"><a style="color:#8a6520;font-weight:600" '
                f'href="{_esc(item["url"])}" target="_blank" rel="noopener noreferrer">'
                f'{_esc(item["title"])}</a>{note}</li>'
            )
        parts.append("</ol></div>")

    fig = sources.get("oa_figure") or {}
    if image_mode == "oa" and fig:
        lic = fig.get("license") or "open-access via PMC"
        art = fig.get("article_url") or (
            f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{fig.get('pmcid')}/" if fig.get("pmcid") else ""
        )
        cap = fig.get("caption") or "Clinical figure from open-access source."
        attr = (
            f'{_esc(L["image_oa"])} '
            f'Source: PMC{_esc(str(fig.get("pmcid") or ""))} {_esc(str(fig.get("figure") or ""))}. '
            f'{_esc(cap)} License: {_esc(lic)}.'
        )
        if art:
            attr += (
                f' <a style="color:#8a6520;font-weight:700" href="{_esc(art)}" '
                f'target="_blank" rel="noopener noreferrer">Article →</a>'
            )
        parts.append(f'<p style="font-size:0.85rem;color:#5a7084;margin:12px 0"><em>{attr}</em></p>')
    else:
        parts.append(
            f'<p style="font-size:0.85rem;color:#5a7084;margin:12px 0"><em>{_esc(L["image_ai"])}</em></p>'
        )

    return "\n".join(parts)


def append_sources_before_byline(html: str, sources_html: str) -> str:
    if not sources_html:
        return html
    if "dwf-topic-sources-v1" in html:
        return html
    marker = "<!-- neuro-author-byline -->"
    if marker in html:
        return html.replace(marker, sources_html + "\n" + marker, 1)
    contact = "<!-- dwf-contact-footer-v1 -->"
    if contact in html:
        return html.replace(contact, sources_html + "\n" + contact, 1)
    return html.rstrip() + "\n" + sources_html
