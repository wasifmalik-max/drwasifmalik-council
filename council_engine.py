#!/usr/bin/env python3
"""
THE NEURO COUNCIL v2.6 STABLE
Dr. Wasif Rizwan Malik | PMDC 47983-P | drwasifmalik.com
Adds: WP timeout + retry + preflight checks + dry-run
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


# -------------------- ENV --------------------
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
PUBLISH_MODE = os.environ.get("PUBLISH_MODE", "draft").lower()

# Runtime flags
DRY_RUN = "--dry-run" in sys.argv

# WP reliability knobs (optional env overrides)
WP_VERIFY_TIMEOUT = int(os.environ.get("WP_VERIFY_TIMEOUT", "45"))
WP_PUBLISH_TIMEOUT = int(os.environ.get("WP_PUBLISH_TIMEOUT", "60"))
WP_VERIFY_RETRIES = int(os.environ.get("WP_VERIFY_RETRIES", "2"))
WP_PUBLISH_RETRIES = int(os.environ.get("WP_PUBLISH_RETRIES", "2"))
WP_RETRY_SLEEP = int(os.environ.get("WP_RETRY_SLEEP", "8"))

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


def preflight():
    print(f"CWD: {os.getcwd()}")
    print(f"SCRIPT: {os.path.abspath(__file__)}")
    print(f"WP_URL: {WP_URL}")
    print(f"WP_USER set: {bool(WP_USER)} | WP_PASS set: {bool(WP_PASS)}")
    print(f"Dry Run: {DRY_RUN}")

    if not WP_URL.startswith("http"):
        print("ERROR: WP_URL must start with http/https")
        sys.exit(1)

    os.makedirs("council_output", exist_ok=True)


def get_topic():
    if MANUAL_TOPIC:
        return {"t": MANUAL_TOPIC, "k": MANUAL_TOPIC}
    return TOPICS[datetime.now().isocalendar()[1] % len(TOPICS)]


def verify_wp():
    if not all([WP_URL, WP_USER, WP_PASS]):
        return False, f"Missing: USER={bool(WP_USER)} PASS={bool(WP_PASS)}"

    last_error = "unknown"
    for attempt in range(1, WP_VERIFY_RETRIES + 1):
        try:
            r = requests.get(
                f"{WP_URL}/wp-json/wp/v2/posts?per_page=1",
                auth=HTTPBasicAuth(WP_USER, WP_PASS),
                timeout=WP_VERIFY_TIMEOUT,
            )
            if r.status_code == 200:
                return True, f"HTTP 200 (attempt {attempt})"

            last_error = f"HTTP {r.status_code}"
            print(f"WP verify attempt {attempt} failed: {last_error}")
        except Exception as exc:
            last_error = str(exc)
            print(f"WP verify attempt {attempt} exception: {last_error}")

        if attempt < WP_VERIFY_RETRIES:
            time.sleep(WP_RETRY_SLEEP)

    return False, last_error


def verify_pmid(pmid):
    pmid = re.sub(r"[^\d]", "", str(pmid))
    if not pmid or len(pmid) < 5:
        return False
    try:
        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params={"db": "pubmed", "id": pmid, "retmode": "json"},
            timeout=10,
        )
        data = r.json()
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
            print(f"Removed unverified PMID: {pmid}")
    return content


def grok_research(topic):
    if not GROK_KEY:
        print("No Grok key")
        return ""
    print(f"GROK: {topic}")
    try:
        r = requests.post(
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
        r.raise_for_status()
        brief = r.json()["choices"][0]["message"]["content"]
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
                r = requests.post(
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
                if r.status_code == 200:
                    text = r.json()["content"][0]["text"]
                    print(f"SUCCESS: {len(text.split())}w | {model}")
                    return clean_pmids(text)

                print(f"Error {r.status_code}: {r.text[:150]}")
                if r.status_code in (400, 404):
                    break
            except requests.exceptions.ReadTimeout:
                print("Claude timeout, retrying...")
                time.sleep(10)
            except Exception as exc:
                print(f"Claude error: {exc}")
                break

    print("ERROR: All Claude models failed")
    sys.exit(1)


def to_html(content):
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", content, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    return "<p>" + html.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"


def publish_wp(title, content, status="draft"):
    ok, msg = verify_wp()
    if not ok:
        print(f"WP FAILED precheck: {msg} | USER={WP_USER} PASS_LEN={len(WP_PASS)}")
        return None

    print(f"WP precheck OK: {msg}")
    payload = {
        "title": title,
        "content": to_html(content),
        "status": status if status in {"draft", "publish"} else "draft",
        "excerpt": re.sub(r"[#*_]", "", content)[:155],
    }

    for attempt in range(1, WP_PUBLISH_RETRIES + 1):
        try:
            r = requests.post(
                f"{WP_URL}/wp-json/wp/v2/posts",
                json=payload,
                auth=HTTPBasicAuth(WP_USER, WP_PASS),
                timeout=WP_PUBLISH_TIMEOUT,
            )
            if r.status_code in (200, 201):
                data = r.json()
                print(f"WP {payload['status']} success (attempt {attempt}): {data.get('link', '')}")
                return data

            print(f"WP publish attempt {attempt} HTTP {r.status_code}: {r.text[:250]}")
        except Exception as exc:
            print(f"WP publish attempt {attempt} exception: {exc}")

        if attempt < WP_PUBLISH_RETRIES:
            time.sleep(WP_RETRY_SLEEP)

    return None


def notify(subject, body):
    if GMAIL_USER and GMAIL_PASS:
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = GMAIL_USER
            msg["To"] = GMAIL_USER
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
                timeout=12,
            )
            print("Telegram sent")
        except Exception as exc:
            print(f"Telegram error: {exc}")


def main():
    print("=" * 60)
    print("THE NEURO COUNCIL v2.6 STABLE")
    print(datetime.now().strftime("%A %d %B %Y %H:%M PKT"))
    print(f"Mode: {PUBLISH_MODE}")
    print("=" * 60)

    preflight()

    td = get_topic()
    topic, keyword = td["t"], td["k"]
    print(f"Topic: {topic}")

    brief = grok_research(topic)
    content = claude_generate(topic, keyword, brief)

    wc = len(content.split())
    print(f"Generated: {wc:,}w")

    ds = datetime.now().strftime("%Y%m%d_%H%M")
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:40]
    fname = f"council_output/{ds}_{slug}.md"

    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n{content}")
    print(f"Saved: {fname}")

    if DRY_RUN:
        print("DRY RUN enabled: skipping WordPress publish and notifications.")
        url = "dry-run (not published)"
    else:
        result = publish_wp(topic, content, PUBLISH_MODE)
        url = result.get("link", "") if result else "not published"
        notify(
            f"Neuro Council: {topic}",
            f"Topic: {topic}\nWords: {wc:,}\nMode: {PUBLISH_MODE}\nURL: {url}",
        )

    print("=" * 60)
    print(f"DONE - {wc:,}w | {url}")
    print("=" * 60)


if __name__ == "__main__":
    main()
