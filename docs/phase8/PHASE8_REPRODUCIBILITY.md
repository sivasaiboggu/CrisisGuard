# CrisisGuard — Phase 8: Big Data Pipeline Reproducibility Guide

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **REPRODUCIBLE RESEARCH PROTOCOL**

---

## 1. System & Environment Specifications

- **Operating System:** Ubuntu 24.04 LTS on Microsoft Windows 11 (WSL2 environment)
- **Linux Kernel:** `6.6.87.2-microsoft-standard-WSL2` (x86_64 architecture)
- **Host CPU:** AMD Ryzen / Intel Core with 8 vCPUs allocated to WSL2
- **Memory Allocated:** 16 GB RAM allocated to WSL2 VM
- **Java Virtual Machine:** OpenJDK 64-Bit Server VM 11.0.32.1 (`/usr/lib/jvm/java-11-openjdk-amd64`)
- **Scala Compiler & Code Runner:** Scala 2.12.18 (`/usr/local/bin/scalac`, `/usr/local/bin/scala`)
- **Apache Hadoop:** Version 3.3.6 (`/opt/hadoop`)
- **Apache Spark:** Version 3.5.1 with PySpark and GraphX (`/usr/local/lib/python3.12/dist-packages/pyspark`)
- **Apache Kafka:** Version 3.7.0 running in KRaft mode (`/opt/kafka`)
- **Apache Hive:** Version 3.1.3 (`/opt/hive`)
- **Python Environment:** Python 3.12.3 with `pyspark 3.5.1`, `kafka-python-ng 2.2.3`, `pandas 2.1.4`, `pyarrow 25.0.1`, `matplotlib 3.6.3`

---

## 2. Infrastructure Startup Commands

Ensure background services are active:
```bash
# 1. Start Hadoop HDFS (NameNode & DataNode)
/opt/hadoop/sbin/start-dfs.sh

# 2. Start Apache Kafka in KRaft mode
/opt/kafka/bin/kafka-server-start.sh -daemon /opt/kafka/config/kraft/server.properties
```

---

## 3. End-to-End Pipeline Execution Sequence

Execute each stage in sequential order from the workspace root:

```bash
# Step 1: Input Audit
python3 scripts/phase8/audit_inputs.py

# Step 2: HDFS Ingestion & Namespace Provisioning
python3 scripts/phase8/hdfs_ingest.py

# Step 3: Spark Batch Preprocessing & Graph Preparation
python3 scripts/phase8/spark_prepare_propagation.py

# Step 4: GraphX Compilation, Packaging & Execution
python3 scripts/phase8/compile_and_run_graphx.py

# Step 5: Kafka Stream Event Replay
python3 scripts/phase8/kafka/produce_propagation_events.py

# Step 6: Kafka Consumer Audit Tooling
python3 scripts/phase8/kafka/consume_and_validate.py

# Step 7: Spark Structured Streaming & Windowed Aggregation
python3 scripts/phase8/streaming/propagation_stream.py

# Step 8: Hive Warehouse Table Provisioning & Analytical SQL
python3 scripts/phase8/hive/run_hive_pipeline.py

# Step 9: Graph Analytics & Visualizations
python3 scripts/phase8/generate_graph_analytics.py

# Step 10: Controlled Failure & Quality Resilience Testing
python3 scripts/phase8/test_failure_resilience.py

# Step 11: Master Validation Suite (15/15 Criteria)
python3 scripts/validation/validate_phase8.py
```

---

## 4. Expected Output Artifacts

| Generated Artifact Path | Type | Key Verified Dimension |
| :--- | :--- | :--- |
| `docs/phase8/input_audit_data.json` | JSON | Cryptographic SHA-256 hashes of 6 frozen inputs |
| `docs/phase8/hdfs_ingest_evidence.json` | JSON | HDFS `-ls` and `-du` listings across 7 subdirectories |
| `docs/phase8/spark_batch_summary.json` | JSON | 5,004 batch events, 4,999 edges, 7,494 vertices (historical pre-filter 7,495) |
| `target/phase8/crisisguard-graphx.jar` | JAR | Compiled Scala GraphX binary (13,092 bytes) |
| `data/features/phase8/graph/graphx_vertex_metrics.csv` | CSV | 7,494 vertices with PageRank, CC, and Degree metrics |
| `docs/phase8/graphx_metrics_summary.json` | JSON | Max PageRank: 121.9683, Largest CC: 4,986 vertices |
| `docs/phase8/kafka_producer_stats.json` | JSON | 5,004 produced events, 2,570.1 events/s throughput |
| `docs/phase8/kafka_validation_summary.json` | JSON | 5,004 consumed messages, 0 drops, 0 duplicates |
| `data/features/phase8/streaming/propagation_stream_metrics.parquet` | Parquet | 32 temporal windowed metrics |
| `docs/phase8/streaming_metrics_summary.json` | JSON | 5,004 stream events, 4,986 sources, 2,509 targets |
| `docs/phase8/hive_query_results.json` | JSON | 6 executed analytical Hive queries and outputs |
| `docs/phase8/figures/*.png` | PNG | 4 analytical plots (Degree, PageRank, Rate, CC) |
| `docs/phase8/failure_testing_summary.json` | JSON | 5/5 controlled failure tests passed |

---

## 5. Execution Benchmarks (Single-Node Profile)

- **Total End-to-End Pipeline Wall-Clock Time:** ~2.5 to 3.0 minutes
- **HDFS Ingestion:** ~3.5s
- **Spark Batch:** ~33.8s
- **GraphX Scala Compilation & Run:** ~20.7s
- **Kafka Replay & Audit:** ~8.8s
- **Structured Streaming:** ~37.8s
- **Hive Queries:** ~35.9s
- **Master Validation:** ~7.8s
