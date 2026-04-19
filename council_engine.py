#!/usr/bin/env python3
"""
THE NEURO COUNCIL — Python Content Engine
Dr. Wasif Rizwan Malik | PMDC 47983-P | drwasifmalik.com
Claude + Grok automated neuroscience publishing pipeline
"""

import os
import requests
import re
import time
from datetime import datetime

# ─── CONFIG ─────────────────────────────────────────────────
CLAUDE_KEY     = os.environ.get('ANTHROPIC_API_KEY', '')
GROK_KEY       = os.environ.get('GROK_API_KEY', '')
WP_URL         = os.environ.get('WP_URL', 'https://drwasifmalik.com')
WP_USER        = os.environ.get('WP_USERNAME', '')
WP_PASS        = os.environ.get('WP_APP_PASSWORD', '')
TG_TOKEN       = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT        = os.environ.get('TELEGRAM_CHAT_ID', '')
MANUAL_TOPIC   = os.environ.get('MANUAL_TOPIC', '')
CONTENT_TYPE   = os.environ.get('CONTENT_TYPE', 'patient_guide')
PUBLISH_MODE   = os.environ.get('PUBLISH_MODE', 'draft')

AUTHOR_BRAND = "Dr. Wasif Rizwan Malik | MBBS, FCPS (Neurosurgery) | PMDC 47983-P | Consultant Neurosurgeon, Faraz Hospital, Dubai Mahal Chowk, Bahawalpur"
CLINIC_CTA   = "📞 Book Consultation: WhatsApp +923458254232 | Faraz Hospital, Bahawalpur"

# ─── TOPIC POOL ─────────────────────────────────────────────
TOPIC_POOL = [
    {"topic": "Awake craniotomy: why we operate on the conscious brain", "pillar": "brand_authority", "keywords": ["awake craniotomy", "brain mapping surgery"]},
    {"topic": "Lumbar disc herniation: when to operate and when to wait", "pillar": "patient_education", "keywords": ["lumbar disc", "slipped disc", "back surgery Pakistan"]},
    {"topic": "Brain tumour diagnosis: the headache you must not ignore", "pillar": "patient_education", "keywords": ["brain tumour symptoms", "brain cancer Pakistan"]},
    {"topic": "Cervical myelopathy: the silent killer of hand function", "pillar": "clinical_advances", "keywords": ["cervical myelopathy", "neck surgery"]},
    {"topic": "Epilepsy surgery: when medications fail", "pillar": "clinical_advances", "keywords": ["epilepsy surgery", "refractory epilepsy"]},
    {"topic": "Brain aneurysm: understanding the worst headache of your life", "pillar": "patient_education", "keywords": ["brain aneurysm", "subarachnoid haemorrhage"]},
]

def get_topic():
    if MANUAL_TOPIC:
        return {"topic": MANUAL_TOPIC, "pillar": "patient_education", "keywords": []}
    wk = datetime.now().isocalendar()[1]
    return TOPIC_POOL[wk % len(TOPIC_POOL)]

def grok_research(topic):
    if not GROK_KEY:
        print("⚠️ No Grok key — skipping research phase")
        return ""
    print(f"🔵 Grok researching: {topic}")
    prompt = f'Research for neuroscience article on "{topic}". Provide: latest trials (2023-2026), key statistics, current guidelines (AAN/NICE/AANS), 5 PubMed citations with PMID, Pakistan-specific context if relevant. Keep under 500 words.'
    try:
        r = requests.post('https://api.x.ai/v1/chat/completions',
            headers={'Authorization': f'Bearer {GROK_KEY}', 'Content-Type': 'application/json'},
            json={'model': 'grok-3', 'max_tokens': 800, 'temperature': 0.2, 'messages': [{'role': 'user', 'content': prompt}]},
            timeout=60)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ Grok error: {e}")
        return ""

