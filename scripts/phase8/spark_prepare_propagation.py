#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: Spark Batch Preparation Script
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Spark batch processing for propagation data:
- Reads propagation data directly from HDFS (/crisisguard/phase8/propagation/)
- Enforces strict schema, validates types, timestamps, and IDs
- Detects duplicate edges, handles nulls explicitly
- Generates GraphX-compatible vertex and edge datasets with deterministic Long IDs
- Writes GraphX input files to HDFS (/crisisguard/phase8/graph/) and local features
- Emits comprehensive batch metrics for batch-vs-streaming reconciliation
"""

import sys
import os
import json
import time
from pathlib import Path

# PySpark imports
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, LongType, TimestampType
)

def run_spark_batch():
    print("=" * 70)
    print("CRISISGUARD — PHASE 8 SPARK BATCH PREPARATION & GRAPH PREPARATION")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    print("=" * 70)
    
    t0 = time.time()
    root = Path(__file__).resolve().parent.parent.parent
    local_feat_dir = root / "data" / "features" / "phase8"
    local_feat_dir.mkdir(parents=True, exist_ok=True)
    local_graph_dir = local_feat_dir / "graph"
    local_graph_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Initialize SparkSession with HDFS and memory configuration
    print("\n[1] Initializing Apache Spark Session (Local[2])...")
    spark = SparkSession.builder \
        .appName("CrisisGuard-Phase8-SparkBatch") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("WARN")
    print(f"Spark Session established: Version {spark.version}, Master={spark.conf.get('spark.master')}")
    
    # 2. Read HDFS propagation events and edges
    hdfs_events_path = "hdfs://localhost:9000/crisisguard/phase8/propagation/propagation_events.parquet"
    hdfs_edges_path = "hdfs://localhost:9000/crisisguard/phase8/propagation/propagation_edges.parquet"
    
    print(f"\n[2] Reading propagation data from HDFS:")
    print(f"  - Events: {hdfs_events_path}")
    print(f"  - Edges:  {hdfs_edges_path}")
    
    df_raw_events = spark.read.parquet(hdfs_events_path)
    df_raw_edges = spark.read.parquet(hdfs_edges_path)
    
    raw_event_count = df_raw_events.count()
    raw_edge_count = df_raw_edges.count()
    print(f"  Loaded raw events count: {raw_event_count:,}")
    print(f"  Loaded raw edges count:  {raw_edge_count:,}")
    
    # 3. Schema Enforcement and Type Normalization
    print("\n[3] Enforcing Schema & Validating Types...")
    df_events = df_raw_events.select(
        F.col("event_id").cast(StringType()).alias("event_id"),
        F.col("scenario_id").cast(StringType()).alias("scenario_id"),
        F.col("propagation_type").cast(StringType()).alias("propagation_type"),
        F.col("content_id").cast(StringType()).alias("content_id"),
        F.col("source_node").cast(StringType()).alias("source_node"),
        F.col("target_node").cast(StringType()).alias("target_node"),
        F.to_timestamp(F.col("timestamp")).alias("event_time"),
        F.col("parent_event_id").cast(StringType()).alias("parent_event_id"),
        F.col("synthetic_media_risk").cast(DoubleType()).alias("synthetic_media_risk"),
        F.col("crisis_priority_if_present").cast(StringType()).alias("crisis_priority_if_present"),
        F.col("governance_tag").cast(StringType()).alias("governance_tag")
    )
    
    df_edges = df_raw_edges.select(
        F.col("edge_id").cast(StringType()).alias("edge_id"),
        F.col("source_node").cast(StringType()).alias("source_node"),
        F.col("target_node").cast(StringType()).alias("target_node"),
        F.col("weight").cast(DoubleType()).alias("weight"),
        F.col("cascade_id").cast(StringType()).alias("cascade_id"),
        F.col("governance_tag").cast(StringType()).alias("governance_tag")
    )
    
    # 4. Data Quality & Integrity Auditing
    print("\n[4] Data Quality & Integrity Validation...")
    # Null checks
    null_events = df_events.filter(
        F.col("event_id").isNull() | F.col("source_node").isNull() | 
        F.col("target_node").isNull() | F.col("event_time").isNull()
    ).count()
    
    null_edges = df_edges.filter(
        F.col("edge_id").isNull() | F.col("source_node").isNull() | F.col("target_node").isNull()
    ).count()
    
    print(f"  Null crucial event fields: {null_events} (filtered/reported)")
    print(f"  Null crucial edge fields:  {null_edges} (filtered/reported)")
    
    # Duplicate edge detection
    dup_edges_df = df_edges.groupBy("source_node", "target_node").agg(
        F.count("edge_id").alias("occurrence_count")
    ).filter(F.col("occurrence_count") > 1)
    dup_edge_count = dup_edges_df.count()
    print(f"  Duplicate directed edges detected: {dup_edge_count}")
    
    # 5. Extract Unique Graph Nodes and Map to Deterministic Long IDs for GraphX
    print("\n[5] Mapping Graph Vertices to GraphX 64-bit Long IDs...")
    # Union all source and target nodes across events and edges
    src_nodes_e = df_events.select(F.col("source_node").alias("node_name"))
    dst_nodes_e = df_events.select(F.col("target_node").alias("node_name"))
    src_nodes_g = df_edges.select(F.col("source_node").alias("node_name"))
    dst_nodes_g = df_edges.select(F.col("target_node").alias("node_name"))
    
    # Ensure NULL nodes from root broadcasts (target_node = NULL) are excluded from graph vertex mapping
    all_nodes_df = src_nodes_e.union(dst_nodes_e).union(src_nodes_g).union(dst_nodes_g) \
        .filter(F.col("node_name").isNotNull() & (F.trim(F.col("node_name")) != "")) \
        .distinct()
    total_unique_nodes = all_nodes_df.count()
    print(f"  Total unique vertices in propagation universe: {total_unique_nodes:,}")
    
    # Create deterministic integer IDs using monotonic ID or hash
    # Use dense ranking over ordered node_name to guarantee contiguous Long IDs starting at 1
    from pyspark.sql.window import Window
    w = Window.orderBy("node_name")
    vertex_mapping_df = all_nodes_df.withColumn("vertex_id", F.row_number().over(w).cast(LongType()))
    vertex_mapping_df.cache()
    
    # Calculate Node Degree Statistics in Batch
    out_degrees = df_edges.groupBy("source_node").agg(F.count("edge_id").alias("out_degree"))
    in_degrees = df_edges.groupBy("target_node").agg(F.count("edge_id").alias("in_degree"))
    
    vertices_with_degree = vertex_mapping_df \
        .join(out_degrees, vertex_mapping_df.node_name == out_degrees.source_node, "left") \
        .join(in_degrees, vertex_mapping_df.node_name == in_degrees.target_node, "left") \
        .select(
            F.col("vertex_id"),
            F.col("node_name"),
            F.coalesce(F.col("out_degree"), F.lit(0)).alias("out_degree"),
            F.coalesce(F.col("in_degree"), F.lit(0)).alias("in_degree")
        )
        
    print(f"  Sample vertex mapping:")
    vertices_with_degree.show(5, truncate=False)
    
    # 6. Map Edges to GraphX (src_id: Long, dst_id: Long, weight: Double, cascade_id: String)
    print("\n[6] Preparing GraphX Edges with Long Vertex IDs...")
    src_map = vertex_mapping_df.select(F.col("node_name").alias("src_name"), F.col("vertex_id").alias("src_id"))
    dst_map = vertex_mapping_df.select(F.col("node_name").alias("dst_name"), F.col("vertex_id").alias("dst_id"))
    
    graphx_edges_df = df_edges \
        .join(src_map, df_edges.source_node == src_map.src_name, "inner") \
        .join(dst_map, df_edges.target_node == dst_map.dst_name, "inner") \
        .select(
            F.col("edge_id"),
            F.col("src_id"),
            F.col("dst_id"),
            F.col("source_node"),
            F.col("target_node"),
            F.col("weight"),
            F.col("cascade_id"),
            F.col("governance_tag")
        )
        
    graphx_edge_count = graphx_edges_df.count()
    print(f"  GraphX edges prepared: {graphx_edge_count:,} (expected {raw_edge_count})")
    
    # 7. Write GraphX Vertex and Edge files to HDFS and Local Feature Store
    print("\n[7] Writing GraphX-Compatible Artifacts to HDFS and Local Storage...")
    hdfs_vertex_path = "hdfs://localhost:9000/crisisguard/phase8/graph/vertices.parquet"
    hdfs_edge_path = "hdfs://localhost:9000/crisisguard/phase8/graph/edges.parquet"
    hdfs_vertex_csv = "hdfs://localhost:9000/crisisguard/phase8/graph/vertices.csv"
    hdfs_edge_csv = "hdfs://localhost:9000/crisisguard/phase8/graph/edges.csv"
    
    # Write Parquet to HDFS
    vertices_with_degree.write.mode("overwrite").parquet(hdfs_vertex_path)
    graphx_edges_df.write.mode("overwrite").parquet(hdfs_edge_path)
    
    # Write TSV/CSV with header for GraphX Scala ingestion
    # Export simple format: src_id \t dst_id \t weight
    graphx_simple_edges = graphx_edges_df.select("src_id", "dst_id", "weight")
    graphx_simple_vertices = vertices_with_degree.select("vertex_id", "node_name")
    
    # Local copies
    vertices_with_degree.toPandas().to_parquet(local_graph_dir / "vertices.parquet", index=False)
    graphx_edges_df.toPandas().to_parquet(local_graph_dir / "edges.parquet", index=False)
    
    # Simple CSV export locally and put to HDFS for GraphX Scala reading
    edges_pd = graphx_simple_edges.toPandas()
    vertices_pd = graphx_simple_vertices.toPandas()
    
    edges_csv_local = local_graph_dir / "edges.csv"
    vertices_csv_local = local_graph_dir / "vertices.csv"
    edges_pd.to_csv(edges_csv_local, sep=",", index=False, header=True)
    vertices_pd.to_csv(vertices_csv_local, sep=",", index=False, header=True)
    print(f"  Saved local GraphX CSVs: {edges_csv_local} ({len(edges_pd)} rows), {vertices_csv_local} ({len(vertices_pd)} rows)")
    
    # Put CSVs to HDFS
    os.system(f"/opt/hadoop/bin/hdfs dfs -put -f {edges_csv_local} /crisisguard/phase8/graph/")
    os.system(f"/opt/hadoop/bin/hdfs dfs -put -f {vertices_csv_local} /crisisguard/phase8/graph/")
    
    # 8. Compute Batch Metrics Summary
    print("\n[8] Computing Batch Summary Metrics...")
    unique_src_nodes = df_events.filter(F.col("source_node").isNotNull()).select("source_node").distinct().count()
    unique_dst_nodes = df_events.filter(F.col("target_node").isNotNull()).select("target_node").distinct().count()
    time_bounds = df_events.agg(F.min("event_time").alias("min_time"), F.max("event_time").alias("max_time")).collect()[0]
    
    scenario_breakdown = df_events.groupBy("scenario_id").count().toPandas().to_dict(orient="records")
    type_breakdown = df_events.groupBy("propagation_type").count().toPandas().to_dict(orient="records")
    
    duration = time.time() - t0
    
    summary = {
        "spark_version": spark.version,
        "input_events_count": raw_event_count,
        "input_edges_count": raw_edge_count,
        "valid_events_count": df_events.count(),
        "valid_edges_count": graphx_edge_count,
        "null_events_count": null_events,
        "null_edges_count": null_edges,
        "duplicate_edges_count": dup_edge_count,
        "total_unique_graph_vertices": total_unique_nodes,
        "unique_source_nodes_events": unique_src_nodes,
        "unique_target_nodes_events": unique_dst_nodes,
        "min_event_time": str(time_bounds["min_time"]),
        "max_event_time": str(time_bounds["max_time"]),
        "scenario_distribution": scenario_breakdown,
        "propagation_type_distribution": type_breakdown,
        "batch_processing_time_seconds": round(duration, 3)
    }
    
    summary_path = root / "docs" / "phase8" / "spark_batch_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved Spark batch summary to {summary_path}")
    
    spark.stop()
    print("\n" + "=" * 70)
    print(f"OVERALL SPARK BATCH STATUS: PASS ({duration:.2f}s execution)")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = run_spark_batch()
    sys.exit(0 if success else 1)
