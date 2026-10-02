# CrisisGuard — Project-Wide Reproducibility Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Audit Purpose:** Verify Independent Reproducibility from Scratch  
**Audit Date:** September 2026  

---

## 1. Executive Summary

This audit assesses whether an independent researcher or course evaluator could successfully reproduce the CrisisGuard architecture from a fresh machine using only the repository assets and documented instructions.

The audit identifies all environmental assumptions, software versions, external dependencies, and execution sequences required to run Phases 4 through 9.

---

## 2. Software Stack & System Prerequisites

The CrisisGuard system is verified under the following primary stack:

| Component | Verified Version | Environment Location / Command | Role in CrisisGuard |
| :--- | :--- | :--- | :--- |
| **Operating System** | Ubuntu 24.04 LTS (WSL2) | Linux kernel 5.15 / 6.6 on Windows 11 | Host operating system for distributed daemons |
| **Python** | 3.12.3 | `/usr/bin/python3` | Core scripting, deep learning, PySpark driver |
| **Java Development Kit** | OpenJDK 11.0.28 | `/usr/lib/jvm/java-11-openjdk-amd64` | Required for Hadoop, Spark, GraphX, Kafka, Hive |
| **Apache Hadoop / HDFS** | 3.3.6 | `/home/sivasai/hadoop-3.3.6` | Distributed file system storage |
| **Apache Spark** | 3.5.1 (PySpark + Scala 2.12) | `/home/sivasai/spark-3.5.1-bin-hadoop3` | Batch preprocessing, Structured Streaming |
| **Scala** | 2.12.18 | Scala compiler / sbt 1.9.9 | Spark GraphX compilation |
| **Apache Kafka** | 3.6.0 (Scala 2.13 build) | `/home/sivasai/kafka_2.13-3.6.0` | Real-time event streaming bus |
| **Apache Hive** | 3.1.3 | `/home/sivasai/apache-hive-3.1.3-bin` | Analytical metastore and SQL warehouse |
| **PyTorch** | 2.5.1+cpu | Python package | ResNet-18 image and video deepfake inference |
| **Hugging Face Transformers**| 4.48.0 | Python package | DistilBERT NLP inference |
| **PyArrow** | 19.0.1 | Python package | Parquet I/O across all feature pipelines |

---

## 3. Directory Layout & Data Locations

All input, intermediate, and output datasets occupy well-defined, standardized relative paths:

- **Raw Data:** `data/raw/` (controlled subsets for CIFAKE, DFD, HumAID, CrisisMMD, CrisisLex, OSM).
- **Interim / Staged Data:** `data/interim/` (canonical CSV manifests and extracted facial frames).
- **Processed Data:** `data/processed/` (clean Parquet records for all datasets).
- **Features Data:** `data/features/`
  - `data/features/synthetic_media/`: Phase 6 media risk outputs (77 records)
  - `data/features/crisis_information/`: Phase 7 crisis intelligence outputs (104,130 records)
  - `data/features/phase8/`: Phase 8 GraphX CSVs (7,494 rows) and Streaming Parquets (32 windows)
  - `data/features/phase9/`: Phase 9 parallel feature streams (175,361 total rows)
- **Model Checkpoints:** `models/synthetic_media/` and `models/crisis_information/`
- **Schemas:** `schemas/` (`media_risk_schema.json`, `crisis_intelligence_schema.json`, `phase9/...`)

---

## 4. End-to-End Execution Sequence

To reproduce the pipeline end-to-end:

### Phase 4 (Preprocessing):
```bash
python3 scripts/preprocessing/preprocess_cifake.py
python3 scripts/preprocessing/preprocess_deepfake_dfd.py
python3 scripts/preprocessing/preprocess_humaid.py
python3 scripts/preprocessing/preprocess_crisismmd.py
python3 scripts/preprocessing/preprocess_crisislex.py
python3 scripts/preprocessing/preprocess_osm.py
python3 scripts/preprocessing/generate_propagation_data.py
python3 scripts/validation/validate_processed_data.py
```

### Phase 6 (Synthetic Media):
```bash
python3 scripts/synthetic_media/infer_media.py
python3 scripts/validation/validate_phase6_final.py
```

### Phase 7 (Crisis Information):
```bash
python3 scripts/crisis_information/train_distilbert_crisismmd.py
python3 scripts/crisis_information/baseline_audit.py
python3 scripts/crisis_information/build_unified_features.py
python3 scripts/validation/validate_phase7_models.py
python3 scripts/validation/audit_phase7_consistency.py
```

### Phase 8 (Big Data Pipeline):
```bash
# 1. Start Services
$HADOOP_HOME/sbin/start-dfs.sh
$KAFKA_HOME/bin/zookeeper-server-start.sh -daemon $KAFKA_HOME/config/zookeeper.properties
$KAFKA_HOME/bin/kafka-server-start.sh -daemon $KAFKA_HOME/config/server.properties

# 2. Ingest to HDFS
python3 scripts/phase8/hdfs_ingest.py

# 3. Batch Preparation
python3 scripts/phase8/spark_prepare_propagation.py

# 4. GraphX Computation
sbt assembly
python3 scripts/phase8/compile_and_run_graphx.py

# 5. Kafka Streaming
python3 scripts/phase8/kafka_producer.py

# 6. Spark Structured Streaming
python3 scripts/phase8/spark_stream_aggregation.py

# 7. Hive Warehouse Setup
python3 scripts/phase8/hive_setup.py

# 8. Validation
python3 scripts/validation/validate_phase8.py
```

### Phase 9 (Multi-Stream Integration):
```bash
python3 scripts/phase9/build_phase9_intelligence.py
python3 scripts/validation/validate_phase9.py
python3 scripts/validation/audit_phase9_consistency.py
```

---

## 5. Reproducibility Assessment Verdict

- **Automated Validation:** 6 / 6 automated test suites execute cleanly and return returncode 0.
- **Data Determinism:** All outputs are deterministic; random seeds are pinned across scripts.
- **Hardware Limitations:** Requires 16 GB RAM and ~20 GB free disk space for Hadoop/Hive metastore. Cannot be executed in a lightweight container without Java 11 and Spark.
- **Overall Status:** **PASS — FULLY REPRODUCIBLE WITH DOCUMENTED DEPENDENCIES.**
