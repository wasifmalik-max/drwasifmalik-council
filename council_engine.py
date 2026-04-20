#!/usr/bin/env python3
"""
THE NEURO COUNCIL v2.2 FINAL
Dr. Wasif Rizwan Malik | PMDC 47983-P | drwasifmalik.com
FIXES: WP username slug, model fallback, auth verify, sys.exit on fail
"""
import os, re, time, sys
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

CLAUDE_KEY   = os.environ.get('ANTHROPIC_API_KEY', '')
GROK_KEY     = os.environ.get('GROK_API_KEY', '')
WP_URL       = os.environ.get('WP_URL', 'https://drwasifmalik.com')
WP_USER      = os.environ.get('WP_USERNAME', '')
WP_PASS      = os.environ.get('WP_APP_PASSWORD', '')
TG_TOKEN     = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT      = os.environ.get('TELEGRAM_CHAT_ID', '')
MANUAL_TOPIC = os.environ.get('MANUAL_TOPIC', '')
PUBLISH_MODE = os.environ.get('PUBLISH_MODE', 'draft')

AUTHOR = "Dr. Wasif Rizwan Malik | MBBS, FCPS (Neurosurgery) | PMDC 47983-P | Consultant Neurosurgeon, Faraz Hospital, Dubai Mahal Chowk, Bahawalpur"
CTA    = "Book Consultation: WhatsApp +923458254232 | Faraz Hospital, Bahawalpur"

MODELS = [
    "claude-sonnet-4-20250514",
    "claude-sonnet-4",
    "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet-20241022",
]

TOPICS = [
    {"t": "Lumbar disc herniation: when to operate and when to wait", "k": "lumbar disc slipped disc back surgery Pakistan"},
    {"t": "Brain tumour diagnosis: the headache you must not ignore", "k": "brain tumour symptoms brain cancer Pakistan"},
    {"t": "Cervical myelopathy: the silent killer of hand function", "k": "cervical myelopathy neck surgery hand weakness"},
    {"t": "Epilepsy surgery: when medications fail", "k": "epilepsy surgery refractory epilepsy"},
    {"t": "Brain aneurysm: the worst headache of your life explained", "k": "brain aneurysm subarachnoid haemorrhage"},
    {"t": "Carpal tunnel syndrome: the wrist problem explained", "k": "carpal tunnel wrist pain hand numbness"},
    {"t": "Hydrocephalus in adults: the treatable cause of dementia", "k": "hydrocephalus water on brain VP shunt"},
    {"t": "Intraoperative CT: how BodyTom changed surgical precision", "k": "intraoperative CT BodyTom brain imaging"},
    {"t": "Pituitary adenoma: the tumour hiding behind hormonal chaos", "k": "pituitary tumour endonasal surgery"},
    {"t": "Parkinson disease: from diagnosis to deep brain stimulation", "k": "Parkinson disease Pakistan DBS tremor"},
    {"t": "CVST: the stroke that strikes young women after childbirth", "k": "CVST cerebral venous sinus thrombosis"},
    {"t": "Bell palsy: complete recovery is possible", "k": "Bell palsy facial nerve facial palsy"},
    {"t": "Awake craniotomy: why we operate on the conscious brain", "k": "awake craniotomy brain mapping surgery"},
    {"t": "Glioblastoma 2025: new treatments changing the prognosis", "k": "glioblastoma GBM treatment 2025"},
    {"t": "Trigeminal neuralgia: the most painful condition known to medicine", "k": "trigeminal neuralgia MVD surgery"},
    {"t": "Myelomeningocele: what parents need to know from day one", "k": "myelomeningocele spina bifida"},
    {"t": "AI in neurosurgery: promise, reality, and caution", "k": "AI neurosurgery machine learning brain"},
    {"t": "Spinal cord injury: what neuroscience offers in 2025", "k": "spinal cord injury SCI rehab"},
]

def get_topic():
    if MANUAL_TOPIC: return {"t": MANUAL_TOPIC, "k": MANUAL_TOPIC}
    return TOPICS[datetime.now().isocalendar()[1] % len(TOPICS)]

def verify_wp():
    if not all([WP_URL, WP_USER, WP_PASS]):
        return False, f"Missing: URL={bool(WP_URL)} USER={bool(WP_USER)} PASS={bool(WP_PASS)}"
    try:
        r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts?per_page=1",
            auth=HTTPBasicAuth(WP_USER, WP_PASS), timeout=15)
        return r.status_code == 200, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)

