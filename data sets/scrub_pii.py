#!/usr/bin/env python3
"""
scrub_pii.py

Scrubs PII (emails, phones, credit cards, SSNs) from CSV files
and logs before/after differences for rows that changed.

Usage:
  python scrub_pii.py --input-dir ./output --out-dir ./processed [--report-diffs]

Dependencies:
  pip install pandas tqdm
"""

import argparse
import os
import re
from pathlib import Path
from collections import Counter

import pandas as pd
from tqdm import tqdm

# -----------------------
# Regexes
# -----------------------
EMAIL_RE = re.compile(r"([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,})")
SSN_RE = re.compile(r"\b(\d{3}-\d{2}-\d{4}|\d{9})\b")
PHONE_RE = re.compile(
    r"""(
        (?:\+?\d{1,3}[\s\-\.])?            # optional country code
        (?:\(?\d{3}\)?[\s\-\.]?)           # area code
        \d{3}[\s\-\.]?\d{4}                # rest
    )""", re.VERBOSE)
CC_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

# -----------------------
# Helper Functions
# -----------------------
def luhn_checksum(card_number: str) -> bool:
    digits = [int(ch) for ch in card_number if ch.isdigit()]
    checksum = 0
    dbl = False
    for d in reversed(digits):
        if dbl:
            d = d * 2
            if d > 9:
                d -= 9
        checksum += d
        dbl = not dbl
    return checksum % 10 == 0

def mask_email(_): return "[EMAIL_REDACTED]"

# fixed: compute digits outside f-string to avoid backslash in expression
def mask_ssn(m):
    digits = re.sub(r"\D", "", m.group(0))
    return "***-**-" + digits[-4:]

def mask_phone(m):
    digits = re.sub(r"\D", "", m.group(0))
    if len(digits) >= 4:
        return f"***-***-{digits[-4:]}"
    return "[PHONE_REDACTED]"

def mask_creditcard(m):
    digits = re.sub(r"\D", "", m.group(0))
    if not luhn_checksum(digits):
        return m.group(0)
    # keep last4, mask the rest with grouped Xs
    last4 = digits[-4:]
    # produce masked groups (XXXX-XXXX-...-last4)
    masked_groups = []
    num_mask = len(digits) - 4
    while num_mask > 4:
        masked_groups.append("XXXX")
        num_mask -= 4
    if num_mask > 0:
        masked_groups.append("X" * num_mask)
    if masked_groups:
        return "-".join(masked_groups) + "-" + last4
    else:
        return "XXXX-" + last4

def scrub_text(s: str, counters: Counter) -> str:
    if not isinstance(s, str) or s.strip() == "":
        return s
    orig = s

    s, n1 = EMAIL_RE.subn(lambda m: (counters.update({"emails":1}) or mask_email(m)), s)
    s, n2 = SSN_RE.subn(lambda m: (counters.update({"ssns":1}) or mask_ssn(m)), s)
    s, n3 = CC_RE.subn(lambda m: (counters.update({"credit_cards":1}) or mask_creditcard(m)), s)
    s, n4 = PHONE_RE.subn(lambda m: (counters.update({"phones":1}) or mask_phone(m)), s)
    return s

# -----------------------
# File processing
# -----------------------
def process_csv_file(input_path: Path, output_path: Path, report_diffs=False):
    counters = Counter()
    try:
        df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    except Exception as e:
        print(f"Failed to read {input_path}: {e}")
        return counters, 0

    changes = []

    for i, row in df.iterrows():
        row_changed = False
        new_row = row.copy()
        for col in df.columns:
            old_val = row[col]
            new_val = scrub_text(old_val, counters)
            if old_val != new_val:
                new_row[col] = new_val
                row_changed = True
        if row_changed:
            diff_info = {"row": i + 1, "changes": []}
            for col in df.columns:
                if row[col] != new_row[col]:
                    diff_info["changes"].append(
                        (col, row[col], new_row[col])
                    )
            changes.append(diff_info)
        df.iloc[i] = new_row

    # Save cleaned CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    # Save diff report (if requested)
    if report_diffs and changes:
        report_path = output_path.with_name(output_path.stem + "_scrub_report.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"Scrub Report for {input_path}\n{'='*60}\n")
            for diff in changes:
                f.write(f"\nRow {diff['row']}:\n")
                for col, before, after in diff["changes"]:
                    f.write(f"  Column: {col}\n")
                    f.write(f"    BEFORE: {before}\n")
                    f.write(f"    AFTER:  {after}\n")
                    f.write("  ---\n")
        print(f"[+] Wrote scrub report: {report_path}")

    return counters, len(changes)

# -----------------------
# Main
# -----------------------
def main(argv=None):
    p = argparse.ArgumentParser(description="Scrub PII from CSVs and report before/after differences.")
    p.add_argument("--input-dir", default="./output")
    p.add_argument("--out-dir", default="./processed")
    p.add_argument("--report-diffs", action="store_true", help="Write sidecar text reports showing which rows changed")
    args = p.parse_args(argv)

    input_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir)

    csv_files = sorted(input_dir.glob("**/*.csv"))
    if not csv_files:
        print(f"No CSVs found under {input_dir}")
        return

    totals = Counter()
    total_changed = 0

    for csv_path in tqdm(csv_files, desc="Scrubbing PII"):
        rel = csv_path.relative_to(input_dir)
        out_path = out_dir / rel
        counters, changed_rows = process_csv_file(csv_path, out_path, args.report_diffs)
        totals.update(counters)
        total_changed += changed_rows

    print("\n=== Scrub Summary ===")
    print(f"Files processed:  {len(csv_files)}")
    print(f"Rows changed:     {total_changed}")
    for k, v in totals.items():
        print(f"{k.capitalize()} masked: {v}")
    print(f"Cleaned data saved to: {out_dir.resolve()}")

if __name__ == "__main__":
    main()
