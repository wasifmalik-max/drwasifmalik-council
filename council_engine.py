#!/usr/bin/env python3
"""
THE NEURO COUNCIL - Python Content Engine
Dr. Wasif Rizwan Malik | PMDC 47983-P | drwasifmalik.com
Claude + Grok automated neuroscience publishing pipeline
"""
import os, json, requests, re
from datetime import datetime

CLAUDE_KEY   = os.environ.get('ANTHROPIC_API_KEY','')
GROK_KEY     = os.environ.get('GROK_API_KEY','')
WP_URL       = os.environ.get('WP_URL','https://drwasifmalik.com')
WP_USER      = os.environ.get('WP_USERNAME','')
WP_PASS      = os.environ.get('WP_APP_PASSWORD','')
TG_TOKEN     = os.environ.get('TELEGRAM_BOT_TOKEN','')
TG_CHAT      = os.environ.get('TELEGRAM_CHAT_ID','')
MANUAL_TOPIC = os.environ.get('MANUAL_TOPIC','')
CONTENT_TYPE = os.environ.get('CONTENT_TYPE','full_package')
PUBLISH_MODE = os.environ.get('PUBLISH_MODE','draft')

AUTHOR_BRAND = "Dr. Wasif Rizwan Malik | MBBS, FCPS (Neurosurgery) | PMDC 47983-P | Consultant Neurosurgeon, Faraz Hospital, Dubai Mahal Chowk, Bahawalpur"

TOPIC_POOL = [
  {"topic": "Lumbar disc herniation: when to operate and when to wait", "pillar": "patient_education", "keywords": ["lumbar disc","slipped disc","back surgery Pakistan"]},
  {"topic": "Brain tumour diagnosis: the headache you must not ignore", "pillar": "patient_education", "keywords": ["brain tumour symptoms","brain cancer Pakistan"]},
  {"topic": "Cervical myelopathy: the silent killer of hand function", "pillar": "clinical_advances", "keywords": ["cervical myelopathy","neck surgery","hand weakness"]},
  {"topic": "Epilepsy surgery: when medications fail", "pillar": "clinical_advances", "keywords": ["epilepsy surgery","refractory epilepsy","seizure surgery Pakistan"]},
  {"topic": "Brain aneurysm: understanding the worst headache of your life", "pillar": "patient_education", "keywords": ["brain aneurysm","subarachnoid haemorrhage"]},
  {"topic": "Carpal tunnel syndrome: the wrist problem explained", "pillar": "patient_education", "keywords": ["carpal tunnel","wrist pain","hand numbness"]},
  {"topic": "Hydrocephalus in adults: the treatable cause of dementia", "pillar": "patient_education", "keywords": ["hydrocephalus","water on brain","VP shunt"]},
  {"topic": "Intraoperative CT scanning: how BodyTom changed surgical precision", "pillar": "brand_authority", "keywords": ["intraoperative CT","BodyTom","brain imaging surgery"]},
  {"topic": "Pituitary adenoma: the tumour hiding behind hormonal chaos", "pillar": "patient_education", "keywords": ["pituitary tumour","pituitary adenoma","endonasal surgery"]},
  {"topic": "Parkinson's disease: from diagnosis to deep brain stimulation", "pillar": "patient_education", "keywords": ["Parkinson disease Pakistan","DBS tremor"]},
  {"topic": "Spinal cord injury: what neuroscience offers in 2025", "pillar": "research_news", "keywords": ["spinal cord injury","SCI rehab","neurorehabilitation"]},
  {"topic": "CVST: the stroke that strikes young women after childbirth", "pillar": "clinical_advances", "keywords": ["CVST","cerebral venous sinus thrombosis","postpartum stroke"]},
  {"topic": "Bell's palsy: complete recovery is possible", "pillar": "patient_education", "keywords": ["Bell palsy","facial nerve","facial palsy"]},
  {"topic": "Awake craniotomy: why we operate on the conscious brain", "pillar": "brand_authority", "keywords": ["awake craniotomy","brain mapping surgery"]},
  {"topic": "Glioblastoma 2025: new treatments changing the prognosis", "pillar": "research_news", "keywords": ["glioblastoma","GBM treatment 2025","brain cancer survival"]},
  {"topic": "Trigeminal neuralgia: the most painful condition known to medicine", "pillar": "patient_education", "keywords": ["trigeminal neuralgia","facial pain","MVD surgery"]},
  {"topic": "Myelomeningocele: what parents need to know from day one", "pillar": "patient_education", "keywords": ["myelomeningocele","spina bifida","MMC Pakistan"]},
  {"topic": "AI in neurosurgery: promise, reality, and caution", "pillar": "research_news", "keywords": ["AI neurosurgery","machine learning brain"]},
]

def get_topic():
    if MANUAL_TOPIC:
        return {"topic": MANUAL_TOPIC, "pillar": "patient_education", "keywords": []}
    wk = datetime.now().isocalendar()[1]
    return TOPIC_POOL[wk % len(TOPIC_POOL)]