def grok_research(topic):
    if not GROK_KEY: print("No Grok key"); return ""
    print(f"GROK: {topic}")
    try:
        r = requests.post('https://api.x.ai/v1/chat/completions',
            headers={'Authorization': f'Bearer {GROK_KEY}', 'Content-Type': 'application/json'},
            json={'model': 'grok-3', 'max_tokens': 600, 'temperature': 0.2,
                  'messages': [{'role': 'user', 'content': f'Research "{topic}": key stats, AAN/NICE/AANS guidelines, 3 confirmed PubMed PMIDs, Pakistan context. 400 words max.'}]},
            timeout=60)
        b = r.json()['choices'][0]['message']['content']
        print(f"Grok: {len(b.split())}w"); return b
    except Exception as e:
        print(f"Grok error: {e}"); return ""

def claude_generate(topic, kw, brief):
    if not CLAUDE_KEY:
        print("ERROR: No ANTHROPIC_API_KEY"); sys.exit(1)
    research = f"\n\nGROK RESEARCH:\n{brief}" if brief else ""
    system = f"You are author of The Neuro Council, writing as {AUTHOR}. Write authoritative, evidence-based, SEO-optimised neuroscience content. Always include author byline and CTA: {CTA}. Only cite PubMed references you are certain exist. Educational disclaimer required."
    prompt = f"""Write complete SEO blog article: **{topic}**
Keyword: {kw}{research}

Structure (1500w):
META TITLE: [60 chars]
META DESCRIPTION: [155 chars]
# [H1]
## Introduction (150w - real statistic hook)
## What is it? (200w)
## Causes (150w)
## Symptoms - bold red flags (200w)
## Diagnosis at Faraz Hospital (150w)
## Treatment - cite evidence, BodyTom CT + Zeiss microscope (250w)
## Recovery (150w)
## FAQ 5 questions (200w)
## Conclusion + CTA (100w)
References: only certain ones. Otherwise: References available upon request.
Author: {AUTHOR} | {CTA} | Disclaimer: Educational only."""

    for model in MODELS:
        for attempt in range(2):
            try:
                print(f"CLAUDE: {model} attempt {attempt+1}")
                r = requests.post('https://api.anthropic.com/v1/messages',
                    headers={'x-api-key': CLAUDE_KEY, 'anthropic-version': '2023-06-01', 'Content-Type': 'application/json'},
                    json={'model': model, 'max_tokens': 4096, 'system': system, 'messages': [{'role': 'user', 'content': prompt}]},
                    timeout=180)
                if r.status_code == 200:
                    t = r.json()['content'][0]['text']
                    print(f"SUCCESS: {len(t.split())}w | {model}"); return t
                print(f"Error {r.status_code}: {r.text[:150]}")
                if r.status_code in [400, 404]: break
            except requests.exceptions.ReadTimeout:
                print("Timeout, retrying..."); time.sleep(10)
            except Exception as e:
                print(f"ERR: {e}"); break
    print("ERROR: All Claude models failed"); sys.exit(1)

def to_html(content):
    h = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    h = re.sub(r'^## (.+)$', r'<h2>\1</h2>', h, flags=re.MULTILINE)
    h = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', h)
    return '<p>' + h.replace('\n\n', '</p><p>').replace('\n', '<br>') + '</p>'

def publish_wp(title, content, status='draft'):
    ok, msg = verify_wp()
    if not ok:
        print(f"WP FAILED: {msg} | USER={WP_USER} PASS_LEN={len(WP_PASS)}"); return None
    print(f"WP OK: {msg}")
    try:
        r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts",
            json={'title': title, 'content': to_html(content), 'status': status,
                  'excerpt': re.sub(r'[#*_]', '', content)[:155]},
            auth=HTTPBasicAuth(WP_USER, WP_PASS), timeout=30)
        if r.status_code in [200, 201]:
            d = r.json(); print(f"WP {status}: {d.get('link','')}"); return d
        print(f"WP error {r.status_code}: {r.text[:300]}")
    except Exception as e: print(f"WP error: {e}")
    return None

