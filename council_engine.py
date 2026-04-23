#!/usr/bin/env python3
"""
THE NEURO COUNCIL v2.5 FINAL
Dr. Wasif Rizwan Malik | PMDC 47983-P | drwasifmalik.com
Best of v2.2 + v2.5: PMID verify, model fallback, optional Gmail, secure
"""

import os
import re
import sys
import time
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

import requests
from requests.auth import HTTPBasicAuth


CLAUDE_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not CLAUDE_KEY:
    print("ERROR: ANTHROPIC_API_KEY required")
    sys.exit(1)

GROK_KEY = os.environ.get("GROK_API_KEY", "")
WP_URL = os.environ.get("WP_URL", "https://drwasifmalik.com").rstrip("/")
WP_USER = os.environ.get("WP_USERNAME", "")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_APP_PASSWORD", "")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
MANUAL_TOPIC = os.environ.get("MANUAL_TOPIC", "")
PUBLISH_MODE = os.environ.get("PUBLISH_MODE", "draft")
DRY_RUN = "--dry-run" in sys.argv

AUTHOR = (
    "Dr. Wasif Rizwan Malik | MBBS, FCPS (Neurosurgery) | PMDC 47983-P | "
    "Consultant Neurosurgeon, Faraz Hospital, Dubai Mahal Chowk, Bahawalpur"
)
CTA = "Book Consultation: WhatsApp +923458254232 | Faraz Hospital, Bahawalpur"

MODELS = [
    "claude-sonnet-4-20250514",
    "claude-sonnet-4",
    "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet-20241022",
]

TOPICS = [
    {"t": "How to find the best neurosurgeon in Pakistan", "k": "best neurosurgeon Pakistan Bahawalpur"},
    {"t": "Brain tumor symptoms you must not ignore", "k": "brain tumor warning signs symptoms"},
    {"t": "When to go to emergency for neurological symptoms", "k": "neurosurgery emergency red flags"},
    {"t": "Spine surgery recovery: what to expect", "k": "spine surgery recovery timeline"},
    {"t": "Epilepsy first aid: what to do during a seizure", "k": "epilepsy first aid seizure"},
    {"t": "How to prepare for FCPS neurosurgery exams", "k": "FCPS neurosurgery preparation"},
    {"t": "Latest advances in minimally invasive spine surgery", "k": "MISS minimally invasive spine surgery"},
    {"t": "Role of intraoperative MRI in brain tumor surgery", "k": "intraoperative iMRI brain tumor"},
    {"t": "Management of acute ischemic stroke", "k": "acute stroke management protocol"},
    {"t": "Spinal cord injury emergency protocol", "k": "spinal cord injury emergency"},
    {"t": "Lumbar disc herniation: when to operate and when to wait", "k": "lumbar disc Pakistan"},
    {"t": "Brain tumour: the headache you must not ignore", "k": "brain tumour Pakistan"},
    {"t": "Cervical myelopathy: the silent killer of hand function", "k": "cervical myelopathy"},
    {"t": "Epilepsy surgery: when medications fail", "k": "epilepsy surgery"},
    {"t": "Brain aneurysm: the worst headache of your life", "k": "brain aneurysm"},
    {"t": "Carpal tunnel syndrome explained", "k": "carpal tunnel Pakistan"},
    {"t": "Hydrocephalus: the treatable cause of dementia", "k": "hydrocephalus VP shunt"},
    {"t": "BodyTom intraoperative CT: surgical precision redefined", "k": "BodyTom intraoperative CT"},
    {"t": "Pituitary adenoma: the tumour behind hormonal chaos", "k": "pituitary tumour Pakistan"},
    {"t": "Parkinson disease: from diagnosis to deep brain stimulation", "k": "Parkinson disease Pakistan"},
    {"t": "CVST: the stroke that strikes young women after childbirth", "k": "CVST postpartum stroke"},
    {"t": "Bell palsy: complete recovery is possible", "k": "Bell palsy facial nerve"},
    {"t": "Awake craniotomy: why we operate on the conscious brain", "k": "awake craniotomy Pakistan"},
    {"t": "Glioblastoma 2025: new hope and new treatments", "k": "glioblastoma treatment 2025"},
    {"t": "Trigeminal neuralgia: the most painful condition known", "k": "trigeminal neuralgia MVD"},
    {"t": "Myelomeningocele: what parents must know from day one", "k": "myelomeningocele spina bifida"},
    {"t": "AI in neurosurgery: promise, reality, and caution", "k": "AI neurosurgery Pakistan"},
    {"t": "Spinal cord injury 2025: what neuroscience offers", "k": "spinal cord injury rehab"},
]


