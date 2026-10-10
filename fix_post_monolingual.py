#!/usr/bin/env python3
"""One-shot: strip Arabic-script mashup from a WP post_content (EN must stay monolingual)."""
import os
import re
import sys

import requests
from requests.auth import HTTPBasicAuth

WP_URL = os.environ.get("WP_URL", "https://drwasifmalik.com").rstrip("/")
WP_USER = os.environ.get("WP_USERNAME", "")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")
POST_ID = int(os.environ.get("FIX_POST_ID", sys.argv[1] if len(sys.argv) > 1 else "0"))


def main():
    if not POST_ID or not all([WP_URL, WP_USER, WP_PASS]):
        print("ERROR: need FIX_POST_ID / WP credentials")
        sys.exit(1)
    auth = HTTPBasicAuth(WP_USER, WP_PASS)
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}", auth=auth, timeout=45, params={"context": "edit"})
    r.raise_for_status()
    data = r.json()
    content = data.get("content", {}).get("raw") or data.get("content", {}).get("rendered") or ""
    before = len(content)
    # Drop Arabic-script runs (Urdu/Arabic mashup) from EN body.
    cleaned = re.sub(r"\s*[\u0600-\u06FF][\u0600-\u06FF\s\W\d]*", "", content, flags=re.UNICODE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip() + "\n"
    still = bool(re.search(r"[\u0600-\u06FF]", cleaned))
    print(f"post={POST_ID} before={before} after={len(cleaned)} arabic_still={'Y' if still else 'N'}")
    if cleaned == content:
        print("NO_CHANGE")
        return
    u = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
        auth=auth,
        json={"content": cleaned},
        timeout=45,
    )
    print(f"UPDATE HTTP {u.status_code}")
    u.raise_for_status()
    # Confirm meta i18n still present
    m = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
        auth=auth,
        timeout=45,
        params={"context": "edit"},
    )
    meta = m.json().get("meta") or {}
    print(
        "meta ur=",
        "yes" if meta.get("_dwf_nn_body_ur") else "no",
        "ar=",
        "yes" if meta.get("_dwf_nn_body_ar") else "no",
        "nn=",
        "yes" if meta.get("_dwf_nn_generated") else "no",
    )


if __name__ == "__main__":
    main()
