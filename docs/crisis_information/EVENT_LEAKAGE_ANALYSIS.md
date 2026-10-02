# CrisisGuard — Phase 7: Event Leakage & Generalization Analysis
**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 7 — Crisis Information Intelligence Engine  
**Date:** September 2026  
**Status:** COMPLETED SCIENTIFIC EVALUATION  

---

## 1. Executive Summary & Leakage Problem Formulation

In crisis informatics, random row-level train/dev/test splits frequently introduce **event-level data leakage**. When tweets originating from the exact same disaster event appear in both training and test partitions, models can achieve deceptively high accuracy by memorizing event-specific geographic terms (e.g. "Houston", "San Juan", "Oaxaca"), localized hashtags (e.g. `#HurricaneHarvey`), and temporary local infrastructure names, rather than learning generalizable disaster semantics.

In accordance with Phase 7 Steps 4 and 16:
1. We analyze the event overlap within the official QCRI benchmark splits.
2. We document the exact overlap across all partitions.
3. We perform a secondary **Leave-One-Event-Out (LOEO)** experiment holding out an entire unseen disaster event to measure true generalization.
4. We strictly refrain from claiming "unseen-event generalization" on the official benchmark.

---

## 2. Event Distribution Across Official Splits (CrisisMMD)

Empirical cross-tabulation of disaster events across official benchmark splits in `data/processed/crisismmd/crisismmd_records.parquet`:

| Disaster Event | Train Split | Dev Split | Test Split | Total Records | Event Share |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `california_wildfires` | 362 | 71 | 78 | 511 | 6.33% |
| `hurricane_harvey` | 1,483 | 223 | 248 | 1,954 | 24.19% |
| `hurricane_irma` | 1,392 | 241 | 215 | 1,848 | 22.87% |
| `hurricane_maria` | 1,724 | 272 | 232 | 2,228 | 27.58% |
| `iraq_iran_earthquake` | 175 | 29 | 23 | 227 | 2.81% |
| `mexico_earthquake` | 428 | 78 | 79 | 585 | 7.24% |
| `srilanka_floods` | 562 | 84 | 80 | 726 | 8.99% |
| **All Events (Total)** | **6,126** | **998** | **955** | **8,079** | **100.00%** |

### Critical Leakage Finding
- **Unique Events in Train:** 7 (100.0%)
- **Unique Events in Dev:** 7 (100.0%)
- **Unique Events in Test:** 7 (100.0%)
- **Event Intersection (Train $\cap$ Test):** Exactly **7 out of 7 events**.

**Scientific Implication:**  
The official QCRI CrisisMMD benchmark partition is a stratified row-level split that maintains identical event distributions across train, dev, and test. While this provides a valid benchmark for **in-event message classification**, test set performance inevitably benefits from lexical familiarity with named entities from all 7 disaster events.

---

## 3. Secondary Generalization Experiment: Unseen-Event Holdout

To evaluate performance under authentic disaster triage conditions (where a newly occurring disaster has zero prior labeled tweets in the training set), a Leave-One-Event-Out (LOEO) evaluation was conducted:
- **Holdout Event:** `hurricane_maria` (the largest event in the corpus: 2,228 records, tropical cyclone / severe flooding).
- **Training Partition:** 6 remaining disaster events (5,851 records: California Wildfires, Hurricane Harvey, Hurricane Irma, Iraq-Iran Earthquake, Mexico Earthquake, Sri Lanka Floods).
- **Evaluation Partition:** `hurricane_maria` exclusively (2,228 unseen records).

### Empirical Results Comparison
| Metric | Official In-Distribution Split | Unseen-Event Holdout (`hurricane_maria`) | Generalization Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **0.6754** | **0.5637** | **-11.17%** |
| **Macro F1** | **0.5364** | **0.4864** | **-5.00%** |

### Error & Vocabulary Shift Analysis
1. **Entity-Specific Vocabulary Drop:** Tweets referring to local geography ("San Juan", "Puerto Rico", "Arecibo", "Guajataca Dam") had never appeared in the 6 training disasters.
2. **Transferable Humanitarian Signals:** Core disaster action verbs ("evacuate", "rescued", "destroyed", "supplies", "shelter") transferred successfully, enabling a respectable **0.4864 Macro F1** on completely unseen disaster data.
3. **Minority Class Fragility:** Classes like `affected_individuals` and `infrastructure_and_utility_damage` suffered the largest recall degradations on unseen events due to localized descriptions of damage.

---

## 4. Architectural Policy

1. **Benchmark Preservation:** In accordance with Step 4, we retain the official benchmark split as the primary evaluation standard to ensure comparability with published literature.
2. **Honest Reporting:** Every model card, final report, and documentation artifact explicitly qualifies benchmark results as in-event performance and cites the -11.2% generalization penalty for unseen events.
