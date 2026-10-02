# CrisisGuard — Phase 8: Apache Spark Batch Preprocessing Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **PASS — SPARK BATCH PREPROCESSING & GRAPH PREPARATION COMPLETE**

---

## 1. Executive Summary

Apache Spark batch preprocessing (`scripts/phase8/spark_prepare_propagation.py`) executed successfully on Apache Spark 3.5.1 against HDFS data ingested in Phase 8.2 (`hdfs://localhost:9000/crisisguard/phase8/propagation/`).

The batch pipeline validated schema contracts, enforced strong data types, audited timestamp continuity, performed duplicate edge analysis, mapped arbitrary string node IDs to contiguous 64-bit Long integers required by GraphX, and exported prepared vertex and edge structures to HDFS and local feature tables.

---

## 2. Ingested Data Dimensions & Quality Audit

| Metric | Measured Value | Verification Rationale |
| :--- | :---: | :--- |
| **Input Propagation Events** | **5,004** | Matches Phase 4 frozen propagation events exactly |
| **Input Propagation Edges** | **4,999** | Matches Phase 4 frozen directed edges exactly |
| **Root Broadcast Events** | **5** | Initial unparented seed posts (`ROOT_BROADCAST`) |
| **Cascade Edges** | **4,999** | Directed transmissions ($5,004 - 5 = 4,999$) |
| **Duplicate Directed Edges** | **0** | Graph topology contains zero multigraph edge collisions |
| **Total Unique Graph Vertices** | **7,494** | Distinct non-null union vertices (reconciled from historical 7,495 after filtering NULL targets from 5 root broadcasts) |
| **Unique Event Sources** | **4,986** | Nodes initiating broadcasts or forwarding events |
| **Unique Non-Null Event Targets**| **2,508** | Nodes receiving cascade messages (2,509 if including historical NULL target) |
| **Min Event Time** | `2026-09-27 00:00:00` | Temporal baseline start |
| **Max Event Time** | `2026-09-28 03:38:50` | Temporal cascade span |

---

## 3. Propagation Scenario & Mechanism Distribution

### 3.1 Scenario Breakdown
- `ORGANIC_DIFFUSION`: **3,047** events (60.89%) — Stochastic user-to-user retweet cascade.
- `COORDINATED_BOT_BURST`: **1,002** events (20.02%) — Rapid synchronized amplification.
- `HIGH_VELOCITY_VIRAL`: **955** events (19.08%) — Dense hub broadcast and rapid forward branch.

### 3.2 Propagation Mechanism Breakdown
- `ORGANIC_RETWEET`: **3,044** events
- `BOT_AMPLIFIED`: **1,001** events
- `HIGH_VELOCITY_SHARE`: **954** events
- `ROOT_BROADCAST`: **5** events (the 5 seed origins)

---

## 4. GraphX Preprocessing & Transformation

### 4.1 Vertex ID Mapping
GraphX requires vertices to be indexed as 64-bit signed Long values (`VertexId = Long`). The batch preprocessor established a bijective mapping:
- Vertices sorted alphabetically and assigned dense contiguous Long IDs: $1 \le \text{vertex\_id} \le 7,494$ (historical pre-reconciliation batch run indexed $7,495$ prior to explicit NULL filtering).
- Node metadata joined with in-degree and out-degree metrics.
- Exported to:
  - HDFS: `hdfs://localhost:9000/crisisguard/phase8/graph/vertices.parquet` and `vertices.csv`
  - Local: `data/features/phase8/graph/vertices.parquet` and `vertices.csv`

### 4.2 Edge Mapping
- Each directed transmission $(u, v)$ mapped to $(src\_id: \text{Long}, dst\_id: \text{Long}, weight: \text{Double})$.
- Exported to:
  - HDFS: `hdfs://localhost:9000/crisisguard/phase8/graph/edges.parquet` and `edges.csv`
  - Local: `data/features/phase8/graph/edges.parquet` and `edges.csv`

---

## 5. Performance & Execution Profile

- **Spark Version:** 3.5.1
- **Master:** `local[2]`
- **Total Batch Execution Time:** **33.75 seconds**
- **Output Artifacts Verified:**
  - `docs/phase8/spark_batch_summary.json`
  - `data/features/phase8/graph/vertices.csv` ($N=7,494$ reconciled; historical pre-filter $N=7,495$)
  - `data/features/phase8/graph/edges.csv` ($N=4,999$)
  - HDFS `/crisisguard/phase8/graph/` verified populated.

**Spark Batch Status: PASS — GRAPHX INPUTS READY**
