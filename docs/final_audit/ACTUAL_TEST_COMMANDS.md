# CrisisGuard — Actual Pipeline Execution & Test Commands Inventory

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Document Purpose:** Discover and Document Actual Existing Execution & Test Commands  
**Date:** September 2026  

---

## 1. Executive Summary

This inventory catalogs the genuine, physical execution and test commands implemented in the CrisisGuard codebase. No commands have been invented. Every command corresponds to an existing Python script, Scala build artifact, shell script, or SQL script verified on disk.

---

## 2. Component Execution Commands Matrix

| Component | Actual Command | Primary Inputs | Primary Outputs | Expected Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Data Preprocessing: CIFAKE** | `python3 scripts/preprocessing/preprocess_cifake.py` | `data/raw/synthetic_media_eval/` | `data/processed/cifake/cifake_records.parquet` | Preprocesses 500 image catalog records with labels and metadata |
| **Data Preprocessing: DFD** | `python3 scripts/preprocessing/preprocess_deepfake_dfd.py` | `data/raw/deepfake_dfd/` | `data/processed/deepfake_dfd/media_records.parquet` | Preprocesses 4 video records and 12 sample frames |
| **Data Preprocessing: HumAID** | `python3 scripts/preprocessing/preprocess_humaid.py` | `data/raw/humaid/all_combined/` | `data/processed/humaid/humaid_records.parquet` | Ingests 76,484 multi-split humanitarian disaster records |
| **Data Preprocessing: CrisisMMD**| `python3 scripts/preprocessing/preprocess_crisismmd.py` | `data/raw/crisismmd/` | `data/processed/crisismmd/crisismmd_records.parquet` | Preprocesses 8,079 crisis records with text and image references |
| **Data Preprocessing: CrisisLex**| `python3 scripts/preprocessing/preprocess_crisislex.py` | `data/raw/crisislex/data/` | `data/processed/crisislex/crisislex_records.parquet` | Ingests 88,015 records across CrisisLex T6 and T26 |
| **Data Preprocessing: OSM** | `python3 scripts/preprocessing/preprocess_osm.py` | `data/raw/osm/regional_extract.osm.pbf` | `data/processed/osm/road_nodes.parquet`, `road_edges.parquet` | Extracts 63,660 road nodes and 146,156 road edges |
| **Data Preprocessing: Cascades**| `python3 scripts/preprocessing/generate_propagation_data.py` | Parameterized diffusion models | `data/processed/propagation/propagation_events.parquet` | Generates 5,004 propagation events and 4,999 directed edges |
| **Data Validation: Phase 4** | `python3 scripts/validation/validate_processed_data.py` | `data/processed/` Parquet files | Terminal validation report | Verifies row counts, schemas, and immutability across all 7 datasets |
| **Phase 6: Media Inference** | `python3 scripts/synthetic_media/infer_media.py` | ResNet-18 models + `data/raw/synthetic_media_eval/` | `data/features/synthetic_media/unified_media_risk.parquet` | Performs deepfake/synthetic inference yielding 77 records (`calibration=UNCALIBRATED`) |
| **Phase 6: Explainability** | `python3 scripts/synthetic_media/generate_explainability.py` | `models/synthetic_media/resnet18_cifake_v1.0.pt` | `outputs/synthetic_media/explainability/*.png` | Generates Grad-CAM attention heatmaps |
| **Phase 6: Master Validation**| `python3 scripts/validation/validate_phase6_final.py` | `data/features/synthetic_media/` | Terminal validation report | Verifies 11/11 forensic media risk checks |
| **Phase 7: Unified NLP** | `python3 scripts/crisis_information/build_unified_features.py` | Phase 4 CrisisLex, HumAID, CrisisMMD | `data/features/crisis_information/unified_crisis_intelligence.parquet` | Assembles 104,130 records under text-only contract |
| **Phase 7: DistilBERT NLP** | `python3 scripts/crisis_information/train_crisismmd.py` | `data/processed/crisismmd/` | `models/crisis_information/distilbert_crisismmd/` | Evaluates DistilBERT text classification |
| **Phase 7: Baseline Audit** | `python3 scripts/crisis_information/baseline_audit.py` | `models/crisis_information/tfidf_logistic_crisismmd.joblib` | `docs/crisis_information/baseline_audit_data.json` | Audits TF-IDF baseline ($Acc=0.7445, F1=0.6171$) |
| **Phase 7: Master Validation**| `python3 scripts/validation/validate_phase7_models.py` | `data/features/crisis_information/` | Terminal validation report | Verifies 15/15 crisis intelligence checks |
| **Phase 7: Consistency Audit** | `python3 scripts/validation/audit_phase7_consistency.py` | Phase 7 models, schemas, and Parquets | Terminal validation report | Independently verifies 12/12 checks |
| **Phase 8: HDFS Ingestion** | `python3 scripts/phase8/hdfs_ingest.py` | `data/processed/propagation/events.jsonl` | HDFS `/crisisguard/data/processed/propagation/` | Ingests 5,004 cascade events to Hadoop HDFS |
| **Phase 8: Spark Batch ETL** | `python3 scripts/phase8/spark_prepare_propagation.py` | Ingested cascade events | `data/features/phase8/graph/vertices.csv`, `edges.csv` | Indexes 7,494 unique graph nodes and 4,999 directed edges |
| **Phase 8: Spark GraphX** | `python3 scripts/phase8/compile_and_run_graphx.py` | `vertices.csv`, `edges.csv` | `data/features/phase8/graph/graphx_vertex_metrics.csv` | Runs PageRank (20 iter) & Connected Components on 7,494 vertices |
| **Phase 8: Kafka Producer** | `python3 scripts/phase8/kafka/produce_propagation_events.py` | `data/processed/propagation/events.jsonl` | Kafka topic `crisisguard.propagation.events` | Publishes 5,004 JSON messages with 0 drops |
| **Phase 8: Kafka Consumer** | `python3 scripts/phase8/kafka/consume_and_validate.py` | Kafka broker stream | `docs/phase8/kafka_validation_summary.json` | Validates consumption, offsets, and schema |
| **Phase 8: Structured Stream** | `python3 scripts/phase8/streaming/propagation_stream.py` | Kafka stream `crisisguard.propagation.events` | `data/features/phase8/streaming/propagation_stream_metrics.parquet` | Tumbling 1-min window watermarked aggregations (32 windows) |
| **Phase 8: Hive Warehouse** | `python3 scripts/phase8/hive/run_hive_pipeline.py` | `data/features/phase8/` sinks | `metastore_db/`, `docs/phase8/hive_query_results.json` | Creates 3 Hive external tables and executes analytical SQL |
| **Phase 8: Failure Testing** | `python3 scripts/phase8/test_failure_resilience.py` | Synthetic failure fixtures | `docs/phase8/failure_testing_summary.json` | Executes 5 controlled failure and resilience tests |
| **Phase 8: Master Validation**| `python3 scripts/validation/validate_phase8.py` | Phase 8 HDFS, Spark, GraphX, Kafka, Hive | Terminal validation report | Verifies 15/15 distributed pipeline checks |
| **Phase 9: Multi-Stream Engine**| `python3 scripts/phase9/build_phase9_intelligence.py` | Phases 6, 7, 8, OSM outputs | `data/features/phase9/phase9_multi_stream_intelligence.parquet` | Compiles 175,361-record Multi-Stream Ledger (`NO_VALID_JOIN`) |
| **Phase 9: Master Validation**| `python3 scripts/validation/validate_phase9.py` | `data/features/phase9/` | Terminal validation report | Verifies 14/14 multi-stream integration checks |
| **Phase 9: Consistency Audit** | `python3 scripts/validation/audit_phase9_consistency.py` | Schema, parity, and parquets | Terminal validation report | Independently verifies 10/10 checks |
| **Master Project Validator** | `python3 scripts/validation/validate_final_project.py` | Entire project tree | Terminal validation report | Master objective validator (10/10 checks) |
| **Independent Final Auditor** | `python3 scripts/validation/audit_final_project.py` | Code, docs, and parquets | Terminal validation report | Second-opinion independent consistency auditor (6/6 checks) |

---

*Inventory complete: 28 concrete execution and test commands documented from verified repository scripts.*
