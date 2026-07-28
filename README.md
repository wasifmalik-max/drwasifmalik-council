# 🧠 The Neuro Council

**Grok 4.5 (primary) + Claude (optional fallback) for drwasifmalik.com**

*Dr. Wasif Rizwan Malik | MBBS, FCPS (Neurosurgery) | PMDC 47983-P*  
*Consultant Neurosurgeon, Faraz Hospital, Dubai Mahal Chowk, Bahawalpur*

---

## What This Does

Weekly neuroscience content pipeline — powered by:

- 🔵 **Grok 4.5 (xAI)** — Primary research + article generation
- 🟡 **Claude (Anthropic)** — Optional fallback only (not required)

Produces weekly SEO blog articles (PubMed-checked) and auto-publishes to WordPress every Monday 07:00 PKT.

## Setup

Add these GitHub Secrets (Settings → Secrets → Actions):

| Secret | Value |
|---|---|
| GROK_API_KEY | xAI API key from console.x.ai (**required**) |
| ANTHROPIC_API_KEY | Claude API key — optional fallback only |
| WP_URL | https://drwasifmalik.com |
| WP_USERNAME | WordPress username |
| WP_APP_PASSWORD | WP Application Password |
| TELEGRAM_BOT_TOKEN | From @BotFather |
| TELEGRAM_CHAT_ID | From @userinfobot |
| GMAIL_USER | Notification email |
| GMAIL_APP_PASSWORD | Gmail app password |

## Run Manually

GitHub → Actions → Neuro Council Weekly Pipeline → Run workflow

Optionally override the topic and enable **dry_run** to skip WordPress publish.

## Daily Neurosciences News (separate)

Lightweight **daily** short briefs on brain / spine / nerve / mind advances.

- Workflow: `.github/workflows/neuro-daily-news.yml`
- Script: `daily_neuro_news.py`
- Default publish mode: **publish** (live). Scheduled daily runs go live automatically.
- Does **not** replace or modify the Monday weekly council pipeline or keepalive.

Manual dry-run: Actions → Neurosciences Daily News → Run workflow → `dry_run=true` (optional staging).

## Image policy

Shared module: `image_policy.py` (used by daily + weekly publishers).

| Surface | Rule |
|---|---|
| Homepage / promo | Real occasion portraits — media **1606** (white coat), **1637** (OR), **1638** (academic) |
| Post featured / cover | AI medical/neuroscience visual via **Grok Imagine** (`/v1/images/generations`). Never doctor personal photos. No paediatric faces. |
| Post footer | Mini author byline: name + MBBS/FCPS/PMDC + small circular photo (1606) |

Booking CTAs remain `https://rx.drwasifmalik.com`.

---
*drwasifmalik.com | WhatsApp +923458254232*