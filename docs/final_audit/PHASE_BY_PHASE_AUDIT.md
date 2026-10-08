# CrisisGuard — Phase-by-Phase Audit & Dataset Provenance Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Status:** ALL PHASES (4–9) FROZEN & AUDITED  
**Audit Date:** September 2026  

---

## 1. Executive Summary

This forensic report audits the complete implementation, datasets, outputs, schemas, validators, metrics, and documentation across all frozen development phases of the CrisisGuard project (Phases 4 through 9). Every reported row count, model score, graph metric, and architectural flow has been independently verified against the physical artifacts on disk.

---

## 2. Dataset Provenance & Modality Audit

In accordance with strict academic integrity rules, the provenance, sample sizes, and modality availability of all seven data assets are detailed below:

| Dataset | Real vs Synthetic | Actual Local Count | Data Modality | True Pipeline Role | Epistemic Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Google DFD Controlled Sample** | **REAL** (Manipulated facial video) | 5 video sequences (1,714 extracted facial frames) | Video (MP4) + Facial bounding-box frames | Controlled development sample for temporal video deepfake detection | **NOT** the full official DFD benchmark; sample size limited to 5 sequences for development feasibility. |
| **CIFAKE Controlled Subset** | **REAL** (Diffusion images + real photos) | 72 evaluated test images (36 real, 36 synthetic) | Image (PNG, $32 \times 32$ RGB) | Controlled evaluation of spatial ResNet-18 synthetic image detection | **NOT** the full 120,000-image CIFAKE dataset; sample size constrained to local GPU/CPU compute budget. |
| **HumAID (QCRI)** | **REAL** (Human disaster communications) | 15,160 test records (from 76,484 multi-split corpus) | Dehydrated Tweet IDs + Humanitarian Category Labels | Humanitarian crisis category classification | **Dehydrated Twitter data:** Raw tweet body text was unavailable due to Twitter API policy; models evaluate label distributions and metadata. |
| **CrisisMMD (QCRI)** | **REAL** (Disaster communications) | 8,079 total records (955 test partition records) | Text (TSV) + Image URL references (`image_available = False`) | Supervised text-based humanitarian categorization | **TEXT-ONLY MODELING:** Zero local image binaries exist; image references retained for metadata tracking only. **Never claim multimodal visual classification.** |
| **CrisisLex (T6 + T26)** | **REAL** (Disaster social media text) | 88,015 records across 32 disaster events | Clean text + Informative/Topical labels | High-volume contextual disaster information filtering | Historical crisis text (2012–2018); lacks direct cross-dataset timestamps or entity links. |
| **OpenStreetMap (OSM)** | **REAL** (Physical geospatial road network) | 63,660 road nodes, 146,156 road edges | Spatial vector coordinates (WGS84 Lat/Lon) | Physical routing infrastructure for dispatch reachability | Spatial coordinates cannot be joined to tweets/cascades due to absence of verified GPS geotags in social data. |
| **Propagation Cascades** | **SEMI_SYNTHETIC** | 5,004 propagation events, 4,999 directed edges | Streaming JSONL events + Graph edges | Distributed pipeline benchmarking (Kafka, GraphX, Streaming, Hive) | **SEMI-SYNTHETIC:** Cascade dynamics follow parameterized simulation models (`ORGANIC`, `VIRAL`, `BOT_BURST`), not live Twitter firehose. |

---

## 3. Phase-by-Phase Audit Findings

### Phase 4: Data Profiling, Ingestion & Preprocessing
- **Status:** PASS — FROZEN.
- **Implementation:** Preprocessing pipelines in `scripts/preprocessing/` (`preprocess_cifake.py`, `preprocess_deepfake_dfd.py`, `preprocess_humaid.py`, `preprocess_crisismmd.py`, `preprocess_crisislex.py`, `preprocess_osm.py`, `generate_propagation_data.py`).
- **Datasets:** All 7 processed datasets present in `data/processed/` in Parquet and CSV formats.
- **Physical Row Counts Verified:**
  - `data/processed/cifake/cifake_records.parquet`: 72 records
  - `data/processed/deepfake_dfd/frame_samples.parquet`: 1,714 frames
  - `data/processed/deepfake_dfd/media_records.parquet`: 5 video records
  - `data/processed/humaid/humaid_records.parquet`: 15,160 records
  - `data/processed/crisismmd/crisismmd_records.parquet`: 8,079 records (6,126 train, 998 dev, 955 test)
  - `data/processed/crisislex/crisislex_records.parquet`: 88,015 records
  - `data/processed/osm/road_nodes.parquet`: 63,660 nodes
  - `data/processed/osm/road_edges.parquet`: 146,156 edges
