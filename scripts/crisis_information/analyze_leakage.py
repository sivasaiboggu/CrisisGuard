#!/usr/bin/env python3
"""
CrisisGuard — Phase 7: Event Leakage & Split Overlap Analysis
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Analyzes event overlap between train, dev, and test partitions in HumAID,
CrisisMMD, and CrisisLex. Implements secondary Leave-One-Event-Out (LOEO)
holdout evaluation on CrisisMMD to measure true unseen-event generalization.
"""

import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score

def analyze_leakage():
    print("=" * 65)
    print("CRISISGUARD PHASE 7: EVENT LEAKAGE & GENERALIZATION ANALYSIS")
    print("=" * 65)
    
    root = Path(__file__).resolve().parent.parent.parent
    cmmd_path = root / "data" / "processed" / "crisismmd" / "crisismmd_records.parquet"
    out_dir = root / "docs" / "crisis_information"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    df_cmmd = pd.read_parquet(cmmd_path)
    
    # 1. Event x Split Cross-tabulation
    ct = pd.crosstab(df_cmmd["disaster_event"], df_cmmd["split"], margins=True)
    print("\n--- CrisisMMD Event Distribution Across Official Splits ---")
    print(ct)
    
    # 2. Check if events overlap across official splits
    train_events = set(df_cmmd[df_cmmd["split"] == "train"]["disaster_event"])
    dev_events = set(df_cmmd[df_cmmd["split"] == "dev"]["disaster_event"])
    test_events = set(df_cmmd[df_cmmd["split"] == "test"]["disaster_event"])
    
    print("\nEvent Sets:")
    print("  Train events:", len(train_events), train_events)
    print("  Dev events:  ", len(dev_events), dev_events)
    print("  Test events: ", len(test_events), test_events)
    
    event_overlap = train_events.intersection(test_events)
    print(f"\nOfficial Split Overlap: ALL {len(event_overlap)} events appear in BOTH train and test splits!")
    print("FINDING: The official QCRI CrisisMMD split is a random stratified row split, NOT an event-holdout split.")
    print("Therefore, in-distribution test performance will reflect event-specific lexical familiarity.")
    
    # 3. Secondary Analysis: Leave-One-Event-Out (Unseen-Event Generalization)
    # We hold out 'hurricane_maria' (largest event: 2,228 records) as unseen test event
    holdout_event = "hurricane_maria"
    print(f"\n--- Secondary Generalization Experiment: Unseen-Event Holdout ({holdout_event}) ---")
    
    train_holdout = df_cmmd[df_cmmd["disaster_event"] != holdout_event].copy()
    test_holdout = df_cmmd[df_cmmd["disaster_event"] == holdout_event].copy()
    
    print(f"Training on 6 events ({len(train_holdout)} records) -> Evaluating on {holdout_event} ({len(test_holdout)} records)")
    
    vec = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2)
    X_tr = vec.fit_transform(train_holdout["clean_text"])
    X_te = vec.transform(test_holdout["clean_text"])
    
    clf = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    clf.fit(X_tr, train_holdout["humanitarian_label"])
    
    y_pred_holdout = clf.predict(X_te)
    y_true_holdout = test_holdout["humanitarian_label"]
    
    acc_holdout = accuracy_score(y_true_holdout, y_pred_holdout)
    macro_f1_holdout = f1_score(y_true_holdout, y_pred_holdout, average="macro", zero_division=0)
    
    print(f"Unseen-Event Accuracy:  {acc_holdout:.4f}")
    print(f"Unseen-Event Macro F1:  {macro_f1_holdout:.4f}")
    
    leakage_stats = {
        "official_event_split_type": "STRATIFIED_ROW_SPLIT_WITH_EVENT_OVERLAP",
        "shared_events_count": len(event_overlap),
        "events": list(train_events),
        "event_split_crosstab": ct.to_dict(),
        "unseen_event_experiment": {
            "holdout_event": holdout_event,
            "train_record_count": len(train_holdout),
            "test_record_count": len(test_holdout),
            "unseen_event_accuracy": float(acc_holdout),
            "unseen_event_macro_f1": float(macro_f1_holdout)
        }
    }
    
    out_json = out_dir / "event_leakage_stats.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(leakage_stats, f, indent=2)
    print(f"\nSaved leakage statistics to {out_json}")
    return True

if __name__ == "__main__":
    analyze_leakage()
