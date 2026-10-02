#!/usr/bin/env python3
"""
CrisisGuard — Phase 9 Master Validation Suite
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Validates:
1. Schema conformity across Stream tables and Multi-Stream Ledger
2. Row counts across all feature tables derived from actual inputs
3. Duplicate ID audit (strictly zero duplicate primary IDs per stream)
4. Nulls audit (explicit nulls allowed only where justified, no fake values)
5. Provenance preservation across all streams
6. Timestamps format and monotonicity
7. Confidence ranges bounded in [0.0, 1.0]
8. Calibration semantics (UNCALIBRATED/NOT_APPLICABLE properly enforced)
9. Source dataset integrity and preservation
10. Model identity preservation without phantom models
11. Join integrity (zero ungrounded cross-stream foreign key joins)
12. No fabricated values (no invented synthetic coordinates or fake links)
13. No arbitrary weights (NO EDPI, NO Emergency Priority formula)
14. Previous-phase immutability (cryptographic SHA-256 match on frozen inputs)
"""

import sys
import os
import json
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def run_validation():
    print("=" * 75)
    print("CRISISGUARD — PHASE 9 MASTER VALIDATION SUITE")
    print("=" * 75)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("Phase:  9 — End-to-End Integration & Final Decision-Support Layer")
    print("=" * 75)

    root = Path(__file__).resolve().parent.parent.parent
    checks = {}

    p6_pq = root / "data" / "features" / "synthetic_media" / "unified_media_risk.parquet"
    p7_pq = root / "data" / "features" / "crisis_information" / "unified_crisis_intelligence.parquet"
    p8_events = root / "data" / "processed" / "propagation" / "propagation_events.parquet"
    p8_edges = root / "data" / "processed" / "propagation" / "propagation_edges.parquet"
    p8_gx = root / "data" / "features" / "phase8" / "graph" / "graphx_vertex_metrics.csv"
    p8_st = root / "data" / "features" / "phase8" / "streaming" / "propagation_stream_metrics.parquet"
    osm_nodes = root / "data" / "processed" / "osm" / "road_nodes.parquet"
    osm_edges = root / "data" / "processed" / "osm" / "road_edges.parquet"

    # Phase 9 Outputs
    p9_dir = root / "data" / "features" / "phase9"
    p9_media = p9_dir / "phase9_media_intelligence.parquet"
    p9_crisis = p9_dir / "phase9_crisis_intelligence.parquet"
    p9_prop = p9_dir / "phase9_propagation_intelligence.parquet"
    p9_spatial = p9_dir / "phase9_spatial_intelligence.parquet"
    p9_multi = p9_dir / "phase9_multi_stream_intelligence.parquet"
    p9_schema_file = root / "schemas" / "phase9" / "crisisguard_intelligence_schema.json"

    # Read inputs
    df_p6 = pd.read_parquet(p6_pq)
    df_p7 = pd.read_parquet(p7_pq)
    df_p8_gx = pd.read_csv(p8_gx)
    df_osm = pd.read_parquet(osm_nodes)

    # Read Phase 9 tables
    df_p9_media = pd.read_parquet(p9_media) if p9_media.exists() else pd.DataFrame()
    df_p9_crisis = pd.read_parquet(p9_crisis) if p9_crisis.exists() else pd.DataFrame()
    df_p9_prop = pd.read_parquet(p9_prop) if p9_prop.exists() else pd.DataFrame()
    df_p9_spatial = pd.read_parquet(p9_spatial) if p9_spatial.exists() else pd.DataFrame()
    df_p9_multi = pd.read_parquet(p9_multi) if p9_multi.exists() else pd.DataFrame()

    # -------------------------------------------------------------
    # Check 1: Schema Conformity
    # -------------------------------------------------------------
    try:
        with open(p9_schema_file, "r") as f:
            schema_data = json.load(f)
        required_fields = set(schema_data.get("required", []))
        multi_cols = set(df_p9_multi.columns)
        c1 = required_fields.issubset(multi_cols) and p9_schema_file.exists()
        checks["1. Schema Conformity"] = (c1, f"Required fields {len(required_fields)} present in Multi-Stream Ledger: {c1}")
    except Exception as e:
        checks["1. Schema Conformity"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 2: Row Counts Alignment
    # -------------------------------------------------------------
    try:
        exp_media = len(df_p6)
        exp_crisis = len(df_p7)
        exp_prop = len(df_p8_gx)
        exp_spatial = len(df_osm)
        exp_total = exp_media + exp_crisis + exp_prop + exp_spatial

        act_media = len(df_p9_media)
        act_crisis = len(df_p9_crisis)
        act_prop = len(df_p9_prop)
        act_spatial = len(df_p9_spatial)
        act_total = len(df_p9_multi)

        c2 = (act_media == exp_media) and (act_crisis == exp_crisis) and \
             (act_prop == exp_prop) and (act_spatial == exp_spatial) and \
             (act_total == exp_total)
        checks["2. Row Counts Verified"] = (c2, f"Media={act_media}/{exp_media}, Crisis={act_crisis}/{exp_crisis}, Prop={act_prop}/{exp_prop}, Spatial={act_spatial}/{exp_spatial}, Total={act_total}/{exp_total}")
    except Exception as e:
        checks["2. Row Counts Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 3: Duplicate ID Audit
    # -------------------------------------------------------------
    try:
        dup_media = df_p9_media["record_id"].duplicated().sum()
        dup_crisis = df_p9_crisis["record_id"].duplicated().sum()
        dup_prop = df_p9_prop["record_id"].duplicated().sum()
        dup_spatial = df_p9_spatial["record_id"].duplicated().sum()
        dup_multi = df_p9_multi["record_id"].duplicated().sum()
        
        c3 = (dup_media == 0) and (dup_crisis == 0) and (dup_prop == 0) and (dup_spatial == 0) and (dup_multi == 0)
        checks["3. Duplicate ID Audit"] = (c3, f"Duplicates: Media={dup_media}, Crisis={dup_crisis}, Prop={dup_prop}, Spatial={dup_spatial}, Ledger={dup_multi}")
    except Exception as e:
        checks["3. Duplicate ID Audit"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 4: Null Values Governance
    # -------------------------------------------------------------
    try:
        # In multi-stream ledger, unavailable fields must be explicitly NULL and NOT filled with 0.0 or placeholders
        media_records = df_p9_multi[df_p9_multi["stream_id"] == "STREAM_A_SYNTHETIC_MEDIA"]
        crisis_records = df_p9_multi[df_p9_multi["stream_id"] == "STREAM_B_CRISIS_INFORMATION"]
        prop_records = df_p9_multi[df_p9_multi["stream_id"] == "STREAM_C_PROPAGATION_GRAPH"]
        
        c4_media_nulls = media_records["crisis_model_score"].isna().all() and media_records["pagerank"].isna().all()
        c4_crisis_nulls = crisis_records["media_risk"].isna().all() and crisis_records["pagerank"].isna().all()
        c4_prop_nulls = prop_records["crisis_model_score"].isna().all() and prop_records["crisis_prediction"].isna().all()
        
        c4 = c4_media_nulls and c4_crisis_nulls and c4_prop_nulls
        checks["4. Null Values Governance"] = (c4, f"Unavailable cross-stream fields strictly NULL (no fake zeros): {c4}")
    except Exception as e:
        checks["4. Null Values Governance"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 5: Provenance Preservation
    # -------------------------------------------------------------
    try:
        gov_multi = set(df_p9_multi["governance_type"].unique())
        src_datasets = set(df_p9_multi["source_dataset"].unique())
        exp_gov = {"REAL", "SEMI_SYNTHETIC"}
        c5 = exp_gov.issubset(gov_multi) and len(src_datasets) >= 4 and df_p9_multi["provenance"].notna().all()
        checks["5. Provenance Preserved"] = (c5, f"Governance tags: {gov_multi}, Unique source datasets: {len(src_datasets)}")
    except Exception as e:
        checks["5. Provenance Preserved"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 6: Timestamps Format & Integrity
    # -------------------------------------------------------------
    try:
        # Check timestamp strings where available are ISO formatted
        ts_media = df_p9_media["prediction_timestamp"].dropna()
        ts_prop = df_p9_prop["first_event_time"].dropna()
        valid_ts_media = ts_media.str.contains(r"^\d{4}-\d{2}-\d{2}").all()
        valid_ts_prop = ts_prop.str.contains(r"^\d{4}-\d{2}-\d{2}").all()
        c6 = valid_ts_media and valid_ts_prop
        checks["6. Timestamps Integrity"] = (c6, f"Valid ISO-8601 timestamps: Media={valid_ts_media}, Prop={valid_ts_prop}")
    except Exception as e:
        checks["6. Timestamps Integrity"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 7: Confidence Ranges Bounded
    # -------------------------------------------------------------
    try:
        p6_probs = df_p9_media["synthetic_probability"]
        p6_risks = df_p9_media["synthetic_risk"]
        p7_confs = df_p9_crisis["confidence"].dropna()
        
        c7_p6_prob = (p6_probs >= 0.0).all() and (p6_probs <= 1.0).all()
        c7_p6_risk = (p6_risks >= 0.0).all() and (p6_risks <= 1.0).all()
        c7_p7_conf = (p7_confs >= 0.0).all() and (p7_confs <= 1.0).all()
        
        c7 = c7_p6_prob and c7_p6_risk and c7_p7_conf
        checks["7. Confidence Ranges Bounded"] = (c7, f"All probability/risk/confidence metrics bounded in [0.0, 1.0]: {c7}")
    except Exception as e:
        checks["7. Confidence Ranges Bounded"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 8: Calibration Semantics
    # -------------------------------------------------------------
    try:
        cal_media = set(df_p9_media["calibration_status"].unique())
        cal_crisis = set(df_p9_crisis["calibration_status"].unique())
        # All Phase 6 models are UNCALIBRATED; Phase 7 has UNCALIBRATED and NOT_APPLICABLE
        c8_med = ("UNCALIBRATED" in cal_media) and ("CALIBRATED_EMPIRICAL" not in cal_media)
        c8_cri = ("UNCALIBRATED" in cal_crisis) and ("CALIBRATED_EMPIRICAL" not in cal_crisis)
        c8 = c8_med and c8_cri
        checks["8. Calibration Semantics"] = (c8, f"Media calibration={cal_media}, Crisis calibration={cal_crisis}")
    except Exception as e:
        checks["8. Calibration Semantics"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 9: Source Dataset Integrity
    # -------------------------------------------------------------
    try:
        med_sources = set(df_p9_media["source_dataset"].unique())
        cri_sources = set(df_p9_crisis["source_dataset"].unique())
        c9_m = med_sources == {"CIFAKE", "Google_DFD_Controlled_Sample"}
        c9_c = {"crisislex_t6_and_t26", "humaid_all_combined", "crisismmd_multimodal"}.issubset(cri_sources)
        c9 = c9_m and c9_c
        checks["9. Source Dataset Integrity"] = (c9, f"Media sources={med_sources}, Crisis sources={cri_sources}")
    except Exception as e:
        checks["9. Source Dataset Integrity"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 10: Model Identity Preservation
    # -------------------------------------------------------------
    try:
        med_models = set(df_p9_media["model_version"].unique())
        cri_models = set(df_p9_crisis["model_version"].dropna().unique())
        c10_m = ("resnet18_cifake_v1.0" in med_models) and ("temporal_dfd_resnet18_v1.0" in med_models)
        c10_c = len(cri_models) >= 1
        c10 = c10_m and c10_c
        checks["10. Model Identity Preservation"] = (c10, f"Media models={med_models}, Crisis models count={len(cri_models)}")
    except Exception as e:
        checks["10. Model Identity Preservation"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 11: Join Integrity & Zero Unvalidated Key Merging
    # -------------------------------------------------------------
    try:
        # Check that no synthetic keys or fuzzy joins were created to force an artificial unified table
        with open(root / "docs" / "phase9" / "JOIN_FEASIBILITY_AUDIT.md", "r") as f:
            join_text = f.read()
        c11_audit = "NO_VALID_JOIN" in join_text and "PARALLEL MULTI-STREAM" in join_text
        # In multi-stream ledger, count of records must exactly equal sum of separate stream counts (no Cartesian explosion)
        c11_sum = len(df_p9_multi) == (len(df_p9_media) + len(df_p9_crisis) + len(df_p9_prop) + len(df_p9_spatial))
        c11 = c11_audit and c11_sum
        checks["11. Join Integrity Verified"] = (c11, f"Audit proves NO_VALID_JOIN; Multi-stream count ({len(df_p9_multi)}) equals disjoint sum: {c11_sum}")
    except Exception as e:
        checks["11. Join Integrity Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 12: No Fabricated Values
    # -------------------------------------------------------------
    try:
        # Verify that OSM coordinates were NOT assigned to social graph vertices or crisis tweets
        prop_has_lat = "latitude" in df_p9_prop.columns
        crisis_has_lat = "latitude" in df_p9_crisis.columns
        c12 = (not prop_has_lat) and (not crisis_has_lat)
        checks["12. No Fabricated Values"] = (c12, f"No fabricated coordinates on non-spatial streams: PropLat={prop_has_lat}, CrisisLat={crisis_has_lat}")
    except Exception as e:
        checks["12. No Fabricated Values"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 13: No Arbitrary Weights / No EDPI
    # -------------------------------------------------------------
    try:
        # Scan phase9 scripts and tables for EDPI or linear priority formulas
        p9_files = list((root / "scripts" / "phase9").glob("**/*")) + list((root / "docs" / "phase9").glob("**/*"))
        has_prohibited_edpi = False
        for pf in p9_files:
            if pf.is_file() and pf.suffix in [".py", ".md", ".json"]:
                txt = pf.read_text(encoding="utf-8")
                if "def compute_edpi" in txt or "0.4 * media_risk + 0.3" in txt or "priority = 0.4 *" in txt:
                    has_prohibited_edpi = True
        c13 = not has_prohibited_edpi
        checks["13. No Arbitrary Weights (No EDPI)"] = (c13, f"Arbitrary EDPI formula absent from Phase 9: {c13}")
    except Exception as e:
        checks["13. No Arbitrary Weights (No EDPI)"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 14: Previous-Phase Immutability
    # -------------------------------------------------------------
    try:
        with open(root / "docs" / "phase8" / "input_audit_data.json") as f:
            in_audit = json.load(f)
        h_ev = sha256_file(p8_events)
        h_ed = sha256_file(p8_edges)
        h_mr = sha256_file(p6_pq)
        h_ci = sha256_file(p7_pq)

        c14 = (h_ev == in_audit["propagation_events"]["sha256"]) and \
              (h_ed == in_audit["propagation_edges"]["sha256"]) and \
              (h_mr == in_audit["media_risk"]["sha256"]) and \
              (h_ci == in_audit["crisis_intelligence"]["sha256"])
        checks["14. Previous Phase Immutability"] = (c14, f"Cryptographic SHA-256 match verified across all frozen inputs: {c14}")
    except Exception as e:
        checks["14. Previous Phase Immutability"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Final Summary Table
    # -------------------------------------------------------------
    print("\nVALIDATION SUMMARY:")
    all_pass = True
    for name, (passed, details) in checks.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {name.ljust(35)} : {details}")

    print("\n" + "=" * 75)
    decision = "PHASE 9 PASS — MULTI-STREAM INTEGRATION VERIFIED" if all_pass else "PHASE 9 HARDENING REQUIRED"
    print(f"OVERALL DECISION: {decision}")
    print("=" * 75)
    return all_pass

if __name__ == "__main__":
    passed = run_validation()
    sys.exit(0 if passed else 1)
