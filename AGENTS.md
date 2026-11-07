# Agent notes — drwasifmalik-council

## Always-on rules
See `.cursor/rules/monolingual-i18n.mdc` and `.cursor/rules/topic-sources-and-links.mdc` (mirrored on homepage `drwasif-homepage-fix`).

**Daily neurosciences news:**
- One 365-calendar topic → one WP post (`daily_neuro_news.py`, `MAX_UPLOADS_PER_DAY=1`).
- Day 1 = **2026-10-02** PKT (`topic_of_the_day.py`).
- Monolingual EN in content; separate UR/AR meta; Latin contact digits; RTL for UR/AR.
- Scheduled by `.github/workflows/neuro-daily-news.yml`.
- **Every topic** must include: primary study/source link, **3–5 further-reading** links (PubMed/PMC/guidelines/textbooks/reputable reviews), and prefer attributed PMC/OA clinical figures via `image_policy.py` (Imagine only as fallback). Never invent DOIs/PMIDs.

## Do not
- Multi-post daily batches, bilingual mashup HTML, or Urdu/Arabic-Indic phone digits.
- Publish without real citations / further reading, or scrape paywalled images.
