#!/usr/bin/env python3
"""
CrisisGuard — Phase 4 Preprocessing: HumAID Humanitarian Text Dataset
Author: B.SIVASAI (Roll No: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Processes:
- All 3 official splits: train (53,531), dev (7,793), test (15,160) = 76,484 records
- Category preservation across 10 humanitarian classes
- Missing text field documentation (text unavailable in all_combined split archive)
- Canonical interim and processed outputs (Parquet & CSV)
"""

import os
import sys
import csv
from pathlib import Path
from collections import Counter
import pandas as pd

def preprocess_humaid():
    print("=" * 60)
    print("CrisisGuard Phase 4: Preprocessing HumAID Dataset")
    print("=" * 60)

    root = Path(__file__).resolve().parent.parent.parent
    raw_dir = root / "data" / "raw" / "humaid" / "all_combined"
    interim_dir = root / "data" / "interim" / "humaid"
    processed_dir = root / "data" / "processed" / "humaid"

    interim_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    splits = ["train", "dev", "test"]
    all_records = []
    class_counts = Counter()
    split_counts = Counter()
    duplicate_ids = 0
    seen_ids = set()

    for split in splits:
        fp = raw_dir / f"all_{split}.tsv"
        if not fp.exists():
            print(f"[WARN] HumAID file not found: {fp}")
            continue

        print(f"Reading HumAID split: {split} ({fp.name})...")
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader, None)
            
            for row in reader:
                if not row or len(row) < 2:
                    continue
                tweet_id = row[0].strip()
                class_label = row[1].strip()

                if tweet_id in seen_ids:
                    duplicate_ids += 1
                seen_ids.add(tweet_id)
                class_counts[class_label] += 1
                split_counts[split] += 1

                record = {
                    "event_id": f"humaid_{tweet_id}",
                    "source_dataset": "humaid_all_combined",
                    "source_record_id": tweet_id,
                    "raw_text": None,
                    "clean_text": None,
                    "category": class_label,
                    "disaster_event": "multi_disaster_global_corpus",
                    "split": split,
                    "timestamp_if_available": None,
                    "location_if_available": None,
                    "governance_type": "REAL"
                }
                all_records.append(record)

    df_humaid = pd.DataFrame(all_records)
    print(f"\nHumAID Extraction Summary:")
    print(f"  Total Extracted Records: {len(df_humaid)}")
    print(f"  Splits Distribution: {dict(split_counts)}")
    print(f"  Duplicate Tweet IDs across splits: {duplicate_ids}")
    print(f"  Distinct Categories: {len(class_counts)}")
    for cat, cnt in class_counts.most_common():
        pct = (cnt / len(df_humaid)) * 100
        print(f"    - {cat}: {cnt} ({pct:.2f}%)")

    # Save interim and processed representations
    df_humaid.to_csv(interim_dir / "humaid_canonical.csv", index=False)
    df_humaid.to_csv(processed_dir / "humaid_records.csv", index=False)
    df_humaid.to_parquet(processed_dir / "humaid_records.parquet", index=False)

    print(f"  Saved to {interim_dir / 'humaid_canonical.csv'}")
    print(f"  Saved to {processed_dir / 'humaid_records.parquet'}")
    return len(df_humaid) == 76484

if __name__ == "__main__":
    success = preprocess_humaid()
    sys.exit(0 if success else 1)
