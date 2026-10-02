# CrisisGuard — Phase 7: CrisisMMD Data & Modality Audit
**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 7 — Crisis Information Intelligence Engine  
**Date:** September 2026  
**Status:** COMPLETE & EMPIRICALLY AUDITED  

---

## 1. Overview & Dataset Provenance

CrisisMMD (Alam et al., ICWSM 2018) is a multimodal crisis dataset collected during seven major natural disasters in 2017:
- Hurricane Maria
- Hurricane Harvey
- Hurricane Irma
- Sri Lanka Floods
- Mexico Earthquake
- California Wildfires
- Iraq-Iran Earthquake

The dataset was curated by the Qatar Computing Research Institute (QCRI) with crowdsourced annotations assessing tweet text and attached imagery.

---

## 2. Empirical Schema & Entity Inventory

Audit performed on `data/processed/crisismmd/crisismmd_records.parquet`:
- **Total Records:** 8,079
- **Columns (18):**
  1. `event_id`: Unique identifier formatted as `cmmd_{image_id}` (0 nulls)
  2. `source_dataset`: `"crisismmd_multimodal"` (0 nulls)
  3. `source_record_id`: Original tweet snowflake ID (0 nulls)
  4. `image_id`: Image annotation unit ID (0 nulls)
  5. `disaster_event`: Specific disaster name (0 nulls)
  6. `raw_text`: Original tweet text (0 nulls, **100% available**)
  7. `clean_text`: Normalized tweet text (0 nulls, **100% available**)
  8. `image_reference`: Filepath reference from original dataset release (0 nulls)
  9. `image_available_locally`: Boolean flag (**100% False**)
  10. `humanitarian_label`: Consensus humanitarian category (0 nulls)
  11. `humanitarian_text_label`: Unimodal text annotation (0 nulls)
  12. `humanitarian_image_label`: Unimodal image annotation (0 nulls)
  13. `crossmodal_agreement`: Agreement indicator (`Positive` / `Negative`) (0 nulls)
  14. `informative_label`: Binary informativeness rating (0 nulls)
  15. `split`: Official partition: `train` (6,126), `dev` (998), `test` (955) (0 nulls)
  16. `timestamp_if_available`: Extracted temporal date string (0 nulls)
  17. `location_if_available`: Disaster geographic context (0 nulls)
  18. `governance_type`: `"REAL"` (0 nulls)

---

## 3. Modality Policy & Scientific Honesty Mandate

### 3.1 Empirical Verification of Image Assets
- A scan of `data/raw/crisismmd/` confirms that only TSV metadata tables were distributed in `crisismmd_datasplit_agreed_label.zip`.
- **Local Image Binary Count:** Exactly **0** image files exist locally.
- In `data/processed/crisismmd/crisismmd_records.parquet`:
  - `image_available_locally == False` across all 8,079 rows.

### 3.2 Strict Architectural Modality Policy
1. **NO Fake Image Features:** The pipeline strictly refuses to synthesize random tensors, mock embeddings, or pseudo-features from file paths or image URLs.
2. **NO False Multimodal Claims:** We strictly declare CrisisMMD as **Text-Only Crisis Classification with Crossmodal Metadata Tracking**.
3. **Reproducibility & Integrity:** Downstream consumers (and validation scripts) are provided an honest, verifiable feature layer reflecting actual data state.

---

## 4. Class & Event Distributions

### 4.1 Humanitarian Categories (5 Classes)
| Humanitarian Category | Total Records | Train (6,126) | Dev (998) | Test (955) | Class Share |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `not_humanitarian` | 4,277 | 3,244 | 525 | 508 | 52.94% |
| `other_relevant_information` | 1,753 | 1,328 | 219 | 206 | 21.70% |
| `rescue_volunteering_or_donation_effort` | 1,187 | 903 | 149 | 135 | 14.69% |
| `infrastructure_and_utility_damage` | 773 | 587 | 96 | 90 | 9.57% |
| `affected_individuals` | 89 | 64 | 9 | 16 | 1.10% |

### 4.2 Informativeness Categories (Binary)
- `not_informative`: 4,277 (52.94%)
- `informative`: 3,802 (47.06%)

### 4.3 Disaster Events
- `hurricane_maria`: 2,228 (27.58%)
- `hurricane_harvey`: 1,954 (24.19%)
- `hurricane_irma`: 1,848 (22.87%)
- `srilanka_floods`: 726 (8.99%)
- `mexico_earthquake`: 585 (7.24%)
- `california_wildfires`: 511 (6.33%)
- `iraq_iran_earthquake`: 227 (2.81%)
