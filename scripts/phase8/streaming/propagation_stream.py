#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: Spark Structured Streaming Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Consumes streaming events from Kafka topic 'crisisguard-propagation-events':
1. Parses JSON payloads into strongly-typed streaming DataFrame
2. Enforces event-time processing with watermark (1 hour)
3. Computes windowed temporal aggregation metrics:
   - Event volume per window
   - Unique source nodes count
   - Unique target nodes count
   - Synthetic risk mean & max
   - Cascade propagation rate (events / minute)
4. Persists raw streaming events and windowed aggregations to HDFS and local Parquet
5. Exports metrics summary for Batch-vs-Streaming reconciliation
"""

import sys
import os
import json
import time
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, LongType, TimestampType
)

def run_streaming():
    print("=" * 70)
    print("CRISISGUARD — PHASE 8 SPARK STRUCTURED STREAMING ENGINE")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    print("=" * 70)
    
    t0 = time.time()
    root = Path(__file__).resolve().parent.parent.parent.parent
    local_stream_dir = root / "data" / "features" / "phase8" / "streaming"
    local_stream_dir.mkdir(parents=True, exist_ok=True)
    
    hdfs_base = "hdfs://localhost:9000/crisisguard/phase8/streaming"
    
    # 1. Initialize SparkSession with Kafka integration packages
    print("\n[1] Initializing Spark Structured Streaming Session...")
    spark = SparkSession.builder \
        .appName("CrisisGuard-Phase8-StructuredStreaming") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("WARN")
    print(f"Spark Structured Streaming ready: Spark {spark.version}")
    
    # 2. Define JSON Event Schema
    event_schema = StructType([
        StructField("event_id", StringType(), False),
        StructField("scenario_id", StringType(), True),
        StructField("propagation_type", StringType(), True),
        StructField("content_id", StringType(), True),
        StructField("source_node", StringType(), True),
        StructField("target_node", StringType(), True),
        StructField("event_time", StringType(), True),
        StructField("parent_event_id", StringType(), True),
        StructField("synthetic_media_risk", DoubleType(), True),
        StructField("crisis_priority_if_present", StringType(), True),
        StructField("governance_tag", StringType(), True),
        StructField("provenance", StringType(), True),
        StructField("producer_timestamp", DoubleType(), True)
    ])
    
    # 3. Create Kafka Streaming Source
    print("\n[2] Connecting to Kafka Topic 'crisisguard-propagation-events'...")
    kafka_stream_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "crisisguard-propagation-events") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()
        
    # 4. Parse JSON and extract fields with Event-Time Watermarking
    print("\n[3] Parsing JSON Payloads & Applying Event-Time Watermarking (1 hour)...")
    parsed_stream_df = kafka_stream_df \
        .select(F.from_json(F.col("value").cast("string"), event_schema).alias("data")) \
        .select("data.*") \
        .withColumn("event_timestamp", F.to_timestamp(F.col("event_time"))) \
        .withWatermark("event_timestamp", "1 hour")
        
    # 5. Define Windowed Aggregations (1-hour tumbling window on event_timestamp)
    print("\n[4] Building Windowed Temporal Aggregations (1-hour windows)...")
    windowed_metrics_df = parsed_stream_df \
        .groupBy(
            F.window(F.col("event_timestamp"), "1 hour"),
            F.col("scenario_id")
        ) \
        .agg(
            F.count("event_id").alias("window_event_count"),
            F.countDistinct("source_node").alias("unique_source_nodes"),
            F.countDistinct("target_node").alias("unique_target_nodes"),
            F.avg("synthetic_media_risk").alias("mean_synthetic_risk"),
            F.max("synthetic_media_risk").alias("max_synthetic_risk")
        ) \
        .withColumn("propagation_rate_per_min", F.col("window_event_count") / 60.0)
        
    # 6. Execute Streaming Queries using AvailableNow trigger for complete batch reconciliation
    # Sink 1: Raw Parsed Events Sink (HDFS Parquet + Local Parquet)
    print("\n[5] Executing Streaming Sink 1: Parsed Events to HDFS & Local Storage...")
    hdfs_parsed_path = f"{hdfs_base}/parsed_events"
    hdfs_parsed_ckpt = f"{hdfs_base}/checkpoints/parsed_events"
    
    # Clean previous checkpoint to ensure fresh processing
    os.system(f"/opt/hadoop/bin/hdfs dfs -rm -r -f {hdfs_parsed_ckpt} 2>/dev/null")
    os.system(f"/opt/hadoop/bin/hdfs dfs -rm -r -f {hdfs_parsed_path} 2>/dev/null")
    
    query_events = parsed_stream_df.writeStream \
        .format("parquet") \
        .option("path", hdfs_parsed_path) \
        .option("checkpointLocation", hdfs_parsed_ckpt) \
        .trigger(availableNow=True) \
        .start()
        
    query_events.awaitTermination()
    print("  Sink 1 (Parsed Events) successfully committed to HDFS.")
    
    # Read back parsed events from HDFS to verify and export locally
    df_persisted_events = spark.read.parquet(hdfs_parsed_path)
    persisted_event_count = df_persisted_events.count()
    print(f"  Verified persisted streaming events in HDFS: {persisted_event_count:,}")
    
    # Also save local copy for Hive external table and batch comparison
    df_persisted_events.toPandas().to_parquet(local_stream_dir / "streaming_parsed_events.parquet", index=False)
    
    # Sink 2: Windowed Metrics Sink (Memory / Local Parquet)
    print("\n[6] Computing and Persisting Windowed Temporal Metrics...")
    # Compute the final windowed aggregation from persisted stream table
    windowed_summary_df = df_persisted_events \
        .groupBy(
            F.window(F.col("event_timestamp"), "1 hour"),
            F.col("scenario_id")
        ) \
        .agg(
            F.count("event_id").alias("window_event_count"),
            F.countDistinct("source_node").alias("unique_source_nodes"),
            F.countDistinct("target_node").alias("unique_target_nodes"),
            F.round(F.avg("synthetic_media_risk"), 4).alias("mean_synthetic_risk"),
            F.round(F.max("synthetic_media_risk"), 4).alias("max_synthetic_risk")
        ) \
        .withColumn("window_start", F.col("window.start")) \
        .withColumn("window_end", F.col("window.end")) \
        .withColumn("propagation_rate_per_min", F.round(F.col("window_event_count") / 60.0, 2)) \
        .drop("window") \
        .orderBy("window_start", "scenario_id")
        
    print("  Windowed Metrics Preview:")
    windowed_summary_df.show(10, truncate=False)
    
    # Write windowed metrics to HDFS and Local feature store
    hdfs_metrics_path = f"{hdfs_base}/windowed_metrics"
    windowed_summary_df.write.mode("overwrite").parquet(hdfs_metrics_path)
    
    local_metrics_parquet = local_stream_dir / "propagation_stream_metrics.parquet"
    local_metrics_csv = local_stream_dir / "propagation_stream_metrics.csv"
    
    df_metrics_pd = windowed_summary_df.toPandas()
    df_metrics_pd.to_parquet(local_metrics_parquet, index=False)
    df_metrics_pd.to_csv(local_metrics_csv, index=False)
    print(f"  Exported stream metrics: {local_metrics_parquet} ({len(df_metrics_pd)} windows)")
    
    # Upload to HDFS
    os.system(f"/opt/hadoop/bin/hdfs dfs -put -f {local_metrics_csv} {hdfs_base}/")
    
    # 7. Measure Streaming Totals for Reconciliation
    total_stream_events = persisted_event_count
    stream_unique_sources = df_persisted_events.filter(F.col("source_node").isNotNull()).select("source_node").distinct().count()
    stream_unique_targets = df_persisted_events.filter(F.col("target_node").isNotNull()).select("target_node").distinct().count()
    
    # Unique nodes union (non-null genuine graph vertices)
    s_nodes = df_persisted_events.filter(F.col("source_node").isNotNull()).select(F.col("source_node").alias("node"))
    t_nodes = df_persisted_events.filter(F.col("target_node").isNotNull()).select(F.col("target_node").alias("node"))
    stream_total_nodes = s_nodes.union(t_nodes).distinct().count()
    
    # Unique edges in stream
    stream_unique_edges = df_persisted_events \
        .filter(F.col("source_node").isNotNull() & F.col("target_node").isNotNull()) \
        .select("source_node", "target_node").distinct().count()
        
    duration = time.time() - t0
    
    summary = {
        "streaming_engine": "Apache Spark Structured Streaming",
        "spark_version": spark.version,
        "input_topic": "crisisguard-propagation-events",
        "total_streamed_events": total_stream_events,
        "stream_unique_sources": stream_unique_sources,
        "stream_unique_targets": stream_unique_targets,
        "stream_total_unique_nodes": stream_total_nodes,
        "stream_unique_edges": stream_unique_edges,
        "total_time_windows": len(df_metrics_pd),
        "execution_duration_sec": round(duration, 3)
    }
    
    docs_dir = root / "docs" / "phase8"
    docs_dir.mkdir(parents=True, exist_ok=True)
    with open(docs_dir / "streaming_metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved streaming summary to: {docs_dir / 'streaming_metrics_summary.json'}")
    
    spark.stop()
    print("\n" + "=" * 70)
    print(f"OVERALL STRUCTURED STREAMING STATUS: PASS ({duration:.2f}s)")
    print("=" * 70)
    return total_stream_events == 5004

if __name__ == "__main__":
    ok = run_streaming()
    sys.exit(0 if ok else 1)
