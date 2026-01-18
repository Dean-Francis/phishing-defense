#!/usr/bin/env python3
"""
scrub_training_dataset.py

Scrubs PII from training datasets in format:
    url,label

- Only scrubs URL column
- Preserves label column
- Writes cleaned CSV
- Writes before/after scrub report

Usage:
    python scrub_training_dataset.py \
        --input training_dataset.csv \
        --output processed/training_dataset_clean.csv \
        --report
"""

import argparse
import os
import re
from pathlib import Path
from collections import Counter

import pandas as pd
from tqdm import tqdm

# -----------------------
# Regex Patterns
# -----------------------
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}")
SSN_RE = re.compile(r"\b(\d{3}-\d{2}-\d{4}|\d{9})\b")
PHONE_RE = re.compile(
    r"""(
        (?:\+?\d{1,3}[\s\-\.])?
        (?:\(?\d{3}\)?[\s\-\.]?)
        \d{3}[\s\-\.]?\d{4}
    )""", re.VERBOSE)
CC_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

# -----------------------
# Helpers
# -----------------------
def luhn(card):
    digits = [int(c) for c in card if c.isdigit()]
    s = 0
    alt = False
    for d in reversed(digits):
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        s += d
        alt = not alt
    return s % 10 == 0

def scrub_text(text, counters):
    original = text

    text = EMAIL_RE.sub(lambda _: "[EMAIL_REDACTED]", text)
    text = SSN_RE.sub(lambda m: "***-**-" + re.sub(r"\D", "", m.group())[-4:], text)
    text = PHONE_RE.sub(lambda _: "[PHONE_REDACTED]", text)

    def cc_replace(m):
        digits = re.sub(r"\D", "", m.group())
        if not luhn(digits):
            return m.group()
        return "XXXX-XXXX-XXXX-" + digits[-4:]

    text = CC_RE.sub(cc_replace, text)

    if text != original:
        counters["rows_modified"] += 1

    return text

# -----------------------
# Main
# -----------------------
def main():
    parser = argparse.ArgumentParser(description="Scrub PII from URL training dataset")
    parser.add_argument("--input", required=True, help="Input CSV (url,label)")
    parser.add_argument("--output", required=True, help="Output cleaned CSV")
    parser.add_argument("--report", action="store_true", help="Write before/after scrub report")

    args = parser.parse_args()

    print(f"[+] Loading dataset: {args.input}")
    df = pd.read_csv(args.input, dtype=str)

    if "url" not in df.columns or "label" not in df.columns:
        raise ValueError("CSV must contain columns: url,label")

    counters = Counter()
    diffs = []

    print("[+] Scrubbing URLs...")
    for i in tqdm(range(len(df))):
        original = df.at[i, "url"]
        cleaned = scrub_text(original, counters)

        if original != cleaned:
            diffs.append((i+1, original, cleaned))
            df.at[i, "url"] = cleaned

    # Save cleaned dataset
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    print(f"[+] Cleaned dataset written to: {out_path}")

    # Write report
    if args.report:
        report_path = out_path.with_suffix(".scrub_report.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("PII Scrub Report\n")
            f.write("=" * 60 + "\n\n")
            if not diffs:
                f.write("No PII found in dataset.\n")
            else:
                for row, before, after in diffs:
                    f.write(f"Row {row}:\n")
                    f.write(f"  BEFORE: {before}\n")
                    f.write(f"  AFTER : {after}\n")
                    f.write("-" * 60 + "\n")

        print(f"[+] Scrub report written to: {report_path}")

    print("\n=== Scrub Summary ===")
    print(f"Rows processed: {len(df)}")
    print(f"Rows modified:  {counters['rows_modified']}")

if __name__ == "__main__":
    main()
