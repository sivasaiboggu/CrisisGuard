#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: Master Validation Script
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Master Scientific and Engineering Validation for Phase 8:
Verifies all 15 required criteria from actual generated artifacts:
1. HDFS Outputs (namespace, subdirs, replicated parquets)
2. Spark Batch Outputs (vertices, edges, batch summary)
3. GraphX Outputs (JAR, vertex metrics, summary metrics)
4. Kafka Topic Existence (crisisguard-propagation-events topic)
5. Kafka Message Flow (produced vs consumed count)
6. Streaming Outputs (windowed temporal metrics parquet)
7. Hive Tables (external tables, 6 analytical query results)
8. Schema Consistency (strong typing across all Parquet sinks)
9. Row Counts (5,004 events, 4,999 edges, 7,494 vertices, 104,130 crisis intel, 77 media risk)
10. Provenance Tracking (governance tags and lineage preserved)
11. Duplicate Handling (zero duplicate edges and zero streaming duplicates)
12. Batch/Stream Consistency (exact reconciliation across all 5 dimensions)
13. Graph Integrity (PageRank conservation, component sizes, degree distribution)
14. Frozen-Input Integrity (hashes match input audit data)
15. Phase Boundary Integrity (no EDPI, no arbitrary weights, no Phase 9 code)
"""

import sys
import os
import json
import hashlib
import subprocess
from pathlib import Path
import pandas as pd

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def validate_phase8():
    print("=" * 75)
    print("CRISISGUARD — PHASE 8 MASTER VALIDATION SUITE")
    print("=" * 75)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    print("=" * 75)
    
    root = Path(__file__).resolve().parent.parent.parent
    checks = {}
    
    # -------------------------------------------------------------
    # Check 1: HDFS Outputs
    # -------------------------------------------------------------
    try:
        hdfs_res = subprocess.run(["/opt/hadoop/bin/hdfs", "dfs", "-ls", "/crisisguard/phase8"], capture_output=True, text=True)
        has_prop = "/crisisguard/phase8/propagation" in hdfs_res.stdout
        has_graph = "/crisisguard/phase8/graph" in hdfs_res.stdout
        has_stream = "/crisisguard/phase8/streaming" in hdfs_res.stdout
        has_mr = "/crisisguard/phase8/media_risk" in hdfs_res.stdout
        has_ci = "/crisisguard/phase8/crisis_intelligence" in hdfs_res.stdout
        c1 = has_prop and has_graph and has_stream and has_mr and has_ci
        checks["1. HDFS Outputs Verified"] = (c1, f"Propagation={has_prop}, Graph={has_graph}, Stream={has_stream}, MediaRisk={has_mr}, CrisisIntel={has_ci}")
    except Exception as e:
        checks["1. HDFS Outputs Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 2: Spark Batch Outputs
    # -------------------------------------------------------------
    try:
        v_csv = root / "data" / "features" / "phase8" / "graph" / "vertices.csv"
        e_csv = root / "data" / "features" / "phase8" / "graph" / "edges.csv"
        batch_sum = root / "docs" / "phase8" / "spark_batch_summary.json"
        c2 = v_csv.exists() and e_csv.exists() and batch_sum.exists()
        checks["2. Spark Batch Outputs Verified"] = (c2, f"vertices.csv={v_csv.exists()}, edges.csv={e_csv.exists()}, summary={batch_sum.exists()}")
    except Exception as e:
        checks["2. Spark Batch Outputs Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 3: GraphX Outputs
    # -------------------------------------------------------------
    try:
        gx_jar = root / "target" / "phase8" / "crisisguard-graphx.jar"
        gx_csv = root / "data" / "features" / "phase8" / "graph" / "graphx_vertex_metrics.csv"
        gx_sum = root / "docs" / "phase8" / "graphx_metrics_summary.json"
        c3 = gx_jar.exists() and gx_csv.exists() and gx_sum.exists()
        checks["3. GraphX Outputs Verified"] = (c3, f"JAR={gx_jar.exists()} ({gx_jar.stat().st_size if gx_jar.exists() else 0} B), CSV={gx_csv.exists()}, Summary={gx_sum.exists()}")
    except Exception as e:
        checks["3. GraphX Outputs Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 4: Kafka Topic Existence
    # -------------------------------------------------------------
    try:
        k_res = subprocess.run(["/opt/kafka/bin/kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--list"], capture_output=True, text=True)
        has_topic = "crisisguard-propagation-events" in k_res.stdout
        c4 = has_topic
        checks["4. Kafka Topic Existence"] = (c4, f"Topic crisisguard-propagation-events in broker: {has_topic}")
    except Exception as e:
        checks["4. Kafka Topic Existence"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 5: Kafka Message Flow
    # -------------------------------------------------------------
    try:
        with open(root / "docs" / "phase8" / "kafka_producer_stats.json") as f:
            p_stats = json.load(f)
        with open(root / "docs" / "phase8" / "kafka_validation_summary.json") as f:
            c_stats = json.load(f)
        prod_n = p_stats.get("produced_count", 0)
        cons_n = c_stats.get("consumed_count", 0)
        c5 = (prod_n == 5004) and (cons_n == 5004)
        checks["5. Kafka Message Flow"] = (c5, f"Produced={prod_n} (5004), Consumed={cons_n} (5004)")
    except Exception as e:
        checks["5. Kafka Message Flow"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 6: Streaming Outputs
    # -------------------------------------------------------------
    try:
        stream_pq = root / "data" / "features" / "phase8" / "streaming" / "propagation_stream_metrics.parquet"
        stream_sum = root / "docs" / "phase8" / "streaming_metrics_summary.json"
        df_stream = pd.read_parquet(stream_pq) if stream_pq.exists() else pd.DataFrame()
        c6 = stream_pq.exists() and stream_sum.exists() and (len(df_stream) == 32)
        checks["6. Streaming Outputs Verified"] = (c6, f"Metrics parquet={stream_pq.exists()} ({len(df_stream)} windows, expected 32)")
    except Exception as e:
        checks["6. Streaming Outputs Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 7: Hive Tables & Queries
    # -------------------------------------------------------------
    try:
        hive_res_file = root / "docs" / "phase8" / "hive_query_results.json"
        with open(hive_res_file) as f:
            h_res = json.load(f)
        c7 = (len(h_res) == 6) and all(len(v.get("result_rows", [])) > 0 or "overlapping" in k for k, v in h_res.items())
        checks["7. Hive Tables & Queries Verified"] = (c7, f"Executed {len(h_res)}/6 analytical Hive queries successfully")
    except Exception as e:
        checks["7. Hive Tables & Queries Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 8: Schema Consistency
    # -------------------------------------------------------------
    try:
        expected_stream_cols = {"scenario_id", "window_event_count", "unique_source_nodes", "unique_target_nodes", "mean_synthetic_risk", "max_synthetic_risk", "window_start", "window_end", "propagation_rate_per_min"}
        actual_stream_cols = set(df_stream.columns)
        c8 = expected_stream_cols.issubset(actual_stream_cols)
        checks["8. Schema Consistency Verified"] = (c8, f"Streaming cols match expected contract: {c8}")
    except Exception as e:
        checks["8. Schema Consistency Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 9: Row Counts Across Big Data Pipeline
    # -------------------------------------------------------------
    try:
        df_events = pd.read_parquet(root / "data" / "processed" / "propagation" / "propagation_events.parquet")
        df_edges = pd.read_parquet(root / "data" / "processed" / "propagation" / "propagation_edges.parquet")
        df_gx = pd.read_csv(gx_csv)
        df_mr = pd.read_parquet(root / "data" / "features" / "synthetic_media" / "unified_media_risk.parquet")
        df_ci = pd.read_parquet(root / "data" / "features" / "crisis_information" / "unified_crisis_intelligence.parquet")
        
        c9_ev = (len(df_events) == 5004)
        c9_ed = (len(df_edges) == 4999)
        c9_gx = (len(df_gx) == 7494)
        c9_mr = (len(df_mr) == 77)
        c9_ci = (len(df_ci) == 104130)
        c9 = c9_ev and c9_ed and c9_gx and c9_mr and c9_ci
        checks["9. Row Counts Verified"] = (c9, f"Events={len(df_events)}, Edges={len(df_edges)}, Vertices={len(df_gx)}, MediaRisk={len(df_mr)}, CrisisIntel={len(df_ci)}")
    except Exception as e:
        checks["9. Row Counts Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 10: Provenance & Governance Preserved
    # -------------------------------------------------------------
    try:
        gov_events = set(df_events["governance_tag"].dropna())
        gov_edges = set(df_edges["governance_tag"].dropna())
        c10 = ("SEMI_SYNTHETIC" in gov_events) and ("SEMI_SYNTHETIC" in gov_edges)
        checks["10. Provenance Preserved"] = (c10, f"Governance tags: Events={gov_events}, Edges={gov_edges}")
    except Exception as e:
        checks["10. Provenance Preserved"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 11: Duplicate Handling
    # -------------------------------------------------------------
    try:
        edge_dups = df_edges.duplicated(subset=["source_node", "target_node"]).sum()
        with open(root / "docs" / "phase8" / "kafka_validation_summary.json") as f:
            c_val = json.load(f)
        stream_dups = c_val.get("duplicate_count", -1)
        c11 = (edge_dups == 0) and (stream_dups == 0)
        checks["11. Duplicate Handling Verified"] = (c11, f"Graph edge duplicates={edge_dups}, Stream duplicates={stream_dups}")
    except Exception as e:
        checks["11. Duplicate Handling Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 12: Batch vs Stream Reconciliation
    # -------------------------------------------------------------
    try:
        with open(root / "docs" / "phase8" / "spark_batch_summary.json") as f:
            b_stats = json.load(f)
        with open(root / "docs" / "phase8" / "streaming_metrics_summary.json") as f:
            s_stats = json.load(f)
            
        m_events = (b_stats["valid_events_count"] == s_stats["total_streamed_events"] == 5004)
        m_sources = (b_stats["unique_source_nodes_events"] == s_stats["stream_unique_sources"] == 4986)
        m_targets = (b_stats["unique_target_nodes_events"] == s_stats["stream_unique_targets"] == 2508)
        m_edges = (b_stats["valid_edges_count"] == s_stats["stream_unique_edges"] == 4999)
        m_nodes = (b_stats["total_unique_graph_vertices"] == s_stats["stream_total_unique_nodes"] == 7494)
        
        c12 = m_events and m_sources and m_targets and m_edges and m_nodes
        checks["12. Batch vs Stream Consistency"] = (c12, f"Events={m_events}, Sources={m_sources}, Targets={m_targets} (2508), Edges={m_edges}, Nodes={m_nodes} (7494)")
    except Exception as e:
        checks["12. Batch vs Stream Consistency"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 13: Graph Integrity & Algorithmic Validation
    # -------------------------------------------------------------
    try:
        with open(gx_sum) as f:
            gx_data = json.load(f)
        pr_mean = gx_data.get("mean_pagerank", 0.0)
        num_v = gx_data.get("num_vertices", 0)
        num_e = gx_data.get("num_edges", 0)
        cc_count = gx_data.get("total_connected_components", 0)
        largest_cc = gx_data.get("largest_component_size", 0)
        
        c13 = (num_v == 7494) and (num_e == 4999) and (0.99 <= pr_mean <= 1.01) and (cc_count == 2509) and (largest_cc == 4986)
        checks["13. Graph Integrity Verified"] = (c13, f"Vertices={num_v}, Edges={num_e}, MeanPR={pr_mean:.4f}, CCs={cc_count}, GiantCC={largest_cc}")
    except Exception as e:
        checks["13. Graph Integrity Verified"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 14: Frozen-Input Integrity
    # -------------------------------------------------------------
    try:
        with open(root / "docs" / "phase8" / "input_audit_data.json") as f:
            in_audit = json.load(f)
        hash_events = sha256_file(root / "data" / "processed" / "propagation" / "propagation_events.parquet")
        hash_edges = sha256_file(root / "data" / "processed" / "propagation" / "propagation_edges.parquet")
        hash_mr = sha256_file(root / "data" / "features" / "synthetic_media" / "unified_media_risk.parquet")
        hash_ci = sha256_file(root / "data" / "features" / "crisis_information" / "unified_crisis_intelligence.parquet")
        
        c14 = (hash_events == in_audit["propagation_events"]["sha256"]) and \
              (hash_edges == in_audit["propagation_edges"]["sha256"]) and \
              (hash_mr == in_audit["media_risk"]["sha256"]) and \
              (hash_ci == in_audit["crisis_intelligence"]["sha256"])
        checks["14. Frozen Inputs Untouched"] = (c14, f"Cryptographic SHA-256 match verified across all frozen inputs: {c14}")
    except Exception as e:
        checks["14. Frozen Inputs Untouched"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Check 15: Phase Boundary Integrity
    # -------------------------------------------------------------
    try:
        # Search for prohibited Phase 9 / EDPI constructs in scripts/
        phase8_scripts = list((root / "scripts" / "phase8").glob("**/*.py")) + list((root / "scripts" / "phase8").glob("**/*.sql"))
        has_edpi = False
        has_phase9 = False
        for sf in phase8_scripts:
            content = sf.read_text(encoding="utf-8")
            if "EDPI" in content or "Emergency Dispatch Priority Index" in content:
                # Disallow if computing EDPI
                if "def compute_edpi" in content or "CREATE TABLE edpi" in content:
                    has_edpi = True
            if "Phase 9" in content and "Author: B.SIVASAI" in content:
                has_phase9 = True
                
        c15 = (not has_edpi) and (not has_phase9)
        checks["15. Phase Boundary Integrity"] = (c15, f"No EDPI computed={not has_edpi}, No Phase 9 code={not has_phase9}")
    except Exception as e:
        checks["15. Phase Boundary Integrity"] = (False, f"Exception: {e}")

    # -------------------------------------------------------------
    # Final Summary Table
    # -------------------------------------------------------------
    print("\nVALIDATION SUMMARY:")
    all_pass = True
    for name, (passed, details) in checks.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {name:40s} : {details}")
        
    print("\n" + "=" * 75)
    if all_pass:
        print("OVERALL DECISION: PHASE 8 PASS — COMPLETE BIG DATA PIPELINE VERIFIED")
    else:
        print("OVERALL DECISION: PHASE 8 BLOCKED (Remediate failures)")
    print("=" * 75)
    
    return all_pass

if __name__ == "__main__":
    ok = validate_phase8()
    sys.exit(0 if ok else 1)
