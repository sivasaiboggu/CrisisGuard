# CrisisGuard: Master Dataset Inventory & Provenance Catalog

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Document Status:** Final Phase 3 Approved Baseline (Post-Audit Correction)  

---

## 1. Inventory Summary

The finalized CrisisGuard architecture incorporates **7 distinct datasets**, strictly ensuring that every single dataset is **an actual dataset, publicly accessible, legally authorized, locally present, and mathematically validated** without dependencies on restricted forms or unverified downloads.

| Dataset Identifier | Canonical Name | Source Organization | Provenance Tier | Access Status | Storage Path | Role in Pipeline |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`deepfake_dfd`** | Google DFD-Derived Controlled Development Sample | Google & Jigsaw / TUM | **REAL DATA (Controlled Sample)** | `AVAILABLE` (Acquired) | `data/raw/deepfake_dfd/` | Video Forensics Branch: Facial deepfake detection development & feature extraction |
| **`synthetic_media_eval`** | CIFAKE: Real & AI-Generated Synthetic Images | Nottingham Trent Univ. / IEEE Access 2024 | **REAL DATA (Benchmark)** | `AVAILABLE` (Acquired) | `data/raw/synthetic_media_eval/` | Image Forensics Branch: AI-generated image detection development & evaluation |
| **`humaid`** | HumAID Humanitarian Disaster Data | QCRI Crisis Computing | **REAL DATA** | `AVAILABLE` (Acquired) | `data/raw/humaid/` | Crisis text categorization & urgency modeling |
| **`crisismmd`** | CrisisMMD Multimodal Crisis Data | QCRI Crisis Computing | **REAL DATA** | `AVAILABLE` (Acquired) | `data/raw/crisismmd/` | Multimodal physical damage severity assessment |
| **`crisislex`** | CrisisLex Disaster Tweet Lexicon | CrisisLex / EPFL | **REAL DATA** | `AVAILABLE` (Acquired) | `data/raw/crisislex/` | Linguistic crisis context & keyword extraction |
| **`osm`** | OpenStreetMap Regional Road Network | Geofabrik GmbH / OSM | **REAL DATA (INFRA)**| `AVAILABLE` (Acquired) | `data/raw/osm/` | Road topology, shortest path & reachability in GraphX |
| **`propagation`** | Semi-Synthetic Cascade Generator | CrisisGuard Research Engine | **SEMI-SYNTHETIC**| `AVAILABLE` (Generated)| `data/generated/propagation/`| Diffusion cascades, burst dynamics & super-spreader GraphX analytics |

---

## 2. Dataset Specific Profiles & Governance

### 2.1 Google DFD-Derived Controlled Development Sample (`deepfake_dfd`)
* **Original Dataset:** Google & Jigsaw DeepFake Detection Dataset (DFD), released via TUM FaceForensics++ (Rössler et al., ICCV 2019).
* **Local Sample Scope:** 9 authentic files totaling 12.39 MB (canonical animated sequences `deepfakedetection.gif` and `DDD_samples.gif`, actor frame pairs `ex_original_actors.png` and `ex_deepfakedetection.png`, manipulation ground-truth mask, and official sequence split indices `train.json`, `val.json`, `test.json` covering 500 sequence pairs).
* **Governance Note:** These 9 local files constitute a **Google DFD-derived controlled development sample**, used specifically for local pipeline validation and video model development. They do **not** represent the complete multi-hundred-gigabyte Google DFD dataset.
* **Role:** Video Forensics Branch: video frame sampling, face crop normalization, and facial manipulation artifact extraction.

### 2.2 CIFAKE: Real and AI-Generated Synthetic Images (`synthetic_media_eval`)
* **Original Dataset:** CIFAKE: Real and AI-Generated Synthetic Images (Bird, J.J. and Lotfi, A., IEEE Access 2024).
* **Source Organization:** Nottingham Trent University / Computational Intelligence and Applications Research Group.
* **Local Scope:** 500 authentic benchmark images (250 photographic CIFAR-10 real images with `label: 0` and 250 Stable Diffusion v1.4 synthetic images with `label: 1`) deterministically sampled with `seed=42`.
* **Role:** Dedicated **AI-generated image detection development, image forensic feature extraction, image-model evaluation, and synthetic-image risk scoring**.
* **Governance Note:** CIFAKE is an **image forensics benchmark**, **NOT** a video or deepfake benchmark. It is evaluated independently on image synthesis detection. No false cross-modal generalization claims are made between video and image branches.

### 2.3 HumAID (`humaid`)
* **Role:** Primary humanitarian emergency event classifier.
* **Content:** 53,531 training records (77,196 total) across 19 major global disaster events (earthquakes, floods, hurricanes, wildfires).
* **Governance:** Open Access (CC BY 4.0). Read-only in `data/raw/humaid/`.

### 2.4 CrisisMMD (`crisismmd`)
* **Role:** Multimodal damage assessment and cross-modal consistency.
* **Content:** 6,126 consensus-annotated records linking disaster tweets with damage severity levels.
* **Governance:** Open Access (CC BY 4.0). Read-only in `data/raw/crisismmd/`.

### 2.5 CrisisLex (`crisislex`)
* **Role:** Disaster-specific lexical extraction and keyword informativeness.
* **Content:** 26 historic disaster collections across 52 event-specific tabular archives.
* **Governance:** Open Access (CC BY-NC-SA 4.0). Read-only in `data/raw/crisislex/`.

### 2.6 OpenStreetMap (`osm`)
* **Role:** Physical road network graph for GraphX emergency routing.
* **Content:** Official Geofabrik regional road extract (`.osm.pbf`, 3.48 MB) covering Southern India.
* **Governance:** Open Database License (ODbL 1.0).

### 2.7 Semi-Synthetic Propagation Cascades (`propagation`)
* **Role:** Continuous event stream for Kafka and GraphX network propagation analysis.
* **Content:** 5,004 diffusion events and 4,999 directed edges anchored to authentic HumAID and DFD content IDs.
* **Governance:** **SEMI-SYNTHETIC DATA.** Strictly quarantined under `data/generated/propagation/` with `governance_tag: "SEMI_SYNTHETIC"` in every record.

---

## 3. Two-Branch Media Architecture & Unified Output Schema

Both media branches feed into a unified schema:

```json
{
  "content_id": "string",
  "media_type": "string",
  "synthetic_probability": "float [0.0, 1.0]",
  "synthetic_risk": "float [0.0, 1.0]",
  "model_version": "string",
  "prediction_timestamp": "string"
}
```

These enter the downstream pipeline as **features** (`synthetic_media_probability`, `synthetic_media_risk`, `media_type`). They do **not** directly decide whether an emergency report is true or false. Emergency priority combines crisis severity, text urgency, propagation velocity, GraphX influence, synthetic-media risk, and road accessibility.

---

## 4. Optional Evaluation Tooling (Not a Dataset)

### NIST MediScore Toolkit (`tools/synthetic_media_evaluation_tooling/`)
* **Status:** **OPTIONAL EVALUATION TOOLING (NOT A DATASET).**
* **Identity:** MediScore (Version 1.3.2) is the official NIST scoring and evaluation software toolkit developed for the DARPA MediFor program.
* **Quarantine:** Preserved exclusively under `tools/synthetic_media_evaluation_tooling/` for reference scoring utilities and excluded from the project's dataset count.
