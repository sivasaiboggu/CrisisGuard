# CRISISGUARD — COMPLETE FINAL FILE INVENTORY

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Status:** Audit Complete — Zero Deletions Authorized at This Stage

---

## 1. Executive Inventory Summary

| Classification Category | File Count | Total Size (MB) | Proposed Action |
|:---|---:|---:|:---|
| **A. CORE SOURCE** | 78 | 0.35 MB | **KEEP** (Protected Pipeline Code) |
| **B. CONFIGURATION** | 7 | 0.01 MB | **KEEP** (Cluster & Tool Configurations) |
| **C. SCHEMA** | 3 | 0.01 MB | **KEEP** (Frozen Schemas) |
| **D. DATASET / DATA REFERENCE** | 742 | 233.90 MB | **KEEP** (Frozen Datasets & Manifests) |
| **E. MODEL** | 18 | 299.39 MB | **KEEP** (Frozen Trained ML/DL Checkpoints) |
| **F. VALIDATION / TEST** | 1,325 | 176.09 MB | **KEEP** (Automated Test Suites & Benchmarks) |
| **G. REQUIRED OUTPUT** | 225 | 63.11 MB | **KEEP** (Frozen Parquet, Graph & Hive Ledger) |
| **H. DOCUMENTATION** | 103 | 0.58 MB | **KEEP** (Architecture Specs & Audit Trails) |
| **I. DEMO / PRESENTATION EVIDENCE** | 10 | 0.62 MB | **KEEP** (Plots, Diagrams & Visual Assets) |
| **J. REPRODUCIBILITY** | Integrated | Integrated | **KEEP** (SBT, Requirements & Shell Scripts) |
| **K. GENERATED BUT REGENERABLE** | 9 | 0.07 MB | **ARCHIVE / IGNORE** (Build jars, Derby logs) |
| **L. TEMPORARY** | 25 | 0.20 MB | **REMOVE AFTER AUTHORIZATION** (.DS_Store, session logs) |
| **M. DUPLICATE** | 70 sets | 0.84 MB | **REVIEW** (Test suite duplicate masks) |
| **N. OBSOLETE** | 8 | 0.00 MB | **REMOVE AFTER AUTHORIZATION** (macOS resource forks) |
| **O. UNKNOWN** | 0 | 0.00 MB | **KEEP** (None unclassified) |
| **TOTAL REPOSITORY** | **2,552** | **774.35 MB** | **ZERO DELETIONS PERFORMED** |

---

## 2. Directory Breakdown & Core Subsystems

### 2.1 Core Source Code (`src/`, `scripts/`) — 78 Files (0.35 MB)
- `src/main/scala/com/crisisguard/graph/CrisisGraphAnalytics.scala`: Core Apache Spark GraphX graph computation engine (PageRank, Connected Components, Triangle Count, Degree Centrality on 7,494 vertices and 4,999 directed edges).
- `scripts/phase8/batch/`: Batch ingestion, GraphFrames feature extraction, node-ID mapping, and propagation graph assembly.
- `scripts/phase8/streaming/`: Spark Structured Streaming consumer (`propagation_stream.py`), Kafka producer simulator (`producer_simulation.py`), event-time windowed aggregations (1-hour tumbling window, 1-hour watermark, 32 windows).
- `scripts/phase8/hive/`: Hive external table DDL (`create_phase8_tables.sql`), analytical verification (`phase8_analysis.sql`), and pipeline runner (`run_hive_pipeline.py`).
- `scripts/phase8/reconciliation/`: Dual-path batch vs stream reconciliation scripts (`reconcile_batch_stream.py`).
- `scripts/phase9/`: Multi-stream intelligence integration (`build_phase9_intelligence.py`), schema validator (`audit_inputs.py`), identifier integrity probe (`inspect_dups.py`).
- `scripts/synthetic_media/`: Phase 6 ResNet-18 image and temporal video forensics preprocessing, training, explainability, and inference engines.
- `scripts/crisis_information/`: Phase 7 NLP text classification, fine-tuning, HumAID baseline training, and inference pipelines.

### 2.2 Model Artifacts (`models/`) — 18 Files (299.39 MB)
- `models/crisis_information/`: Trained scikit-learn LogisticRegression, LinearSVC, TF-IDF vectorizers, LabelEncoders, HumAID baseline models, metadata JSONs, tokenizer configurations.
- `models/synthetic_media/`: Trained PyTorch forensics models (`image_model_best.pt`, 44.8 MB ResNet-18; `video_model_best.pt`, 134 KB ResNet-18 temporal extractor), model registry YAML (`model_registry.yaml`), and training histories.

### 2.3 Schemas (`schemas/`) — 3 Files (0.01 MB)
- `schemas/media_risk_schema.json`: Schema specification for Phase 6 synthetic media inference events.
- `schemas/crisis_intelligence_schema.json`: Schema specification for Phase 7 crisis information intelligence events.
- `schemas/phase9/crisisguard_intelligence_schema.json`: Standardized schema contract for the Phase 9 multi-stream intelligence layer in CrisisGuard.

