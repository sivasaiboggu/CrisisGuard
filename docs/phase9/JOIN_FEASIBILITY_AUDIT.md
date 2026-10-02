# CrisisGuard — Phase 9.2: Identifier & Join Feasibility Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 9 — End-to-End Intelligence Integration, Analytical Validation & Final Decision-Support Layer  
**Date:** September 30, 2026  
**Status:** **PASS — ARCHITECTURALLY HONEST MULTI-STREAM ARCHITECTURE CONFIRMED**

---

## 1. Executive Summary & Scientific Mandate

A foundational scientific principle of the CrisisGuard project is:
> **"DO NOT create arbitrary joins. DO NOT manufacture relationships between datasets. If two datasets have no validated common identifier, KEEP THEM AS SEPARATE FEATURE STREAMS."**

This audit systematically evaluates every candidate join key between Phase 6 (Synthetic Media Intelligence), Phase 7 (Crisis Information Intelligence), Phase 8 (Propagation Graph & Streaming), and OpenStreetMap Road Infrastructure to determine whether any genuine, semantically valid relational linkages exist.

---

## 2. Cross-Dataset Identifier Evaluation

### 2.1. Pair 1: Phase 6 (Synthetic Media) ↔ Phase 7 (Crisis Information)
- **Phase 6 Candidate Key:** `content_id` (Forensics assets: 75 CIFAKE images, 2 Google DFD video clips, format `cifake_real_0000_4`, `dfd_synthetic_01`).
- **Phase 7 Candidate Key:** `content_id` / `source_record_id` (Disaster tweets and humanitarian text records: 88,015 CrisisLex, 15,160 HumAID, 955 CrisisMMD, format `humaid_721630546711986178`, `clex_t6_2012_sandy_1029`).
- **Identifier Semantics:** Incompatible. Phase 6 content IDs index computer vision forensics benchmarks; Phase 7 IDs index Twitter/social disaster text records.
- **Physical Key Overlap:** **0 records (0.00%)**.
- **Null Rates:** Phase 6 `content_id`: 0.00%; Phase 7 `content_id`: 0.00%.
- **Decision:** **`NO_VALID_JOIN`**

### 2.2. Pair 2: Phase 6 (Synthetic Media) ↔ Phase 8 (Propagation Graph & Streaming)
- **Phase 6 Candidate Key:** `content_id` (77 evaluated forensic media items).
- **Phase 8 Candidate Key:** `content_id` (5 simulated cascade topic identifiers: `dfdc_syn_bridge_collapse_84920`, `ff_face2face_mayoral_evac_0091`, `humaid_irma_2017_001928`, `crisismmd_harvey_img_49102`, `crisislex_california_fire_81729`).
- **Identifier Semantics:** The Phase 8 propagation cascades simulate the diffusion of 5 disaster/misinformation narratives across 7,494 social network accounts. While Phase 8 simulates propagation scenarios inspired by synthetic media topics, the specific experimental bench items in Phase 6 (`CIFAKE` and `Google DFD`) do not share direct entity IDs with the 5 simulated cascade topics.
- **Physical Key Overlap:** **0 records (0.00%)**.
- **Decision:** **`NO_VALID_JOIN`**

### 2.3. Pair 3: Phase 7 (Crisis Information) ↔ Phase 8 (Propagation Graph & Streaming)
- **Phase 7 Candidate Key:** `content_id` / `source_record_id` (104,130 specific disaster tweets).
- **Phase 8 Candidate Key:** `content_id` (5 topic-level narrative cascades) / `event_id` (5,004 individual retweet/forwarding events: `evt_humaid_irm_0000`, etc.).
- **Identifier Semantics:** Incompatible. Phase 8 `event_id` represents an instantaneous retweet/share event between two user nodes (`source_node` $\to$ `target_node`) in a simulated graph; Phase 7 `source_record_id` represents specific historical crisis tweets from 2012–2018.
- **Physical Key Overlap:** **0 records (0.00%)**.
- **Decision:** **`NO_VALID_JOIN`**

### 2.4. Pair 4: Phase 8 (Propagation Graph) ↔ OpenStreetMap (Road Infrastructure)
- **Phase 8 Candidate Key:** `node_name` / `vertex_id` (7,494 virtual social media accounts in the user interaction graph).
- **OSM Candidate Key:** `node_id` (63,660 physical road intersection coordinates with latitude and longitude).
- **Identifier Semantics:** Completely disjoint. Social network accounts represent human users and automated bots in a digital network topology, whereas OSM road nodes represent physical geographic coordinates in a road transportation network.
- **Physical Key Overlap:** **0 records (0.00%)**.
- **Decision:** **`NO_VALID_JOIN`**

---

## 3. Join Feasibility Matrix

| Dataset A | Dataset B | Candidate Key | Overlap Count | Collision Rate | Valid Semantic Relationship? | Join Decision |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Phase 6 (Media Risk)** | **Phase 7 (Crisis Intel)** | `content_id` | **0** / 77 | 0.00% | No (CV Forensics vs. Disaster Tweets) | **`NO_VALID_JOIN`** |
| **Phase 6 (Media Risk)** | **Phase 8 (Propagation)** | `content_id` | **0** / 77 | 0.00% | No (Bench forensics vs. simulated cascades) | **`NO_VALID_JOIN`** |
| **Phase 7 (Crisis Intel)** | **Phase 8 (Propagation)** | `content_id` / `event_id` | **0** / 104,130 | 0.00% | No (Historical tweets vs. cascade share events) | **`NO_VALID_JOIN`** |
| **Phase 8 (Social Graph)** | **OSM (Road Network)** | `node_id` / `node_name` | **0** / 7,494 | 0.00% | No (Social users vs. Physical road intersections) | **`NO_VALID_JOIN`** |
| **Phase 7 (Crisis Intel)** | **OSM (Road Network)** | `location` / `coordinates` | **0** | N/A | No (Unhydrated/missing micro-coordinates) | **`NO_VALID_JOIN`** |

---

## 4. Architectural Resolution: Provenance-Preserving Multi-Stream Architecture

Because no legitimate relational foreign keys exist across these independent data streams, **any forced join (e.g. fuzzy text matching, Cartesian cross-products, or fabricated synthetic keys) would constitute scientific misconduct and introduce catastrophic data leakage.**

Therefore, Phase 9 implements a **Parallel Feature Stream Architecture**:
1. **STREAM A — Synthetic Media Intelligence:** Preserves asset-level forensic scores, bounded synthetic risk, and model calibration status.
2. **STREAM B — Crisis Information Intelligence:** Preserves tweet-level crisis categories, humanitarian response labels, and confidence metrics.
3. **STREAM C — Propagation & Graph Intelligence:** Preserves node-level structural centrality (PageRank, degrees, connected components) and windowed diffusion velocities.
4. **STREAM D — Spatial & Road Infrastructure:** Preserves physical road network topologies for prospective emergency routing.

Each stream maintains 100% provenance integrity and is exposed through dedicated analytical tables without artificial concatenation.

**JOIN FEASIBILITY DECISION: PASS — PARALLEL MULTI-STREAM ARCHITECTURE APPROVED**
