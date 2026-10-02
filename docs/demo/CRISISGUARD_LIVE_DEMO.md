# CrisisGuard — Live Demonstration & Verification Guide

**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  

---

## 1. Overview

This guide provides step-by-step procedures for demonstrating the operational CrisisGuard Big Data system before evaluation committees, faculty evaluators, and external examiners.

CrisisGuard is an end-to-end Big Data pipeline combining:
- **Distributed Ingestion:** Apache Kafka message broker (partitioned topics, durable replay)
- **Real-Time Stream Processing:** Apache Spark Structured Streaming with 1-hour event-time watermark and 1-hour tumbling windows
- **Distributed Graph Analytics:** Apache Spark GraphX (PageRank, Connected Components, In/Out-Degrees on 7,494 vertices)
- **Scalable File Storage:** Apache Hadoop HDFS cluster (3x replication, high-throughput batch sinks)
- **Analytical Catalog:** Apache Hive Warehouse (Derby metastore with 4 external tables)
- **Multimodal Machine Learning:** ResNet-18 Image/Video Forensics and TF-IDF NLP Crisis Intelligence
- **Multi-Stream Decision Ledger:** Phase 9 Union Architecture (175,361 rows, NO_VALID_JOIN governance)

---

## 2. Pre-Demo Environment Verification

Before presenting, run the environment health check to confirm all services are active:

```bash
# From project root in WSL2:
.venv/bin/python scripts/demo/check_demo_environment.py
```

### Expected Output Checklist:
- [x] **Python Runtime & Packages:** `pandas`, `pyarrow`, `kafka`, `torch`, `torchvision`, `sklearn`, `yaml`, `jsonschema`, `scipy` all **OK**
- [x] **Java Runtime Environment:** OpenJDK 11 **OK**
- [x] **Apache Kafka (localhost:9092):** Broker **OPEN & REACHABLE**
- [x] **Apache Hadoop HDFS (localhost:9000):** NameNode RPC **OPEN & REACHABLE** (>900 GB available)
- [x] **Apache Spark 3.5.1:** Spark Submit **OK**
- [x] **GraphX Assembly JAR:** `target/phase8/crisisguard-graphx.jar` (13,092 bytes) **FOUND**
- [x] **Hive Derby Metastore:** `metastore_db/` **FOUND**
- [x] **Environment Health Check Result:** **PASS**

---

## 3. Demonstration Mode Options

CrisisGuard provides two demo execution modes:

```
                  ┌──────────────────────────────────────────────┐
                  │          CRISISGUARD DEMO MODES              │
                  └──────────────────────┬───────────────────────┘
                                         │
                 ┌───────────────────────┴──────────────────────┐
                 ▼                                              ▼
    [MODE A: Interactive / User Input]              [MODE B: Autonomous Live Runner]
    - Direct CLI input across modalities           - 1-Click end-to-end pipeline run
    - Custom event creation & injection            - Automated Kafka -> Spark -> HDFS
    - Live text / image / video inference          - Dynamic UUID event verification
    - Inspection of output Parquet tables          - 6-step scorecard for professors
```

---

## 4. Mode B: Master Autonomous Live Demo (Recommended for Presentations)

To run the complete live pipeline in a single command:

```bash
# WSL2 Ubuntu-24.04 terminal:
cd /mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard
bash scripts/demo/start_demo.sh
```

Or to run only the Python pipeline steps directly:
```bash
.venv/bin/python scripts/demo/run_live_demo.py
```

### Execution Progression (69 seconds):
1. **Step 1:** Verifies HDFS cluster, Kafka broker, and Spark 3.5.1 runtime.
2. **Step 2:** Executes multimodal model inference:
   - ResNet-18 Image Forensics on sample test image.
   - ResNet-18 Temporal Forensics on sample video.
   - CrisisMMD text classifier on simulated disaster message.
3. **Step 3:** Generates a live dynamic event with a unique ID (`demo_live_<timestamp>_<uuid>`) and dispatches to Kafka topic `crisisguard-demo-events`.
4. **Step 4:** Launches Spark Structured Streaming with 1-hour event-time watermark and 1-hour tumbling window aggregation.
5. **Step 5:** Reads back committed outputs and verifies that the exact generated `event_id` exists in both local Parquet and HDFS (`/crisisguard/demo/streaming/`).
6. **Step 6:** Prints the verified Windowed Temporal Metrics Table and 10/10 Scorecard.

---

## 5. Mode A: Live Interactive Professor Testing

If the evaluator requests custom input:

### 5.1 Test 1: Injecting a Custom Propagation Event
```bash
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type propagation \
  --source-node osm_node_99999 \
  --target-node osm_node_88888 \
  --scenario yamuna_crest_surge \
  --risk 0.95 \
  --priority CRITICAL
```
*Observe Kafka broker confirm partition, offset, and event ID.*

### 5.2 Test 2: Ingest via Spark Streaming
```bash
.venv/bin/python scripts/demo/run_demo_streaming.py --once
```
*Observe Spark consume from Kafka, calculate window metrics, and commit to HDFS.*

### 5.3 Test 3: Inspect Persisted Tables
```bash
.venv/bin/python scripts/demo/run_demo_streaming.py --view
```

### 5.4 Test 4: Live Text Classification
Ask the professor to provide any disaster or non-disaster sentence:
```bash
.venv/bin/python scripts/demo/run_text_demo.py "Bridge on Ring Road collapsed, emergency vehicles stuck in traffic"
```

### 5.5 Test 5: Live Image Forensics
```bash
.venv/bin/python scripts/demo/run_image_demo.py data/demo/input/sample_image.jpg
```

---

## 6. Safe Demo Reset

Between presentations, cleanly reset demo artifacts without affecting frozen Phase 6–9 data:

```bash
.venv/bin/python scripts/demo/reset_demo.py
```

---

## 7. Master System Verification

To confirm that frozen Phase 4–9 benchmarks remain untouched:

```bash
# Master Final Project Validator (10/10 PASS)
.venv/bin/python scripts/validation/validate_final_project.py

# Functional Acceptance Suite (10/10 PASS)
.venv/bin/python scripts/validation/run_functional_acceptance_tests.py
```
