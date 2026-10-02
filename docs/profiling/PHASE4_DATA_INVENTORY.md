# CrisisGuard: Phase 4 Master Data Inventory & Inspection Catalog

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Status:** Phase 4 Audited Baseline  

---

## 1. Executive Data Inventory Summary

Every dataset file under `data/raw/` and `data/generated/propagation/` was forensically inspected. Raw data files remain completely immutable, and all transformations have been partitioned into `data/interim/`, `data/processed/`, and `data/features/`.

| Dataset | Local Raw Path | File Count | Raw Size | File Formats | Record / Media Count | Primary Role |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **Google DFD-Derived Controlled Sample** | `data/raw/deepfake_dfd/` | 9 | 12.39 MB | .gif (2), .png (3), .json (4) | 4 media assets (12 sampled frames) | Video Forensics Branch |
| **CIFAKE Benchmark** | `data/raw/synthetic_media_eval/` | 501 | 0.59 MB | .jpg (500), .json (1) | 500 images (250 real, 250 synthetic) | Image Forensics Branch |
| **HumAID** | `data/raw/humaid/all_combined/` | 7 | 4.27 MB | .tsv (3), .txt (4) | 76,484 records across 3 splits | Text Urgency Classification |
| **CrisisMMD** | `data/raw/crisismmd/crisismmd_datasplit_agreed_label/` | 8 | 7.49 MB | .tsv (6), .txt (1), .DS_Store (1) | 8,079 multimodal records across 3 splits | Multimodal Damage Severity |
| **CrisisLex** | `data/raw/crisislex/data/` | 110 | 109.80 MB | .csv (58), .json (26), .md (2), other (24) | 88,015 records across 32 crises | Crisis Lexicon Extraction |
| **OpenStreetMap** | `data/raw/osm/` | 3 | 3.48 MB | .pbf (1), .json (1), .md5 (1) | 63,660 road nodes, 146,156 road edges | Emergency Road Routing Graph |
| **Semi-Synthetic Propagation** | `data/generated/propagation/` | 3 | 2.44 MB | .jsonl (1), .csv (1), .json (1) | 5,004 cascade events, 4,999 directed edges | Cascade Diffusion Analysis |

---

## 2. Granular Dataset Profiles

### 2.1 Google DFD-Derived Controlled Development Sample
* **Location:** `data/raw/deepfake_dfd/`
* **Files Retained:** 9 files (totaling 12.39 MB)
  - `videos/deepfakedetection.gif`: 600x338, 100 frames, manipulated face-swap sequence (`label=1`)
  - `videos/DDD_samples.gif`: 614x460, 50 frames, multi-actor comparison sequence (`label=1`)
  - `frames/ex_original_actors.png`: 1920x1080 RGB pristine frame (`label=0`)
  - `frames/ex_deepfakedetection.png`: 1920x1080 RGB manipulated frame (`label=1`)
  - `frames/ex_deepfakedetection_mask.png`: 1920x1080 binary manipulation mask
  - `splits/train.json`, `val.json`, `test.json`: 500 official TUM sequence split pairs
* **Canonical Schema:** `content_id`, `source_dataset`, `source_record_id`, `media_type`, `label`, `split`, `actor_id_if_available`, `manipulation_type_if_available`, `width`, `height`, `frame_count`, `source_path`, `governance_type`
* **Missing Values:** None in metadata fields. Actor IDs mapped to official TUM pair identifiers.

### 2.2 CIFAKE AI-Generated Synthetic Image Benchmark
* **Location:** `data/raw/synthetic_media_eval/`
* **Files Retained:** 500 JPEG images (250 in `real/`, 250 in `fake/`) + `metadata.json`
* **Dimensions:** Uniform 32x32x3 RGB across all 500 images
* **Label Distribution:** Exactly 250 label 0 (real photographic CIFAR-10) and 250 label 1 (Stable Diffusion v1.4 synthetic)
* **Verification:** SHA256 verified for 100% of images. Zero corrupted images, zero duplicate hashes.
* **Canonical Schema:** `content_id`, `source_dataset`, `source_record_id`, `media_type`, `label`, `generator`, `width`, `height`, `channels`, `file_size`, `source_path`, `governance_type`

