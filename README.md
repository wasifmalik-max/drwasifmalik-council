# 🧠 The Neuro Council

**Claude + Grok AI Content Empire for drwasifmalik.com**

*Dr. Wasif Rizwan Malik | MBBS, FCPS (Neurosurgery) | PMDC 47983-P*  
*Consultant Neurosurgeon, Faraz Hospital, Dubai Mahal Chowk, Bahawalpur*

---

## What This Does

The world's first continuously self-upgrading neuroscience content platform — powered by a dual AI editorial council:

- 🟡 **Claude (Anthropic)** — Clinical reasoning depth, FCPS-grade writing, brand voice
- 🔵 **Grok (xAI)** — Real-time research, latest trials, current guidelines

Together they produce weekly:
- 📝 Blog articles (2000 words, SEO, PubMed-cited)
- 🏥 Patient guides (bilingual EN + Urdu Nastaliq)
- 🎥 YouTube video scripts
- 📱 Social media suites (FB, IG, Twitter, LinkedIn, WhatsApp)
- 🎓 CME summaries for doctors

Auto-published to WordPress every Monday 07:00 PKT.

## Setup

Add these GitHub Secrets (Settings → Secrets → Actions):

| Secret | Value |
|---|---|
| ANTHROPIC_API_KEY | Claude API key from console.anthropic.com |
| GROK_API_KEY | Grok API key from console.x.ai |
| WP_URL | https://drwasifmalik.com |
| WP_USERNAME | WordPress username |
| WP_APP_PASSWORD | WP Application Password |
| TELEGRAM_BOT_TOKEN | From @BotFather |
| TELEGRAM_CHAT_ID | From @userinfobot |

## Run Manually

GitHub → Actions → Neuro Council Weekly Pipeline → Run workflow

Optionally override the topic and set publish mode to 'publish'.

---
*drwasifmalik.com | WhatsApp +923458254232*