#!/usr/bin/env python3
"""
CrisisGuard — Phase 4 Preprocessing: CrisisLex Disaster Tweet Lexicon & Collections
Author: B.SIVASAI (Roll No: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Processes:
- CrisisLexT26: 26 disaster events (27,933 labeled tweets + timestamp mapping)
- CrisisLexT6: 6 major disasters (60,082 ontopic/offtopic labeled tweets)
- Text cleaning (Step 12): retains raw_text, creates clean_text
- Preserves lexical attributes, informativeness labels, and disaster event metadata
- Canonical interim and processed outputs (Parquet & CSV)
"""

import os
import sys
import re
import csv
import html
import unicodedata
from pathlib import Path
from collections import Counter
import pandas as pd

def clean_crisis_text(text: str) -> str:
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text)
    t = html.unescape(t)
    t = re.sub(r"https?://\S+|www\.\S+", "[URL]", t)
    t = re.sub(r"@\w+", "[USER]", t)
    t = re.sub(r"[\r\n\t]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def preprocess_crisislex():
    print("=" * 60)
    print("CrisisGuard Phase 4: Preprocessing CrisisLex Dataset")
    print("=" * 60)

    root = Path(__file__).resolve().parent.parent.parent
    raw_dir = root / "data" / "raw" / "crisislex" / "data"
    interim_dir = root / "data" / "interim" / "crisislex"
    processed_dir = root / "data" / "processed" / "crisislex"

    interim_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    t26_dir = raw_dir / "CrisisLexT26"
    t6_dir = raw_dir / "CrisisLexT6"

    records = []
    seen_ids = set()
    dup_count = 0
    t26_count = 0
    t6_count = 0

    # 1. Process CrisisLexT26
    if t26_dir.exists():
        event_dirs = sorted([d for d in t26_dir.iterdir() if d.is_dir()])
        print(f"Processing CrisisLexT26: {len(event_dirs)} disaster events...")
        for ed in event_dirs:
            event_name = ed.name
            labeled_csv = list(ed.glob("*-tweets_labeled.csv"))
            period_csv = list(ed.glob("*-tweetids_entire_period.csv"))

            # Build timestamp lookup from period CSV if present
            timestamp_map = {}
            if period_csv:
                with open(period_csv[0], "r", encoding="utf-8", errors="ignore") as pf:
                    preader = csv.reader(pf)
                    p_hdr = next(preader, None)
                    for prow in preader:
                        if len(prow) >= 2:
                            ts = prow[0].strip()
                            tid = prow[1].strip()
                            timestamp_map[tid] = ts

            if labeled_csv:
                with open(labeled_csv[0], "r", encoding="utf-8", errors="ignore") as lf:
                    reader = csv.reader(lf)
                    hdr = next(reader, None)
                    # Normalize header column names (trim whitespace)
                    col_map = {col.strip(): i for i, col in enumerate(hdr)} if hdr else {}

                    id_idx = col_map.get("Tweet ID", 0)
                    text_idx = col_map.get("Tweet Text", 1)
                    src_idx = col_map.get("Information Source", 2)
                    type_idx = col_map.get("Information Type", 3)
                    info_idx = col_map.get("Informativeness", 4)

                    for row in reader:
                        if not row or len(row) <= max(id_idx, text_idx):
                            continue
                        tid = row[id_idx].strip()
                        raw_txt = row[text_idx].strip()
                        if not tid or not raw_txt:
                            continue

                        info_src = row[src_idx].strip() if len(row) > src_idx else "Not specified"
                        info_type = row[type_idx].strip() if len(row) > type_idx else "Not specified"
                        informativeness = row[info_idx].strip() if len(row) > info_idx else "Not specified"

                        key = (tid, event_name)
                        if key in seen_ids:
                            dup_count += 1
                        seen_ids.add(key)
                        t26_count += 1

                        cleaned = clean_crisis_text(raw_txt)
                        ts = timestamp_map.get(tid)

                        records.append({
                            "event_id": f"clex_{tid}",
                            "source_dataset": "crisislex_t26",
                            "source_record_id": tid,
                            "disaster_event": event_name,
                            "raw_text": raw_txt,
                            "clean_text": cleaned,
                            "information_source": info_src,
                            "information_type": info_type,
                            "informativeness_label": informativeness,
                            "timestamp_if_available": ts,
                            "location_if_available": event_name.split("_", 1)[-1].replace("_", " ").title(),
                            "governance_type": "REAL"
                        })

    # 2. Process CrisisLexT6
    if t6_dir.exists():
        event_dirs_t6 = sorted([d for d in t6_dir.iterdir() if d.is_dir()])
        print(f"Processing CrisisLexT6: {len(event_dirs_t6)} disaster events...")
        for ed in event_dirs_t6:
            event_name = ed.name
            csvs = list(ed.glob("*.csv"))
            for csv_f in csvs:
                with open(csv_f, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    hdr = next(reader, None)
                    col_map = {col.strip(): i for i, col in enumerate(hdr)} if hdr else {}

                    id_idx = col_map.get("tweet id", 0)
                    text_idx = col_map.get("tweet", 1)
                    lbl_idx = col_map.get("label", 2)

                    for row in reader:
                        if not row or len(row) <= max(id_idx, text_idx):
                            continue
                        tid = row[id_idx].strip()
                        raw_txt = row[text_idx].strip()
                        if not tid or not raw_txt:
                            continue
                        lbl = row[lbl_idx].strip() if len(row) > lbl_idx else "unknown"

                        key = (tid, event_name)
                        if key in seen_ids:
                            dup_count += 1
                        seen_ids.add(key)
                        t6_count += 1

                        cleaned = clean_crisis_text(raw_txt)

                        records.append({
                            "event_id": f"clex_{tid}",
                            "source_dataset": "crisislex_t6",
                            "source_record_id": tid,
                            "disaster_event": event_name,
                            "raw_text": raw_txt,
                            "clean_text": cleaned,
                            "information_source": "Crowdsourced_Volunteers",
                            "information_type": "Ontopic_Classification",
                            "informativeness_label": lbl,
                            "timestamp_if_available": None,
                            "location_if_available": event_name.split("_", 1)[-1].replace("_", " ").title(),
                            "governance_type": "REAL"
                        })

    df_clex = pd.DataFrame(records)
    print(f"\nCrisisLex Preprocessing Summary:")
    print(f"  Total Processed Records: {len(df_clex)}")
    print(f"  From CrisisLexT26: {t26_count} records across 26 events")
    print(f"  From CrisisLexT6: {t6_count} records across 6 events")
    print(f"  Duplicates Detected: {dup_count}")
    print(f"  Distinct Disaster Events: {df_clex['disaster_event'].nunique()}")

    # Save interim and processed tables
    df_clex.to_csv(interim_dir / "crisislex_canonical.csv", index=False)
    df_clex.to_csv(processed_dir / "crisislex_records.csv", index=False)
    df_clex.to_parquet(processed_dir / "crisislex_records.parquet", index=False)

    print(f"  Saved to {interim_dir / 'crisislex_canonical.csv'}")
    print(f"  Saved to {processed_dir / 'crisislex_records.parquet'}")
    return len(df_clex) > 80000

if __name__ == "__main__":
    success = preprocess_crisislex()
    sys.exit(0 if success else 1)
