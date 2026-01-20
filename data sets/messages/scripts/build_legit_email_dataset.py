#!/usr/bin/env python3
"""
build_legit_email_dataset.py

Builds legitimate email training dataset with format:

sender,message_body,url,flag

Rules:
- Only emails containing a URL are included
- Stops after 5000 valid rows
- Flag is always 0 (legitimate)

Usage:
    python build_legit_email_dataset.py \
        --input legit_emails_raw.csv \
        --output legit_emails_with_urls.csv
"""

import argparse
import pandas as pd
import re
from pathlib import Path
from tqdm import tqdm
from email.utils import parseaddr

URL_RE = re.compile(r"https?://[^\s\"'>]+")

def extract_first_url(text):
    if not isinstance(text, str):
        return ""
    match = URL_RE.search(text)
    return match.group(0) if match else ""

def extract_sender_from_message(message_text):
    """Extract sender from email message body."""
    if not isinstance(message_text, str):
        return ""
    
    for line in message_text.split('\n'):
        if line.lower().startswith('from:'):
            sender = line[5:].strip()
            _, email = parseaddr(sender)
            if email:
                return email.lower()
            # If parseaddr didn't work, try extracting email from angle brackets
            match = re.search(r'<([^>]+)>', sender)
            if match:
                return match.group(1).lower()
            return sender.lower()
    
    return ""

def find_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    raise ValueError(f"Could not find any of these columns: {candidates}")

def main():
    parser = argparse.ArgumentParser(description="Build legitimate email dataset")
    parser.add_argument("--input", required=True, help="Raw legitimate email CSV")
    parser.add_argument("--output", required=True, help="Output training CSV")
    parser.add_argument("--limit", type=int, default=5000, help="Number of legitimate emails to collect")
    args = parser.parse_args()

    print(f"[+] Loading dataset: {args.input}")
    df = pd.read_csv(args.input, dtype=str).fillna("")

    message_col = find_column(df, ["message", "body", "content", "email_body", "text"])

    print(f"[+] Message column: {message_col}")
    print(f"[+] Target rows: {args.limit}")

    records = []
    counter = 0

    print("[+] Extracting legitimate emails with URLs...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        message = row[message_col].strip()
        
        if not message:
            continue

        sender = extract_sender_from_message(message)
        if not sender:
            sender = "Unknown"

        url = extract_first_url(message)

        if not url:
            continue  # discard emails without URLs

        records.append({
            "sender": sender,
            "message_body": message,
            "url": url,
            "flag": 0
        })
        counter += 1

        if len(records) >= args.limit:
            break

    if len(records) < args.limit:
        print(f"[!] Warning: Only found {len(records)} emails with URLs")

    out_df = pd.DataFrame(records)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)

    print("\n=== Dataset Build Complete ===")
    print(f"Total entries collected: {counter}")
    print(f"Rows written: {len(out_df)}")
    print(f"Output file: {out_path}")

if __name__ == "__main__":
    main()
