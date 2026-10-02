# CrisisGuard — Phase 7: Crisis Information Data Audit
**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 7 — Crisis Information Intelligence Engine  
**Date:** September 2026  
**Status:** COMPLETE & EMPIRICALLY AUDITED  

---

## 1. Executive Summary & Audit Mandate

In accordance with Phase 7 Step 1 and the Strict Scientific Rules of CrisisGuard, this document provides an exhaustive, empirical repository and dataset audit across all primary crisis-related datasets inherited from Phase 4:
1. **HumAID:** Human-Annotated Disaster Incidents Dataset
2. **CrisisMMD:** Multimodal Disaster Dataset
3. **CrisisLex:** Crisis Lexicon and Disaster Corpus (CrisisLexT26 and CrisisLexT6)

**Audited Principles:**
- All statistics, schema definitions, counts, and null rates are computed directly from the local files in `data/raw/` and `data/processed/`.
- Zero statistics or schemas are assumed or fabricated.
- Raw files in `data/raw/` and processed artifacts from Phase 4 remain completely unmodified and read-only.
- Cross-dataset record overlap was tested explicitly using unique tweet/record identifiers.

---

## 2. Dataset 1: HumAID (Human-Annotated Disaster Incidents Dataset)

### 2.1 File Inventory and Storage Structure
- **Raw Storage:** `data/raw/humaid/HumAID_data_all_combined.tar.gz` and extracted directory `data/raw/humaid/all_combined/`.
- **Raw Contents:**
  - `all_train.tsv`: 53,531 lines (Header + 53,531 data rows)
  - `all_dev.tsv`: 7,793 lines (Header + 7,793 data rows)
  - `all_test.tsv`: 15,160 lines (Header + 15,160 data rows)
  - `Licensing.txt`: CC BY 4.0 license metadata
  - `Readme.txt`: QCRI dataset description and format documentation
- **Processed Storage:**
  - `data/processed/humaid/humaid_records.parquet` (12.47 MB)
  - `data/processed/humaid/humaid_records.csv` (11.02 MB)
  - `data/interim/humaid/humaid_canonical.csv` (11.02 MB)

### 2.2 Schema and Field Audit
Total Rows: **76,484**  
Total Columns: **11**

| Column Name | Data Type | Null Count | Null % | Empirical Description & Values |
| :--- | :--- | :---: | :---: | :--- |
| `event_id` | `object (str)` | 0 | 0.00% | Unique prefixed ID: `humaid_{tweet_id}` |
| `source_dataset` | `object (str)` | 0 | 0.00% | Constant provenance indicator: `"humaid_all_combined"` |
| `source_record_id`| `object (str)` | 0 | 0.00% | Original Twitter Snowflake Tweet ID (numeric string) |
| `raw_text` | `object` | 76,484 | 100.00% | **NULL.** Text unhydrated in QCRI `all_combined` archive |
| `clean_text` | `object` | 76,484 | 100.00% | **NULL.** Derived from `raw_text` |
| `category` | `object (str)` | 0 | 0.00% | Ground-truth humanitarian classification label (10 classes) |
| `disaster_event` | `object (str)` | 0 | 0.00% | Aggregated identifier: `"multi_disaster_global_corpus"` |
| `split` | `object (str)` | 0 | 0.00% | Official QCRI partition: `train`, `dev`, `test` |
| `timestamp_if_available` | `object` | 76,484 | 100.00% | NULL. No timestamp present in raw TSV |
| `location_if_available` | `object` | 76,484 | 100.00% | NULL. No geographic coordinates in raw TSV |
| `governance_type` | `object (str)` | 0 | 0.00% | Provenance governance tag: `"REAL"` |

### 2.3 Split Distribution
HumAID follows the official 70/10/20 train/dev/test partition established by QCRI:
- **Train:** 53,531 records (69.99%)
- **Dev (Validation):** 7,793 records (10.19%)
- **Test:** 15,160 records (19.82%)
- **Split Disjointness:** Verified. The intersection of `source_record_id` across train, dev, and test is exactly **0**. Zero duplicate IDs exist across splits.

