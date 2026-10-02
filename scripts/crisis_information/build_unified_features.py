#!/usr/bin/env python3
"""
CrisisGuard — Phase 7: Unified Crisis Intelligence Feature Assembly
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Consolidates source-specific feature streams into a standardized unified
contract preserving exact provenance, lineage, and validation constraints.
Does NOT join or merge records arbitrarily across datasets.
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import jsonschema

def build_unified_features():
    print("=" * 65)
    print("CRISISGUARD PHASE 7: UNIFIED CRISIS INTELLIGENCE FEATURE ASSEMBLY")
    print("=" * 65)
    
    root = Path(__file__).resolve().parent.parent.parent
    feat_dir = root / "data" / "features" / "crisis_information"
    schema_path = root / "schemas" / "crisis_intelligence_schema.json"
    
    humaid_pq = feat_dir / "humaid_predictions.parquet"
    cmmd_pq = feat_dir / "crisismmd_predictions.parquet"
    clex_pq = feat_dir / "crisislex_features.parquet"
    out_pq = feat_dir / "unified_crisis_intelligence.parquet"
    
    # Load schema for validation
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    records = []
    current_time_iso = datetime.now(timezone.utc).isoformat()
    
    # 1. Process HumAID Predictions
    if humaid_pq.exists():
        df_h = pd.read_parquet(humaid_pq)
        print(f"Ingesting HumAID predictions: {len(df_h)} records...")
        for _, row in df_h.iterrows():
            rec = {
                "content_id": str(row["event_id"]),
                "source_dataset": "humaid_all_combined",
                "source_record_id": str(row["source_record_id"]),
                "event_id": str(row.get("disaster_event", "multi_disaster_global_corpus")),
                "text_available": False,
                "image_available": False,
                "crisis_category": str(row["predicted_category"]),
                "task_name": "humanitarian_classification_10class",
                "model_score": float(row["model_score"]),
                "confidence": float(row["confidence"]),
                "quality_status": "VALID",
                "calibration_status": "UNCALIBRATED",
                "temporal_features": None,
                "context_features": {
                    "disaster_event": str(row.get("disaster_event", "multi_disaster_global_corpus")),
                    "location": None,
                    "casualty_terms": None,
                    "damage_terms": None,
                    "rescue_terms": None,
                    "alert_terms": None
                },
                "provenance": "humaid_official_test_split",
                "model_version": "humaid_stratified_baseline_v1",
                "prediction_timestamp": current_time_iso,
                "governance_type": "REAL"
            }
            records.append(rec)
    else:
        print(f"[WARN] HumAID predictions not found at {humaid_pq}")
        
    # 2. Process CrisisMMD Predictions
    if cmmd_pq.exists():
        df_c = pd.read_parquet(cmmd_pq)
        print(f"Ingesting CrisisMMD predictions: {len(df_c)} records...")
        for _, row in df_c.iterrows():
            rec = {
                "content_id": str(row["event_id"]),
                "source_dataset": "crisismmd_multimodal",
                "source_record_id": str(row["source_record_id"]),
                "event_id": str(row["disaster_event"]),
                "text_available": True,
                "image_available": False,  # Strictly honest
                "crisis_category": str(row["predicted_category"]),
                "task_name": "humanitarian_classification_5class",
                "model_score": float(row["model_score"]),
                "confidence": float(row["confidence"]),
                "quality_status": "VALID",
                "calibration_status": "UNCALIBRATED",
                "temporal_features": {
                    "timestamp_str": str(row["timestamp_if_available"]) if row.get("timestamp_if_available") else None,
                    "date_extracted": str(row["timestamp_if_available"]) if row.get("timestamp_if_available") else None
                },
                "context_features": {
                    "disaster_event": str(row["disaster_event"]),
                    "location": str(row.get("location_if_available", "")),
                    "casualty_terms": None,
                    "damage_terms": None,
                    "rescue_terms": None,
                    "alert_terms": None
                },
                "provenance": "crisismmd_official_test_split",
                "model_version": "crisismmd_distilbert_v1",
                "prediction_timestamp": current_time_iso,
                "governance_type": "REAL"
            }
            records.append(rec)
    else:
        print(f"[WARN] CrisisMMD predictions not found at {cmmd_pq}")
        
    # 3. Process CrisisLex Context Features
    if clex_pq.exists():
        df_l = pd.read_parquet(clex_pq)
        print(f"Ingesting CrisisLex context features: {len(df_l)} records...")
        for _, row in df_l.iterrows():
            rec = {
                "content_id": str(row["event_id"]),
                "source_dataset": "crisislex_t6_and_t26",
                "source_record_id": str(row["source_record_id"]),
                "event_id": str(row["disaster_event"]),
                "text_available": True,
                "image_available": False,
                "crisis_category": str(row.get("information_type", "Contextual_Evidence")),
                "task_name": "linguistic_context_extraction",
                "model_score": None,
                "confidence": None,
                "quality_status": "VALID",
                "calibration_status": "NOT_APPLICABLE",
                "temporal_features": {
                    "timestamp_str": str(row["timestamp_if_available"]) if row.get("timestamp_if_available") else None,
                    "date_extracted": None
                },
                "context_features": {
                    "disaster_event": str(row["disaster_event"]),
                    "location": str(row.get("location_if_available", "")),
                    "casualty_terms": int(row.get("casualty_term_count", 0)),
                    "damage_terms": int(row.get("damage_term_count", 0)),
                    "rescue_terms": int(row.get("rescue_term_count", 0)),
                    "alert_terms": int(row.get("alert_term_count", 0))
                },
                "provenance": "crisislex_t6_and_t26_processed",
                "model_version": "crisislex_context_v1",
                "prediction_timestamp": current_time_iso,
                "governance_type": "REAL"
            }
            records.append(rec)
    else:
        print(f"[WARN] CrisisLex features not found at {clex_pq}")
        
    unified_df = pd.DataFrame(records)
    print(f"\nUnified Intelligence Table Assembled: {len(unified_df)} total records")
    print("Breakdown by Source Dataset:")
    print(unified_df["source_dataset"].value_counts())
    
    # Validate first 100 records against JSON schema
    print("\nValidating records against crisis_intelligence_schema.json...")
    sample_records = unified_df.head(100).to_dict(orient="records")
    for s_rec in sample_records:
        jsonschema.validate(instance=s_rec, schema=schema)
    print("Schema Validation: 100/100 sample records fully conform to JSON schema contract.")
    
    # Save unified parquet
    unified_df.to_parquet(out_pq, index=False)
    print(f"\nSaved unified features to: {out_pq}")
    return True

if __name__ == "__main__":
    success = build_unified_features()
    sys.exit(0 if success else 1)
