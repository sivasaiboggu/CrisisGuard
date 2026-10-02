# CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization

[![Course](https://img.shields.io/badge/Course-CSE412%20Big%20Data%20%26%20Large--Scale%20Computing-blue.svg)](#)
[![Status](https://img.shields.io/badge/Status-Phases%204--9%20FROZEN-success.svg)](#)
[![Author](https://img.shields.io/badge/Author-B.SIVASAI%20%282023BCS0228%29-orange.svg)](#)
[![Validators](https://img.shields.io/badge/Validators-10%2F10%20PASS-brightgreen.svg)](#)
[![FAT](https://img.shields.io/badge/FAT-10%2F10%20PASS-brightgreen.svg)](#)

---

## 1. Problem Statement

During acute humanitarian emergencies, disasters, and civil crises, real-time social media streams serve as a vital signal for situational awareness and emergency response coordination. However, the emergence of advanced generative models has introduced high-fidelity **synthetic media (deepfakes, manipulated crisis video, misleading imagery)** into crisis communications.

When propagated virally, synthetic media:
- **Misdirects critical relief resources** to non-existent or fabricated emergency locations.
- **Amplifies public hysteria and confusion**, impeding official evacuation and emergency instructions.
- **Overwhelms first responders** with automated amplification cascades.

Existing architectures treat deepfake detection as a static offline image/video classification task, failing to account for **temporal diffusion dynamics**, **network amplification cascades**, and **physical road reachability**. A single computing tool cannot concurrently handle high-throughput streaming ingestion, iterative network graph computation, distributed machine learning, and structured analytical data warehousing.

---

## 2. Objectives

**CrisisGuard** bridges this operational gap with an end-to-end distributed Big Data analytics pipeline:

1. **Distributed Event Storage:** Persist high-volume crisis propagation events in **Hadoop HDFS** with partitioned distributed storage.
2. **Distributed Batch ETL & Preprocessing:** Utilize **Apache Spark** for distributed schema enforcement, node ID indexing, and edge list extraction.
3. **Iterative Graph Analytics:** Deploy **Spark GraphX** to model social amplification networks (PageRank for structural authority, Connected Components for isolated cascade clusters).
4. **High-Throughput Stream Ingestion:** Ingest crisis event streams and cascade edge metadata through **Apache Kafka** with topic partitioning.
5. **Low-Latency Streaming Analytics:** Utilize **Spark Structured Streaming** to calculate temporal sliding/tumbling window metrics and burst velocity with event-time watermarking.
6. **Analytical Warehousing & Governance:** Maintain partitioned, queryable analytical tables in **Apache Hive** (backed by HDFS/Parquet) for post-disaster forensics and auditing.
7. **Provenance-Preserving Decision Support (Phase 9):** Assemble a **Parallel Multi-Stream Analytical Ledger** (175,361 records) integrating synthetic media risk, crisis information, graph centralities, and spatial road topology without arbitrary heuristic weights or manufactured joins.

---

## 3. High-Level Architecture

The pipeline enforces genuine, unidirectional, tool-to-tool data transformation:

```
+-----------------------------------------------------------------------------------------+
|                                  1. DATA PREPARATION                                   |
|   Real Crisis Datasets         Synthetic Media Subsets             OpenStreetMap (OSM)  |
|  (HumAID, CrisisMMD, Lex)       (CIFAKE, Google DFD)             (Regional Road Network)|
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                              2. DISTRIBUTED STORAGE (HDFS)                              |
|           Path: hdfs://localhost:9000/crisisguard/data/processed/propagation/          |
|                  Immutable Cascade Logs (5,004 events, 4,999 edges)                     |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                          3. DISTRIBUTED BATCH (APACHE SPARK)                            |
|             Bijective Node ID Indexing (7,494 vertices) & Edge Extraction               |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                           4. GRAPH COMPUTATION (SPARK GRAPHX)                           |
|      Propagation Network: PageRank (20 iterations) & Connected Components (2,509)       |
|                 Topological Metrics Computed across 7,494 Vertices                      |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                            5. STREAM INGESTION (APACHE KAFKA)                           |
|       Topic: crisisguard.propagation.events  |  Topic: crisisguard.propagation.edges    |
|                      Partition-Level Parallelism & Zero Drop Rate                       |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                    6. STREAM PROCESSING (SPARK STRUCTURED STREAMING)                    |
|             Tumbling 1-Minute Window Aggregations, Event-Time Watermarking (5m)         |
|                          32 Streaming Windows & Velocity Profiles                       |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                       7. ANALYTICAL WAREHOUSE & FORENSICS (APACHE HIVE)                 |
|             Tables: default.propagation_events, default.graphx_vertex_metrics,          |
|                     default.propagation_stream_metrics (Hive Metastore)                 |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                      8. PHASE 9 PARALLEL MULTI-STREAM DECISION SUPPORT                  |
|     Stream A: Media Forensics (77)      |  Stream B: Crisis NLP (104,130)               |
|     Stream C: Graph & Stream (7,494)    |  Stream D: Spatial Routing (63,660)           |
|            Unified Multi-Stream Ledger: 175,361 Records (Explicit NULL Semantics)       |
+-----------------------------------------------------------------------------------------+
```

---

## 4. Dataset Roles & Provenance Policy

CrisisGuard strictly adheres to data transparency. We distinguish between **Real Data**, **Controlled Evaluation Subsets**, and **Semi-Synthetic Cascades**:

| Dataset | Type / Source | Actual Evaluated Size | Role in Pipeline | Provenance & Modality Policy |
| :--- | :--- | :--- | :--- | :--- |
| **CIFAKE Subset** | Real (Diffusion + Real Photos) | 72 test images ($32 \times 32$) | Spatial synthetic image detection (ResNet-18) | Controlled evaluation subset; not the full 120k dataset. `calibration_status = UNCALIBRATED`. |
| **Google DFD Sample** | Real (Manipulated Video) | 5 videos (1,714 facial frames) | Temporal video deepfake detection | Controlled development sample; not full DFD benchmark. `calibration_status = UNCALIBRATED`. |
| **HumAID** | Real / QCRI | 15,160 test records | Humanitarian crisis task categorization | Dehydrated Twitter IDs and category labels. Evaluated without live tweet text. |
| **CrisisMMD** | Real / QCRI | 8,079 preprocessed (955 test) | Supervised humanitarian text classification | **TEXT-ONLY MODELING:** Zero image binaries available locally; image references retained for metadata tracking only. |
| **CrisisLex (T6 + T26)** | Real / CrisisLex.org | 88,015 records across 32 events | High-volume crisis informativeness filtering | Historical disaster text (2012–2018). Contextual feature stream. |
| **OpenStreetMap (OSM)** | Real / Geofabrik | 63,660 nodes, 146,156 edges | Physical road network routing graph | Spatial routing topology; not joined to tweets due to lack of verified social GPS coordinates. |
| **Propagation Cascades** | **SEMI_SYNTHETIC** | 5,004 events, 4,999 edges | Big Data distributed pipeline benchmarking | **SEMI-SYNTHETIC:** Generated via parameterized stochastic diffusion models (`ORGANIC`, `VIRAL`, `BOT_BURST`). |

---

## 5. Technology Stack

* **Distributed Storage:** Hadoop HDFS 3.3.6
* **Distributed Batch Processing:** Apache Spark 3.5.1 (PySpark)
* **Distributed Graph Analytics:** Spark GraphX (Scala 2.12.18 / sbt 1.9.9)
* **Streaming Message Bus:** Apache Kafka 3.6.0 (Scala 2.13)
* **Real-Time Stream Processing:** Spark Structured Streaming 3.5.1
* **Analytical Data Warehousing:** Apache Hive 3.1.3 (Derby Metastore)
* **Deep Learning & NLP Engines:** PyTorch 2.14.0+cpu (ResNet-18) & Hugging Face Transformers (DistilBERT)
* **Tabular Feature Storage:** PyArrow 25.0.1 (Parquet)
* **Operating Environment:** WSL2 Ubuntu 24.04 LTS on Windows 11 with OpenJDK 11.0.32.1
* **Python Runtime (Demo):** Python 3.12.3 via project `.venv` (WSL2 only)

---

## 6. Phase Execution & Freeze Status

All implementation phases of CrisisGuard are completed, scientifically validated, and permanently **FROZEN**:

| Phase | Description | Key Output Artifacts | Status |
| :--- | :--- | :--- | :---: |
| **Phase 4** | Data Profiling, Ingestion & Preprocessing | 7 clean Parquet datasets in `data/processed/` | **PASS — FROZEN** |
| **Phase 5** | Distributed Cluster Environment Configuration | XML configs in `config/`, 12 environment reports | **PASS — FROZEN** |
| **Phase 6** | Synthetic Media Detection Engine | `unified_media_risk.parquet` (77 rows), ResNet-18 checkpoints | **PASS — FROZEN** |
| **Phase 7** | Crisis Information Intelligence Engine | `unified_crisis_intelligence.parquet` (104,130 rows), DistilBERT | **PASS — FROZEN** |
| **Phase 8** | Big Data Pipeline (HDFS $\to$ Spark $\to$ GraphX $\to$ Kafka $\to$ Streaming $\to$ Hive) | 7,494 GraphX vertices, 32 stream windows, 3 Hive tables | **PASS — FROZEN** |
| **Phase 9** | End-to-End Decision Support & Multi-Stream Integration | `phase9_multi_stream_intelligence.parquet` (175,361 rows) | **PASS — FROZEN** |

---

## 7. Epistemic Principles & Limitations

CrisisGuard adheres strictly to academic honesty and course guidelines:
1. **Zero Arbitrary Emergency Priority Scores:** We explicitly reject and prohibit composite indexes such as EDPI (Emergency Dispatch Priority Index) or Danger Score constructed from arbitrary linear weights ($0.4 \times \text{media} + 0.3 \times \text{crisis} + \dots$). Feature streams are presented transparently to assist qualified human analysts.
2. **Parallel Feature Stream Isolation:** Because forensic media, historical crisis tweets, cascade graphs, and road networks possess zero common primary keys, **no artificial joins were forced** (`NO_VALID_JOIN`). Cross-stream attributes maintain explicit `NULL` semantics rather than fabricated zero values.
3. **Uncalibrated Model Scores:** ResNet-18 models are formally audited as `UNCALIBRATED`. Logit scores represent raw network activations, not true Bayesian posterior probabilities.
4. **Text-Only CrisisMMD:** CrisisMMD is modeled strictly with NLP pipelines; no multimodal visual classification was performed.
5. **No Causal Social Claims:** GraphX PageRank reflects structural position within directed cascade trees, not real-world malice or source intent.
6. **No Autonomous Dispatch Operations:** CrisisGuard is an academic research pipeline; it is not certified for life-safety emergency dispatch.

---

## 8. Installation & Demo Environment

> **CRITICAL:** Run ALL demo commands from **WSL2 Ubuntu-24.04** using the project `.venv`. Do NOT use Windows Python 3.14 (missing kafka-python and torchvision).

### Verified Runtime Environment

| Component | Version |
| :--- | :--- |
| OS (Demo) | WSL2 Ubuntu 24.04 LTS |
| Python | 3.12.3 (project `.venv`) |
| PyTorch | 2.14.0+cpu |
| torchvision | 0.29.0+cpu |
| scikit-learn | 1.5.2 |
| kafka-python | 2.2.3 |
| pandas | 2.1.4 |
| pyarrow | 25.0.1 |
| Java | OpenJDK 11.0.32.1 |
| Kafka Broker | localhost:9092 |
| Hadoop HDFS | localhost:9000 |
| Spark | 3.5.1 |

### Quick Demo (WSL2 Terminal)

```bash
cd /mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard
bash scripts/demo/start_demo.sh
```

### Quick Demo (Windows PowerShell)

```powershell
cd C:\Users\HP\OneDrive\Desktop\CrisisGuard
.\scripts\demo\start_demo.ps1
```

### Individual Mode A Inputs

```bash
# Propagation event → Kafka crisisguard-demo-events
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type propagation \
  --source-node osm_node_552190 \
  --target-node osm_node_884102 \
  --risk 0.92 \
  --scenario delhi_flood_live

# Crisis text classification (Phase 7 frozen model)
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type text \
  --text "Embankment collapsed, urgent rescue boats required!"

# Image synthetic media forensics (Phase 6 ResNet-18)
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type image \
  --path data/demo/input/sample_image.jpg

# Video temporal forensics (Phase 6 ResNet-18 Temporal)
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type video \
  --path data/demo/input/sample_video.gif
```

### Autonomous Demonstration (Mode B)

```bash
.venv/bin/python scripts/demo/run_live_demo.py
```

---

## 9. Master Validation & Reproducibility

To verify the complete project from clean state (WSL2, project .venv):

```bash
# Run from WSL2 terminal:
cd /mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard

# Master Final Project Validator (10/10 Checks)
.venv/bin/python scripts/validation/validate_final_project.py

# Functional Acceptance Tests (10/10 Checks)
.venv/bin/python scripts/validation/run_functional_acceptance_tests.py
```

All validators execute in < 15 seconds and verify 100% PASS without warnings.

**Verified Results (Frozen 2026-09-30):**

| Check | Expected | Actual | Result |
| :--- | :--- | :--- | :---: |
| Phase 9 Ledger Total | 175,361 | 175,361 | **PASS** |
| Phase 8 Events | 5,004 | 5,004 | **PASS** |
| Phase 8 Edges | 4,999 | 4,999 | **PASS** |
| Phase 8 Vertices | 7,494 | 7,494 | **PASS** |
| Phase 8 Windows | 32 | 32 | **PASS** |
| Phase 6 Unified Risk | 77 | 77 | **PASS** |
| Phase 7 Crisis Total | 104,130 | 104,130 | **PASS** |
| GraphX Top PageRank | > 100.0 | 121.97 | **PASS** |
| Cross-stream Overlap | 0 | 0 | **PASS** |
| Failure Resilience | 5/5 | 5/5 | **PASS** |

---

## 10. Limitations & Scientific Hardening (Phase 10 Audit)

CrisisGuard clearly documents all epistemic, empirical, and operational boundaries:

1. **Synthetic Media Calibration (Partially Resolved):** Image scores are calibrated using Platt scaling on a held-out validation partition (reducing 5-bin ECE from 0.4686 to 0.4061 and 10-bin ECE from 0.4827 to 0.4411 on the holdout test set while preserving 0.9815 ROC-AUC); the video branch remains uncalibrated because the available validation sample is insufficient for defensible calibration.
2. **CrisisMMD Modality (Retained with Justification):** CrisisMMD is used for text-based classification with multimodal metadata retained; no local image binaries were available for the current experiment. On the CrisisMMD humanitarian classification test split ($N=955$), accuracy was 74.45% and macro F1 was 61.71% (total dataset: 8,079 records).
3. **HumAID Text Availability (Retained with Justification):** The local HumAID representation contains humanitarian labels and Twitter identifiers but no original tweet text, so the project does not perform unrestricted tweet-text classification on HumAID. Formalized as a 10-class empirical prior benchmark ($N=76,484$; Train/Test $D_{\text{KL}} = 0.000002$) with majority and stratified baseline benchmarks.
4. **Cross-Stream Relational Join (Retained with Justification):** An audit of candidate entity/event keys found no defensible cross-stream join, so the system preserves separate streams in an evidence-aware ledger rather than creating unsupported joins ($A \cap B = 0, B \cap C = 0, C \cap D = 0$; Multi-Stream Ledger: 175,361 records with explicit NULL semantics).
5. **GraphX Behavioral Intent (Retained with Justification):** GraphX measures propagation topology and structural indicators; it does not establish malicious intent or deception. Vocabulary is strictly hardened to "topological structural indicators", explicitly rejecting ungrounded claims of malice.
6. **Decision Support Scope (Resolved for Prototype Governance):** CrisisGuard provides human-in-the-loop decision support and does not autonomously dispatch emergency services. Implements an evidence-aware review queue ($N=625$) with 3 priority tiers where 100% of items require human verification, with zero arbitrary linear dispatch formulas (no EDPI).
7. **Demo Runtime Consideration:** Spark Structured Streaming execution requires 60–90 seconds for JVM startup and Kafka state store initialization. This is normal distributed runtime latency.

Full forensic evidence, metrics, and methodology are detailed in [docs/phase10/PHASE10_LIMITATION_RESOLUTION_REPORT.md](file:///c:/Users/HP/OneDrive/Desktop/CrisisGuard/docs/phase10/PHASE10_LIMITATION_RESOLUTION_REPORT.md).

---

## 11. Team & Author Information

| Field | Detail |
| :--- | :--- |
| **Author** | B.SIVASAI |
| **Roll Number** | 2023BCS0228 |
| **Course** | CSE412 — Big Data & Large-Scale Computing |
| **Project** | CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization |
| **Submission Year** | 2026 |
| **Institution** | (CSE412 Department) |

---

## 12. Official Professor Demo Command

> **The single recommended demo command for professor evaluation:**

```bash
# From WSL2 Ubuntu-24.04 terminal:
cd /mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard
bash scripts/demo/start_demo.sh
```

> Alternatively from Windows PowerShell:
> ```powershell
> cd C:\Users\HP\OneDrive\Desktop\CrisisGuard
> .\scripts\demo\start_demo.ps1
> ```

**Rationale for WSL2 as primary:** All Big Data services (Hadoop, Kafka, Spark, Hive) run natively in WSL2. The project `.venv` contains the exact versions of `torch`, `torchvision`, `kafka-python`, and `scikit-learn` required for inference. Windows Python 3.14 lacks these.