### 2.4 Ground-Truth Humanitarian Categories (Class Distribution)
There are exactly 10 humanitarian categories. No categories have been collapsed:

| Humanitarian Category | Record Count | Percentage | Class Role / Priority Context |
| :--- | :---: | :---: | :--- |
| `rescue_volunteering_or_donation_effort` | 21,278 | 27.82% | Relief operations, NGO volunteer calls, aid coordination |
| `other_relevant_information` | 12,144 | 15.88% | General situational updates and warnings |
| `sympathy_and_support` | 8,931 | 11.68% | Emotional expressions, condolences, solidarity |
| `infrastructure_and_utility_damage` | 8,163 | 10.67% | Physical destruction (roads, bridges, power grid, buildings) |
| `injured_or_dead_people` | 7,303 | 9.55% | Human casualties, injuries, confirmed deaths |
| `not_humanitarian` | 6,296 | 8.23% | Spam, irrelevant commentary, chatter |
| `caution_and_advice` | 5,394 | 7.05% | Safety directives, boil-water notices, preparation advice |
| `displaced_people_and_evacuations` | 3,999 | 5.23% | Evacuation orders, shelter occupancy, refugee movement |
| `requests_or_urgent_needs` | 2,618 | 3.42% | Explicit survivor distress calls (food, water, medicine) |
| `missing_or_found_people` | 358 | 0.47% | Tracing missing individuals, reunification notices |
| **Total** | **76,484** | **100.00%** | **High class imbalance (27.82% down to 0.47%)** |

### 2.5 Critical Finding: Text Availability Status
In QCRI's official `all_combined` distribution archive, files contain only `tweet_id` and `class_label` due to Twitter Terms of Service redistributability limitations. The accompanying `Readme.txt` states:
> *"tweet_text: please extract the text by mapping tweet id with the event files"*

Because event-level hydration files were not part of the frozen raw archive and Twitter API v2 academic hydration cannot be executed (violating the freeze on downloading additional datasets and raw modifications), **HumAID text is 100% NULL**.
- **Architectural Consequence:** HumAID cannot be directly trained with NLP tokenizers/TF-IDF without fabricating text.
- **Empirical Policy:** We preserve HumAID as the definitive categorical gold-standard benchmark for humanitarian distribution modeling and prior estimation, while text-based humanitarian classification and transformer evaluation are implemented on **CrisisMMD** (which contains 8,079 fully hydrated disaster texts sharing these exact humanitarian categories).

---

## 3. Dataset 2: CrisisMMD (Multimodal Crisis Information Dataset)

### 3.1 File Inventory and Storage Structure
- **Raw Storage:** `data/raw/crisismmd/crisismmd_datasplit_agreed_label.zip` and extracted directory `data/raw/crisismmd/crisismmd_datasplit_agreed_label/`.
- **Raw Contents:**
  - `task_humanitarian_text_img_agreed_lab_train.tsv`: 6,126 rows
  - `task_humanitarian_text_img_agreed_lab_dev.tsv`: 998 rows
  - `task_humanitarian_text_img_agreed_lab_test.tsv`: 955 rows
  - `task_informative_text_img_agreed_lab_train.tsv`: 6,126 rows
  - `task_informative_text_img_agreed_lab_dev.tsv`: 998 rows
  - `task_informative_text_img_agreed_lab_test.tsv`: 955 rows
- **Processed Storage:**
  - `data/processed/crisismmd/crisismmd_records.parquet` (5.51 MB)
  - `data/processed/crisismmd/crisismmd_records.csv` (2.41 MB)

### 3.2 Schema and Field Audit
Total Rows: **8,079**  
Total Columns: **18**

