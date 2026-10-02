# CrisisGuard — Phase 7: CrisisLex Data & Context Audit
**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 7 — Crisis Information Intelligence Engine  
**Date:** September 2026  
**Status:** COMPLETE & EMPIRICALLY AUDITED  

---

## 1. Overview & Dataset Provenance

CrisisLex (Olteanu et al., ICWSM 2014) is a benchmark lexicon and disaster tweet corpus comprising two major sub-corpora:
1. **CrisisLexT26:** 26 disaster events from 2012–2013 across the globe, annotated by crowdsourced volunteers for informativeness, information source, and information type.
2. **CrisisLexT6:** 6 major disasters with binary on-topic vs. off-topic annotations.

Both collections were standardized in Phase 4 under `data/processed/crisislex/crisislex_records.parquet`.

---

## 2. Schema and Entity Profile

Audit performed on `data/processed/crisislex/crisislex_records.parquet`:
- **Total Records:** 88,015
- **Unique Tweet IDs:** 88,010 (5 cross-event overlaps)
- **Sub-Corpora Breakdown:**
  - `crisislex_t6`: 60,082 records (68.26%)
  - `crisislex_t26`: 27,933 records (31.74%)
- **Disaster Events:** 32 distinct natural and civil emergencies

### Schema Columns (12)
| Column Name | Data Type | Null Count | Description & Empirical Values |
| :--- | :--- | :---: | :--- |
| `event_id` | `object (str)` | 0 | Unique identifier: `clex_{tweet_id}` |
| `source_dataset` | `object (str)` | 0 | `"crisislex_t6"` or `"crisislex_t26"` |
| `source_record_id` | `object (str)` | 0 | Raw Twitter ID string |
| `disaster_event` | `object (str)` | 0 | Event name (e.g. `2012_Sandy_Hurricane`, `2013_Boston_Bombings`) |
| `raw_text` | `object (str)` | 0 | Original tweet text (**100% available**) |
| `clean_text` | `object (str)` | 0 | Cleaned tweet text (**100% available**) |
| `information_source` | `object (str)` | 0 | Source category (Media, Eyewitness, NGO, etc.) |
| `information_type` | `object (str)` | 0 | Content category (Casualties, Donations, Infrastructure, etc.) |
| `informativeness_label`| `object (str)` | 0 | Informativeness rating |
| `timestamp_if_available`| `object (str)` | 60,082 | Available for T26 (27,933 records); NULL for T6 |
| `location_if_available` | `object (str)` | 0 | Geographic event location descriptor |
| `governance_type` | `object (str)` | 0 | Provenance governance tag: `"REAL"` |

---

## 3. Disaster Event Inventory (Top 10 Events by Volume)

| Disaster Event | Sub-Corpus | Records | Event Type |
| :--- | :---: | :---: | :--- |
| `2013_Queensland_Floods` | T6 | 10,033 | Monsoonal Floods (Australia) |
| `2013_Alberta_Floods` | T6 | 10,031 | Riverine Floods (Canada) |
| `2013_Boston_Bombings` | T6 | 10,012 | Civil / Terror Incident (USA) |
| `2012_Sandy_Hurricane` | T6 | 10,008 | Hurricane / Storm Surge (USA) |
| `2013_West_Texas_Explosion` | T6 | 10,006 | Industrial Explosion (USA) |
| `2013_Oklahoma_Tornado` | T6 | 9,992 | Severe Tornado (USA) |
| `2013_Russia_meteor` | T26 | 1,442 | Celestial / Shockwave Incident (Russia) |
| `2012_Costa_Rica_earthquake` | T26 | 1,412 | Severe Seismic Event (Costa Rica) |
| `2013_Savar_building_collapse` | T26 | 1,250 | Structural Disaster (Bangladesh) |
| `2012_Colorado_wildfires` | T26 | 1,200 | Conflagration / Wildfire (USA) |

---

## 4. Informativeness Label Distribution

| Label | Record Count | Percentage | Annotator Interpretation |
| :--- | :---: | :---: | :--- |
| `on-topic` | 32,462 | 36.88% | Relevant to disaster (T6 sub-corpus) |
| `off-topic` | 27,620 | 31.38% | Irrelevant chatter (T6 sub-corpus) |
| `Related and informative` | 16,849 | 19.14% | Actionable crisis information (T26) |
| `Related - but not informative` | 7,732 | 8.78% | Crisis mention without actionable facts (T26) |
| `Not related` | 2,863 | 3.25% | Completely unrelated tweet (T26) |
| `Not applicable` | 489 | 0.56% | Ambiguous / unjudgeable (T26) |
| **Total** | **88,015** | **100.00%** | **Consensus Crowdsourced Annotations** |

---

## 5. Architectural Role in CrisisGuard (Step 14 Compliance)

In strict adherence to Step 14:
- CrisisLex is **NOT** forced into an artificial single-label classifier across heterogeneous sub-corpora.
- Instead, CrisisLex serves as the **Crisis-Event Linguistic and Context Engine**:
  1. **Disaster Vocabulary Extraction:** Top crisis keywords across casualty, infrastructure, rescue, and alert dimensions.
  2. **Event Activity Modeling:** Event frequency, message volume, and source distributions.
  3. **Linguistic Surface Statistics:** Tweet length, token counts, uppercase ratio (urgency proxy), mention density, and URL density.
- **Strict Prohibition:** Zero synthetic "severity", "urgency weights", or "ground truth probabilities" are fabricated from CrisisLex.
