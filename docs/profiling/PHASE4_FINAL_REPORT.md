# CrisisGuard: Phase 4 Final Dataset Profiling & Preprocessing Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase Status:** Phase 4 Completed & Audited (Phase 5 NOT Started)  

---

## 1. Executive Summary

Phase 4 of Project CrisisGuard has completed comprehensive dataset profiling, data quality analysis, non-destructive cleaning, and transformation across all **7 project datasets**. 

### Critical Architecture Boundaries Strictly Observed:
1. **Raw Data Immutability:** Raw data in `data/raw/` remains 100% untouched.
2. **Intermediate & Processed Segregation:** All clean representations reside strictly under `data/interim/` (CSV/JSONL), `data/processed/` (Parquet), and `data/features/` (feature matrices).
3. **No Big Data Tools Installed Yet:** Hadoop, Spark, Kafka, Hive, and Scala were **not** installed.
4. **No Premature Model Training:** No machine learning models were trained. Feature contracts for downstream Kafka, Spark Streaming, GraphX, MLlib, and Hive were formally established without fabricating predictions or heuristic weights.
5. **MediScore Quarantined as Tooling:** Confirmed exclusively under `tools/synthetic_media_evaluation_tooling/` and excluded from dataset counts.

---

## 2. Processed Dataset Inventory & Statistics

| Dataset | Local Raw Path | Processed Output Path | Entity Count | Disk Footprint | Primary Role in Pipeline |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Google DFD Sample** | `data/raw/deepfake_dfd/` | `data/processed/deepfake_dfd/` | 4 media assets / 12 keyframes | 0.02 MB | Video Forensics Branch: Keyframe extraction & face swap artifact scoring |
| **CIFAKE Benchmark** | `data/raw/synthetic_media_eval/` | `data/processed/cifake/` | 500 images (250 real / 250 syn) | 0.16 MB | Image Forensics Branch: Diffusion artifact detection & synthetic image risk |
| **HumAID Corpus** | `data/raw/humaid/all_combined/` | `data/processed/humaid/` | 76,484 records (10 classes) | 12.47 MB | Humanitarian text urgency classification & crisis category modeling |
| **CrisisMMD** | `data/raw/crisismmd/...` | `data/processed/crisismmd/` | 8,079 multimodal records | 5.51 MB | Multimodal damage severity & crossmodal agreement assessment |
| **CrisisLex** | `data/raw/crisislex/data/` | `data/processed/crisislex/` | 88,015 records (32 events) | 43.34 MB | Disaster linguistic context & informativeness keyword extraction |
| **OpenStreetMap** | `data/raw/osm/` | `data/processed/osm/` | 63,660 nodes / 146,156 edges | 3.85 MB | Physical road network topology for GraphX emergency routing |
| **Semi-Synthetic Propagation** | `data/generated/propagation/`| `data/processed/propagation/`| 5,004 events / 4,999 edges | 2.24 MB | Cascade diffusion simulation for Kafka & GraphX PageRank analysis |

---

## 3. Data Cleaning & Transformation Achievements

1. **Google DFD-Derived Sample (`scripts/preprocessing/preprocess_deepfake_dfd.py`):**
   * Sampled 12 representative keyframes without exploding storage.
   * Extracted spatial frequency metrics (Laplacian blur variance, RGB statistics).
   * Verified TUM sequence partition splits (`train.json`, `val.json`, `test.json`) with zero actor leakage.

2. **CIFAKE Benchmark (`scripts/preprocessing/preprocess_cifake.py`):**
   * Validated 500 images with cryptographic SHA256 hashes (zero corruptions, zero duplicates).
   * Confirmed exact ground truth mappings: `label 0 = real (CIFAR-10)`, `label 1 = synthetic (Stable Diffusion v1.4)`.
   * Extracted 2D FFT frequency energy and Laplacian variance features.