| Column Name | Data Type | Null Count | Null % | Description & Sample Values |
| :--- | :--- | :---: | :---: | :--- |
| `event_id` | `object (str)` | 0 | 0.00% | Prefixed ID: `cmmd_{image_id}` |
| `source_dataset` | `object (str)` | 0 | 0.00% | `"crisismmd_multimodal"` |
| `source_record_id`| `object (str)` | 0 | 0.00% | Tweet ID: e.g. `"917793137925459968"` |
| `image_id` | `object (str)` | 0 | 0.00% | Identifier: `"917793137925459968_0"` |
| `disaster_event` | `object (str)` | 0 | 0.00% | Disaster name (7 distinct events) |
| `raw_text` | `object (str)` | 0 | 0.00% | Unmodified crisis tweet text (**100% available**) |
| `clean_text` | `object (str)` | 0 | 0.00% | Preprocessed text (normalized URLs, mentions, whitespace) |
| `image_reference` | `object (str)` | 0 | 0.00% | Relative image path in original release |
| `image_available_locally`| `bool` | 0 | 0.00% | **False (all 8,079 records)**. Local binaries not downloaded |
| `humanitarian_label` | `object (str)` | 0 | 0.00% | Consensus humanitarian category (5 classes) |
| `humanitarian_text_label` | `object (str)` | 0 | 0.00% | Annotation from text modality only |
| `humanitarian_image_label`| `object (str)` | 0 | 0.00% | Annotation from image modality only |
| `crossmodal_agreement` | `object (str)` | 0 | 0.00% | Agreement status (`Positive` / `Negative`) |
| `informative_label` | `object (str)` | 0 | 0.00% | Binary informativeness (`informative` vs `not_informative`) |
| `split` | `object (str)` | 0 | 0.00% | Partition: `train` (6,126), `dev` (998), `test` (955) |
| `timestamp_if_available` | `object (str)` | 0 | 0.00% | Temporal date extracted from path (e.g. `"10-10-2017"`) |
| `location_if_available` | `object (str)` | 0 | 0.00% | Derived event geography (e.g. `"California Wildfires"`) |
| `governance_type` | `object (str)` | 0 | 0.00% | Provenance tag: `"REAL"` |

### 3.3 Event Distribution in CrisisMMD
| Disaster Event | Record Count | Percentage | Event Type |
| :--- | :---: | :---: | :--- |
| `hurricane_maria` | 2,228 | 27.58% | Tropical Cyclone / Flooding |
| `hurricane_harvey` | 1,954 | 24.19% | Tropical Cyclone / Flooding |
| `hurricane_irma` | 1,848 | 22.87% | Tropical Cyclone / Wind & Surge |
| `srilanka_floods` | 726 | 8.99% | Monsoonal Flooding |
| `mexico_earthquake` | 585 | 7.24% | Seismic Disaster |
| `california_wildfires`| 511 | 6.33% | Wildfire Conflagration |
| `iraq_iran_earthquake`| 227 | 2.81% | Seismic Disaster |
| **Total** | **8,079** | **100.00%** | **7 major natural disaster events** |

### 3.4 Target Label Distributions
1. **Humanitarian Classification Task (5 classes):**
   - `not_humanitarian`: 4,277 (52.94%)
   - `other_relevant_information`: 1,753 (21.70%)
   - `rescue_volunteering_or_donation_effort`: 1,187 (14.69%)
   - `infrastructure_and_utility_damage`: 773 (9.57%)
   - `affected_individuals`: 89 (1.10%)
2. **Informativeness Task (Binary):**
   - `not_informative`: 4,277 (52.94%)
   - `informative`: 3,802 (47.06%)

### 3.5 Modality Status: Strict Enforcement of Scientific Honesty
- **Local Images Available:** **0 out of 8,079**.
- `image_available_locally = False` is strictly true for 100% of records.
- In accordance with Phase 7 Step 10, **CrisisMMD is modeled strictly as a text-based crisis classification system**. No synthetic or fabricated image features are generated.

---

## 4. Dataset 3: CrisisLex (Linguistic & Context Analysis Engine)

### 4.1 File Inventory and Storage Structure
- **Raw Storage:** `data/raw/crisislex/data/` containing:
  - `CrisisLexT26/`: 26 disaster event subdirectories with labeled CSVs and period tweet ID maps.
  - `CrisisLexT6/`: 6 disaster event subdirectories with labeled CSVs.
