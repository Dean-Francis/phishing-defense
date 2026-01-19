#!/usr/bin/env python3
"""
build_training_dataset.py

Builds a balanced dataset from a phishing CSV.

- Takes 5000 legitimate URLs
- Takes 5000 phishing URLs
- Converts labels:
    legitimate -> 0
    phishing   -> 1
- Outputs a single unified CSV

Usage:
    python build_training_dataset.py \
        --input phishing_site_urls.csv \
        --output training_dataset.csv

Dependencies:
    pip install pandas
"""

import argparse
import pandas as pd
import sys

def main():
    parser = argparse.ArgumentParser(description="Build balanced phishing dataset")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", default="training_dataset.csv", help="Output CSV file")
    parser.add_argument("--legit", type=int, default=5000, help="Number of legitimate URLs")
    parser.add_argument("--phish", type=int, default=5000, help="Number of phishing URLs")
    args = parser.parse_args()

    print(f"[+] Loading dataset: {args.input}")
    df = pd.read_csv(args.input)

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Auto-detect columns
    if "url" not in df.columns:
        print("[-] ERROR: CSV must contain a 'url' column")
        sys.exit(1)

    label_col = None
    for c in ["label", "type", "class", "category"]:
        if c in df.columns:
            label_col = c
            break

    if not label_col:
        print("[-] ERROR: Could not find label column (label/type/class/category)")
        sys.exit(1)

    print(f"[+] Using label column: {label_col}")

    # Normalize labels
    df[label_col] = df[label_col].astype(str).str.lower().str.strip()

    legit_df = df[df[label_col].isin(["legitimate", "benign", "good", "0"])]
    phish_df = df[df[label_col].isin(["phishing", "malicious", "bad", "1"])]

    print(f"[+] Found {len(legit_df)} legitimate URLs")
    print(f"[+] Found {len(phish_df)} phishing URLs")

    if len(legit_df) < args.legit or len(phish_df) < args.phish:
        print("[-] ERROR: Not enough URLs to sample from.")
        sys.exit(1)

    # Sample
    legit_sample = legit_df.sample(args.legit, random_state=42)
    phish_sample = phish_df.sample(args.phish, random_state=42)

    # Build final dataset
    legit_sample = legit_sample[["url"]].copy()
    legit_sample["label"] = 0

    phish_sample = phish_sample[["url"]].copy()
    phish_sample["label"] = 1

    final_df = pd.concat([legit_sample, phish_sample], ignore_index=True)
    final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save
    final_df.to_csv(args.output, index=False)

    print("\n=== Dataset Created ===")
    print(f"Legitimate (0): {len(legit_sample)}")
    print(f"Phishing   (1): {len(phish_sample)}")
    print(f"Total rows:    {len(final_df)}")
    print(f"Saved to:      {args.output}")

if __name__ == "__main__":
    main()