def grok_research(topic):
    if not GROK_KEY: return ""
    print(f"Grok researching: {topic}")
    prompt = f'Research for neuroscience article: "{topic}". Provide: latest trials (2023-2026), key statistics, current guidelines (AAN/NICE/AANS), 5 PubMed citations with PMID, Pakistan-specific context. 500 words max.'
    try:
        r = requests.post('https://api.x.ai/v1/chat/completions',
            headers={'Authorization': f'Bearer {GROK_KEY}', 'Content-Type': 'application/json'},
            json={'model':'grok-3','max_tokens':800,'temperature':0.2,'messages':[{'role':'user','content':prompt}]},timeout=30)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Grok error: {e}"); return ""

def claude_generate(topic, pillar, keywords, grok_brief):
    if not CLAUDE_KEY: raise ValueError("No Claude key")
    print(f"Claude generating: {topic}")
    research = f"\n\nGROK RESEARCH:\n{grok_brief}" if grok_brief else ""
    seo = f"\nPrimary keyword: {keywords[0] if keywords else topic}"
    system = f"""You are The Neuro Council author — writing as Dr. Wasif Rizwan Malik, MBBS FCPS (Neurosurgery) PMDC 47983-P, Consultant Neurosurgeon, Faraz Hospital, Dubai Mahal Chowk, Bahawalpur, Pakistan.
Write authoritative, evidence-based, patient-accessible neuroscience content. Every piece must include:
- Author byline: {AUTHOR_BRAND}
- CTA: Book consultation WhatsApp +923458254232
- Disclaimer: Educational content only
SEO-optimised, PubMed-cited, bilingual English and Urdu where indicated."""
    
    prompt = f"""Write FULL CONTENT PACKAGE for: **{topic}**{research}{seo}

PART 1 - BLOG ARTICLE (1800+ words, SEO):
META TITLE: [60 chars, keyword first]
META DESCRIPTION: [155 chars]
# [H1 title]
## Introduction | ## What is it | ## Causes | ## Symptoms | ## Diagnosis | ## Treatment | ## Recovery | ## FAQ | ## Conclusion + CTA
References: [8 PubMed citations]

PART 2 - PATIENT GUIDE ENGLISH (400 words)
PART 3 - PATIENT GUIDE URDU NASTALIQ (400 words)
PART 4 - YOUTUBE SCRIPT (600 words outline)
PART 5 - CME SUMMARY for doctors (300 words, evidence-graded)

Author: {AUTHOR_BRAND}
Book: WhatsApp +923458254232 | Faraz Hospital Bahawalpur"""
    
    r = requests.post('https://api.anthropic.com/v1/messages',
        headers={'x-api-key':CLAUDE_KEY,'anthropic-version':'2023-06-01','Content-Type':'application/json'},
        json={'model':'claude-sonnet-4-20250514','max_tokens':4096,'system':system,'messages':[{'role':'user','content':prompt}]},
        timeout=60)
    return r.json()['content'][0]['text']

def publish_wp(title, content, status='draft', tags=None):
    if not all([WP_URL, WP_USER, WP_PASS]): return None
    clean = re.sub(r'[*_#`]|={3,}','',content)
    meta = clean[:155]
    html = content.replace('\n\n','</p><p>').replace('\n','<br>')
    html = re.sub(r'^#{1}\s+(.+)$',r'<h1>\1</h1>',html,flags=re.MULTILINE)
    html = re.sub(r'^#{2}\s+(.+)$',r'<h2>\1</h2>',html,flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',html)
    try:
        r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts",
            json={'title':title,'content':'<p>'+html+'</p>','status':status,'excerpt':meta,'tags':tags or []},
            auth=(WP_USER, WP_PASS), timeout=30)
        d = r.json()
        if r.status_code in [200,201]: return {'id':d['id'],'url':d.get('link','')}
    except Exception as e: print(f"WP error: {e}")
    return None

def notify_tg(topic, result, wc):
    if not TG_TOKEN or not TG_CHAT: return
    msg = f"Neuro Council Session Complete\n\nTopic: {topic}\nWords: {wc:,}\nStatus: {PUBLISH_MODE}"
    if result: msg += f"\nURL: {result.get('url','')}"
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={'chat_id':TG_CHAT,'text':msg},timeout=10)
    except: pass

def main():
    print("THE NEURO COUNCIL - Session Starting")
    print(f"Date: {datetime.now().strftime('%A %d %B %Y %H:%M')}")
    td = get_topic()
    topic = td['topic']; pillar = td.get('pillar','patient_education'); keywords = td.get('keywords',[])
    print(f"Topic: {topic}")
    grok_brief = grok_research(topic)
    content = claude_generate(topic, pillar, keywords, grok_brief)
    wc = len(content.split())
    print(f"Generated: {wc} words")
    os.makedirs('council_output', exist_ok=True)
    with open(f"council_output/{datetime.now().strftime('%Y%m%d')}.md",'w') as f: f.write(content)
    result = publish_wp(topic, content, PUBLISH_MODE, keywords)
    notify_tg(topic, result, wc)
    print(f"Complete. URL: {result.get('url','') if result else 'saved locally'}")

if __name__ == '__main__':
    main()