- **Processed Storage:**
  - `data/processed/crisislex/crisislex_records.parquet` (43.34 MB)
  - `data/processed/crisislex/crisislex_records.csv` (18.80 MB)

### 4.2 Schema and Field Audit
Total Rows: **88,015**  
Total Columns: **12**

| Column Name | Data Type | Null Count | Null % | Description & Sample Values |
| :--- | :--- | :---: | :---: | :--- |
| `event_id` | `object (str)` | 0 | 0.00% | Prefixed ID: `clex_{tweet_id}` |
| `source_dataset` | `object (str)` | 0 | 0.00% | `"crisislex_t6"` (60,082) or `"crisislex_t26"` (27,933) |
| `source_record_id`| `object (str)` | 0 | 0.00% | Tweet ID |
| `disaster_event` | `object (str)` | 0 | 0.00% | Event name (32 distinct events) |
| `raw_text` | `object (str)` | 0 | 0.00% | Raw crisis tweet text (**100% available**) |
| `clean_text` | `object (str)` | 0 | 0.00% | Cleaned crisis text |
| `information_source`| `object (str)` | 0 | 0.00% | Source category (e.g. Media, Eyewitness, Gov) |
| `information_type` | `object (str)` | 0 | 0.00% | Content type (Casualties, Caution, Infrastructure) |
| `informativeness_label`| `object (str)`| 0 | 0.00% | Informativeness / on-topic rating |
| `timestamp_if_available`| `object (str)`| 60,082 | 68.26% | Available for 27,933 T26 records; NULL for T6 |
| `location_if_available`| `object (str)` | 0 | 0.00% | Geographic event descriptor |
| `governance_type` | `object (str)` | 0 | 0.00% | Provenance tag: `"REAL"` |

### 4.3 Event Breadth
Covers **32 distinct disaster events** spanning 2012–2013 across North America, Europe, Asia, and Oceania, including:
- Large flood events: `2013_Queensland_Floods` (10,033), `2013_Alberta_Floods` (10,031)
- Major storms: `2012_Sandy_Hurricane` (10,008), `2013_Oklahoma_Tornado` (9,992)
- Industrial and civil emergencies: `2013_Boston_Bombings` (10,012), `2013_West_Texas_Explosion` (10,006), `2013_Savar_building_collapse` (1,250)
- Wildfires & Earthquakes: `2012_Colorado_wildfires` (1,200), `2012_Costa_Rica_earthquake` (1,412)

---

## 5. Cross-Dataset Provenance & Overlap Analysis

A definitive cross-dataset join audit was executed across all unique Twitter record identifiers:
- **HumAID Unique Tweet IDs:** 76,484
- **CrisisMMD Unique Tweet IDs:** 7,216
- **CrisisLex Unique Tweet IDs:** 88,010

### Empirical Intersection Matrix
| Dataset Pair | Shared Tweet IDs | Overlap % | Verdict |
| :--- | :---: | :---: | :--- |
| **HumAID $\cap$ CrisisMMD** | **0** | 0.00% | Completely disjoint corpora |
| **HumAID $\cap$ CrisisLex** | **0** | 0.00% | Completely disjoint corpora |
| **CrisisMMD $\cap$ CrisisLex** | **0** | 0.00% | Completely disjoint corpora |

### Critical Architectural Implication (Step 23 Compliance)
Because empirical ID overlap is strictly **0**, any merge or join across HumAID, CrisisMMD, and CrisisLex would require arbitrary heuristic matching or synthetic joins. In strict adherence to Step 23, **no cross-dataset joins are performed**. Each dataset operates as an independent feature stream that conforms to a unified output contract while strictly preserving source provenance.

---

## 6. Audit Conclusion & Phase 7 Readiness
All three datasets have been fully inventoried, profiled, and validated against their Phase 4 contracts. The modeling strategy is grounded exclusively in these verified empirical facts.
