#!/usr/bin/env python3
"""
download_urls.py

Downloads phishing URLs from PhishTank and legitimate domains from Tranco,
then exports three sets of CSVs:
  - phishing_urls.csv
  - legitimate_urls.csv
  - all_urls.csv

Each set is stored in its own subdirectory under the output folder.

USAGE:
  python download_urls.py --phish 500 --legit 500 --sets 3 --outdir ./output

Dependencies:
  pip install requests pandas tqdm
"""

import argparse
import csv
import io
import os
import random
import re
import zipfile
from collections import OrderedDict

import pandas as pd
import requests
from tqdm import tqdm

# ------------------- CONFIG -------------------
DEFAULT_CONFIG = {
    "phish_feeds": [
        "https://data.phishtank.com/data/online-valid.csv"
    ],
    "legit_feeds": [
        "https://tranco-list.eu/top-1m.csv.zip"
    ],
    "user_agent": "url-collector/1.1 (+https://example.com)",
    "timeout": 20,
    "max_retries": 3,
}

URL_RE = re.compile(r"https?://[^\s,'\"]+", re.IGNORECASE)


# ------------------- HELPERS -------------------
def fetch_text(url, timeout=20, headers=None):
    """GET text content with simple retries."""
    headers = headers or {}
    for _ in range(DEFAULT_CONFIG["max_retries"]):
        try:
            r = requests.get(url, timeout=timeout, headers=headers)
            r.raise_for_status()
            r.encoding = r.encoding or "utf-8"
            return r.text
        except Exception as e:
            last_exc = e
    raise last_exc


def parse_phishtank_csv(text):
    """Parse a PhishTank CSV to extract URLs."""
    urls = []
    f = io.StringIO(text)
    reader = csv.DictReader(f)
    if "url" in reader.fieldnames:
        for row in reader:
            url = row.get("url")
            if url:
                urls.append(url.strip())
    else:
        for m in URL_RE.finditer(text):
            urls.append(m.group(0))
    return urls


def parse_plain_feed(text):
    """Parse plaintext feed (e.g. OpenPhish)."""
    urls = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("http://") or line.startswith("https://"):
            urls.append(line)
        else:
            m = URL_RE.search(line)
            if m:
                urls.append(m.group(0))
    return urls


def parse_top1m_domains(text):
    """Parse top-1m CSV and return full URLs (https://domain/)."""
    urls = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(',')
        domain = parts[-1].strip()
        if re.match(r"^[A-Za-z0-9\-\.]+\.[A-Za-z]{2,}$", domain):
            urls.append("https://" + domain)
    return urls


def collect_from_feed(url, kind="phish"):
    """Download and parse feed depending on kind ('phish' | 'legit')."""
    headers = {"User-Agent": DEFAULT_CONFIG["user_agent"]}
    try:
        print(f"Fetching {url} ...")
        r = requests.get(url, timeout=DEFAULT_CONFIG["timeout"], headers=headers, stream=True)
        r.raise_for_status()

        if kind == "legit" and url.endswith(".zip"):
            # Handle Tranco zipped CSV
            z = zipfile.ZipFile(io.BytesIO(r.content))
            name = z.namelist()[0]
            with z.open(name) as f:
                text = f.read().decode("utf-8", errors="ignore")
            domains = parse_top1m_domains(text)
            print(f"  -> Parsed {len(domains)} domains from Tranco ZIP")
            return domains

        elif kind == "phish":
            text = r.text
            low = text.lower()
            first = low.splitlines()[0] if low.splitlines() else ""
            if "url" in first or ",url" in low[:2000]:
                return [u.strip() for u in parse_phishtank_csv(text) if u.strip()]
            else:
                return parse_plain_feed(text)

        else:
            text = r.text
            return parse_top1m_domains(text)

    except Exception as e:
        print(f"  -> Failed to fetch {url}: {e}")
        return []


def gather_urls(phish_feeds, legit_feeds, needed_phish, needed_legit):
    """Fetch and combine phishing + legit URLs."""
    phish_set = OrderedDict()
    legit_set = OrderedDict()

    # --- phishing ---
    for feed in phish_feeds:
        found = collect_from_feed(feed, kind="phish")
        for u in found:
            phish_set[u] = feed
        if len(phish_set) >= needed_phish:
            break

    # --- legitimate ---
    for feed in legit_feeds:
        found = collect_from_feed(feed, kind="legit")
        for u in found:
            if u not in phish_set:
                legit_set[u] = feed
        if len(legit_set) >= needed_legit:
            break

    phish_list = list(phish_set.keys())
    legit_list = list(legit_set.keys())

    random.shuffle(phish_list)
    random.shuffle(legit_list)

    return phish_list[:needed_phish], legit_list[:needed_legit], phish_set, legit_set


def save_csv(urls, sources_map, outpath, label=None):
    """Save URLs to CSV."""
    rows = []
    for u in urls:
        rows.append({"url": u, "source_feed": sources_map.get(u, ""), "label": label})
    df = pd.DataFrame(rows)
    df.to_csv(outpath, index=False)
    return df


# ------------------- MAIN -------------------
def main():
    parser = argparse.ArgumentParser(description="Collect phishing and legitimate URLs.")
    parser.add_argument("--phish", type=int, default=500)
    parser.add_argument("--legit", type=int, default=500)
    parser.add_argument("--sets", type=int, default=3)
    parser.add_argument("--outdir", default="./output")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    for i in range(1, args.sets + 1):
        print(f"\n=== Collecting Set {i} ===")

        # Create subdirectory for this set
        set_dir = os.path.join(args.outdir, f"set{i}")
        os.makedirs(set_dir, exist_ok=True)

        phish_urls, legit_urls, phish_map, legit_map = gather_urls(
            DEFAULT_CONFIG["phish_feeds"],
            DEFAULT_CONFIG["legit_feeds"],
            args.phish,
            args.legit
        )

        phishing_csv = os.path.join(set_dir, "phishing_urls.csv")
        legitimate_csv = os.path.join(set_dir, "legitimate_urls.csv")
        combined_csv = os.path.join(set_dir, "all_urls.csv")

        df_phish = save_csv(phish_urls, phish_map, phishing_csv, "phishing")
        df_legit = save_csv(legit_urls, legit_map, legitimate_csv, "legitimate")
        df_combined = pd.concat([df_phish, df_legit], ignore_index=True)
        df_combined.to_csv(combined_csv, index=False)

        print(f"[Set {i}] {len(df_phish)} phishing + {len(df_legit)} legitimate URLs written in {set_dir}")

    print("\nAll sets completed successfully.")


if __name__ == "__main__":
    main()
