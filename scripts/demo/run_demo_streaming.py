#!/usr/bin/env python3
"""
CrisisGuard — Demo Spark Structured Streaming Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Live Demonstration Streaming Consumer:
1. Consumes dynamically injected events from Kafka topic (default: 'crisisguard-demo-events')
2. Parses strongly-typed JSON records
3. Enforces 1-hour event-time watermark
4. Commits streaming micro-batches to isolated demo storage
5. Computes 1-hour tumbling window temporal aggregations:
   - window_event_count
   - unique_source_nodes
   - unique_target_nodes
   - mean_synthetic_risk & max_synthetic_risk
   - propagation_rate_per_min
6. Persists raw and windowed metrics to local Parquet and HDFS (/crisisguard/demo/streaming/)
7. Displays formatted live tables in console for professor demonstration
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path

def run_streaming(args):
    print("=" * 70)
    print("CRISISGUARD — DEMO SPARK STRUCTURED STREAMING ENGINE")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print(f"Target Kafka Topic: {args.topic}")
    print(f"Broker Servers:     {args.bootstrap_servers}")
    print(f"Execution Mode:     {'Single Trigger (AvailableNow)' if args.once else f'Timed Stream ({args.duration}s)'}")
    print("=" * 70)

    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import (
        StructType, StructField, StringType, DoubleType, LongType, TimestampType
    )

    root = Path(__file__).resolve().parent.parent.parent
    local_demo_dir = root / "data" / "demo" / "streaming"
    raw_dir = local_demo_dir / "raw_events"
    metrics_dir = local_demo_dir / "windowed_metrics"
    ckpt_dir = local_demo_dir / "checkpoints" / "stream_events"

    raw_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    hdfs_base = "hdfs://localhost:9000/crisisguard/demo/streaming"

    print("\n[1] Initializing Apache Spark Structured Streaming...")
    spark = SparkSession.builder \
        .appName("CrisisGuard-Demo-Streaming") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    print(f"Spark Engine Active: version {spark.version}")

    # Schema definition
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

    print(f"\n[2] Connecting to Kafka Stream (topic: '{args.topic}')...")
    kafka_stream_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", args.bootstrap_servers) \
        .option("subscribe", args.topic) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()

    print("[3] Parsing JSON payloads & Applying 1-Hour Event-Time Watermarking...")
    parsed_stream_df = kafka_stream_df \
        .select(F.from_json(F.col("value").cast("string"), event_schema).alias("data")) \
        .select("data.*") \
        .withColumn("event_timestamp", F.to_timestamp(F.col("event_time"))) \
        .withWatermark("event_timestamp", "1 hour")

    # In single trigger mode or timed execution, persist parsed events to local and HDFS
    print("\n[4] Consuming streaming events into demo feature store...")
    query = parsed_stream_df.writeStream \
        .format("parquet") \
        .option("path", str(raw_dir)) \
        .option("checkpointLocation", str(ckpt_dir))

    if args.once:
        active_q = query.trigger(availableNow=True).start()
        active_q.awaitTermination()
    else:
        active_q = query.start()
        print(f"Streaming query running. Listening for events for {args.duration}s...")
        time.sleep(args.duration)
        active_q.stop()

    print("  Streaming sink committed successfully.")

    # Read back persisted raw events to compute exact window aggregations and summary
    print("\n[5] Computing 1-Hour Tumbling Window Aggregations...")
    try:
        df_persisted = spark.read.parquet(str(raw_dir))
        total_events = df_persisted.count()
        print(f"  Total Ingested Events: {total_events:,}")

        if total_events > 0:
            print("\nLatest Ingested Events Preview:")
            df_persisted.select(
                "event_id", "scenario_id", "source_node", "target_node",
                "synthetic_media_risk", "crisis_priority_if_present", "event_time"
            ).show(5, truncate=False)

            windowed_metrics_df = df_persisted \
                .filter(F.col("event_timestamp").isNotNull()) \
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

            print("\nWindowed Temporal Metrics Summary (1-Hour Windows):")
            windowed_metrics_df.show(truncate=False)

            # Persist windowed metrics
            local_metrics_parquet = metrics_dir / "demo_stream_metrics.parquet"
            local_metrics_csv = metrics_dir / "demo_stream_metrics.csv"
            df_metrics_pd = windowed_metrics_df.toPandas()
            df_metrics_pd.to_parquet(local_metrics_parquet, index=False)
            df_metrics_pd.to_csv(local_metrics_csv, index=False)
            print(f"  Windowed metrics persisted locally: {local_metrics_parquet}")

            # Export to HDFS
            try:
                windowed_metrics_df.write.mode("overwrite").parquet(f"{hdfs_base}/windowed_metrics")
                print(f"  Windowed metrics mirrored to HDFS: {hdfs_base}/windowed_metrics")
            except Exception as e:
                print(f"  HDFS export notice: {e}")

    except Exception as e:
        print(f"[!] Warning reading persisted events: {e}")

    spark.stop()
    print("\n" + "=" * 70)
    print("STREAMING PROCESSING COMPLETED SUCCESSFULLY")
    print("=" * 70)
    return 0

def show_batch_view():
    print("=" * 70)
    print("CRISISGUARD — DEMO STREAMING DATA VIEW")
    print("=" * 70)
    import pandas as pd
    root = Path(__file__).resolve().parent.parent.parent
    raw_dir = root / "data" / "demo" / "streaming" / "raw_events"
    metrics_file = root / "data" / "demo" / "streaming" / "windowed_metrics" / "demo_stream_metrics.csv"

    if raw_dir.exists():
        try:
            df_raw = pd.read_parquet(raw_dir)
            print(f"\nPersisted Raw Events ({len(df_raw)} records):")
            cols = [c for c in ["event_id", "scenario_id", "source_node", "target_node", "synthetic_media_risk", "crisis_priority_if_present", "event_time"] if c in df_raw.columns]
            print(df_raw[cols].to_string(index=False))
        except Exception as e:
            print(f"Could not read raw events: {e}")

    if metrics_file.exists():
        try:
            df_m = pd.read_csv(metrics_file)
            print(f"\nPersisted Windowed Aggregations ({len(df_m)} records):")
            print(df_m.to_string(index=False))
        except Exception as e:
            print(f"Could not read metrics: {e}")

def main():
    parser = argparse.ArgumentParser(description="CrisisGuard Demo Spark Structured Streaming Consumer")
    parser.add_argument("--topic", default="crisisguard-demo-events", help="Kafka topic to consume")
    parser.add_argument("--bootstrap-servers", default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--once", action="store_true", help="Process all available events and terminate immediately")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds to run streaming")
    parser.add_argument("--view", action="store_true", help="Display saved demo tables and exit")

    args = parser.parse_args()
    if args.view:
        show_batch_view()
        return 0

    return run_streaming(args)

if __name__ == "__main__":
    sys.exit(main())
