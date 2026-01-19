#!/usr/bin/env python3
"""
build_phishing_email_dataset.py

Builds phishing email training dataset with format:

sender,message_body,url,label

Rules:
- Only emails containing a URL are included
- Stops after 5000 valid rows
- Label is always 1 (phishing)

Usage:
    python build_phishing_email_dataset.py \
        --input phishing_emails_raw.csv \
        --output phishing_email_dataset.csv
"""

import argparse
import pandas as pd
import re
from pathlib import Path
from tqdm import tqdm
from email.utils import parseaddr  # <- added

URL_RE = re.compile(r"https?://[^\s\"'>]+")

def extract_first_url(text):
    if not isinstance(text, str):
        return ""
    match = URL_RE.search(text)
    return match.group(0) if match else ""

def find_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    raise ValueError(f"Could not find any of these columns: {candidates}")

def main():
    parser = argparse.ArgumentParser(description="Build phishing email dataset")
    parser.add_argument("--input", required=True, help="Raw phishing email CSV")
    parser.add_argument("--output", required=True, help="Output training CSV")
    parser.add_argument("--limit", type=int, default=5000, help="Number of phishing emails to collect")
    args = parser.parse_args()

    print(f"[+] Loading dataset: {args.input}")
    df = pd.read_csv(args.input, dtype=str).fillna("")

    sender_col = find_column(df, ["sender", "from", "email", "sender_email"])
    body_col = find_column(df, ["body", "message", "content", "email_body", "text"])

    print(f"[+] Sender column: {sender_col}")
    print(f"[+] Body column: {body_col}")
    print(f"[+] Target rows: {args.limit}")

    records = []

    print("[+] Extracting phishing emails with URLs...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        if len(records) >= args.limit:
            break

        # Extract only the email address from the sender field
        raw_sender = row[sender_col].strip()
        _, sender = parseaddr(raw_sender)
        sender = sender.lower()  # optional: normalize to lowercase

        if not sender:
            continue  # skip rows without a valid email

        body = row[body_col].strip()
        url = extract_first_url(body)

        if not url:
            continue  # discard emails without URLs

        records.append({
            "sender": sender,
            "message_body": body,
            "url": url,
            "label": 1
        })

    if len(records) < args.limit:
        print(f"[!] Warning: Only found {len(records)} emails with URLs")

    out_df = pd.DataFrame(records)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)

    print("\n=== Dataset Build Complete ===")
    print(f"Rows written: {len(out_df)}")
    print(f"Output file: {out_path}")

if __name__ == "__main__":
    main()