def main():
    print("="*55)
    print("THE NEURO COUNCIL v2.2 FINAL")
    print(datetime.now().strftime('%A %d %B %Y %H:%M PKT'))
    print(f"Mode: {PUBLISH_MODE}")
    print("="*55)
    td = get_topic(); topic, kw = td['t'], td['k']
    print(f"Topic: {topic}")
    brief = grok_research(topic)
    content = claude_generate(topic, kw, brief)
    wc = len(content.split()); print(f"Generated: {wc:,}w")
    os.makedirs('council_output', exist_ok=True)
    ds = datetime.now().strftime('%Y%m%d_%H%M')
    fname = f"council_output/{ds}_{re.sub(chr(91)+'a-z0-9'+chr(93)+'+','-',topic.lower())[:40]}.md"
    with open(fname, 'w', encoding='utf-8') as f: f.write(f"# {topic}\n\n{content}")
    print(f"Saved: {fname}")
    result = publish_wp(topic, content, PUBLISH_MODE)
    url = result.get('link','') if result else ''
    if TG_TOKEN and TG_CHAT:
        try: requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",json={'chat_id':TG_CHAT,'text':f"Neuro Council\nTopic: {topic}\nWords: {wc:,}\nURL: {url}"},timeout=10)
        except: pass
    print(f"DONE - {wc:,}w | {url}")

if __name__ == '__main__': main()#!/usr/bin/env python3
"""
THE NEURO COUNCIL - Production Engine v2.0
Dr. Wasif Rizwan Malik | PMDC 47983-P | drwasifmalik.com
KEY FIXES: timeout=180, model=claude-sonnet-4-20250514, 3x retry, 18-topic pool
"""
import os, requests, re, time
from datetime import datetime

CLAUDE_KEY   = os.environ.get('ANTHROPIC_API_KEY', '')
GROK_KEY     = os.environ.get('GROK_API_KEY', '')
WP_URL       = os.environ.get('WP_URL', 'https://drwasifmalik.com')
WP_USER      = os.environ.get('WP_USERNAME', '')
WP_PASS      = os.environ.get('WP_APP_PASSWORD', '')
TG_TOKEN     = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT      = os.environ.get('TELEGRAM_CHAT_ID', '')
MANUAL_TOPIC = os.environ.get('MANUAL_TOPIC', '')
CONTENT_TYPE = os.environ.get('CONTENT_TYPE', 'blog_post')
PUBLISH_MODE = os.environ.get('PUBLISH_MODE', 'draft')

AUTHOR_BRAND = "Dr. Wasif Rizwan Malik | MBBS, FCPS (Neurosurgery) | PMDC 47983-P | Consultant Neurosurgeon, Faraz Hospital, Dubai Mahal Chowk, Bahawalpur"
CLINIC_CTA   = "Book Consultation: WhatsApp +923458254232 | Faraz Hospital, Bahawalpur"

TOPIC_POOL = [
    {"topic": "Lumbar disc herniation: when to operate and when to wait", "pillar": "patient_education", "keywords": ["lumbar disc","slipped disc","back surgery Pakistan"]},
    {"topic": "Brain tumour diagnosis: the headache you must not ignore", "pillar": "patient_education", "keywords": ["brain tumour symptoms","brain cancer Pakistan"]},
    {"topic": "Cervical myelopathy: the silent killer of hand function", "pillar": "clinical_advances", "keywords": ["cervical myelopathy","neck surgery","hand weakness"]},
    {"topic": "Epilepsy surgery: when medications fail", "pillar": "clinical_advances", "keywords": ["epilepsy surgery","refractory epilepsy"]},
    {"topic": "Brain aneurysm: the worst headache of your life explained", "pillar": "patient_education", "keywords": ["brain aneurysm","subarachnoid haemorrhage"]},
    {"topic": "Carpal tunnel syndrome: the wrist problem explained", "pillar": "patient_education", "keywords": ["carpal tunnel","wrist pain","hand numbness"]},
    {"topic": "Hydrocephalus in adults: the treatable cause of dementia", "pillar": "patient_education", "keywords": ["hydrocephalus","water on brain","VP shunt"]},
    {"topic": "Intraoperative CT: how BodyTom changed surgical precision", "pillar": "brand_authority", "keywords": ["intraoperative CT","BodyTom","brain imaging"]},
    {"topic": "Pituitary adenoma: the tumour hiding behind hormonal chaos", "pillar": "patient_education", "keywords": ["pituitary tumour","endonasal surgery"]},
    {"topic": "Parkinson disease: from diagnosis to deep brain stimulation", "pillar": "patient_education", "keywords": ["Parkinson disease Pakistan","DBS tremor"]},
    {"topic": "CVST: the stroke that strikes young women after childbirth", "pillar": "clinical_advances", "keywords": ["CVST","cerebral venous sinus thrombosis"]},
    {"topic": "Bell palsy: complete recovery is possible", "pillar": "patient_education", "keywords": ["Bell palsy","facial nerve","facial palsy"]},
    {"topic": "Awake craniotomy: why we operate on the conscious brain", "pillar": "brand_authority", "keywords": ["awake craniotomy","brain mapping surgery"]},
    {"topic": "Glioblastoma 2025: new treatments changing the prognosis", "pillar": "research_news", "keywords": ["glioblastoma","GBM treatment 2025"]},
    {"topic": "Trigeminal neuralgia: the most painful condition known to medicine", "pillar": "patient_education", "keywords": ["trigeminal neuralgia","MVD surgery"]},
    {"topic": "Myelomeningocele: what parents need to know from day one", "pillar": "patient_education", "keywords": ["myelomeningocele","spina bifida"]},
    {"topic": "AI in neurosurgery: promise, reality, and caution", "pillar": "research_news", "keywords": ["AI neurosurgery","machine learning brain"]},
    {"topic": "Spinal cord injury: what neuroscience offers in 2025", "pillar": "research_news", "keywords": ["spinal cord injury","SCI rehab"]},
]

