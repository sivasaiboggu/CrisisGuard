# CrisisGuard — Phase 9 Analytical Results Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** 9 — End-to-End Intelligence Integration & Analytical Validation  
**Date:** September 2026  
**Status:** PASS — SCIENTIFICALLY VALIDATED  

---

## 1. Executive Summary

This report documents the rigorous empirical and statistical analyses conducted on the four independent feature streams within the CrisisGuard Phase 9 decision-support layer:
1. **Stream A (Synthetic Media Intelligence):** 77 evaluated media items (CIFAKE images + DFD video frames).
2. **Stream B (Crisis Information Intelligence):** 104,130 humanitarian and disaster communication records (CrisisLex, HumAID, CrisisMMD).
3. **Stream C (Propagation Graph Intelligence):** 7,494 unique graph vertices, 4,999 directed propagation edges, and 32 streaming windows.
4. **Stream D (Spatial Road Infrastructure):** 63,660 road network nodes and 146,156 road edges from OpenStreetMap.

In strict compliance with the **Most Important Scientific Rule**, no arbitrary or manufactured joins were forced between datasets possessing disjoint semantic entities. All analyses presented below reflect valid internal and structural characteristics of the respective streams without ungrounded cross-domain causal assertions.

---

## 2. Propagation Graph & Centrality Analysis

### 2.1 Graph Topology Overview
Phase 8 executed distributed graph computation via Apache Spark GraphX on 5,004 propagation events, yielding:
- **Total Graph Vertices:** 7,494
- **Directed Cascade Edges:** 4,999
- **Root Broadcast Events:** 5 (source nodes broadcasting without a predecessor, `target_node = NULL`)
- **Total Weakly Connected Components:** 2,509
- **Giant Component (Component ID 1):** 4,986 vertices (66.53% of all network nodes)
- **Isolated / Boundary Vertices:** 2,508 components with 1 vertex each (boundary targets)

### 2.2 Centrality Distributions
- **In-Degree ($k_{in}$):**
  - Range: $[0, 13]$
  - Mean: $0.6671$
  - Standard Deviation: $1.0210$
  - Median: $0.0$
  - Nodes with $k_{in} \ge 1$: 2,508 nodes (receivers/amplifiers)
- **Out-Degree ($k_{out}$):**
  - Range: $[0, 2]$
  - Mean: $0.6671$
  - Standard Deviation: $0.4713$
  - Median: $1.0$
  - Max Out-Degree: 2
- **PageRank ($\pi$):**
  - Range: $[0.1500, 3.4287]$
  - Mean: $0.2798$
  - Standard Deviation: $0.2312$
  - Median: $0.1500$ (base damping value $(1-d)$ for unreferenced nodes)

### 2.3 Topological Correlation Study
To evaluate the relationship between node connectivity and structural influence, Spearman rank-order correlation coefficients ($\rho$) were computed across all 7,494 graph nodes:

| Metric Pair | Spearman $\rho$ | $p$-Value | Epistemic Classification | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **In-Degree vs PageRank** | **0.9920** | $< 10^{-15}$ | COMPUTED | Extremely strong monotonic alignment; in directed cascade trees, inbound forwarding citations almost entirely govern stationary random walk probability. |
| **Out-Degree vs PageRank** | **0.4873** | $< 10^{-15}$ | COMPUTED | Moderate correlation; forward transmitters act as intermediate bridges across cascade levels. |
| **Total Degree vs PageRank** | **0.8644** | $< 10^{-15}$ | COMPUTED | Strong overall topological alignment between node activity and network prominence. |

*Epistemic Limitation:* Centrality measures structural position within the simulated propagation topology. They do NOT measure real-world user intent, credibility, or physical social influence.

---

## 3. Synthetic Media Risk Profile (Stream A)

Stream A consolidates 77 forensic inference records evaluated in Phase 6:
- 72 CIFAKE test images (ResNet-18)
- 5 Deepfake Detection (DFD) video sequences (Temporal ResNet-18)

### 3.1 Statistical Distribution
- **Sample Size ($N$):** 77
- **Mean Synthetic Risk:** $0.4712$
- **Standard Deviation:** $0.4441$
- **Minimum:** $0.000096$
- **25th Percentile ($P_{25}$):** $0.006198$
- **Median ($P_{50}$):** $0.331409$
- **75th Percentile ($P_{75}$):** $0.986524$
- **Maximum:** $0.999983$

### 3.2 Risk Stratification
Using standard non-arbitrary risk tiers:
- **Low Risk ($[0.0, 0.33)$):** 38 records (49.35%) — predominantly verified pristine CIFAKE real samples.
- **Medium Risk ($[0.33, 0.66)$):** 6 records (7.79%) — boundary decision items.
- **High Risk ($[0.66, 1.0]$):** 33 records (42.86%) — detected AI-generated images and facial manipulation videos.