- **Validators:** `scripts/validation/validate_processed_data.py` (PASS).
- **Documentation:** `docs/profiling/` (8 reports).

---

### Phase 5: Big Data Environment & Architecture Configuration
- **Status:** PASS — FROZEN.
- **Implementation:** Automated cluster scripts in `scripts/environment/` configuring Hadoop 3.3.6 HDFS, Apache Spark 3.5.1, Apache Kafka 3.6.0, and Apache Hive 3.1.3 on WSL2 (Ubuntu 24.04).
- **Configuration Artifacts:** Verified in `config/hadoop/`, `config/spark/`, `config/kafka/`, and `config/hive/`.
- **Validators:** `scripts/validation/validate_phase5_environment.py` (PASS).
- **Documentation:** `docs/environment/` (12 comprehensive reports).

---

### Phase 6: Synthetic Media Detection Engine
- **Status:** PASS — FROZEN WITH DOCUMENTED LIMITATIONS.
- **Implementation:** Inference engine `scripts/synthetic_media/infer_media.py`, explainability generator `generate_explainability.py`, error analysis `inspect_errors.py`.
- **Models:**
  - `models/synthetic_media/resnet18_cifake_v1.0.pt` (spatial image classifier, 42.7 MB)
  - `models/synthetic_media/dfd_resnet18_temporal_v1.pt` (temporal video classifier, 42.8 MB)
  - `models/synthetic_media/model_registry.json`
- **Feature Artifacts Verified:**
  - `data/features/synthetic_media/unified_media_risk.parquet`: **77 records**
  - `data/features/synthetic_media/image_predictions.parquet`: 75 records (72 eval + 3 test samples)
  - `data/features/synthetic_media/video_predictions.parquet`: 2 test video sequence records
- **Calibration Semantics:** Strictly enforced as **`calibration_status = UNCALIBRATED`** for 100% of records.
- **Epistemic Rule Verification:**
  - `synthetic_risk` is treated strictly as an analytical feature and **NEVER** as proof of malicious intent or real-world falsity.
  - Raw sigmoid model scores are never described as calibrated probabilities.
- **Validators:** `validate_phase6_final.py` (11/11 PASS), `validate_phase6_models.py` (PASS).
- **Documentation:** `docs/synthetic_media/` (10 reports).

---

### Phase 7: Crisis Information Intelligence Engine
- **Status:** PASS — FROZEN WITH DOCUMENTED LIMITATIONS.
- **Implementation:** Pipeline in `scripts/crisis_information/` (`train_distilbert_crisismmd.py`, `baseline_audit.py`, `evaluate_crisismmd.py`, `build_crisislex_features.py`, `build_unified_features.py`, `analyze_leakage.py`).
- **Models:**
  - `models/crisis_information/distilbert_crisismmd/` (Fine-tuned DistilBERT transformer, 255.4 MB)
  - `models/crisis_information/tfidf_logistic_crisismmd.joblib` (Multinomial Logistic Regression baseline)
  - `models/crisis_information/humaid_baseline.joblib` (HumAID benchmark classifier)
  - `models/crisis_information/model_registry.json`
- **Feature Artifacts Verified:**
  - `data/features/crisis_information/unified_crisis_intelligence.parquet`: **104,130 records**
  - Breakdown: `crisislex_t6_and_t26` (88,015) + `humaid_all_combined` (15,160) + `crisismmd_multimodal` (955).
- **Evaluated Performance:**
  - CrisisMMD TF-IDF Baseline ($N=955$): Accuracy = 0.7445, Macro F1 = 0.6171, Weighted F1 = 0.7501.
  - CrisisMMD Informativeness ($N=955$): Accuracy = 0.8052, Macro F1 = 0.8051.
- **Epistemic Rule Verification:**
  - CrisisMMD is explicitly declared and modeled as **TEXT-ONLY** with multimodal metadata tracking.
  - An exhaustive grep confirmed **zero claims of "multimodal CrisisMMD classification"** across all documentation.
  - Zero unsupported joins with Phase 6 or Phase 4.
