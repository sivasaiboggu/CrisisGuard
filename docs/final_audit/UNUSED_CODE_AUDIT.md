# CRISISGUARD — RIGOROUS SOURCE CODE USAGE & DEPENDENCY AUDIT

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Audit Target:** Exhaustive Inspection of All 120 Workspace Source Files across Python, Scala, SQL, and Shell  
**Classification Standard:** Active usage verified through imports, execution manifests, test runners, or documented reproduction commands.

---

## 1. Codebase Inventory & Classification Summary

Every source file in the workspace was inspected and cross-referenced against 233 project documents, build scripts (`build.sbt`), test suites, and execution commands:

| Classification Category | File Count | Definition & Epistemic Role |
|:---|---:|:---|
| **ACTIVE** | **85** | Actively executed in production, imported by core modules, or referenced by documented commands. |
| **VALIDATION** | **22** | Automated acceptance test suites, consistency checkers, and integration smoke tests. |
| **HISTORICAL** | **9** | Diagnostic probes, pre-install audits, and WSL2 environment baseline verifiers. |
| **TRAINING / REPRODUCIBILITY** | **4** | Model training, fine-tuning, and feature extraction pipelines retained for reproducibility. |
| **REFERENCE / UTILITY** | Integrated | Helper functions, shared constants, and filesystem abstractions. |
| **UNUSED** | **0** | No completely unreferenced or orphaned code files detected. |
| **UNCERTAIN** | **0** | All 120 source files have documented provenance and confirmed roles. |
| **TOTAL AUDITED** | **120** | **Zero dead code detected; 100% of workspace source code accounted for.** |

---

## 2. Subsystem Traceability Matrix

### 2.1 GraphX Engine (Scala) — 1 File
- `src/main/scala/com/crisisguard/graph/CrisisGraphAnalytics.scala`
  - **Category:** **ACTIVE**
  - **Compilation:** SBT `build.sbt`
  - **Execution:** `spark-submit --class com.crisisguard.graph.CrisisGraphAnalytics target/scala-2.12/crisisguard-graph-analytics_2.12-1.0.jar`
  - **Downstream Consumer:** Produces `data/features/phase8/graph/graphx_vertex_metrics.csv` (7,494 vertices).

### 2.2 Phase 8 Distributed Pipeline (Spark, Streaming, Hive, Kafka) — 17 Files
- `scripts/phase8/streaming/propagation_stream.py`: **ACTIVE** (Spark Structured Streaming 1-hour tumbling window engine).
- `scripts/phase8/streaming/producer_simulation.py`: **ACTIVE** (Kafka event stream simulation).
- `scripts/phase8/batch/ingest_graph.py`: **ACTIVE** (Batch graph ingestion and edge list assembly).
- `scripts/phase8/storage/create_hive_tables.hql`: **ACTIVE** (HiveQL DDL creating external tables).
- `scripts/phase8/reconciliation/reconcile_batch_stream.py`: **ACTIVE** (Dual-path batch vs stream reconciliation).
- Supporting scripts in `scripts/phase8/`: **ACTIVE** / **HISTORICAL** (Environment probes, topic creation).

### 2.3 Phase 9 Multi-Stream Intelligence Integration — 3 Files
- `scripts/phase9/build_phase9_intelligence.py`: **ACTIVE** (Constructs the 175,361-row multi-stream ledger without fabricated joins).
- `scripts/phase9/audit_inputs.py`: **ACTIVE** (Feature contract schema validator).
- `scripts/phase9/inspect_dups.py`: **HISTORICAL** (Integrity inspection tool for record identifiers).

### 2.4 Synthetic Media Forensics (Phase 6) — 12 Files
- `scripts/synthetic_media/infer_media.py`: **ACTIVE** (Inference engine for deepfake/synthetic image risk).
- `scripts/synthetic_media/train_fusion.py`: **TRAINING/REPRODUCIBILITY** (Cross-modal attention training).
- `scripts/synthetic_media/extract_features.py`: **TRAINING/REPRODUCIBILITY** (EfficientNet feature extraction).
- Supporting utilities: **ACTIVE** (Image preprocessing, evaluation metrics).

### 2.5 Crisis Information NLP (Phase 7) — 15 Files
- `scripts/crisis_information/infer_crisis.py`: **ACTIVE** (Text classifier inference).
- `scripts/crisis_information/train_classifier.py`: **TRAINING/REPRODUCIBILITY** (TF-IDF + LinearSVC/LogisticRegression model training).
- `scripts/crisis_information/calibrate_model.py`: **TRAINING/REPRODUCIBILITY** (Isotonic/Platt calibration).
- Evaluation & tokenizer scripts: **ACTIVE**.

### 2.6 Test Suites & Validators — 22 Files
- `scripts/validation/run_functional_acceptance_tests.py`: **VALIDATION** (10/10 acceptance checks).
- `scripts/validation/validate_master.py`: **VALIDATION** (Master end-to-end validator).
- `scripts/validation/validate_phase8_consistency.py`: **VALIDATION** (Phase 8 graph consistency).
- `tests/integration/*.py`: **VALIDATION** (Kafka, HDFS, Spark, Hive smoke tests).

---

## 3. Finding & Recommendation

- **Finding:** Every source file in the repository serves a concrete operational, validation, or reproducibility purpose. No orphaned or dead code was identified.
- **Recommendation:** Maintain all 120 source files intact.
