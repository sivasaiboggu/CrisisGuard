# CRISISGUARD — FINAL EVIDENCE MANIFEST (DO NOT DELETE)

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Purpose:** Permanent Index of Critical Analytical Results, Models, Figures, and Datasets Required for Final Report, Presentation, and Viva Defense.  
**Governing Architecture:** Provenance-Preserving Multi-Stream Architecture (NO_VALID_JOIN decisions enforced).

---

## 1. Critical Result Datasets & Decision Ledgers (DO NOT DELETE)

All computational artifacts below are strictly **FROZEN** and represent verified analytical ground truth:

| Artifact Path | Format | Dimensions | Epistemic Classification & Role |
|:---|:---:|:---:|:---|
| `data/features/phase9/phase9_multi_stream_intelligence.parquet` | Parquet | **175,361 rows × 23 cols** | **Multi-Stream Intelligence Ledger**: Standardized union ledger across 4 parallel streams (Stream A: 77 forensic media items, Stream B: 104,130 crisis texts, Stream C: 7,494 GraphX vertices, Stream D: 63,660 OSM road nodes) governed by the Phase 9 feature schema contract with explicit availability flags and zero fabricated joins. |
| `data/features/phase9/phase9_media_intelligence.parquet` | Parquet | **77 rows × 15 cols** | **Stream A (Synthetic Media)**: Controlled CV forensics evaluation assets (CIFAKE & Google DFD) with bounded synthetic risk scores and uncalibrated status. |
| `data/features/phase9/phase9_crisis_intelligence.parquet` | Parquet | **104,130 rows × 20 cols** | **Stream B (Crisis Information)**: Multiclass humanitarian needs classifications across CrisisLex (88,015 records), HumAID (15,160 test records; modeled via empirical stratified class priors on official partitions), and CrisisMMD (955 text records; text-based classification with multimodal metadata retained; local image binaries = 0, `image_available_locally: False`). |
| `data/features/phase9/phase9_propagation_intelligence.parquet` | Parquet | **7,494 rows × 19 cols** | **Stream C (Propagation & Graph)**: Structural network metrics computed via GraphX (PageRank, degrees, connected components) joined with node-level cascade outbound events. |
| `data/features/phase9/phase9_spatial_intelligence.parquet` | Parquet | **63,660 rows × 7 cols** | **Stream D (Spatial Infrastructure)**: Physical OpenStreetMap road intersection coordinates (latitude, longitude) available for prospective emergency dispatch routing. |
| `data/features/phase8/graph/graphx_vertex_metrics.csv` | CSV | **7,494 rows × 5 cols** | **GraphX Vertex Analytics**: Authoritative structural graph outputs (PageRank, Connected Components, In-Degree, Out-Degree) computed on 7,494 physical vertices and 4,999 directed edges. |
| `data/features/phase8/graph/vertices.parquet` | Parquet | **7,494 rows × 4 cols** | **Node-ID Mapping Table**: Maps string usernames/node identifiers to 64-bit Long IDs for GraphX (`vertex_id`, `node_name`, `out_degree`, `in_degree`). |
| `data/processed/propagation/propagation_events.parquet` | Parquet | **5,004 rows × 11 cols** | **Propagation Event Dataset**: 5,004 simulated cascade events (including 5 root broadcast events with `target_node = NULL` across 5 narrative topics). |
| `data/features/phase8/streaming/streaming_parsed_events.parquet` | Parquet | **5,004 rows × 14 cols** | **Persisted Streaming Events**: Real-time parsed Kafka events committed via Spark Structured Streaming append sink. |
| `data/features/phase8/streaming/propagation_stream_metrics.parquet` | Parquet | **32 rows × 7 cols** | **Streaming Temporal Windows**: 32 hourly windowed aggregations computed with 1-hour tumbling window and 1-hour event-time watermark. |
| `metastore_db/` | Derby Relational | External Catalog | **Hive Metastore Relational Catalog**: Tracks external Hive tables `propagation_graph_metrics`, `propagation_stream_metrics`, `media_risk_features`, and `crisis_intelligence_features` in database `crisisguard_phase8`. |

---

## 2. Frozen Trained Models & Encoders (DO NOT DELETE)

| Artifact Path | Framework | Size | Exact Role & Calibration State |
|:---|:---:|---:|:---|
| `models/synthetic_media/image_model_best.pt` | PyTorch | **44.8 MB** | **ResNet-18 Image Forensics Model**: Pretrained `IMAGENET1K_V1` backbone with custom classification head (`Dropout(0.3) -> Linear(512, 1)`) trained on CIFAKE forensics benchmark (500 samples). Bounded synthetic risk output in [0.0, 1.0]; explicitly **UNCALIBRATED**. |
| `models/synthetic_media/video_model_best.pt` | PyTorch | **134 KB** | **ResNet-18 Temporal Video Forensics Model**: ResNet-18 temporal feature extractor with Temporal Mean Pooling and MLP classification head (`Linear(512, 128) -> ReLU() -> Dropout(0.2) -> Linear(128, 1)`) evaluated on Google DFD video sample keyframes. Bounded risk output; explicitly **UNCALIBRATED**. |
| `models/crisis_information/text_classifier.joblib` | Scikit-Learn | **12 MB** | Calibrated LinearSVC/LogisticRegression model for multiclass crisis text category prediction (Phase 7). Evaluated on CrisisLex text and CrisisMMD text. |
| `models/crisis_information/tfidf_vectorizer.joblib` | Scikit-Learn | **4 MB** | Sublinear TF-IDF text vectorizer for crisis text feature extraction. |
| `models/crisis_information/label_encoder.joblib` | Scikit-Learn | **50 KB** | Label encoder mapping humanitarian needs categories to integer targets. |
| `models/crisis_information/humaid/humaid_baseline_model.joblib` | Scikit-Learn | **25 KB** | Stratified empirical prior distribution baseline (`DummyClassifier(strategy='stratified')`) for HumAID category distribution modeling. |

---

## 3. Figures, Plots & Visual Evidence (DO NOT DELETE)

| Artifact Directory | Format | Role in Report & Presentation |
|:---|:---:|:---|
| `docs/figures/` & `outputs/` | PNG / SVG | Verified architecture diagrams, PageRank distribution curves, ROC/PR curves, confusion matrices, and explainability visualizations. |

---

## 4. Test & Verification Evidence (DO NOT DELETE)

| Test Script | Purpose | Result |
|:---|:---|:---:|
| `scripts/validation/run_functional_acceptance_tests.py` | Final Functional Acceptance Suite (10/10 checks) | **PASS (1.07s)** |
| `scripts/validation/validate_final_project.py` | Master Final Project Validation Suite (10/10 checks) | **PASS** |
| `docs/final_audit/FINAL_FUNCTIONAL_TEST_REPORT.md` | Authoritative Acceptance Audit Record | **PASS** |