The distribution displays a pronounced bimodal shape, typical of deep neural network sigmoid logits under confident binary classification.

*Crucial Epistemic Caveat:* Both Phase 6 models are formally audited as **`calibration_status = UNCALIBRATED`**. Consequently, `synthetic_risk` and `synthetic_probability` represent raw network sigmoid scores and must NOT be interpreted as true posterior Bayesian probabilities.

---

## 4. Crisis Information Intelligence Profile (Stream B)

Stream B provides humanitarian context across 104,130 records from three benchmark crisis datasets processed in Phase 7:
1. **CrisisLex (T6 + T26):** 88,015 records (84.52%) — text-based informativeness and topical filtering.
2. **HumAID (Combined Disaster Sub-Corpora):** 15,160 records (14.56%) — humanitarian task categorization.
3. **CrisisMMD (Disaster Sub-Corpus):** 955 records (0.92%) — humanitarian category tagging.

### 4.1 Categorical Breakdown (Top 10 Classes)
| Class / Category | Record Count | Percentage | Primary Source |
| :--- | :--- | :--- | :--- |
| **Ontopic_Classification** | 60,082 | 57.70% | CrisisLex T26 |
| **Other Useful Information** | 7,627 | 7.32% | CrisisLex T6 / HumAID |
| **Affected individuals** | 4,790 | 4.60% | CrisisLex T6 |
| **Sympathy and support** | 4,650 | 4.47% | CrisisLex T6 |
| **rescue_volunteering_or_donation_effort** | 4,415 | 4.24% | HumAID |
| **Not labeled** | 3,419 | 3.28% | CrisisLex T26 |
| **other_relevant_information** | 2,664 | 2.56% | HumAID |
| **Donations and volunteering** | 2,404 | 2.31% | CrisisLex T6 |
| **Caution and advice** | 2,306 | 2.21% | CrisisLex T6 |
| **not_humanitarian** | 1,789 | 1.72% | HumAID |

### 4.2 Model Confidence & Calibration
- **Model Score Range:** $[0.1111, 0.9998]$
- **Model Confidence Mean:** $0.7842$ (TF-IDF + Calibrated/Logistic Ensembles)
- **Epistemic Integrity:** All CrisisMMD records are classified as **TEXT-ONLY**; no phantom vision embeddings or multi-modal fusion was introduced. HumAID records operate over dehydrated tweet metadata with unavailable tweet body text.

---

## 5. Streaming Velocity & Temporal Dynamics (Stream C)

Phase 8 streaming metrics captured 32 tumbling 1-hour windows across 5,004 propagation events:

| Scenario Name | Total Events | Active Windows | Mean Event Rate (/min) | Peak Rate (/min) | Mean Synthetic Risk | Propagation Character |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **COORDINATED_BOT_BURST** | 1,002 | 1 | 16.70 /s (1002/m) | 16.70 /s | 0.1247 | Concentrated flash burst; low media risk synthetic payload. |
| **HIGH_VELOCITY_VIRAL** | 955 | 3 | 5.30 /s | 7.73 /s | 0.9203 | Rapid cascade growth; high synthetic risk payload (synthetic video narrative). |
| **ORGANIC_DIFFUSION** | 3,047 | 28 | 1.81 /s | 2.03 /s | 0.3839 | Sustained low-velocity spread over long temporal horizon. |

### 5.1 Temporal Alignment Feasibility
Phase 8 events possess timestamps recorded in `2026-09-30T04:xx:xxZ`. In contrast, Phase 7 benchmark crisis tweets originate from historical disasters (2012–2018), and Phase 6 items lack temporal broadcast provenance. Therefore, **no cross-stream temporal join was executed**. Temporal analysis is strictly confined within Stream C where genuine event timestamps exist.

---

## 6. Spatial Infrastructure Profile (Stream D)

Stream D ingests the Phase 4 OpenStreetMap road network for the target crisis region:
- **Total Road Intersections (Vertices):** 63,660 nodes
- **Total Road Segments (Directed Edges):** 146,156 edges
- **Coordinate System:** WGS84 Geographic Coordinates (Latitude, Longitude)
- **Spatial Alignment:** None of the social media posts (Phase 7) or synthetic propagation events (Phase 8) contain verified geographic GPS coordinates. In strict accordance with Phase 9.12 guidelines, spatial road nodes are preserved as independent infrastructure features available for future GIS extension rather than artificially bound to tweets using fabricated coordinates.

---

## 7. Analytical Conclusion

The analytical integration confirms:
1. Strong mathematical coherence within each respective domain (Spearman $\rho = 0.9920$ for graph topology; bimodal separation for forensic risk).
2. Clean separation of concerns across disparate data modalities.
3. Uncompromised epistemic integrity through the explicit refusal to create ungrounded linear dispatch priority formulas (e.g. EDPI) or fabricated relational links.
