# CrisisGuard — Complete Project Structure Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase Status:** Phases 4, 5, 6, 7, 8, and 9 are FROZEN  
**Audit Date:** September 2026  
**Status Evaluation:** PASS / FAIL / UNVERIFIED / NOT_APPLICABLE  

---

## 1. Executive Summary

This document performs an exhaustive repository-wide structural inspection of the CrisisGuard codebase. Every primary artifact, script, schema, dataset, model file, validation suite, and documentation report has been inspected directly on the local physical filesystem (`/mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard/` on Windows/WSL2).

In accordance with audit rules:
- **No files were deleted.**
- **No frozen phase outputs were modified.**
- **Every status is derived from physical disk verification.**

---

## 2. Master Repository Artifact Inventory & Verification Matrix

| Category | Artifact Path | Expected Role / Content | Exists | Verified | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Config** | `config/hadoop/` | Hadoop core-site and hdfs-site XML configurations | Yes | Local XML configs present | **PASS** |
| **Config** | `config/spark/` | Spark defaults and worker configs | Yes | Config files present | **PASS** |
| **Config** | `config/kafka/` | Kafka broker and zookeeper properties | Yes | Properties present | **PASS** |
| **Config** | `config/hive/` | Hive metastore and hive-site XML configurations | Yes | Metastore config present | **PASS** |
| **Source** | `src/main/scala/org/crisisguard/graph/CrisisGraphAnalysis.scala` | Scala Spark GraphX PageRank and Connected Components | Yes | Scala source verified | **PASS** |
| **Source** | `pom.xml` / `build.sbt` | Maven / SBT build descriptors for GraphX job | Yes | Valid build config | **PASS** |
| **Target** | `target/crisisguard-graph-assembly-1.0.jar` | Compiled GraphX assembly fat JAR | Yes | Compiled binary present | **PASS** |
| **Data (Raw)** | `data/raw/synthetic_media_eval/` | Controlled CIFAKE image evaluation subset (72 test images) | Yes | 72 PNGs + metadata.json | **PASS** |
| **Data (Raw)** | `data/raw/deepfake_dfd/` | Google DFD controlled sample (5 videos, 1,714 frames) | Yes | MP4 videos + frame assets | **PASS** |
| **Data (Raw)** | `data/raw/humaid/` | HumAID disaster corpora TSV files (all_train, dev, test) | Yes | TSVs present (15,160 test) | **PASS** |
| **Data (Raw)** | `data/raw/crisismmd/` | CrisisMMD agreed label TSVs across 7 disaster events | Yes | 8,079 total records | **PASS** |
| **Data (Raw)** | `data/raw/crisislex/` | CrisisLexT6 and CrisisLexT26 disaster corpora CSVs | Yes | 88,015 records | **PASS** |
| **Data (Raw)** | `data/raw/osm/regional_extract.osm.pbf` | OpenStreetMap regional PBF network extract | Yes | 58.7 MB extract file | **PASS** |
| **Data (Raw)** | `data/raw/celeb_df/` | Celeb-DF benchmark testing video lists | Yes | Text manifest present | **PASS** |
| **Data (Raw)** | `data/raw/dfdc/metadata.json` | DFDC research manifest / metadata stub | Yes | Metadata stub present | **PASS** |
| **Data (Raw)** | `data/raw/faceforensics/` | FaceForensics++ manipulation metadata | Yes | JSON metadata present | **PASS** |
| **Data (Proc)**| `data/processed/cifake/cifake_records.parquet` | Preprocessed CIFAKE metadata records | Yes | Parquet table verified | **PASS** |
| **Data (Proc)**| `data/processed/deepfake_dfd/frame_samples.parquet` | Preprocessed DFD facial frame samples (1,714 frames) | Yes | Parquet table verified | **PASS** |
| **Data (Proc)**| `data/processed/deepfake_dfd/media_records.parquet` | Preprocessed DFD video sequence metadata (5 videos) | Yes | Parquet table verified | **PASS** |
| **Data (Proc)**| `data/processed/humaid/humaid_records.parquet` | Preprocessed HumAID humanitarian records (15,160 test) | Yes | Parquet table verified | **PASS** |
| **Data (Proc)**| `data/processed/crisismmd/crisismmd_records.parquet` | Preprocessed CrisisMMD records (8,079 rows) | Yes | Parquet table verified | **PASS** |
| **Data (Proc)**| `data/processed/crisislex/crisislex_records.parquet` | Preprocessed CrisisLex records (88,015 rows) | Yes | Parquet table verified | **PASS** |
| **Data (Proc)**| `data/processed/osm/road_nodes.parquet` | Processed OSM road network intersections (63,660 nodes) | Yes | Parquet table verified | **PASS** |
| **Data (Proc)**| `data/processed/osm/road_edges.parquet` | Processed OSM road network segments (146,156 edges) | Yes | Parquet table verified | **PASS** |
| **Data (Proc)**| `data/processed/propagation/propagation_events.parquet` | Ingested propagation cascade events (5,004 rows) | Yes | Parquet table verified | **PASS** |
| **Data (Proc)**| `data/processed/propagation/propagation_edges.parquet` | Ingested propagation cascade edges (4,999 rows) | Yes | Parquet table verified | **PASS** |
| **Features** | `data/features/synthetic_media/unified_media_risk.parquet` | Phase 6 frozen media risk table (77 records) | Yes | 77 records verified | **PASS** |
| **Features** | `data/features/crisis_information/unified_crisis_intelligence.parquet` | Phase 7 frozen crisis intelligence table (104,130 records) | Yes | 104,130 records verified | **PASS** |
| **Features** | `data/features/phase8/graph/graphx_vertex_metrics.csv` | Phase 8 GraphX vertex PageRank/Components (7,494 rows) | Yes | 7,494 vertices verified | **PASS** |
| **Features** | `data/features/phase8/streaming/propagation_stream_metrics.parquet` | Phase 8 Spark Structured Streaming tumbling metrics | Yes | 32 windows verified | **PASS** |
| **Features** | `data/features/phase9/phase9_media_intelligence.parquet` | Phase 9 Stream A media table (77 records) | Yes | 77 records verified | **PASS** |
| **Features** | `data/features/phase9/phase9_crisis_intelligence.parquet` | Phase 9 Stream B crisis table (104,130 records) | Yes | 104,130 records verified | **PASS** |
| **Features** | `data/features/phase9/phase9_propagation_intelligence.parquet` | Phase 9 Stream C propagation table (7,494 records) | Yes | 7,494 records verified | **PASS** |
| **Features** | `data/features/phase9/phase9_spatial_intelligence.parquet` | Phase 9 Stream D spatial table (63,660 records) | Yes | 63,660 records verified | **PASS** |
| **Features** | `data/features/phase9/phase9_multi_stream_intelligence.parquet` | Phase 9 unified multi-stream ledger (175,361 records) | Yes | 175,361 records verified | **PASS** |
| **Warehouse**| `metastore_db/` | Hive Metastore Derby database directory | Yes | 195 files verified | **PASS** |
| **Models** | `models/synthetic_media/resnet18_cifake_v1.0.pt` | PyTorch ResNet-18 weights for synthetic image detection | Yes | 42.7 MB binary verified | **PASS** |
| **Models** | `models/synthetic_media/dfd_resnet18_temporal_v1.pt` | PyTorch temporal ResNet-18 weights for video deepfakes | Yes | 42.8 MB binary verified | **PASS** |
| **Models** | `models/synthetic_media/model_registry.json` | Registry metadata for Phase 6 synthetic media models | Yes | Valid JSON registry | **PASS** |
| **Models** | `models/crisis_information/distilbert_crisismmd/` | Fine-tuned DistilBERT transformer for CrisisMMD | Yes | 255.4 MB PyTorch model | **PASS** |
| **Models** | `models/crisis_information/tfidf_logistic_crisismmd.joblib` | Scikit-learn TF-IDF + Logistic Regression baseline | Yes | Joblib serialized model | **PASS** |
| **Models** | `models/crisis_information/humaid_baseline.joblib` | Scikit-learn baseline model for HumAID | Yes | Joblib serialized model | **PASS** |
| **Models** | `models/crisis_information/model_registry.json` | Registry metadata for Phase 7 crisis models | Yes | Valid JSON registry | **PASS** |
| **Schemas** | `schemas/media_risk_schema.json` | JSON Schema for Phase 6 media risk outputs | Yes | Valid JSON schema | **PASS** |
| **Schemas** | `schemas/crisis_intelligence_schema.json` | JSON Schema for Phase 7 crisis intelligence outputs | Yes | Valid JSON schema | **PASS** |
| **Schemas** | `schemas/phase9/crisisguard_intelligence_schema.json` | JSON Schema for Phase 9 multi-stream contract | Yes | Valid JSON schema | **PASS** |
| **Scripts** | `scripts/acquisition/` | 8 acquisition scripts for raw datasets | Yes | 8 scripts verified | **PASS** |
| **Scripts** | `scripts/preprocessing/` | 7 preprocessing scripts for tabular/text/spatial | Yes | 7 scripts verified | **PASS** |
| **Scripts** | `scripts/synthetic_media/` | 8 scripts for inference, explainability, error inspection | Yes | 8 scripts verified | **PASS** |
| **Scripts** | `scripts/crisis_information/` | 10 scripts for NLP models, baselines, error analysis | Yes | 10 scripts verified | **PASS** |
| **Scripts** | `scripts/phase8/` | 7 scripts for HDFS, GraphX, Kafka, Streaming, Hive | Yes | 7 scripts verified | **PASS** |
| **Scripts** | `scripts/phase9/` | 3 scripts for Phase 9 multi-stream builder and audits | Yes | 3 scripts verified | **PASS** |
| **Validation**| `scripts/validation/validate_phase6_final.py` | Phase 6 final test suite (11/11 checks) | Yes | Verified PASS | **PASS** |
| **Validation**| `scripts/validation/validate_phase7_models.py` | Phase 7 master test suite (15/15 checks) | Yes | Verified PASS | **PASS** |
| **Validation**| `scripts/validation/audit_phase7_consistency.py` | Phase 7 independent consistency test suite (12/12 checks) | Yes | Verified PASS | **PASS** |
| **Validation**| `scripts/validation/validate_phase8.py` | Phase 8 master pipeline test suite (15/15 checks) | Yes | Verified PASS | **PASS** |
| **Validation**| `scripts/validation/validate_phase9.py` | Phase 9 master integration test suite (14/14 checks) | Yes | Verified PASS | **PASS** |
| **Validation**| `scripts/validation/audit_phase9_consistency.py` | Phase 9 independent consistency test suite (10/10 checks) | Yes | Verified PASS | **PASS** |
| **Outputs** | `outputs/synthetic_media/explainability/` | Grad-CAM attention heatmaps for image explainability | Yes | 6 PNG images verified | **PASS** |
| **Docs** | `docs/profiling/` | Phase 4 profiling, data quality, and inventory reports | Yes | 8 MD reports | **PASS** |
| **Docs** | `docs/environment/` | Phase 5 environment, compatibility, service docs | Yes | 12 MD reports | **PASS** |
| **Docs** | `docs/synthetic_media/` | Phase 6 model cards, data profiles, forensic reports | Yes | 10 MD reports | **PASS** |
| **Docs** | `docs/crisis_information/` | Phase 7 model cards, data audits, forensic reports | Yes | 12 MD reports | **PASS** |
| **Docs** | `docs/phase8/` | Phase 8 HDFS, Spark, GraphX, Kafka, Streaming, Hive reports | Yes | 14 MD reports + figures | **PASS** |
| **Docs** | `docs/phase9/` | Phase 9 input audit, join feasibility, architecture, etc. | Yes | 8 MD reports + JSON | **PASS** |
| **Top-Level**| `PROJECT_STATUS.md` | Master project tracking status document | Yes | Active tracking doc | **PASS** |
| **Top-Level**| `README.md` | Main repository landing README | Yes | Stale Phase 0 claims found | **FAIL (STALE)** |

---

## 3. Structural Findings & Anomalies

1. **Overall Health:** The repository structure is exceptionally clean, complete, and fully populated. All code, compiled binaries, schemas, models, features, and validation scripts are present on disk.
2. **README Status:** `README.md` contains historical text from Phase 0 (mentioning EDPI, Phase 0 freeze, DFDC as primary benchmark). It requires updating before final submission.
3. **Stale References in Phase 8 Docs:** A small number of Phase 8 markdown reports reference the pre-reconciliation vertex count `7,495` rather than the reconciled count `7,494`. This is thoroughly detailed in `STALE_ARTIFACT_AUDIT.md`.
4. **Immutability of Frozen Artifacts:** All physical files in `data/processed/`, `data/features/synthetic_media/`, `data/features/crisis_information/`, and `data/features/phase8/` match their verified hashes and row counts.

---

*Structural audit verdict: All critical technical components PASS. Documentation consistency requires targeted updates.*