### 2.3 HumAID Humanitarian Disaster Corpus
* **Location:** `data/raw/humaid/all_combined/`
* **Splits Available:**
  - `all_train.tsv`: 53,531 records
  - `all_dev.tsv`: 7,793 records
  - `all_test.tsv`: 15,160 records
  - **Total Records:** 76,484 records
* **Raw Fields:** `tweet_id`, `class_label`
* **Text Field Status:** `text` is NULL in this split archive (as documented by QCRI authors). Documented without fabricating text.
* **Classes (10):** `rescue_volunteering_or_donation_effort` (27.82%), `other_relevant_information` (15.88%), `sympathy_and_support` (11.68%), `infrastructure_and_utility_damage` (10.67%), `injured_or_dead_people` (9.55%), `not_humanitarian` (8.23%), `caution_and_advice` (7.05%), `displaced_people_and_evacuations` (5.23%), `requests_or_urgent_needs` (3.42%), `missing_or_found_people` (0.47%).

### 2.4 CrisisMMD Multimodal Crisis Dataset
* **Location:** `data/raw/crisismmd/crisismmd_datasplit_agreed_label/`
* **Splits Available:** Train (6,126), Dev (998), Test (955) = 8,079 multimodal records
* **Disaster Events (7):** `hurricane_maria` (2,228), `hurricane_harvey` (1,954), `hurricane_irma` (1,848), `srilanka_floods` (726), `mexico_earthquake` (585), `california_wildfires` (511), `iraq_iran_earthquake` (227).
* **Multimodal Integrity:** Image references are preserved (`image_reference`). `image_available_locally` is explicitly set to `False` adhering strictly to academic honesty.
* **Text Cleaning:** Preserved `raw_text` and generated `clean_text` with normalized URLs, mentions, and whitespace.

### 2.5 CrisisLex Disaster Tweet Lexicon & Collections
* **Location:** `data/raw/crisislex/data/`
* **Collections:**
  - `CrisisLexT26`: 27,933 labeled tweets across 26 global disaster events (with `Information Source`, `Information Type`, `Informativeness`).
  - `CrisisLexT6`: 60,082 labeled tweets across 6 major disasters (`ontopic` vs `offtopic`).
  - **Total Records:** 88,015 records across 32 crises.
* **Timestamps:** 286,096 timestamp records present in period CSVs for longitudinal temporal profiling.

### 2.6 OpenStreetMap Regional Road Extract
* **Location:** `data/raw/osm/regional_extract.osm.pbf` (3.48 MB)
* **Geographic Zone:** Southern India Disaster Response Region (WGS84 EPSG:4326)
* **Extracted Entities:**
  - **Road Nodes:** 63,660 nodes (`node_id`, `latitude`, `longitude`)
  - **Road Edges:** 146,156 directed edges (`edge_id`, `source_node`, `target_node`, `road_type`, `length_m`, `oneway`, `speed_if_available`)
* **Speed Attribute Policy:** 4,368 edges contain explicit `maxspeed` tags; remaining 141,788 edges strictly store `NULL` without inventing synthetic speeds.

### 2.7 Semi-Synthetic Propagation Cascades
* **Location:** `data/generated/propagation/`
* **Events:** 5,004 diffusion events (`events.jsonl`)
* **Edges:** 4,999 directed repost/retweet edges (`edges.csv`)
* **Scenarios:** `ORGANIC_DIFFUSION` (3,047), `COORDINATED_BOT_BURST` (1,002), `HIGH_VELOCITY_VIRAL` (955)
* **Governance Tag:** 100% of records retain `governance_tag: "SEMI_SYNTHETIC"`.