3. **HumAID Text Corpus (`scripts/preprocessing/preprocess_humaid.py`):**
   * Consolidated all 3 official splits: train (53,531), dev (7,793), test (15,160).
   * Preserved all 10 original humanitarian categories without arbitrary collapsing.
   * Documented text unavailability in the `all_combined` split archive without fabricating fake text.

4. **CrisisMMD Multimodal Dataset (`scripts/preprocessing/preprocess_crisismmd.py`):**
   * Processed 8,079 consensus-annotated records across 7 major disaster events.
   * Performed Unicode NFKC normalization, HTML unescaping, URL and mention tokenization into `clean_text` while keeping `raw_text` immutable.
   * Preserved image reference paths with honest `image_available_locally: False` flags.

5. **CrisisLex Collections (`scripts/preprocessing/preprocess_crisislex.py`):**
   * Consolidated 27,933 records from `CrisisLexT26` and 60,082 records from `CrisisLexT6` across 32 disaster events.
   * Deduplicated 4 redundant IDs and produced unified `clean_text`.

6. **OpenStreetMap Regional Extract (`scripts/preprocessing/preprocess_osm.py`):**
   * Parsed `regional_extract.osm.pbf` via `osmium` into 63,660 road nodes and 146,156 edges.
   * Computed geodesic Haversine distance in meters.
   * Strictly retained `NULL` for missing `speed_if_available` tags without inventing speeds.

7. **Semi-Synthetic Propagation Cascades (`scripts/preprocessing/preprocess_propagation.py`):**
   * Validated 5,004 events and 4,999 edges across 3 scenarios (`ORGANIC_DIFFUSION`, `COORDINATED_BOT_BURST`, `HIGH_VELOCITY_VIRAL`).
   * Confirmed 100% adherence to `governance_tag: "SEMI_SYNTHETIC"`.
   * Evaluated graph topology with Python NetworkX (density: 0.000201, max in-degree: 13, 1 weakly connected component).

---

## 4. Downstream Interface Contracts Established

Two formal feature contracts were codified in `docs/profiling/FEATURE_CONTRACTS.md`:
* **Media Risk Feature Contract:** Emits `[content_id, media_type, synthetic_media_probability, synthetic_media_risk, model_version, prediction_timestamp]`. No premature predictions calculated.
* **Crisis Priority Feature Contract:** Assembles 8 orthogonal dimensions `[crisis_severity, urgency, propagation_velocity, propagation_volume, graph_influence, synthetic_media_risk, road_accessibility, resource_distance]`. No arbitrary heuristic weights assigned.

---

## 5. Phase 4 Validation Execution Output

```
============================================================
CRISISGUARD — PHASE 4 PROCESSED DATA VALIDATION
============================================================
DFD Profiling: PASS
CIFAKE Profiling: PASS
HumAID Profiling: PASS
CrisisMMD Profiling: PASS
CrisisLex Profiling: PASS
OSM Profiling: PASS
Propagation Profiling: PASS
Data Quality: PASS
Duplicate Analysis: PASS
Missing Value Analysis: PASS
Class Distribution: PASS
Temporal Analysis: PASS
Location Analysis: PASS
Leakage Control: PASS
Preprocessing: PASS
Processed Data Validation: PASS
Lineage: PASS
Reproducibility: PASS

============================================================
PHASE 4 DECISION
============================================================
PHASE 4 STATUS: PASS (CONDITIONS SATISFIED)
- Every selected dataset was actually profiled
- All preprocessing scripts executed successfully
- Processed data exists in Parquet and CSV formats
- Raw data remains untouched and immutable
- Schemas and feature contracts are fully valid
- Provenance fields and governance tags are preserved
- Leakage controls verified across splits
- Preprocessing is deterministic and reproducible
- No fabricated data or premature predictions were introduced
============================================================
```

---

## 6. Strict Stop Acknowledgment

* **Hadoop / Spark / Kafka / Hive / Scala:** NOT installed.
* **GraphX / Structured Streaming / MLlib / Dashboard:** NOT implemented.
* **Phase 5:** NOT started.
* **Execution Status:** FROZEN. Awaiting explicit user review.
