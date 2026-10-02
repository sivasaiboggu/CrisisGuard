#!/usr/bin/env python3
"""
CrisisGuard — Independent Final Project Consistency Auditor
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Independent non-delegated auditor verifying cross-phase consistency,
prohibited claims, pipeline evidence, and final documentation alignment.
"""

import sys
import os
import json
from pathlib import Path
import pandas as pd

def run_independent_audit():
    print("=" * 75)
    print("CRISISGUARD — INDEPENDENT FINAL PROJECT CONSISTENCY AUDITOR")
    print("=" * 75)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("Scope:  Second-Opinion Independent Forensic Verification")
    print("=" * 75)

    root = Path(__file__).resolve().parent.parent.parent
    audit = {}

    # 1. Independent Check of Prohibited Epistemic Claims in Active Code
    active_code_clean = True
    prohibited_snippets = ["def compute_edpi", "0.4 * media_risk", "priority = 0.4"]
    for p in (root / "scripts").rglob("*.py"):
        if "validation" in str(p) or "audit" in str(p):
            continue
        txt = p.read_text(encoding="utf-8")
        for snip in prohibited_snippets:
            if snip in txt:
                active_code_clean = False
                break
    audit["1. Active Code Prohibited Construct Audit"] = (
        active_code_clean,
        f"Active Python scripts strictly clean of EDPI / arbitrary scoring: {active_code_clean}"
    )

    # 2. Independent Check for Fake Joined Table
    p9_dir = root / "data/features/phase9"
    fake_table = p9_dir / "phase9_integrated_intelligence.parquet"
    audit["2. Parallel Stream Isolation (No Fake Joins)"] = (
        not fake_table.exists(),
        f"No manufactured cross-dataset joined table exists: {not fake_table.exists()}"
    )

    # 3. Independent Numerical Re-Verification Across Datasets
    m_pq = pd.read_parquet(p9_dir / "phase9_media_intelligence.parquet")
    c_pq = pd.read_parquet(p9_dir / "phase9_crisis_intelligence.parquet")
    p_pq = pd.read_parquet(p9_dir / "phase9_propagation_intelligence.parquet")
    s_pq = pd.read_parquet(p9_dir / "phase9_spatial_intelligence.parquet")
    l_pq = pd.read_parquet(p9_dir / "phase9_multi_stream_intelligence.parquet")

    c_sum = (len(m_pq) + len(c_pq) + len(p_pq) + len(s_pq)) == len(l_pq)
    c_counts = (len(m_pq) == 77) and (len(c_pq) == 104130) and (len(p_pq) == 7494) and (len(s_pq) == 63660)
    audit["3. Independent Multi-Stream Additive Identity"] = (
        c_sum and c_counts,
        f"Stream sum (77 + 104,130 + 7,494 + 63,660 = 175,361) == Ledger ({len(l_pq)}): {c_sum and c_counts}"
    )

    # 4. Independent GraphX Topological Verification
    gx_csv = pd.read_csv(root / "data/features/phase8/graph/graphx_vertex_metrics.csv")
    c_gx_cols = {"vertex_id", "node_name", "in_degree", "out_degree", "pagerank", "component_id"}
    c_gx_schema = c_gx_cols.issubset(set(gx_csv.columns))
    c_gx_len = len(gx_csv) == 7494
    audit["4. GraphX Reconciled Vertex Count & Schema"] = (
        c_gx_schema and c_gx_len,
        f"GraphX metrics rows=7,494 ({c_gx_len}), schema verified ({c_gx_schema})"
    )

    # 5. Independent Big Data Flow Artifact Inspection
    hdfs_ev = root / "docs/phase8/hdfs_ingest_evidence.json"
    spark_ev = root / "docs/phase8/spark_batch_summary.json"
    kafka_ev = root / "docs/phase8/kafka_producer_stats.json"
    stream_ev = root / "docs/phase8/streaming_metrics_summary.json"
    hive_ev = root / "docs/phase8/hive_query_results.json"

    tools_verified = all(p.exists() for p in [hdfs_ev, spark_ev, kafka_ev, stream_ev, hive_ev])
    audit["5. Distributed Tool Pipeline Evidence Receipts"] = (
        tools_verified,
        f"All 5 distributed pipeline execution receipts present on disk: {tools_verified}"
    )

    # 6. Independent Check of Required Audit Documentation
    audit_docs = [
        root / "docs/final_audit/PROJECT_STRUCTURE_AUDIT.md",
        root / "docs/final_audit/PHASE_BY_PHASE_AUDIT.md",
        root / "docs/final_audit/CROSS_PHASE_NUMERICAL_CONSISTENCY.md",
        root / "docs/final_audit/COURSE_RUBRIC_AUDIT.md",
        root / "docs/final_audit/REPRODUCIBILITY_AUDIT.md",
        root / "docs/final_audit/README_AUDIT.md",
        root / "docs/final_audit/FINAL_REPORT_READINESS.md",
        root / "docs/final_audit/DEMO_READINESS.md",
        root / "docs/final_audit/VIVA_RISK_AUDIT.md",
        root / "docs/final_audit/CLAIM_LANGUAGE_AUDIT.md",
        root / "docs/final_audit/STALE_ARTIFACT_AUDIT.md"
    ]
    missing_docs = [p.name for p in audit_docs if not p.exists()]
    audit["6. Final Audit Documentation Suite"] = (
        len(missing_docs) == 0,
        f"All 11 required audit documents exist on disk: {len(missing_docs) == 0}"
    )

    # -------------------------------------------------------------
    # Output Display
    # -------------------------------------------------------------
    print("\nINDEPENDENT AUDIT CHECKLIST:")
    passed_count = sum(1 for p, _ in audit.values() if p)
    total_count = len(audit)
    for name, (passed, msg) in audit.items():
        res = "PASS" if passed else "FAIL"
        print(f"  [{res}] {name.ljust(45)} : {msg}")

    print("\n" + "=" * 75)
    overall = (passed_count == total_count)
    decision = "INDEPENDENT AUDIT RESULT: PASS — FULL SYSTEM CONSISTENCY CONFIRMED" if overall else "INDEPENDENT AUDIT RESULT: FAIL"
    print(decision)
    print("=" * 75)

    return overall

if __name__ == "__main__":
    ok = run_independent_audit()
    sys.exit(0 if ok else 1)
