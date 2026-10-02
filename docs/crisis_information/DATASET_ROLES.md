# CrisisGuard — Phase 7: Dataset Roles and Architectural Boundaries
**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 7 — Crisis Information Intelligence Engine  
**Date:** September 2026  
**Status:** FROZEN ROLE CONTRACT  

---

## 1. Architectural Role Framework

The Crisis Information Intelligence Engine ingests three independently collected, labeled, and distributed crisis datasets inherited from Phase 4:
1. **HumAID** (Qatar Computing Research Institute / Imran et al., 2021)
2. **CrisisMMD** (Qatar Computing Research Institute / Alam et al., 2018)
3. **CrisisLex** (CrisisLexT26 & CrisisLexT6 / Olteanu et al., 2014)

```
                            CRISIS INFORMATION
                                    │
                     ┌──────────────┼──────────────┐
                     │              │              │
                     ▼              ▼              ▼
                  HumAID        CrisisMMD       CrisisLex
                     │              │              │
                     ▼              ▼              ▼
              Humanitarian     Multimodal      Crisis Context
              Distribution      Analysis          Analysis
              & Benchmark    (Text Modality)     (Linguistic)
                     │              │              │
                     └──────────────┼──────────────┘
                                    ▼
                         Unified Feature Contract
                    (Preserving Dataset Provenance)
                                    │
                                    ▼
                        Downstream Big Data Layer
                      (Kafka / Spark / MLlib EDPI)
```

---

## 2. Dataset Roles & Validated Prediction Targets

### 2.1 HumAID: Humanitarian Information Classification & Benchmark Prior Engine
- **Core Role:** Establishing global humanitarian taxonomy distribution, class imbalance baselines, and disaster response priority priors across 10 official categories.
- **Empirical Prediction Target:** `category` (10 classes):
  1. `rescue_volunteering_or_donation_effort`
  2. `other_relevant_information`
  3. `sympathy_and_support`
  4. `infrastructure_and_utility_damage`
  5. `injured_or_dead_people`
  6. `not_humanitarian`
  7. `caution_and_advice`
  8. `displaced_people_and_evacuations`
  9. `requests_or_urgent_needs`
  10. `missing_or_found_people`
- **Official Split Protocol:** Maintained strictly per QCRI benchmark (Train: 53,531, Dev: 7,793, Test: 15,160).
- **Text Availability & Role Boundary:** Because raw tweet texts in the QCRI `all_combined` release are unhydrated (100% NULL in local processed files), HumAID serves as:
  - The gold-standard categorical distribution benchmark for class imbalance.
  - The categorical baseline estimator (stratified and prior-weighted baselines).
  - The schema contract definition for 10-class humanitarian classification.
  - **Forbidden:** Blind text synthesis or fabricating tweet text.

---

### 2.2 CrisisMMD: Multimodal-Aware Crisis Analysis (Text Modality Engine)
- **Core Role:** Supervised crisis text classification across humanitarian response categories and binary informativeness, operating under full text availability (8,079 records) and empirical awareness of multimodal constraints.
- **Empirical Prediction Targets:**
  1. **Primary Target — `humanitarian_label` (5 classes):**
     - `not_humanitarian` (52.94%)
     - `other_relevant_information` (21.70%)
     - `rescue_volunteering_or_donation_effort` (14.69%)
     - `infrastructure_and_utility_damage` (9.57%)
     - `affected_individuals` (1.10%)
  2. **Secondary Target — `informative_label` (Binary):**
     - `informative` (47.06%)
     - `not_informative` (52.94%)
- **Modality Boundary (Strict Scientific Honesty):**
  - Raw image references are cataloged in `image_reference`.
  - Local image binary files are **unavailable** (`image_available_locally = False` for 100% of records).
  - **Forbidden:** Claiming multimodal visual inference or synthesizing image vectors from paths. CrisisMMD is explicitly modeled as a verified text-based crisis classifier with crossmodal metadata tracking.

---

### 2.3 CrisisLex: Crisis-Event Linguistic & Context Analysis Engine
- **Core Role:** Large-scale linguistic profiling, disaster vocabulary extraction, temporal activity modeling, and informativeness context generation across 32 natural and civil emergencies.
- **Empirical Prediction Targets / Features:**
  - Rather than forcing an artificial single-label classifier over disparate collections (T26 and T6), CrisisLex provides:
    1. **Crisis Vocabulary Lexicon:** Event-specific and general disaster keyword densities (rescue, damage, medical, evacuation).
    2. **Event Activity Signals:** Message volume, temporal event clustering, and source attribution (`information_source`).
    3. **Content Type Indicators:** Verification of informational categories (`information_type`).
  - **Forbidden:** Inventing artificial "severity scores", "urgency weights", or synthetic truth labels.

---

## 3. Strict Architectural Prohibitions

1. **NO Blind Concatenation:** HumAID, CrisisMMD, and CrisisLex MUST NOT be concatenated into a single training DataFrame. Their schemas, event spans, label definitions, and text hydrations are fundamentally different.
2. **NO Synthetic Keys / Join Heuristics:** Because tweet ID overlap across all three datasets is 0.00%, no records may be merged or joined on tweet text similarity or approximate timestamps.
3. **NO EDPI Calculation in Phase 7:** Emergency Dispatch Priority Index (EDPI) calculations and arbitrary weight combinations (`0.4 * severity + ...`) belong strictly to the later MLlib phase. Phase 7 produces validated crisis information features only.
4. **NO Invented Labels:** Labels such as `"crisis severity"` or `"urgent triage level"` are prohibited unless directly annotated in the ground-truth data.