def get_topic():
    if MANUAL_TOPIC:
        return {"topic": MANUAL_TOPIC, "pillar": "patient_education", "keywords": []}
    wk = datetime.now().isocalendar()[1]
    return TOPIC_POOL[wk % len(TOPIC_POOL)]

def grok_research(topic):
    if not GROK_KEY:
        print("No Grok key - skipping")
        return ""
    print(f"GROK: {topic}")
    try:
        r = requests.post('https://api.x.ai/v1/chat/completions',
            headers={'Authorization': f'Bearer {GROK_KEY}', 'Content-Type': 'application/json'},
            json={'model':'grok-3','max_tokens':800,'temperature':0.2,
                  'messages':[{'role':'user','content':f'Research neuroscience article: "{topic}". Latest trials 2023-2026, statistics, AAN/NICE/AANS guidelines, 5 PubMed citations with PMID, Pakistan context.'}]},
            timeout=60)
        b = r.json()['choices'][0]['message']['content']
        print(f"Grok: {len(b.split())} words")
        return b
    except Exception as e:
        print(f"Grok error: {e}")
        return ""

def claude_generate(topic, pillar, keywords, grok_brief):
    if not CLAUDE_KEY:
        raise ValueError("No Claude key")
    print(f"CLAUDE: {topic}")
    research = f"\n\nGROK RESEARCH:\n{grok_brief}" if grok_brief else ""
    kw = keywords[0] if keywords else topic
    system = f"""You are the official author of The Neuro Council, writing as {AUTHOR_BRAND}.
Write authoritative, evidence-based, patient-accessible neuroscience content.
Always include: author byline, CTA ({CLINIC_CTA}), educational disclaimer.
SEO-optimised, PubMed-cited where possible."""

    prompt = f"""Write a complete SEO blog article for: **{topic}**
Primary keyword: {kw}{research}

Structure (target 1500-1800 words):
META TITLE: [60 chars, keyword first]
META DESCRIPTION: [155 chars]

# [H1 title with keyword]

## Introduction (150 words - hook with statistic or patient scenario)
## What is {topic.split(':')[0]}? (200 words - definition, pathophysiology)
## Causes and Risk Factors (150 words)
## Symptoms and Warning Signs (200 words - bold red flags)
## Diagnosis (150 words - investigations, what to expect at Faraz Hospital)
## Treatment Options (250 words - conservative to surgical, cite evidence, mention BodyTom CT and Zeiss microscope)
## Recovery and Outcomes (150 words)
## Frequently Asked Questions (5 Q&As, 200 words)
## Conclusion + Consultation CTA (100 words)

References: 6-8 PubMed citations [Author et al. Journal Year;Vol:Pages. PMID: XXXXX]

Author: {AUTHOR_BRAND}
{CLINIC_CTA}
Disclaimer: Educational content only. Consult your neurosurgeon for specific advice."""

    for attempt in range(3):
        try:
            print(f"  Claude attempt {attempt+1}/3 | timeout=180s")
            r = requests.post('https://api.anthropic.com/v1/messages',
                headers={'x-api-key':CLAUDE_KEY,'anthropic-version':'2023-06-01','Content-Type':'application/json'},
                json={
                    'model':'claude-sonnet-4-20250514',
                    'max_tokens':4096,
                    'system':system,
                    'messages':[{'role':'user','content':prompt}]
                },
                timeout=180
            )
            if r.status_code == 200:
                t = r.json()['content'][0]['text']
                print(f"Claude: {len(t.split())} words generated")
                return t
            print(f"Claude error {r.status_code}: {r.text[:200]}")
        except requests.exceptions.ReadTimeout:
            print(f"Timeout attempt {attempt+1}. Waiting 15s before retry...")
            time.sleep(15)
        except Exception as e:
            print(f"Error: {e}")
            break
    raise RuntimeError("Claude failed after 3 attempts. Check API key and status.anthropic.com")

