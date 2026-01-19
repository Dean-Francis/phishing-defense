#!/usr/bin/env python3
"""
combine_email_datasets.py

Combines legitimate and phishing email datasets into a single training dataset with format:

sender,message_body,url,label

Rules:
- Combines legit (label=0) and phishing (label=1) emails
- Randomly shuffles entries
- Stops after specified total rows (default 10000)
- Balances or uses all available data

Usage:
    python combine_email_datasets.py \
        --legit legit_emails_with_urls.csv \
        --phishing phishing_email_dataset.csv \
        --output combined_email_dataset.csv \
        --total 10000
"""

import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description="Combine legitimate and phishing email datasets")
    parser.add_argument("--legit", required=True, help="Legitimate email CSV (with flag column)")
    parser.add_argument("--phishing", required=True, help="Phishing email CSV (with label column)")
    parser.add_argument("--output", required=True, help="Output combined CSV")
    parser.add_argument("--total", type=int, default=10000, help="Total rows to output (default 10000)")
    args = parser.parse_args()

    print(f"[+] Loading legitimate emails: {args.legit}")
    legit_df = pd.read_csv(args.legit, dtype=str).fillna("")
    
    # Rename 'flag' to 'label' for consistency
    if 'flag' in legit_df.columns:
        legit_df = legit_df.rename(columns={'flag': 'label'})
    
    legit_df['label'] = legit_df['label'].astype(int)
    print(f"[+] Loaded {len(legit_df)} legitimate emails")

    print(f"[+] Loading phishing emails: {args.phishing}")
    phishing_df = pd.read_csv(args.phishing, dtype=str).fillna("")
    
    if 'label' not in phishing_df.columns:
        phishing_df['label'] = 1
    
    phishing_df['label'] = phishing_df['label'].astype(int)
    print(f"[+] Loaded {len(phishing_df)} phishing emails")

    print(f"\n[+] Combining datasets randomly...")
    
    # Combine datasets
    combined_df = pd.concat([legit_df, phishing_df], ignore_index=True)
    print(f"[+] Total entries before sampling: {len(combined_df)}")
    
    # Shuffle randomly
    combined_df = combined_df.sample(frac=1, random_state=None).reset_index(drop=True)
    
    # Limit to specified total
    if len(combined_df) > args.total:
        combined_df = combined_df.head(args.total)
        print(f"[!] Limited to {args.total} entries")
    
    print(f"[+] Final dataset size: {len(combined_df)}")
    
    # Show label distribution
    label_counts = combined_df['label'].value_counts().sort_index()
    print(f"\n[+] Label distribution:")
    for label, count in label_counts.items():
        label_name = "Phishing" if label == 1 else "Legitimate"
        percentage = (count / len(combined_df)) * 100
        print(f"   {label_name} (label={label}): {count} ({percentage:.1f}%)")

    # Ensure output directory exists and write
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(out_path, index=False)

    print(f"\n=== Dataset Combination Complete ===")
    print(f"Rows written: {len(combined_df)}")
    print(f"Output file: {out_path}")

if __name__ == "__main__":
    main()