def claude_generate(topic, pillar, keywords, grok_brief):
    if not CLAUDE_KEY:
        raise ValueError("❌ No Claude API key found")

    print(f"🟡 Claude generating content for: {topic}")
    research = f"\n\nGROK RESEARCH BRIEF:\n{grok_brief}" if grok_brief else ""
    seo = f"\nPrimary keyword: {keywords[0] if keywords else topic}"

    system = f"""You are the official writer for The Neuro Council — writing as Dr. Wasif Rizwan Malik, MBBS, FCPS (Neurosurgery), PMDC 47983-P, Consultant Neurosurgeon at Faraz Hospital, Bahawalpur, Pakistan.

Style: Authoritative but accessible. Evidence-based. Patient-friendly where needed.
Always include:
- Full author byline: {AUTHOR_BRAND}
- Consultation CTA: {CLINIC_CTA}
- Educational disclaimer: Educational content only. Consult your neurosurgeon for specific advice."""

    prompt = f"""Create a complete content package for: **{topic}**{research}{seo}

Deliver in clear sections:
1. Blog Article (SEO-optimised, ~1500-2000 words) with proper H1, H2, introduction, causes, symptoms, diagnosis, treatment, recovery, FAQ, conclusion + CTA.
2. Patient Guide - English (simple language, ~400 words)
3. Patient Guide - Urdu Nastaliq (~400 words)
4. YouTube Video Script Outline (~600 words)
5. CME Summary for doctors (evidence-graded, ~300 words)

Use natural medical tone."""

    # Retry logic with higher timeout
    for attempt in range(3):
        try:
            print(f"   Attempt {attempt+1}/3 - Calling Claude...")
            r = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': CLAUDE_KEY,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'claude-3-5-sonnet-20241022',   # Stable model
                    'max_tokens': 4096,
                    'system': system,
                    'messages': [{'role': 'user', 'content': prompt}]
                },
                timeout=180   # 3 minutes
            )

            if r.status_code == 200:
                content = r.json()['content'][0]['text']
                print(f"✅ Claude successfully generated {len(content.split())} words")
                return content
            else:
                print(f"❌ Claude API error {r.status_code}")

        except requests.exceptions.ReadTimeout:
            print(f"⏳ Read timeout on attempt {attempt+1}. Retrying in 12 seconds...")
            time.sleep(12)
            continue
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            break

    raise RuntimeError("❌ Claude failed after 3 attempts.")

def publish_wp(title, content, status='draft', tags=None):
    if not all([WP_URL, WP_USER, WP_PASS]):
        print("⚠️ WordPress credentials missing — saving locally only")
        return None

    try:
        html = content.replace('\n\n', '</p><p>').replace('\n', '<br>')
        html = re.sub(r'^#{1}\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^#{2}\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)

        payload = {
            'title': title,
            'content': '<p>' + html + '</p>',
            'status': status,
            'excerpt': content[:155],
            'tags': tags or []
        }

        r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts",
            json=payload,
            auth=(WP_USER, WP_PASS),
            timeout=30)

        if r.status_code in [200, 201]:
            data = r.json()
            print(f"✅ Published to WordPress: {data.get('link', 'No link')}")
            return {'id': data.get('id'), 'url': data.get('link', '')}
        else:
            print(f"❌ WordPress error {r.status_code}")
    except Exception as e:
        print(f"❌ WP publish error: {e}")
    return None

def notify_tg(topic, result, wc):
    if not TG_TOKEN or not TG_CHAT:
        return
    msg = f"""🧠 Neuro Council Session Complete

Topic: {topic}
Words: {wc:,}
Status: {PUBLISH_MODE.upper()}
Time: {datetime.now().strftime('%d %b %Y, %H:%M PKT')}"""

    if result and result.get('url'):
        msg += f"\n\n🔗 Link: {result['url']}"

    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={'chat_id': TG_CHAT, 'text': msg}, timeout=10)
        print("✅ Telegram notification sent")
    except:
        pass

def main():
    print("=" * 70)
    print("🧠 THE NEURO COUNCIL — Content Engine Starting")
    print(f"📅 {datetime.now().strftime('%A, %d %B %Y %H:%M PKT')}")
    print("=" * 70)

    td = get_topic()
    topic = td['topic']
    pillar = td.get('pillar', 'patient_education')
    keywords = td.get('keywords', [])

    print(f"📌 Topic: {topic}")
    print(f"🎯 Pillar: {pillar}")

    grok_brief = grok_research(topic)

    try:
        content = claude_generate(topic, pillar, keywords, grok_brief)
    except Exception as e:
        print(f"❌ Content generation failed: {e}")
        return

    wc = len(content.split())
    print(f"📊 Generated content: {wc:,} words")

    # Save locally
    os.makedirs('council_output', exist_ok=True)
    filename = f"council_output/{datetime.now().strftime('%Y%m%d_%H%M')}_{topic.replace(' ', '_')[:50]}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Saved locally: {filename}")

    # Publish to WordPress
    result = publish_wp(topic, content, PUBLISH_MODE, keywords)

    # Notify via Telegram
    notify_tg(topic, result, wc)

    print("\n" + "=" * 70)
    print("✅ NEURO COUNCIL SESSION COMPLETED")
    print("=" * 70)

if __name__ == '__main__':
    main()