- **Validators:** `validate_phase7_models.py` (15/15 PASS), `audit_phase7_consistency.py` (12/12 PASS).
- **Documentation:** `docs/crisis_information/` (12 reports).

---

### Phase 8: Big Data Propagation & Graph Streaming Pipeline
- **Status:** PASS — FROZEN.
- **Complete Implemented Big Data Flow:**
  $$\text{HDFS} \longrightarrow \text{Apache Spark} \longrightarrow \text{Spark GraphX} \longrightarrow \text{Apache Kafka} \longrightarrow \text{Spark Structured Streaming} \longrightarrow \text{Apache Hive}$$
- **Physical Pipeline Evidence:**
  1. **HDFS Ingestion:** 5,004 propagation events ingested to `/crisisguard/data/processed/propagation/`.
  2. **Spark Batch Processing:** `spark_prepare_propagation.py` mapped node IDs and extracted 4,999 directed edges.
  3. **Spark GraphX:** Scala job executed PageRank and Connected Components on 7,494 vertices.
  4. **Kafka Streaming:** Topics `crisisguard.propagation.events` (5,004 records) and `crisisguard.propagation.edges` (4,999 records).
  5. **Spark Structured Streaming:** Tumbling 1-hour window watermarked aggregations producing 32 window metrics.
  6. **Apache Hive:** Hive Metastore database `metastore_db/` with tables `propagation_events`, `graphx_vertex_metrics`, and `propagation_stream_metrics`.
- **Final Reconciled Graph Metrics Verified:**
  - **Propagation Events:** 5,004
  - **Directed Edges:** 4,999
  - **Root Broadcast Events:** 5 (source nodes where `target_node = NULL`)
  - **Unique Source Nodes:** 4,986
  - **Unique Non-Null Target Nodes:** 2,508
  - **Total Non-Null Union Graph Vertices:** **7,494**
  - **GraphX Vertex Metrics Count:** **7,494**
  - **Total Connected Components:** 2,509
  - **Giant Component Size:** 4,986 vertices (66.53%)
- **Validators:** `scripts/validation/validate_phase8.py` (15/15 PASS).
- **Documentation:** `docs/phase8/` (14 reports + figures).

---

### Phase 9: End-to-End Decision Support & Analytical Integration
- **Status:** PASS — FROZEN.
- **Architecture:** Provenance-Preserving Parallel Feature Streams (`STREAM_A` through `STREAM_D`).
- **Feature Artifacts Verified in `data/features/phase9/`:**
  - `phase9_media_intelligence.parquet`: 77 records (`STREAM_A`)
  - `phase9_crisis_intelligence.parquet`: 104,130 records (`STREAM_B`)
  - `phase9_propagation_intelligence.parquet`: 7,494 records (`STREAM_C`)
  - `phase9_spatial_intelligence.parquet`: 63,660 records (`STREAM_D`)
  - `phase9_multi_stream_intelligence.parquet`: **175,361 records** (Unified Multi-Stream Ledger)
- **Schema:** Standardized under `schemas/phase9/crisisguard_intelligence_schema.json` with 21 contract fields.
- **Scientific Honesty Enforcements:**
  - **`NO_VALID_JOIN` Policy:** Thorough join feasibility audit proved 0.0% entity overlap; zero manufactured joins were created.
  - **Explicit NULL Semantics:** Unavailable cross-stream fields are strictly `NULL`; no fake fallback zeros.
  - **Zero Arbitrary Weights (No EDPI):** No arbitrary linear scoring formulas or composite danger indices were computed.
  - **Non-Causal Topological Analytics:** Spearman correlation between In-Degree and PageRank ($\rho = 0.9920$, $p < 10^{-15}$) is strictly presented as structural graph property without causal social claims.
- **Validators:** `validate_phase9.py` (14/14 PASS), `audit_phase9_consistency.py` (10/10 PASS).
- **Documentation:** `docs/phase9/` (8 reports + analytical JSON).

---

## 4. Phase-by-Phase Audit Conclusion

All six development phases (Phases 4 through 9) are physically intact, completely populated on disk, verified by automated test suites, and adhere 100% to scientific and epistemic guidelines.
