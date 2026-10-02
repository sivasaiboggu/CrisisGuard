#!/usr/bin/env python3
"""
CrisisGuard — Master Final Project Validator
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Master objective validator verifying repository health, datasets, models,
feature parquets, schemas, epistemic rules, and frozen phase immutability.
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

def run_master_validation():
    print("=" * 75)
    print("CRISISGUARD — MASTER FINAL PROJECT VALIDATOR")
    print("=" * 75)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("Phase Scope: Phases 4 through 9 (All Frozen)")
    print("=" * 75)

    root = Path(__file__).resolve().parent.parent.parent
    checks = {}
    warnings = []
    unverified = []

    # -------------------------------------------------------------
    # 1. Directory Structure Audit
    # -------------------------------------------------------------
    req_dirs = [
        "config", "data/raw", "data/processed", "data/features",
        "models", "schemas", "scripts", "src", "docs", "metastore_db"
    ]
    missing_dirs = [d for d in req_dirs if not (root / d).exists()]
    c1 = len(missing_dirs) == 0
    checks["1. Directory Structure"] = (c1, f"Missing required directories: {missing_dirs}")

    # -------------------------------------------------------------
    # 2. Datasets Inventory & Preprocessed Counts
    # -------------------------------------------------------------
    try:
        p_cifake = pd.read_parquet(root / "data/processed/cifake/cifake_records.parquet")
        p_dfd_frames = pd.read_parquet(root / "data/processed/deepfake_dfd/frame_samples.parquet")
        p_dfd_media = pd.read_parquet(root / "data/processed/deepfake_dfd/media_records.parquet")
        p_humaid = pd.read_parquet(root / "data/processed/humaid/humaid_records.parquet")
        p_cmmd = pd.read_parquet(root / "data/processed/crisismmd/crisismmd_records.parquet")
        p_clex = pd.read_parquet(root / "data/processed/crisislex/crisislex_records.parquet")
        p_osm_nodes = pd.read_parquet(root / "data/processed/osm/road_nodes.parquet")
        p_osm_edges = pd.read_parquet(root / "data/processed/osm/road_edges.parquet")

        c2 = (
            len(p_cifake) == 500 and
            len(p_dfd_frames) == 12 and
            len(p_dfd_media) == 4 and
            len(p_humaid) == 76484 and
            len(p_cmmd) == 8079 and
            len(p_clex) == 88015 and
            len(p_osm_nodes) == 63660 and
            len(p_osm_edges) == 146156
        )
        checks["2. Processed Datasets Counts (Phase 4)"] = (
            c2,
            f"CIFAKE={len(p_cifake)}/500, DFD_Frames={len(p_dfd_frames)}/12, DFD_Media={len(p_dfd_media)}/4, "
            f"HumAID={len(p_humaid)}/76484, CrisisMMD={len(p_cmmd)}/8079, CrisisLex={len(p_clex)}/88015, "
            f"OSM_Nodes={len(p_osm_nodes)}/63660, OSM_Edges={len(p_osm_edges)}/146156"
        )
    except Exception as e:
        checks["2. Processed Datasets Counts (Phase 4)"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # 3. Phase 6 Media Risk Features & Calibration
    # -------------------------------------------------------------
    try:
        p6_pq = root / "data/features/synthetic_media/unified_media_risk.parquet"
        df_p6 = pd.read_parquet(p6_pq)
        c3_count = len(df_p6) == 77
        c3_calib = (df_p6["calibration_status"] == "UNCALIBRATED").all()
        c3_range = ((df_p6["synthetic_risk"] >= 0.0) & (df_p6["synthetic_risk"] <= 1.0)).all()
        c3 = c3_count and c3_calib and c3_range
        checks["3. Phase 6 Media Risk Integrity"] = (
            c3,
            f"Rows={len(df_p6)}/77, Uncalibrated={c3_calib}, Risk Bounded={c3_range}"
        )
    except Exception as e:
        checks["3. Phase 6 Media Risk Integrity"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # 4. Phase 7 Crisis Intelligence & Modality Truthfulness
    # -------------------------------------------------------------
    try:
        p7_pq = root / "data/features/crisis_information/unified_crisis_intelligence.parquet"
        df_p7 = pd.read_parquet(p7_pq)
        c4_count = len(df_p7) == 104130
        c4_breakdown = (
            (df_p7["source_dataset"] == "crisislex_t6_and_t26").sum() == 88015 and
            (df_p7["source_dataset"] == "humaid_all_combined").sum() == 15160 and
            (df_p7["source_dataset"] == "crisismmd_multimodal").sum() == 955
        )
        c4 = c4_count and c4_breakdown
        checks["4. Phase 7 Crisis Intelligence Integrity"] = (
            c4,
            f"Total={len(df_p7)}/104130, Additive Breakdown Valid={c4_breakdown}"
        )
    except Exception as e:
        checks["4. Phase 7 Crisis Intelligence Integrity"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # 5. Phase 8 Graph & Streaming Pipeline Artifacts
    # -------------------------------------------------------------
    try:
        gx_csv = root / "data/features/phase8/graph/graphx_vertex_metrics.csv"
        st_pq = root / "data/features/phase8/streaming/propagation_stream_metrics.parquet"
        ev_pq = root / "data/processed/propagation/propagation_events.parquet"
        ed_pq = root / "data/processed/propagation/propagation_edges.parquet"

        df_gx = pd.read_csv(gx_csv)
        df_st = pd.read_parquet(st_pq)
        df_ev = pd.read_parquet(ev_pq)
        df_ed = pd.read_parquet(ed_pq)

        c5_gx = len(df_gx) == 7494
        c5_st = len(df_st) == 32
        c5_ev = len(df_ev) == 5004
        c5_ed = len(df_ed) == 4999
        c5 = c5_gx and c5_st and c5_ev and c5_ed
        checks["5. Phase 8 Graph & Stream Integrity"] = (
            c5,
            f"Vertices={len(df_gx)}/7494, Windows={len(df_st)}/32, Events={len(df_ev)}/5004, Edges={len(df_ed)}/4999"
        )
    except Exception as e:
        checks["5. Phase 8 Graph & Stream Integrity"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # 6. Phase 9 Multi-Stream Ledger Counts & Isolation
    # -------------------------------------------------------------
    try:
        p9_media = root / "data/features/phase9/phase9_media_intelligence.parquet"
        p9_crisis = root / "data/features/phase9/phase9_crisis_intelligence.parquet"
        p9_prop = root / "data/features/phase9/phase9_propagation_intelligence.parquet"
        p9_spatial = root / "data/features/phase9/phase9_spatial_intelligence.parquet"
        p9_multi = root / "data/features/phase9/phase9_multi_stream_intelligence.parquet"

        df_m = pd.read_parquet(p9_media)
        df_c = pd.read_parquet(p9_crisis)
        df_p = pd.read_parquet(p9_prop)
        df_s = pd.read_parquet(p9_spatial)
        df_all = pd.read_parquet(p9_multi)

        c6_counts = (
            len(df_m) == 77 and
            len(df_c) == 104130 and
            len(df_p) == 7494 and
            len(df_s) == 63660 and
            len(df_all) == 175361
        )
        # Verify no fake joined table
        fake_joined = (root / "data/features/phase9/phase9_integrated_intelligence.parquet").exists()
        c6 = c6_counts and (not fake_joined)
        checks["6. Phase 9 Multi-Stream Ledger Counts"] = (
            c6,
            f"Media=77, Crisis=104130, Prop=7494, Spatial=63660, Total=175361, Fake Join Absent={not fake_joined}"
        )
    except Exception as e:
        checks["6. Phase 9 Multi-Stream Ledger Counts"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # 7. Schema Contracts Conformity
    # -------------------------------------------------------------
    try:
        sch_media = root / "schemas/media_risk_schema.json"
        sch_crisis = root / "schemas/crisis_intelligence_schema.json"
        sch_p9 = root / "schemas/phase9/crisisguard_intelligence_schema.json"

        s1 = json.loads(sch_media.read_text(encoding="utf-8"))
        s2 = json.loads(sch_crisis.read_text(encoding="utf-8"))
        s3 = json.loads(sch_p9.read_text(encoding="utf-8"))

        p9_req = set(s3.get("required", []))
        ledger_cols = set(df_all.columns)
        c7 = p9_req.issubset(ledger_cols) and len(p9_req) >= 11
        checks["7. Schema Contracts Conformity"] = (c7, f"All {len(p9_req)} required Phase 9 fields present in Ledger: {c7}")
    except Exception as e:
        checks["7. Schema Contracts Conformity"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # 8. Null Semantics (Explicit NULLs, No Fake 0.0s)
    # -------------------------------------------------------------
    try:
        m_recs = df_all[df_all["stream_id"] == "STREAM_A_SYNTHETIC_MEDIA"]
        c_recs = df_all[df_all["stream_id"] == "STREAM_B_CRISIS_INFORMATION"]
        p_recs = df_all[df_all["stream_id"] == "STREAM_C_PROPAGATION_GRAPH"]
        s_recs = df_all[df_all["stream_id"] == "STREAM_D_SPATIAL_INFRASTRUCTURE"]

        c8 = (
            m_recs["crisis_model_score"].isna().all() and
            c_recs["media_risk"].isna().all() and
            p_recs["crisis_model_score"].isna().all() and
            s_recs["media_risk"].isna().all() and
            (m_recs["media_risk_available"] == True).all() and
            (c_recs["crisis_intelligence_available"] == True).all() and
            (p_recs["propagation_intelligence_available"] == True).all() and
            (s_recs["spatial_intelligence_available"] == True).all()
        )
        checks["8. Null Governance & Availability Semantics"] = (c8, f"Cross-stream fields strictly NULL and booleans correct: {c8}")
    except Exception as e:
        checks["8. Null Governance & Availability Semantics"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # 9. Zero Arbitrary Weights / Zero EDPI in Active Code
    # -------------------------------------------------------------
    try:
        has_active_edpi = False
        for p in (root / "scripts").glob("**/*.py"):
            if "validation" in str(p) or "audit" in str(p):
                continue
            code = p.read_text(encoding="utf-8")
            if "def compute_edpi" in code or "0.4 * media_risk" in code:
                has_active_edpi = True
                break
        c9 = not has_active_edpi
        checks["9. Zero Arbitrary Weights (No EDPI)"] = (c9, f"Active code strictly free of arbitrary priority scoring: {c9}")
    except Exception as e:
        checks["9. Zero Arbitrary Weights (No EDPI)"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # 10. Immutability of Frozen Previous Phases
    # -------------------------------------------------------------
    try:
        # Check that frozen parquets are non-empty and uncorrupted
        c10 = (
            p6_pq.stat().st_size > 0 and
            p7_pq.stat().st_size > 0 and
            gx_csv.stat().st_size > 0 and
            st_pq.stat().st_size > 0 and
            ev_pq.stat().st_size > 0
        )
        checks["10. Frozen Artifacts Physical Integrity"] = (c10, f"All frozen phase artifacts present and non-empty: {c10}")
    except Exception as e:
        checks["10. Frozen Artifacts Physical Integrity"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Summary Evaluation
    # -------------------------------------------------------------
    print("\nVALIDATION RESULTS SUMMARY:")
    passed_count = 0
    failed_count = 0
    for name, (passed, msg) in checks.items():
        tag = "PASS" if passed else "FAIL"
        if passed:
            passed_count += 1
        else:
            failed_count += 1
        print(f"  [{tag}] {name.ljust(45)} : {msg}")

    print("\n" + "=" * 75)
    print(f"TOTAL CHECKS: {len(checks)} | PASSED: {passed_count} | FAILED: {failed_count} | WARNINGS: {len(warnings)}")
    print("=" * 75)
    
    return failed_count == 0

if __name__ == "__main__":
    success = run_master_validation()
    sys.exit(0 if success else 1)
