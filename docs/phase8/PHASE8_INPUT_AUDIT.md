# CrisisGuard — Phase 8: Input Audit & Frozen Baseline Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **PASS — ALL FROZEN INPUTS VERIFIED**

---

## 1. Input Audit Objectives & Policies

Before executing any Phase 8 distributed Big Data operations (HDFS $\rightarrow$ Spark $\rightarrow$ GraphX $\rightarrow$ Kafka $\rightarrow$ Spark Structured Streaming $\rightarrow$ Hive), an exhaustive physical and cryptographic audit of all frozen upstream inputs was performed.

### Strict Governance Rules:
1. **Zero Input Regeneration:** Upstream frozen datasets from Phase 4, Phase 6, and Phase 7 must not be re-generated or retroactively altered.
2. **Zero In-Place Mutation:** Source Parquet files remain read-only; derived features and Big Data outputs are placed in dedicated Phase 8 directories (`/crisisguard/phase8/` in HDFS and `data/features/phase8/` locally).
3. **No Unvalidated Cross-Corpus Joins:** No synthetic or arbitrary joins between HumAID, CrisisMMD, CrisisLex, Media-Risk, or Propagation cascades. Disjoint streams remain independent.

---

## 2. Audit Matrix of Frozen Upstream Inputs

| Dataset / Artifact | Local Physical Path | Record Count | Column Count | Cryptographic SHA-256 Hash | Upstream Phase & Role |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Propagation Events** | `data/processed/propagation/propagation_events.parquet` | **5,004** | 11 | `8e26912215be58dfc17d9b060c8dcea3ad1e96a3cdac600b344dbc8bdc923e03` | Phase 4 (Semi-synthetic cascades; replayed via Kafka) |
| **Propagation Edges** | `data/processed/propagation/propagation_edges.parquet` | **4,999** | 6 | `3b3eb8fbbc97d080df1be7561575e5213aedfb1b28dd3789215701de26497e9f` | Phase 4 (Directed network topology for GraphX) |
| **Unified Media Risk** | `data/features/synthetic_media/unified_media_risk.parquet` | **77** | 12 | `f15771a65c1f73034c9c8a8532f68a74930b4c47a33934cfa5cd0d017765962e` | Phase 6 (Synthetic media risk predictions) |
| **Unified Crisis Intelligence** | `data/features/crisis_information/unified_crisis_intelligence.parquet` | **104,130** | 18 | `2678dcddee3ce6128f5e923d11f717dbfa3b1c3686082948696e7ebf512d945e` | Phase 7 (Humanitarian classification & lexical features) |
| **OSM Road Nodes** | `data/processed/osm/road_nodes.parquet` | **63,660** | 5 | `78256415c4e3ecf0cc3dd9c225fadafab3c45080c889098d68d69f495f7c1415` | Phase 4 (Physical infrastructure coordinates) |
| **OSM Road Edges** | `data/processed/osm/road_edges.parquet` | **146,156** | 9 | `0c1a81eef7eb349b4a995acc8808220e4549736aa7a2beafa7d1ea4052f61ee7` | Phase 4 (Physical road segment graph) |

---

## 3. Schema & Field Verification

### 3.1 Propagation Events Schema ($N=5,004$)
- `event_id`: Unique identifier for each cascade action (string).
- `scenario_id`: Cascade scenario grouping identifier (string).
- `propagation_type`: Cascade mechanism (`BROADCAST`, `CLUSTER_DIFFUSION`, `TREE_CASCADE`).
- `content_id`: Referenced synthetic or authentic media identifier (string).
- `source_node`: Broadcasting / forwarding node ID (string).
- `target_node`: Receiving node ID (string).
- `timestamp`: Event generation timestamp (ISO 8601 string / datetime).
- `parent_event_id`: Preceding event ID in cascade branch.
- `synthetic_media_risk`: Probability score of synthetic media payload.
- `crisis_priority_if_present`: Categorical indicator.
- `governance_tag`: Governance classification tag (`SEMI_SYNTHETIC`).

### 3.2 Propagation Edges Schema ($N=4,999$)
- `edge_id`: Unique directed edge identifier (string).
- `source_node`: Origin vertex ID (string).
- `target_node`: Destination vertex ID (string).
- `weight`: Edge transmission probability / weight (float).
- `cascade_id`: Scenario / cascade group identifier.
- `governance_tag`: Governance label (`SEMI_SYNTHETIC`).

### 3.3 Media Risk & Crisis Intelligence Schemas
- Media Risk ($N=77$): Retains calibrated media authenticity scores across DFD and CIFAKE evaluation subsets.
- Crisis Intelligence ($N=104,130$): Complete union across HumAID test predictions ($15,160$), CrisisMMD test predictions ($955$), and CrisisLex features ($88,015$).

---

## 4. Input Audit Decision

All 6 primary input artifacts were located, checked for row counts, verified against cryptographic checksums, and validated for schema consistency.

**Audit Status: PASS — PROCEED TO PHASE 8.2 (HDFS INGESTION)**
