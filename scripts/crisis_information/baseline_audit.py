#!/usr/bin/env python3
"""
CrisisGuard — Phase 7 Baseline Forensic Audit Collector
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
"""

import os
import hashlib
import json
from pathlib import Path
import pandas as pd

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def collect_baseline():
    root = Path(__file__).resolve().parent.parent.parent
    
    files_to_hash = [
        root / "data/processed/humaid/humaid_records.parquet",
        root / "data/processed/crisismmd/crisismmd_records.parquet",
        root / "data/processed/crisislex/crisislex_records.parquet",
        root / "data/features/crisis_information/humaid_predictions.parquet",
        root / "data/features/crisis_information/crisismmd_predictions.parquet",
        root / "data/features/crisis_information/crisislex_features.parquet",
        root / "data/features/crisis_information/unified_crisis_intelligence.parquet",
        root / "models/crisis_information/humaid/humaid_baseline_model.joblib",
        root / "models/crisis_information/crisismmd/crisismmd_baseline_logistic.joblib",
        root / "models/crisis_information/crisismmd/crisismmd_informative_baseline.joblib",
        root / "models/crisis_information/crisismmd/crisismmd_tfidf_vectorizer.joblib",
        root / "schemas/crisis_intelligence_schema.json"
    ]
    
    baseline = {"hashes": {}, "row_counts": {}, "model_files": {}}
    
    print("=== SHA256 AUDIT BASELINE ===")
    for p in files_to_hash:
        if p.exists():
            h = sha256_file(p)
            size = p.stat().st_size
            print(f"{p.name:45s}: {size:10d} bytes | SHA256: {h}")
            baseline["hashes"][p.name] = {"size": size, "sha256": h}
        else:
            print(f"[MISSING] {p.name}")
            baseline["hashes"][p.name] = "MISSING"

    print("\n=== PARQUET ROW COUNTS ===")
    pqs = [
        root / "data/processed/humaid/humaid_records.parquet",
        root / "data/processed/crisismmd/crisismmd_records.parquet",
        root / "data/processed/crisislex/crisislex_records.parquet",
        root / "data/features/crisis_information/humaid_predictions.parquet",
        root / "data/features/crisis_information/crisismmd_predictions.parquet",
        root / "data/features/crisis_information/crisislex_features.parquet",
        root / "data/features/crisis_information/unified_crisis_intelligence.parquet"
    ]
    for pq in pqs:
        if pq.exists():
            df = pd.read_parquet(pq)
            print(f"{pq.name:45s}: {len(df):7d} rows, {df.shape[1]:2d} cols")
            baseline["row_counts"][pq.name] = {"rows": len(df), "cols": df.shape[1], "columns": list(df.columns)}

    # Model files
    models_dir = root / "models/crisis_information"
    print("\n=== MODEL ARTIFACTS ===")
    for p in models_dir.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(root))
            print(f"{rel:65s}: {p.stat().st_size} bytes")
            baseline["model_files"][rel] = p.stat().st_size
            
    out_json = root / "docs/crisis_information/baseline_audit_data.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)
    print(f"\nBaseline metadata saved to {out_json}")

if __name__ == "__main__":
    collect_baseline()