def get_topic():
    if MANUAL_TOPIC:
        return {"t": MANUAL_TOPIC, "k": MANUAL_TOPIC}
    return TOPICS[datetime.now().isocalendar()[1] % len(TOPICS)]


def verify_wp():
    if not all([WP_URL, WP_USER, WP_PASS]):
        return False, f"Missing: USER={bool(WP_USER)} PASS={bool(WP_PASS)}"
    try:
        response = requests.get(
            f"{WP_URL}/wp-json/wp/v2/posts?per_page=1",
            auth=HTTPBasicAuth(WP_USER, WP_PASS),
            timeout=15,
        )
        return response.status_code == 200, f"HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)


def verify_pmid(pmid):
    pmid = re.sub(r"[^\d]", "", str(pmid))
    if not pmid or len(pmid) < 5:
        return False
    try:
        response = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params={"db": "pubmed", "id": pmid, "retmode": "json"},
            timeout=10,
        )
        data = response.json()
        return pmid in data.get("result", {}) and "error" not in data["result"].get(pmid, {})
    except Exception:
        return False


def clean_pmids(content):
    pmids = re.findall(r"PMID[:\s]*?(\d{5,9})", content, re.IGNORECASE)
    for pmid in pmids:
        if not verify_pmid(pmid):
            content = re.sub(
                rf"PMID[:\s]*?{pmid}",
                "[PMID removed - unverified]",
                content,
                flags=re.IGNORECASE,
            )
            print(f"  Removed unverified PMID: {pmid}")
    return content


def grok_research(topic):
    if not GROK_KEY:
        print("No Grok key")
        return ""
    print(f"GROK: {topic}")
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-3",
                "max_tokens": 600,
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f'Research "{topic}": key stats, AAN/NICE/AANS guidelines, '
                            "3 real PubMed PMIDs, Pakistan context. 400 words max."
                        ),
                    }
                ],
            },
            timeout=60,
        )
        response.raise_for_status()
        brief = response.json()["choices"][0]["message"]["content"]
        print(f"Grok: {len(brief.split())}w")
        return brief
    except Exception as exc:
        print(f"Grok error: {exc}")
        return ""


def claude_generate(topic, keyword, brief):
    research = f"\n\nGROK RESEARCH:\n{brief}" if brief else ""
    system_prompt = (
        f"You are author of The Neuro Council, writing as {AUTHOR}. "
        "Write authoritative, evidence-based, SEO-optimised neuroscience content. "
        f"Always include author byline and CTA: {CTA}. "
        "Only cite PubMed references you are CERTAIN exist - never fabricate PMIDs. "
        "Educational disclaimer required."
    )
    user_prompt = f"""Write complete SEO blog article: **{topic}**
Keyword: {keyword}{research}

Structure (1500w):
META TITLE: [60 chars]
META DESCRIPTION: [155 chars]
# [H1]
## Introduction (150w - real statistic hook)
## What is it? (200w)
## Causes (150w)
## Symptoms - bold red flags (200w)
## Diagnosis at Faraz Hospital (150w)
## Treatment - cite evidence, mention BodyTom CT + Zeiss microscope (250w)
## Recovery (150w)
## FAQ 5 questions (200w)
## Conclusion + CTA (100w)
References: ONLY include if 100% certain they exist.
Author: {AUTHOR} | {CTA} | Disclaimer: Educational only."""

    for model in MODELS:
        for attempt in range(2):
            try:
                print(f"CLAUDE: {model} attempt {attempt + 1}")
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": CLAUDE_KEY,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "max_tokens": 4096,
                        "system": system_prompt,
                        "messages": [{"role": "user", "content": user_prompt}],
                    },
                    timeout=180,
                )
                if response.status_code == 200:
                    text = response.json()["content"][0]["text"]
                    print(f"SUCCESS: {len(text.split())}w | {model}")
                    return clean_pmids(text)

                print(f"Error {response.status_code}: {response.text[:150]}")
                if response.status_code in [400, 404]:
                    break
            except requests.exceptions.ReadTimeout:
                print("Timeout, retrying...")
                time.sleep(10)
            except Exception as exc:
                print(f"ERR: {exc}")
                break

    print("ERROR: All Claude models failed")
    sys.exit(1)


