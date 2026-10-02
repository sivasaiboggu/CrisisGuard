# CrisisGuard: Dataset Access & Compliance Guide (Final Baseline)

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Document Status:** Approved & Audited Access Guide (Post-Audit Correction)  

---

## 1. Compliance & Ethical Use Overview

CrisisGuard operates strictly on **accessible, authorized, research-grade datasets**:
1. **Zero Access Barriers:** The finalized stack completely eliminates dependencies on restricted institutional forms, non-disclosure agreements, or competition-gated portals (DFDC, Celeb-DF, FaceForensics++ are removed as mandatory dependencies).
2. **Transparent Provenance:**
   - **REAL DATA:** Sourced directly from official academic, government, and open-source releases (Google DFD, CIFAKE, QCRI HumAID, QCRI CrisisMMD, CrisisLex, OpenStreetMap).
   - **SEMI-SYNTHETIC DATA:** Artificially generated social cascade diffusion dynamics anchored to real content IDs, explicitly tagged with `governance_tag: "SEMI_SYNTHETIC"`.
   - **OPTIONAL EVALUATION TOOLING:** NIST MediScore evaluation scripts are quarantined under `tools/synthetic_media_evaluation_tooling/` and explicitly excluded from the dataset count.
3. **Controlled Storage:** All raw datasets strictly observe the $\le 5.0$ GB storage budget (total raw storage: 138.03 MB), preserving local disk health.

---

## 2. Ingestion Protocols for the 7 Mandatory Datasets

### 2.1 Google DeepFake Detection Dataset (`deepfake_dfd`) — Controlled Subset
* **Official Source:** Google & Jigsaw in collaboration with Technical University of Munich (TUM)
* **Access Status:** `AVAILABLE` (Acquired)
* **License:** FaceForensics / Google Research Agreement (Non-Commercial Research)
* **Location:** `data/raw/deepfake_dfd/`
* **Acquisition Script:** `python scripts/acquisition/download_google_dfd.py`
* **Subset Scope:** Controlled DFD subset containing canonical release sequences (`deepfakedetection.gif`, `DDD_samples.gif`), frame pairs (`ex_original_actors.png`, `ex_deepfakedetection.png`), binary localization mask, and official sequence partition splits (`train.json`, `val.json`, `test.json`).
* **Governance Note:** Documented explicitly as a "controlled DFD subset / DFD-derived sample" rather than claiming the full multi-hundred-GB video corpus.

### 2.2 Independent Synthetic-Media Dataset: CIFAKE (`synthetic_media_eval`)
* **Official Source:** Nottingham Trent University / Computational Intelligence and Applications Research Group (Bird & Lotfi, IEEE Access 2024)
* **Official Repository:** `https://github.com/jordan-bird/CIFAKE-Real-and-AI-Generated-Synthetic-Images`
* **Access Status:** `AVAILABLE` (Acquired)
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Location:** `data/raw/synthetic_media_eval/`
* **Acquisition Script:** `python scripts/acquisition/acquire_cifake_eval.py`
* **Subset Scope:** 500 authentic images (250 photographic CIFAR-10 test images and 250 AI-synthesized images via Stable Diffusion v1.4) deterministically sampled with `seed=42`.
* **Verification:** SHA256 checksums cataloged in `metadata.json` for every image.
* **Role:** Independent cross-dataset evaluation of deep learning classifiers on unseen generative AI diffusion models.

### 2.3 HumAID (`humaid`)
* **Official Source:** Qatar Computing Research Institute (QCRI / Crisis Computing)
* **Access Status:** `AVAILABLE` (Acquired)
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Location:** `data/raw/humaid/`
* **Files Acquired:** 53,531 training records (77,196 total) across 19 global disaster events.

### 2.4 CrisisMMD (`crisismmd`)
* **Official Source:** Qatar Computing Research Institute (QCRI / Crisis Computing)
* **Access Status:** `AVAILABLE` (Acquired)
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Location:** `data/raw/crisismmd/`
* **Files Acquired:** 6,126 multimodal damage and humanitarian classification records with consensus labels.

### 2.5 CrisisLex (`crisislex`)
* **Official Source:** CrisisLex.org / EPFL (`sajao/CrisisLex`)
* **Access Status:** `AVAILABLE` (Acquired)
* **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)
* **Location:** `data/raw/crisislex/`
* **Files Acquired:** 26 disaster events across 52 event-specific CSV tables.

### 2.6 OpenStreetMap (`osm`)
* **Official Source:** Geofabrik GmbH / OpenStreetMap Contributors
* **Access Status:** `AVAILABLE` (Acquired)
* **License:** Open Database License (ODbL 1.0)
* **Location:** `data/raw/osm/`
* **Files Acquired:** Regional extract `regional_extract.osm.pbf` (3.48 MB) covering Southern India.

### 2.7 Semi-Synthetic Propagation Cascades (`propagation`)
* **Official Source:** CrisisGuard Research Cascade Generator (`scripts/generation/generate_propagation_cascades.py`)
* **Access Status:** `AVAILABLE` (Generated)
* **License:** Project Internal Research Artifact
* **Location:** `data/generated/propagation/`
* **Files Generated:** 5,004 diffusion events (`events.jsonl`) and 4,999 directed edges (`edges.csv`).
* **Governance Note:** Strictly quarantined under `data/generated/propagation/` with `governance_tag: "SEMI_SYNTHETIC"`.

---

## 3. Optional Evaluation Tooling: NIST MediScore

* **Identity:** MediScore (NIST DARPA MediFor Scoring Toolkit)
* **Location:** `tools/synthetic_media_evaluation_tooling/`
* **Status:** **OPTIONAL EVALUATION TOOLING (NOT A DATASET)**
* **License:** Public Domain / NIST Software License
* **Clarification:** MediScore is an evaluation scoring toolkit, not a dataset. OpenMFC is an evaluation program whose datasets require restricted access agreements. MediScore is preserved under `tools/` for scoring scripts and is not counted as a project dataset.
