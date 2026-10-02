# CrisisGuard: Final Phase 3 Dataset Validation & Governance Audit Report

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Date:** 2026-09-27  
**Status:** Approved & Validated Baseline (Post-Audit Correction & Architecture Freeze)  

---

## 1. Final Dataset Standardization & Validation Matrix

| Dataset | Official Source | Access Status | Data Present? | Validated? | Storage Size | Records / Entities | License / Terms | Pipeline Role & Governance |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- |
| **Google DFD-Derived Controlled Development Sample** | Google & Jigsaw / TUM (`github.com/ondyari/FaceForensics`) | `AVAILABLE` | **YES** | **YES** | 12.39 MB | 9 files (2 videos, 3 frames/masks, 3 official split files) | Research Agreement | Video Forensics Branch: Facial deepfake detection development & feature extraction. (Controlled sample, not full 500GB corpus). |
| **CIFAKE: Real & Synthetic Images** | Nottingham Trent Univ / IEEE Access 2024 (`github.com/jordan-bird/...`) | `AVAILABLE` | **YES** | **YES** | 0.59 MB | **500 images** (250 CIFAR-10 real, 250 Stable Diffusion synthetic) | CC BY 4.0 | Image Forensics Branch: AI-generated image detection development & evaluation (NOT a video or deepfake benchmark). |
| **HumAID** | QCRI Crisis Computing (`crisisnlp.qcri.org`) | `AVAILABLE` | **YES** | **YES** | 4.27 MB | **53,531** train records (77,196 total across 19 events) | CC BY 4.0 | Crisis text categorization & urgency modeling. |
| **CrisisMMD** | QCRI Crisis Computing (`crisisnlp.qcri.org`) | `AVAILABLE` | **YES** | **YES** | 7.49 MB | **6,126** multimodal damage assessment records | CC BY 4.0 | Multimodal damage & humanitarian categories. |
| **CrisisLex (T26 & T6)** | CrisisLex.org / EPFL (`github.com/sajao/CrisisLex`) | `AVAILABLE` | **YES** | **YES** | 109.80 MB | **26 disaster events**, 52 CSV archives | CC BY-NC-SA 4.0 | Linguistic crisis context & keyword extraction. |
| **OpenStreetMap** | Geofabrik GmbH (`download.geofabrik.de`) | `AVAILABLE` | **YES** | **YES** | 3.48 MB | Regional road network PBF extract | ODbL 1.0 | Road topology, shortest path & reachability in GraphX. |
| **Semi-Synthetic Propagation** | CrisisGuard Local Engine (`scripts/generation/generate_propagation_cascades.py`)| `AVAILABLE` | **YES** | **YES** | 2.44 MB | **5,004 events, 4,999 directed edges** | Project Internal | **SEMI-SYNTHETIC**: Binds authentic IDs with diffusion cascades. Quarantined in `data/generated/`. |

---

## 2. Dataset Storage Breakdown

* Total Storage Used in `data/raw/`: **138.03 MB** (Strictly within $\le 5.0$ GB raw storage quota).
* Total Storage Used in `data/generated/`: **2.44 MB**.
* Optional Tooling in `tools/synthetic_media_evaluation_tooling/`: **285.35 MB**.
* Host C: Free Space: **> 236 GB**.

---

## 3. Two-Branch Media Architecture & Unified Output Schema

CrisisGuard separates video and image forensics into two dedicated branches:
* **Video Forensics Branch (Google DFD-derived sample):** Video keyframe extraction, facial alignment, and deepfake manipulation artifact scoring.
* **Image Forensics Branch (CIFAKE benchmark):** 2D image diffusion artifact detection and synthetic image risk scoring.
* **Unified Canonical Output:**
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
* **No False Generalization Claims:** Both branches are evaluated independently on their respective domains. Direct cross-dataset generalization between video face swaps and diffusion images is not claimed.

---

## 4. Emergency Priority Integration (Feature Separation)

Synthetic-media outputs enter downstream pipeline stages strictly as **features**:
* `synthetic_media_probability`
* `synthetic_media_risk`
* `media_type`

They do **not** directly determine whether a crisis report is true or false. Emergency dispatch prioritization in Spark MLlib combines:
1. Crisis severity (CrisisMMD)
2. Text urgency (HumAID)
3. Burst velocity (Streaming)
4. PageRank amplifier score (GraphX)
5. Synthetic-media risk (Two-Branch Forensics)
6. Road network accessibility (OpenStreetMap)
7. Physical depot proximity

---

## 5. Tooling Reclassification Note

* **NIST MediScore / OpenMFC:** Confirmed as an evaluation toolkit, NOT a dataset. Preserved under `tools/synthetic_media_evaluation_tooling/` as **OPTIONAL EVALUATION TOOLING** and excluded from the project dataset count.

---

## 6. Final Validation Audit Execution Output

```
============================================================
CRISISGUARD — PHASE 3 FINAL DATASET AUDIT
============================================================

Google DFD:
    ACTUAL DATA = YES
    VALIDATED = YES

Independent Synthetic-Media Dataset:
    DATASET NAME = CIFAKE: Real and AI-Generated Synthetic Images (Bird & Lotfi, IEEE Access 2024)
    ACTUAL DATA = YES
    VALIDATED = YES

HumAID:
    ACTUAL DATA = YES
    VALIDATED = YES

CrisisMMD:
    ACTUAL DATA = YES
    VALIDATED = YES

CrisisLex:
    ACTUAL DATA = YES
    VALIDATED = YES

OpenStreetMap:
    ACTUAL DATA = YES
    VALIDATED = YES

Semi-Synthetic Propagation:
    ACTUAL DATA = YES
    VALIDATED = YES

------------------------------------------------------------

All Mandatory Datasets Present: PASS

Official Provenance:
PASS

Licenses/Terms:
PASS

Actual File Validation:
PASS

Data Quality:
PASS

Leakage Control:
PASS

Reproducibility:
PASS

Data Lineage:
PASS

Storage Governance:
PASS

Synthetic-Media Dataset Validity:
PASS

============================================================
PHASE 3 DECISION
============================================================

PHASE 3 AUDIT STATUS: PASS (CONDITIONS SATISFIED)
- Every mandatory dataset is an actual dataset with verified local data.
- No evaluation tool (MediScore) is falsely claimed as a dataset.
- DFD is correctly documented as a controlled DFD subset / DFD-derived sample.
- Independent evaluation dataset (CIFAKE) is public, unrestricted, and validated.
- Raw data is strictly read-only; semi-synthetic cascades isolated in data/generated/.
- Stack remains frozen; ready for review before Phase 4.
============================================================
```
