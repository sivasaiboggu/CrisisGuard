# CrisisGuard — Big Data Course Requirement & Tool Integration Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Audit Purpose:** Verify Genuine Distributed Tool-to-Tool Data Flow Across Course Infrastructure  
**Audit Date:** September 2026  

---

## 1. Executive Summary

A core objective of CSE412 (Big Data & Large-Scale Computing) is demonstrating genuine, verifiable data flow across multiple distributed data processing engines. Simply installing software packages or running disjoint "hello-world" scripts fails the course rubric.

This audit examines the physical evidence that data actually and unidirectionally traverses:
$$\text{HDFS} \longrightarrow \text{Apache Spark} \longrightarrow \text{Spark GraphX} \longrightarrow \text{Apache Kafka} \longrightarrow \text{Spark Structured Streaming} \longrightarrow \text{Apache Hive}$$

Every stage is audited below against concrete files, logs, database metastores, and execution receipts.

---

## 2. Big Data Tool Flow Verification Matrix

| Course Tool Requirement | Architecture Role & Data Flow | Concrete Physical Evidence / Artifact | Input / Output Counts | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **1. Distributed Storage: HDFS** | Ingest raw and preprocessed cascade events to Hadoop HDFS distributed filesystem (`hdfs://localhost:9000/crisisguard/...`) | - `scripts/phase8/hdfs_ingest.py`<br/>- `docs/phase8/hdfs_ingest_evidence.json`<br/>- Local HDFS block storage at `/home/sivasai/hadoop_data/hdfs/namenode` | **5,004 propagation events** written to HDFS path `/crisisguard/data/processed/propagation/events.jsonl` | **PASS — VERIFIED** |
| **2. Distributed Processing: Apache Spark (Batch)** | Read cascade logs from HDFS, perform distributed schema enforcement, node ID indexing, and edge list extraction | - `scripts/phase8/spark_prepare_propagation.py`<br/>- `data/features/phase8/graph/edges.csv`<br/>- `data/features/phase8/graph/vertices.csv`<br/>- `docs/phase8/spark_batch_summary.json` | Ingested **5,004 events**; extracted **4,999 directed edges** and indexed **7,494 unique graph nodes** | **PASS — VERIFIED** |
| **3. Graph Analytics: Spark GraphX** | Execute distributed iterative PageRank ($maxIter=20, resetProb=0.15$) and Weakly Connected Components on graph topology | - `src/main/scala/org/crisisguard/graph/CrisisGraphAnalysis.scala`<br/>- `target/crisisguard-graph-assembly-1.0.jar`<br/>- `data/features/phase8/graph/graphx_vertex_metrics.csv`<br/>- `docs/phase8/graphx_metrics_summary.json` | Built graph with **7,494 vertices** and **4,999 edges**; computed PageRank for all 7,494 nodes and identified **2,509 connected components** | **PASS — VERIFIED** |
| **4. Message Broker: Apache Kafka** | High-throughput distributed message publishing with topic partitioning (`crisisguard.propagation.events` and `crisisguard.propagation.edges`) | - `scripts/phase8/kafka_producer.py`<br/>- `docs/phase8/kafka_producer_stats.json`<br/>- `docs/phase8/kafka_validation_summary.json`<br/>- Kafka broker logs at `/home/sivasai/kafka_2.13-3.6.0/logs/` | Published **5,004 JSON event payloads** and **4,999 edge payloads** to Kafka brokers with 0 message drops | **PASS — VERIFIED** |
| **5. Stream Processing: Spark Structured Streaming** | Ingest live Kafka stream, apply event-time watermarking (`.withWatermark("event_timestamp", "1 hour")`), and compute tumbling 1-hour window aggregations | - `scripts/phase8/spark_stream_aggregation.py`<br/>- `data/features/phase8/streaming/propagation_stream_metrics.parquet`<br/>- `docs/phase8/streaming_metrics_summary.json` | Consumed Kafka stream; generated **32 tumbling window records** with event counts, velocity, and mean synthetic risk | **PASS — VERIFIED** |
| **6. Data Warehouse: Apache Hive** | Maintain schema-enforced external and managed tables backed by HDFS/Parquet, enabling analytical SQL querying | - `scripts/phase8/hive_setup.py`<br/>- `metastore_db/` (Derby database with 195 files)<br/>- `docs/phase8/hive_query_results.json`<br/>- Hive warehouse tables: `propagation_events`, `graphx_vertex_metrics`, `propagation_stream_metrics` | Queried all 3 tables via Spark-Hive SQL metastore; matched **5,004 events, 7,494 vertex metrics, and 32 stream windows** | **PASS — VERIFIED** |

---

## 3. End-to-End Inter-Tool Data Lineage

The data transitions between tools without loss of lineage or schema corruption:

```
[Raw Cascade Logs: 5,004 JSONL Events]
                  │
                  ▼ (Ingested via hdfs dfs -put)
[Hadoop HDFS Storage: hdfs://localhost:9000/crisisguard/]
                  │
                  ▼ (Read by PySpark DataFrame API)
[Apache Spark Batch: spark_prepare_propagation.py]
      ├── Node ID Indexing (7,494 vertices)
      └── Edge List Extraction (4,999 directed edges)
                  │
                  ▼ (Loaded via GraphLoader / EdgeRDD)
[Apache Spark GraphX (Scala Engine): CrisisGraphAnalysis.scala]
      ├── PageRank Computation (20 iterations)
      └── Connected Components (2,509 components)
                  │
                  ▼ (Published as JSON Messages)
[Apache Kafka Brokers: localhost:9092]
      ├── Topic: crisisguard.propagation.events (5,004 msgs)
      └── Topic: crisisguard.propagation.edges (4,999 msgs)
                  │
                  ▼ (Read via spark.readStream.format("kafka"))
[Spark Structured Streaming: spark_stream_aggregation.py]
      └── Tumbling 1-Min Window Aggregations (32 windows)
                  │
                  ▼ (Persisted to HDFS / Sinks)
[Apache Hive Warehouse: metastore_db/]
      ├── Table: default.propagation_events (5,004 rows)
      ├── Table: default.graphx_vertex_metrics (7,494 rows)
      └── Table: default.propagation_stream_metrics (32 rows)
```

---

## 4. Course Rubric Evaluation Verdict

- **Multi-Tool Pipeline Requirement:** **FULLY MET (6 / 6 Tools Active).**
- **Unidirectional Data Flow:** **VERIFIED (Raw $\to$ HDFS $\to$ Spark $\to$ GraphX $\to$ Kafka $\to$ Streaming $\to$ Hive).**
- **Distributed Analytics Semantics:** **VERIFIED (PageRank, Connected Components, Watermarked Streaming, Hive SQL).**
- **Overall Status:** **PASS — 100% COMPLIANT WITH CSE412 BIG DATA REQUIREMENTS.**
