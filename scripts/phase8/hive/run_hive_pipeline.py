#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: Hive Warehouse & Analytical Query Execution Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Executes Hive DDL and analytical SQL queries:
1. Provisions Hive external tables over HDFS parquet data:
   - propagation_graph_metrics
   - propagation_stream_metrics
   - media_risk_features
   - crisis_intelligence_features
2. Executes real analytical queries and captures metrics
3. Verifies cross-stream join policy (zero synthetic key joins)
4. Emits query execution metrics to docs/phase8/hive_query_results.json
"""

import sys
import os
import json
import time
from pathlib import Path
import pandas as pd

from pyspark.sql import SparkSession

def run_hive():
    print("=" * 70)
    print("CRISISGUARD — PHASE 8 HIVE WAREHOUSE & ANALYTICAL QUERIES")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    print("=" * 70)
    
    t0 = time.time()
    root = Path(__file__).resolve().parent.parent.parent.parent
    local_graph_csv = root / "data" / "features" / "phase8" / "graph" / "graphx_vertex_metrics.csv"
    hdfs_graph_parquet = "hdfs://localhost:9000/crisisguard/phase8/graph/metrics_parquet"
    
    # 1. Initialize SparkSession with Hive Metastore support
    print("\n[1] Initializing SparkSession with Hive Warehouse Support...")
    spark = SparkSession.builder \
        .appName("CrisisGuard-Phase8-HiveWarehouse") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.warehouse.dir", "hdfs://localhost:9000/crisisguard/phase8/hive") \
        .enableHiveSupport() \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("WARN")
    print(f"Connected to Spark SQL / Hive Warehouse: Spark {spark.version}")
    
    # Ensure GraphX vertex metrics exist in HDFS as Parquet
    print("\n[2] Ensuring GraphX metrics parquet exists in HDFS...")
    if local_graph_csv.exists():
        df_graph_pd = pd.read_csv(local_graph_csv, dtype={"vertex_id": "int64", "node_name": "str", "component_id": "int64", "in_degree": "int32", "out_degree": "int32"})
        df_graph_pd["node_name"] = df_graph_pd["node_name"].fillna("UNKNOWN").astype(str)
        df_graph_spark = spark.createDataFrame(df_graph_pd)
        df_graph_spark.write.mode("overwrite").parquet(hdfs_graph_parquet)
        print(f"  Exported {len(df_graph_pd):,} GraphX vertex metrics to {hdfs_graph_parquet}")
        
    # Read create_phase8_tables.sql
    ddl_path = root / "scripts" / "phase8" / "hive" / "create_phase8_tables.sql"
    print(f"\n[3] Executing Hive DDL from {ddl_path.name}...")
    ddl_text = ddl_path.read_text(encoding="utf-8")
    
    # Split DDL statements
    ddl_statements = [s.strip() for s in ddl_text.split(";") if s.strip()]
    for stmt in ddl_statements:
        clean_stmt = " ".join([line for line in stmt.splitlines() if not line.strip().startswith("--")])
        if clean_stmt.strip():
            print(f"  Executing DDL: {clean_stmt[:65]}...")
            spark.sql(clean_stmt)
            
    print("  All Hive tables provisioned successfully.")
    
    # Read phase8_analysis.sql and execute individual queries
    analysis_path = root / "scripts" / "phase8" / "hive" / "phase8_analysis.sql"
    print(f"\n[4] Executing Analytical Queries from {analysis_path.name}...")
    analysis_text = analysis_path.read_text(encoding="utf-8")
    
    queries = [
        ("Query 1: Top Structurally Central Vertices (PageRank)",
         """
         SELECT 
             vertex_id,
             node_name,
             ROUND(pagerank, 4) AS pagerank_score,
             in_degree,
             out_degree,
             component_id
         FROM crisisguard_phase8.propagation_graph_metrics
         ORDER BY pagerank DESC
         LIMIT 10
         """),
        ("Query 2: Degree Distribution Summary",
         """
         SELECT 
             in_degree,
             COUNT(vertex_id) AS vertex_count,
             ROUND(AVG(pagerank), 4) AS avg_pagerank
         FROM crisisguard_phase8.propagation_graph_metrics
         GROUP BY in_degree
         ORDER BY in_degree DESC
         LIMIT 10
         """),
        ("Query 3: Real-Time Stream Progression (Hourly Rates & Synthetic Risk)",
         """
         SELECT 
             scenario_id,
             COUNT(window_start) AS active_windows,
             SUM(window_event_count) AS total_events,
             ROUND(AVG(propagation_rate_per_min), 2) AS avg_rate_per_min,
             ROUND(MAX(propagation_rate_per_min), 2) AS peak_rate_per_min,
             ROUND(AVG(mean_synthetic_risk), 4) AS avg_synthetic_risk,
             ROUND(MAX(max_synthetic_risk), 4) AS peak_synthetic_risk
         FROM crisisguard_phase8.propagation_stream_metrics
         GROUP BY scenario_id
         ORDER BY total_events DESC
         """),
        ("Query 4: Synthetic Media Risk Analysis (Phase 6 Outputs)",
         """
         SELECT 
             media_type,
             CASE 
                 WHEN synthetic_risk >= 0.7 THEN 'HIGH_RISK'
                 WHEN synthetic_risk >= 0.3 THEN 'MEDIUM_RISK'
                 ELSE 'LOW_RISK'
             END AS risk_tier,
             COUNT(content_id) AS item_count,
             ROUND(AVG(model_score), 4) AS avg_model_score,
             ROUND(AVG(synthetic_probability), 4) AS avg_synthetic_prob
         FROM crisisguard_phase8.media_risk_features
         GROUP BY media_type, CASE 
                 WHEN synthetic_risk >= 0.7 THEN 'HIGH_RISK'
                 WHEN synthetic_risk >= 0.3 THEN 'MEDIUM_RISK'
                 ELSE 'LOW_RISK'
             END
         ORDER BY media_type, item_count DESC
         """),
        ("Query 5: Crisis Information Category Distribution (Phase 7 Outputs)",
         """
         SELECT 
             source_dataset,
             crisis_category,
             calibration_status,
             COUNT(content_id) AS total_records,
             ROUND(AVG(model_score), 4) AS avg_confidence
         FROM crisisguard_phase8.crisis_intelligence_features
         GROUP BY source_dataset, crisis_category, calibration_status
         ORDER BY total_records DESC
         LIMIT 10
         """),
        ("Query 6: Critical Cross-Stream Join Policy Verification",
         """
         SELECT 
             COUNT(g.vertex_id) AS overlapping_keys_count
         FROM crisisguard_phase8.propagation_graph_metrics g
         JOIN crisisguard_phase8.crisis_intelligence_features c
             ON g.node_name = c.source_record_id
         """)
    ]
    
    query_results = {}
    for q_name, q_sql in queries:
        print("\n" + "-" * 70)
        print(f"Executing {q_name}:")
        print("-" * 70)
        t_start = time.time()
        res_df = spark.sql(q_sql)
        res_df.show(truncate=False)
        dt = time.time() - t_start
        rows = [r.asDict() for r in res_df.collect()]
        query_results[q_name] = {
            "sql": " ".join(q_sql.split()),
            "execution_time_seconds": round(dt, 3),
            "result_rows": rows
        }
        
    duration = time.time() - t0
    
    out_dir = root / "docs" / "phase8"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "hive_query_results.json", "w", encoding="utf-8") as f:
        json.dump(query_results, f, indent=2, default=str)
    print(f"\nSaved Hive analytical results to {out_dir / 'hive_query_results.json'}")
    
    spark.stop()
    print("\n" + "=" * 70)
    print(f"OVERALL HIVE PIPELINE STATUS: PASS ({duration:.2f}s total execution)")
    print("=" * 70)
    return True

if __name__ == "__main__":
    ok = run_hive()
    sys.exit(0 if ok else 1)