### 2.4 Datasets & Manifests (`data/raw/`, `data/interim/`, `data/processed/`, `data/manifests/`) — 742 Files (233.90 MB)
- `data/raw/crisismmd/`: Text-based CrisisMMD classification with multimodal metadata and provenance retained; local image binaries = 0 and `image_available_locally = False`.
- `data/raw/humaid/`: HumAID benchmark dataset containing 76,484 records (53,531 train, 7,793 dev, 15,160 test) with tweet IDs and humanitarian category labels, without local tweet text; modeled via empirical stratified distribution baselines on the official partitions.
- `data/raw/crisislex/`: CrisisLex disaster tweet corpus with full text.
- `data/interim/`: Tokenized splits, cleaned text corpora.
- `data/processed/`: Standardized CSV/Parquet splits for model training and validation.
- `data/manifests/`: Dataset provenance manifests, SHA-256 integrity hashes, split definitions.

### 2.5 Frozen Computational Outputs (`data/features/`, `data/generated/`, `metastore_db/`) — 225 Files (63.11 MB)
- `data/features/phase8/`: GraphX vertex metrics (`data/features/phase8/graph/graphx_vertex_metrics.csv`, 7,494 rows), node mapping and vertex properties (`data/features/phase8/graph/vertices.parquet`, 7,494 rows), edge list (`edges.parquet`, 4,999 directed edges).
- `data/features/phase8/streaming/`: Streaming parsed events (`streaming_parsed_events.parquet`, 5,004 rows), windowed metrics (`propagation_stream_metrics.parquet`, 32 windows).
- `data/features/phase9/`: Multi-Stream Intelligence Ledger (`phase9_multi_stream_intelligence.parquet`, 175,361 rows) and 4 parallel feature tables (`phase9_media_intelligence.parquet`, `phase9_crisis_intelligence.parquet`, `phase9_propagation_intelligence.parquet`, `phase9_spatial_intelligence.parquet`).
- `metastore_db/`: Apache Hive / Derby relational catalog tracking external tables `propagation_graph_metrics`, `propagation_stream_metrics`, `media_risk_features`, and `crisis_intelligence_features` in database `crisisguard_phase8`.

### 2.6 Validation Suites (`tests/`, `scripts/validation/`, `tools/`) — 1,325 Files (176.09 MB)
- `scripts/validation/`: Acceptance tests (`run_functional_acceptance_tests.py`), master audit validators (`validate_master.py`), independent consistency checkers (`validate_phase8_consistency.py`).
- `tests/integration/`: Spark, HDFS, Kafka, Hive smoke tests.
- `tools/synthetic_media_evaluation_tooling/`: Benchmark MediFor evaluation tools and unit test suites.

### 2.7 Documentation & Evidence (`docs/`, `outputs/`, `results/`) — 113 Files (1.20 MB)
- `docs/phase8/`, `docs/phase9/`, `docs/crisis_information/`, `docs/synthetic_media/`, `docs/environment/`, `docs/final_audit/`: 103 Markdown reports.
- `docs/figures/`, `outputs/`, `results/`: 10 analytical plots, architecture diagrams, explainability visualizations.

---

## 3. High-Priority Cleanup Candidates (Pending Authorization)

| Relative Path | Classification | File Size | Description | Proposed Action |
|:---|:---:|---:|:---|:---:|
| `data/raw/crisismmd/__MACOSX/crisismmd_datasplit_agreed_label/._Readme.txt` | OBSOLETE | 227 B | macOS resource fork | REMOVE AFTER AUTHORIZATION |
| `data/raw/humaid/all_combined/._Readme.txt` | OBSOLETE | 227 B | macOS resource fork | REMOVE AFTER AUTHORIZATION |
| `data/raw/crisismmd/crisismmd_datasplit_agreed_label/.DS_Store` | TEMPORARY | 6,148 B | macOS Desktop Services Store | REMOVE AFTER AUTHORIZATION |
| `tools/.../.DS_Store` (17 occurrences) | TEMPORARY | ~100 KB | macOS folder view metadata | REMOVE AFTER AUTHORIZATION |
| `tools/.../.Rhistory` (5 occurrences) | TEMPORARY | ~74 KB | R statistical console history | REMOVE AFTER AUTHORIZATION |
| `derby.log` | GENERATED | 3,921 B | Apache Derby transaction log | IGNORE / ARCHIVE |
| `target/scala-2.12/*.jar` | GENERATED | 68 KB | SBT packaged assembly JAR | ARCHIVE / REGENERABLE |

---

## 4. Preservation Guarantee

The following critical categories are strictly **FROZEN** and marked **DO NOT DELETE**:
- All 78 Core Source Files (`src/`, `scripts/`)
- All 18 Trained Model Files (`models/`)
- All 742 Raw & Processed Dataset Files (`data/raw/`, `data/processed/`)
- All 225 Frozen Feature & Ledger Outputs (`data/features/`, `data/generated/`, `metastore_db/`)
- All 3 JSON Schema Specifications (`schemas/`)
- All Documentation & Historical Audits (`docs/`, `README.md`)