def generate_social(topic, content):
    if not CLAUDE_KEY:
        return ""
    print("Generating social suite...")
    try:
        r = requests.post('https://api.anthropic.com/v1/messages',
            headers={'x-api-key':CLAUDE_KEY,'anthropic-version':'2023-06-01','Content-Type':'application/json'},
            json={'model':'claude-sonnet-4-20250514','max_tokens':1500,
                  'messages':[{'role':'user','content':f'Create social media posts for "{topic}".\nBased on: {content[:400]}...\n\nGenerate:\nFACEBOOK EN (180 words, end with WhatsApp +923458254232)\nFACEBOOK URDU (180 words)\nINSTAGRAM (caption + 15 hashtags)\nLINKEDIN (professional angle)'}]},
            timeout=120)
        if r.status_code == 200:
            s = r.json()['content'][0]['text']
            print(f"Social: {len(s.split())} words")
            return s
    except Exception as e:
        print(f"Social error: {e}")
    return ""

def publish_wp(title, content, status='draft', tags=None):
    if not all([WP_URL, WP_USER, WP_PASS]):
        print("WP credentials missing - saving locally only")
        return None
    try:
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = html.replace('\n\n', '</p><p>').replace('\n', '<br>')
        r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts",
            json={'title':title,'content':'<p>'+html+'</p>',
                  'status':status,'excerpt':re.sub(r'[#*_]','',content)[:155],'tags':tags or []},
            auth=(WP_USER, WP_PASS), timeout=30)
        if r.status_code in [200, 201]:
            d = r.json()
            print(f"WP published: {d.get('link','')}")
            return {'id':d.get('id'),'url':d.get('link','')}
        print(f"WP error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"WP error: {e}")
    return None

def notify_tg(topic, result, wc):
    if not TG_TOKEN or not TG_CHAT:
        return
    msg = f"Neuro Council Content Ready\nTopic: {topic}\nWords: {wc:,}\nMode: {PUBLISH_MODE}\n{datetime.now().strftime('%d %b %Y %H:%M PKT')}"
    if result:
        msg += f"\nURL: {result.get('url','')}"
    msg += f"\n\n-- drwasifmalik.com | Neuro Council"
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={'chat_id':TG_CHAT,'text':msg}, timeout=10)
        print("Telegram sent")
    except:
        pass

def main():
    print("="*60)
    print("THE NEURO COUNCIL v2.0 - Production Engine")
    print(f"{datetime.now().strftime('%A %d %B %Y %H:%M PKT')}")
    print(f"Type: {CONTENT_TYPE} | Mode: {PUBLISH_MODE}")
    print("="*60)

    td = get_topic()
    topic = td['topic']
    pillar = td.get('pillar','patient_education')
    keywords = td.get('keywords',[])
    print(f"Topic: {topic}")
    print(f"Pillar: {pillar}")

    grok_brief = grok_research(topic)

    try:
        content = claude_generate(topic, pillar, keywords, grok_brief)
    except Exception as e:
        print(f"FAILED: {e}")
        return

    wc = len(content.split())
    print(f"Generated: {wc:,} words")

    social = ""
    if CONTENT_TYPE in ['full_package','social_suite']:
        social = generate_social(topic, content)

    os.makedirs('council_output', exist_ok=True)
    ds = datetime.now().strftime('%Y%m%d_%H%M')
    st = re.sub(r'[^a-z0-9]+','-',topic.lower())[:40]
    fname = f"council_output/{ds}_{st}.md"
    with open(fname,'w',encoding='utf-8') as f:
        f.write(f"# {topic}\n\n{content}")
        if social:
            f.write(f"\n\n---\n## SOCIAL SUITE\n\n{social}")
    print(f"Saved: {fname}")

    result = publish_wp(topic, content, PUBLISH_MODE, keywords)
    notify_tg(topic, result, wc)

    print("\n"+"="*60)
    print(f"COMPLETE - {wc:,} words | Model: claude-sonnet-4-20250514 | Timeout: 180s")
    if result:
        print(f"URL: {result.get('url','')}")
    print("="*60)

if __name__ == '__main__':
    main()
