#!/usr/bin/env python3
"""
CrisisGuard — Comprehensive Functional Acceptance Test Suite
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Executes end-to-end non-destructive functional acceptance tests across all frozen phases:
- Test 1: Data Access (all 7 frozen datasets readable with zero corruption)
- Test 2: Phase 6 Media Intelligence (models, predictions, uncalibrated semantics)
- Test 3: Phase 7 Crisis Intelligence (HumAID, CrisisMMD text-only, CrisisLex, 104,130 rows)
- Test 4: Phase 8 Batch Pipeline (HDFS, Spark, GraphX 7,494 vertices, 4,999 edges)
- Test 5: Graph Analytics (PageRank finite, degree distributions, 2,509 components)
- Test 6: Kafka Message Broker (5,004 produced/consumed, 0 drops, 0 duplicates)
- Test 7: Structured Streaming (32 tumbling windows, watermarking, velocity profiles)
- Test 8: Hive Warehouse (DDL, metastore, analytical SQL queries)
- Test 9: Phase 9 Decision Support (Multi-stream ledger 175,361 rows, NO_VALID_JOIN, explicit NULLs)
- Test 10: Controlled Failure Tests (malformed JSON, duplicate, null time, dangling edge, bad weight)
"""

import sys
import os
import json
import time
from pathlib import Path
import pandas as pd
import numpy as np

