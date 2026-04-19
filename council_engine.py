#!/usr/bin/env python3
"""
THE NEURO COUNCIL — Lightweight Version
Dr. Wasif Rizwan Malik | PMDC 47983-P | drwasifmalik.com
Simplified to reduce timeouts
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
PUBLISH_MODE   = os.environ.get('PUBLISH_MODE', 'draft')

AUTHOR_BRAND = "Dr. Wasif Rizwan Malik | MBBS, FCPS (Neurosurgery) | PMDC 47983-P | Consultant Neurosurgeon, Faraz Hospital, Bahawalpur"
CLINIC_CTA   = "📞 Book Consultation: WhatsApp +923458254232 | Faraz Hospital, Bahawalpur"

# ─── TOPIC POOL ─────────────────────────────────────────────
TOPIC_POOL = [
    {"topic": "Awake craniotomy: why we operate on the conscious brain", "pillar": "brand_authority", "keywords": ["awake craniotomy"]},
]

def get_topic():
    if MANUAL_TOPIC:
        return {"topic": MANUAL_TOPIC, "pillar": "brand_authority", "keywords": []}
    return TOPIC_POOL[0]  # Always use awake craniotomy for testing

def grok_research(topic):
    if not GROK_KEY:
        print("⚠️ No Grok key — skipping research")
        return ""
    print(f"🔵 Grok researching: {topic}")
    prompt = f'Quick research on "{topic}". Key points, statistics, and 3 recent references only.'
    try:
        r = requests.post('https://api.x.ai/v1/chat/completions',
            headers={'Authorization': f'Bearer {GROK_KEY}', 'Content-Type': 'application/json'},
            json={'model': 'grok-3', 'max_tokens': 600, 'temperature': 0.2, 'messages': [{'role': 'user', 'content': prompt}]},
            timeout=60)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ Grok error: {e}")
        return ""

def claude_generate(topic, grok_brief):
    if not CLAUDE_KEY:
        raise ValueError("❌ No Claude API key")

    print(f"🟡 Claude generating: {topic}")
    research = f"\n\nResearch: {grok_brief}" if grok_brief else ""

    system = f"""You are Dr. Wasif Rizwan Malik, Consultant Neurosurgeon, Faraz Hospital, Bahawalpur.
Write clear, professional neuroscience content. Always include your full name, credentials, and consultation CTA."""

    prompt = f"""Write a short, clean patient guide on: **{topic}**{research}

Keep it simple and useful:
- What is it?
- Why is it done?
- What to expect?
- Recovery
- When to contact doctor

End with: Author: {AUTHOR_BRAND}
Consultation: {CLINIC_CTA}"""

    for attempt in range(3):
        try:
            print(f"   Attempt {attempt+1}/3...")
            r = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': CLAUDE_KEY,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'claude-3-5-sonnet-20241022',
                    'max_tokens': 2000,
                    'system': system,
                    'messages': [{'role': 'user', 'content': prompt}]
                },
                timeout=120
            )

            if r.status_code == 200:
                content = r.json()['content'][0]['text']
                print(f"✅ Claude generated {len(content.split())} words")
                return content
            else:
                print(f"Claude error {r.status_code}")

        except requests.exceptions.ReadTimeout:
            print(f"⏳ Timeout on attempt {attempt+1}. Retrying...")
            time.sleep(10)
            continue
        except Exception as e:
            print(f"Error: {e}")
            break

    raise RuntimeError("Claude failed after retries.")

def main():
    print("=" * 60)
    print("🧠 NEURO COUNCIL - LIGHTWEIGHT TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    td = get_topic()
    topic = td['topic']

    print(f"Topic: {topic}")

    grok_brief = grok_research(topic)

    try:
        content = claude_generate(topic, grok_brief)
    except Exception as e:
        print(f"❌ Failed: {e}")
        return

    wc = len(content.split())
    print(f"✅ Generated {wc} words")

    # Save locally
    os.makedirs('council_output', exist_ok=True)
    filename = f"council_output/test_{datetime.now().strftime('%H%M')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Saved to: {filename}")

    print("\n✅ Test completed!")

if __name__ == '__main__':
    main()