def to_html(content):
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", content, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    return "<p>" + html.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"


def publish_wp(title, content, status="draft"):
    ok, message = verify_wp()
    if not ok:
        print(f"WP FAILED: {message} | USER={WP_USER} PASS_LEN={len(WP_PASS)}")
        return None
    print(f"WP OK: {message}")

    try:
        response = requests.post(
            f"{WP_URL}/wp-json/wp/v2/posts",
            json={
                "title": title,
                "content": to_html(content),
                "status": status,
                "excerpt": re.sub(r"[#*_]", "", content)[:155],
            },
            auth=HTTPBasicAuth(WP_USER, WP_PASS),
            timeout=30,
        )
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"WP {status}: {data.get('link', '')}")
            return data
        print(f"WP error {response.status_code}: {response.text[:300]}")
    except Exception as exc:
        print(f"WP error: {exc}")
    return None


def notify(subject, body):
    if GMAIL_USER and GMAIL_PASS:
        try:
            msg = MIMEText(body)
            msg["Subject"], msg["From"], msg["To"] = subject, GMAIL_USER, GMAIL_USER
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(GMAIL_USER, GMAIL_PASS)
                smtp.send_message(msg)
            print("Gmail sent")
        except Exception as exc:
            print(f"Gmail error: {exc}")

    if TG_TOKEN and TG_CHAT:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                json={"chat_id": TG_CHAT, "text": body},
                timeout=10,
            )
            print("Telegram sent")
        except Exception:
            pass


def main():
    print("=" * 55)
    print("THE NEURO COUNCIL v2.5 FINAL")
    print(datetime.now().strftime("%A %d %B %Y %H:%M PKT"))
    print(f"Mode: {PUBLISH_MODE}")
    print(f"Dry Run: {DRY_RUN}")
    print("=" * 55)

    topic_data = get_topic()
    topic, keyword = topic_data["t"], topic_data["k"]
    print(f"Topic: {topic}")

    brief = grok_research(topic)
    content = claude_generate(topic, keyword, brief)

    word_count = len(content.split())
    print(f"Generated: {word_count:,}w")

    os.makedirs("council_output", exist_ok=True)
    date_stamp = datetime.now().strftime("%Y%m%d_%H%M")
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:40]
    filename = f"council_output/{date_stamp}_{slug}.md"

    with open(filename, "w", encoding="utf-8") as output_file:
        output_file.write(f"# {topic}\n\n{content}")
    print(f"Saved: {filename}")

    if DRY_RUN:
        print("DRY RUN enabled: skipping WordPress publish and notifications.")
        result = None
        url = "dry-run (not published)"
    else:
        result = publish_wp(topic, content, PUBLISH_MODE)
        url = result.get("link", "") if result else "not published"
        notify(
            f"Neuro Council: {topic}",
            f"Topic: {topic}\nWords: {word_count:,}\nMode: {PUBLISH_MODE}\nURL: {url}",
        )

    print("=" * 55)
    print(f"DONE - {word_count:,}w | {url}")
    print("=" * 55)


if __name__ == "__main__":
    main()