def run_all_tests():
    t_start = time.time()
    print("=" * 75)
    print("CRISISGUARD — FINAL FUNCTIONAL ACCEPTANCE TEST SUITE")
    print("=" * 75)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("Scope:  Independent Functional & Execution Verification")
    print("=" * 75)

    root = Path(__file__).resolve().parent.parent.parent
    results = []

    def record_test(name, passed, expected, actual, duration, evidence):
        status = "PASS" if passed else "FAIL"
        results.append({
            "feature": name,
            "test": name,
            "expected": str(expected),
            "actual": str(actual),
            "status": status,
            "duration_sec": round(duration, 3),
            "evidence": evidence
        })
        print(f"[{status}] {name.ljust(45)} ({duration:.3f}s)")
        print(f"       Expected: {expected}")
        print(f"       Actual:   {actual}")

    # -------------------------------------------------------------
    # Test 1: Data Access Verification
    # -------------------------------------------------------------
    t0 = time.time()
    try:
        p_cifake = pd.read_parquet(root / "data/processed/cifake/cifake_records.parquet")
        p_dfd_m = pd.read_parquet(root / "data/processed/deepfake_dfd/media_records.parquet")
        p_dfd_f = pd.read_parquet(root / "data/processed/deepfake_dfd/frame_samples.parquet")
        p_hum = pd.read_parquet(root / "data/processed/humaid/humaid_records.parquet")
        p_cmmd = pd.read_parquet(root / "data/processed/crisismmd/crisismmd_records.parquet")
        p_clex = pd.read_parquet(root / "data/processed/crisislex/crisislex_records.parquet")
        p_osm_n = pd.read_parquet(root / "data/processed/osm/road_nodes.parquet")
        p_osm_e = pd.read_parquet(root / "data/processed/osm/road_edges.parquet")
        p_prop_ev = pd.read_parquet(root / "data/processed/propagation/propagation_events.parquet")
        p_prop_ed = pd.read_parquet(root / "data/processed/propagation/propagation_edges.parquet")

        c1 = (
            len(p_cifake) == 500 and len(p_dfd_m) == 4 and len(p_dfd_f) == 12 and
            len(p_hum) == 76484 and len(p_cmmd) == 8079 and len(p_clex) == 88015 and
            len(p_osm_n) == 63660 and len(p_osm_e) == 146156 and
            len(p_prop_ev) == 5004 and len(p_prop_ed) == 4999
        )
        dur = time.time() - t0
        record_test(
            "1. Data Access (7 Frozen Datasets)",
            c1,
            "All 7 datasets readable with verified preprocessed row counts",
            f"CIFAKE={len(p_cifake)}, DFD={len(p_dfd_m)}/{len(p_dfd_f)}, HumAID={len(p_hum)}, "
            f"CrisisMMD={len(p_cmmd)}, CrisisLex={len(p_clex)}, OSM={len(p_osm_n)}/{len(p_osm_e)}, "
            f"Prop={len(p_prop_ev)}/{len(p_prop_ed)}",
            dur,
            "data/processed/*/Parquet tables"
        )
    except Exception as e:
        record_test("1. Data Access (7 Frozen Datasets)", False, "Datasets readable", f"Exception: {e}", time.time() - t0, "data/processed/")

    # -------------------------------------------------------------
    # Test 2: Phase 6 Media Intelligence
    # -------------------------------------------------------------
    t0 = time.time()
    try:
        p6_pq = root / "data/features/synthetic_media/unified_media_risk.parquet"
        p6_img = root / "data/features/synthetic_media/image_predictions.parquet"
        p6_vid = root / "data/features/synthetic_media/video_predictions.parquet"
        m_img = root / "models/synthetic_media/image_model_best.pt"
        m_vid = root / "models/synthetic_media/video_model_best.pt"

        df_p6 = pd.read_parquet(p6_pq)
        df_img = pd.read_parquet(p6_img)
        df_vid = pd.read_parquet(p6_vid)

        c2_counts = (len(df_p6) == 77 and len(df_img) == 75 and len(df_vid) == 2)
        c2_models = (m_img.exists() and m_vid.exists())
        c2_calib = (df_p6["calibration_status"] == "UNCALIBRATED").all()
        c2_qual = (df_p6["quality_status"] == "VALID").all()
        c2_range = ((df_p6["synthetic_risk"] >= 0.0) & (df_p6["synthetic_risk"] <= 1.0)).all()
        c2 = c2_counts and c2_models and c2_calib and c2_qual and c2_range
        dur = time.time() - t0
        record_test(
            "2. Phase 6 Media Intelligence",
            c2,
            "77 unified records (75 images, 2 videos), UNCALIBRATED, risk in [0, 1]",
            f"Unified={len(df_p6)}, Images={len(df_img)}, Videos={len(df_vid)}, "
            f"Uncalibrated={c2_calib}, QualityValid={c2_qual}, RiskBounded={c2_range}",
            dur,
            "data/features/synthetic_media/unified_media_risk.parquet"
        )
    except Exception as e:
        record_test("2. Phase 6 Media Intelligence", False, "Valid media features", f"Exception: {e}", time.time() - t0, "Phase 6 outputs")

    # -------------------------------------------------------------
    # Test 3: Phase 7 Crisis Intelligence
    # -------------------------------------------------------------
    t0 = time.time()
    try:
        p7_pq = root / "data/features/crisis_information/unified_crisis_intelligence.parquet"
        df_p7 = pd.read_parquet(p7_pq)

        c3_count = len(df_p7) == 104130
        c3_clex = (df_p7["source_dataset"] == "crisislex_t6_and_t26").sum() == 88015
        c3_hum = (df_p7["source_dataset"] == "humaid_all_combined").sum() == 15160
        c3_cmmd = (df_p7["source_dataset"] == "crisismmd_multimodal").sum() == 955
        c3_text_only = (df_p7[df_p7["source_dataset"] == "crisismmd_multimodal"]["image_available"] == False).all()
        c3 = c3_count and c3_clex and c3_hum and c3_cmmd and c3_text_only
        dur = time.time() - t0
        record_test(
            "3. Phase 7 Crisis Intelligence",
            c3,
            "104,130 records (88,015 CrisisLex + 15,160 HumAID + 955 CrisisMMD text-only)",
            f"Total={len(df_p7)}, CrisisLex={c3_clex}, HumAID={c3_hum}, CrisisMMD={c3_cmmd}, TextOnly={c3_text_only}",
            dur,
            "data/features/crisis_information/unified_crisis_intelligence.parquet"
        )
    except Exception as e:
        record_test("3. Phase 7 Crisis Intelligence", False, "104,130 records", f"Exception: {e}", time.time() - t0, "Phase 7 outputs")

    # -------------------------------------------------------------
    # Test 4: Phase 8 Batch Pipeline & Graph Reconciled Metrics
    # -------------------------------------------------------------
    t0 = time.time()
    try:
        gx_csv = root / "data/features/phase8/graph/graphx_vertex_metrics.csv"
        df_gx = pd.read_csv(gx_csv)

        c4_events = len(p_prop_ev) == 5004
        c4_edges = len(p_prop_ed) == 4999
        c4_sources = p_prop_ev["source_node"].nunique() == 4986
        c4_targets = p_prop_ev["target_node"].dropna().nunique() == 2508
        c4_vertices = len(df_gx) == 7494
        c4 = c4_events and c4_edges and c4_sources and c4_targets and c4_vertices
        dur = time.time() - t0
        record_test(
            "4. Phase 8 Batch Pipeline Counts",
            c4,
            "Events=5,004, Edges=4,999, Sources=4,986, Non-Null Targets=2,508, Vertices=7,494",
            f"Events={len(p_prop_ev)}, Edges={len(p_prop_ed)}, Sources={p_prop_ev['source_node'].nunique()}, "
            f"Targets={p_prop_ev['target_node'].dropna().nunique()}, Vertices={len(df_gx)}",
            dur,
            "data/features/phase8/graph/graphx_vertex_metrics.csv"
        )
    except Exception as e:
        record_test("4. Phase 8 Batch Pipeline Counts", False, "7,494 vertices", f"Exception: {e}", time.time() - t0, "Phase 8 graph outputs")

    # -------------------------------------------------------------
    # Test 5: Graph Analytics Topological Metrics
    # -------------------------------------------------------------
    t0 = time.time()
    try:
        pr_finite = np.isfinite(df_gx["pagerank"]).all() and (df_gx["pagerank"] > 0).all()
        deg_valid = (df_gx["in_degree"] >= 0).all() and (df_gx["out_degree"] >= 0).all()
        num_cc = df_gx["component_id"].nunique() == 2509
        giant_size = (df_gx["component_id"] == df_gx["component_id"].value_counts().index[0]).sum() == 4986
        c5 = pr_finite and deg_valid and num_cc and giant_size
        dur = time.time() - t0
        record_test(
            "5. Graph Analytics (PageRank & Components)",
            c5,
            "PageRank finite > 0, Degrees >= 0, CC=2,509, Giant Component=4,986",
            f"PR_Finite={pr_finite}, Deg_Valid={deg_valid}, CC_Count={df_gx['component_id'].nunique()}, "
            f"Giant_Size={(df_gx['component_id'] == df_gx['component_id'].value_counts().index[0]).sum()}",
            dur,
            "docs/phase8/graphx_metrics_summary.json"
        )
    except Exception as e:
        record_test("5. Graph Analytics (PageRank & Components)", False, "Valid graph metrics", f"Exception: {e}", time.time() - t0, "GraphX outputs")

    # -------------------------------------------------------------
    # Test 6: Kafka Message Broker Integrity
    # -------------------------------------------------------------
    t0 = time.time()
    try:
        k_prod = root / "docs/phase8/kafka_producer_stats.json"
        k_cons = root / "docs/phase8/kafka_validation_summary.json"
        stat_p = json.loads(k_prod.read_text(encoding="utf-8"))
        stat_c = json.loads(k_cons.read_text(encoding="utf-8"))

        c6_prod = stat_p.get("produced_count", 0) == 5004
        c6_cons = stat_c.get("consumed_count", 0) == 5004
        c6_dups = stat_c.get("duplicate_count", -1) == 0
        c6_inval = stat_c.get("invalid_count", -1) == 0
        c6 = c6_prod and c6_cons and c6_dups and c6_inval
        dur = time.time() - t0
        record_test(
            "6. Kafka Message Broker Replay",
            c6,
            "Produced=5,004, Consumed=5,004, Duplicates=0, Invalid=0",
            f"Produced={stat_p.get('produced_count')}, Consumed={stat_c.get('consumed_count')}, "
            f"Duplicates={stat_c.get('duplicate_count')}, Invalid={stat_c.get('invalid_count')}",
            dur,
            "docs/phase8/kafka_validation_summary.json"
        )
    except Exception as e:
        record_test("6. Kafka Message Broker Replay", False, "5,004 events 0 drops", f"Exception: {e}", time.time() - t0, "Kafka logs")

    # -------------------------------------------------------------
    # Test 7: Spark Structured Streaming Tumbling Windows
    # -------------------------------------------------------------
    t0 = time.time()
    try:
        st_pq = root / "data/features/phase8/streaming/propagation_stream_metrics.parquet"
        df_st = pd.read_parquet(st_pq)
        c7_win = len(df_st) == 32
        c7_events = df_st["window_event_count"].sum() == 5004
        c7_scenarios = set(df_st["scenario_id"].unique()) == {"ORGANIC_DIFFUSION", "HIGH_VELOCITY_VIRAL", "COORDINATED_BOT_BURST"}
        c7 = c7_win and c7_events and c7_scenarios
        dur = time.time() - t0
        record_test(
            "7. Structured Streaming Window Metrics",
            c7,
            "32 windows, 5,004 windowed events across 3 scenarios",
            f"Windows={len(df_st)}, Total_Events={df_st['window_event_count'].sum()}, Scenarios={len(df_st['scenario_id'].unique())}",
            dur,
            "data/features/phase8/streaming/propagation_stream_metrics.parquet"
        )
    except Exception as e:
        record_test("7. Structured Streaming Window Metrics", False, "32 windows", f"Exception: {e}", time.time() - t0, "Streaming outputs")

    # -------------------------------------------------------------
    # Test 8: Apache Hive Warehouse SQL Queries
    # -------------------------------------------------------------
    t0 = time.time()
    try:
        h_res = root / "docs/phase8/hive_query_results.json"
        hive_data = json.loads(h_res.read_text(encoding="utf-8"))
        q_count = len(hive_data)
        q1_top_pr = hive_data.get("Query 1: Top Structurally Central Vertices (PageRank)", {}).get("result_rows", [])[0]["pagerank_score"]
        q6_overlap = hive_data.get("Query 6: Critical Cross-Stream Join Policy Verification", {}).get("result_rows", [])[0]["overlapping_keys_count"]

        c8 = (q_count >= 5 and q1_top_pr > 100.0 and q6_overlap == 0)
        dur = time.time() - t0
        record_test(
            "8. Apache Hive Warehouse Queries",
            c8,
            "6 queries executed, top PageRank > 100.0, cross-stream join overlap == 0",
            f"Queries_Executed={q_count}, Top_PR={q1_top_pr}, Overlapping_Join_Keys={q6_overlap}",
            dur,
            "docs/phase8/hive_query_results.json"
        )
    except Exception as e:
        record_test("8. Apache Hive Warehouse Queries", False, "Queries executed", f"Exception: {e}", time.time() - t0, "Hive metastore")

    # -------------------------------------------------------------
    # Test 9: Phase 9 Multi-Stream Decision Support
    # -------------------------------------------------------------
    t0 = time.time()
    try:
        p9_m = pd.read_parquet(root / "data/features/phase9/phase9_media_intelligence.parquet")
        p9_c = pd.read_parquet(root / "data/features/phase9/phase9_crisis_intelligence.parquet")
        p9_p = pd.read_parquet(root / "data/features/phase9/phase9_propagation_intelligence.parquet")
        p9_s = pd.read_parquet(root / "data/features/phase9/phase9_spatial_intelligence.parquet")
        p9_l = pd.read_parquet(root / "data/features/phase9/phase9_multi_stream_intelligence.parquet")

        c9_counts = (len(p9_m) == 77 and len(p9_c) == 104130 and len(p9_p) == 7494 and len(p9_s) == 63660 and len(p9_l) == 175361)
        # Check explicit NULL governance
        m_recs = p9_l[p9_l["stream_id"] == "STREAM_A_SYNTHETIC_MEDIA"]
        c9_nulls = m_recs["crisis_model_score"].isna().all()
        c9 = c9_counts and c9_nulls
        dur = time.time() - t0
        record_test(
            "9. Phase 9 Multi-Stream Decision Support",
            c9,
            "Media=77, Crisis=104,130, Prop=7,494, Spatial=63,660, Total Ledger=175,361, Explicit NULLs",
            f"Media={len(p9_m)}, Crisis={len(p9_c)}, Prop={len(p9_p)}, Spatial={len(p9_s)}, "
            f"Ledger={len(p9_l)}, ExplicitNulls={c9_nulls}",
            dur,
            "data/features/phase9/phase9_multi_stream_intelligence.parquet"
        )
    except Exception as e:
        record_test("9. Phase 9 Multi-Stream Decision Support", False, "175,361 rows", f"Exception: {e}", time.time() - t0, "Phase 9 ledger")

    # -------------------------------------------------------------
    # Test 10: Controlled Failure & Quality Resilience
    # -------------------------------------------------------------
    t0 = time.time()
    try:
        f_res = root / "docs/phase8/failure_testing_summary.json"
        fail_data = json.loads(f_res.read_text(encoding="utf-8"))
        t_fail_pass = all(v.get("status") == "PASS" for v in fail_data.values()) and len(fail_data) == 5
        dur = time.time() - t0
        record_test(
            "10. Controlled Failure Resilience Tests",
            t_fail_pass,
            "5/5 tests PASS (malformed JSON, duplicate event, null time, dangling edge, invalid weight)",
            f"Pass_Count={sum(1 for v in fail_data.values() if v.get('status') == 'PASS')}/5",
            dur,
            "docs/phase8/failure_testing_summary.json"
        )
    except Exception as e:
        record_test("10. Controlled Failure Resilience Tests", False, "5/5 PASS", f"Exception: {e}", time.time() - t0, "Failure tests")

    # -------------------------------------------------------------
    # Summary Evaluation
    # -------------------------------------------------------------
    total_time = time.time() - t_start
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["status"] == "PASS")
    failed_tests = total_tests - passed_tests

    print("\n" + "=" * 75)
    print(f"FUNCTIONAL ACCEPTANCE SUMMARY: {passed_tests}/{total_tests} PASSED ({total_time:.2f}s total)")
    print("=" * 75)

    return results, total_tests, passed_tests, failed_tests, total_time

if __name__ == "__main__":
    res, tot, pas, fai, dur = run_all_tests()
    sys.exit(0 if fai == 0 else 1)
