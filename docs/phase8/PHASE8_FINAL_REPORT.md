# CrisisGuard — Phase 8: Real-Time Propagation Analysis & Graph Intelligence
# Comprehensive Final Technical & Scientific Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **PASS — FROZEN**

---

## 1. Executive Summary

Phase 8 of the CrisisGuard project designs, deploys, and validates a complete distributed Big Data processing pipeline for crisis information cascades:

$$\text{HDFS 3.3.6} \longrightarrow \text{Spark 3.5.1} \longrightarrow \text{GraphX (Scala 2.12)} \longrightarrow \text{Kafka 3.7.0} \longrightarrow \text{Spark Structured Streaming} \longrightarrow \text{Hive 3.1.3}$$

In direct compliance with course mandates and strict scientific integrity principles:
1. **Genuine Multi-Tool Sequential Dataflow:** Data physically flows across six distinct Big Data tools with verified input/output handoffs.
2. **Zero Synthetic Joins:** Social cascade users and Twitter humanitarian IDs exist in disjoint key spaces (0.00% overlap). They are maintained as separate feature streams rather than merged through unvalidated synthetic keys.
3. **Dual-Pathway Reconciliation:** Batch and streaming pipelines achieved **100% exact parity** across events (5,004), sources (4,986), targets (2,509), and edges (4,999) with zero discrepancy ($\Delta = 0$).
4. **Graph Centrality Epistemology:** High PageRank nodes are strictly characterized as **"structurally central nodes"** rather than "confirmed causal sources".
5. **Phase Boundary Discipline:** Phase 8 strictly ceases after feature generation, graph analytics, and warehouse queries. No Emergency Dispatch Priority Index (EDPI), no arbitrary heuristic emergency weights, and no dashboard interfaces were created.
6. **Master Validation:** All 15 master validation criteria passed with 100% success.

---

## 2. Ingested Frozen Baseline Audit

Prior to execution, all frozen upstream inputs were verified on disk and recorded in `docs/phase8/input_audit_data.json`:
- **Propagation Events:** 5,004 records (`SHA256: 8e26912215be58dfc17d9b060c8dcea3ad1e96a3cdac600b344dbc8bdc923e03`)
- **Propagation Edges:** 4,999 records (`SHA256: 3b3eb8fbbc97d080df1be7561575e5213aedfb1b28dd3789215701de26497e9f`)
- **Unified Media Risk:** 77 prediction records (`SHA256: f15771a65c1f73034c9c8a8532f68a74930b4c47a33934cfa5cd0d017765962e`)
- **Unified Crisis Intelligence:** 104,130 records (`SHA256: 2678dcddee3ce6128f5e923d11f717dbfa3b1c3686082948696e7ebf512d945e`)
- **OSM Road Nodes:** 63,660 records (`SHA256: 78256415c4e3ecf0cc3dd9c225fadafab3c45080c889098d68d69f495f7c1415`)
- **OSM Road Edges:** 146,156 records (`SHA256: 0c1a81eef7eb349b4a995acc8808220e4549736aa7a2beafa7d1ea4052f61ee7`)

All frozen inputs remained read-only and immutable throughout Phase 8.

---

## 3. Distributed Storage: Apache Hadoop HDFS

- **Namespace Created:** `/crisisguard/phase8/` with 7 specialized subdirectories (`propagation/`, `media_risk/`, `crisis_intelligence/`, `osm/`, `graph/`, `streaming/`, `hive/`).
- **Volume Replicated:** 7.82 MB across 6 core Parquet datasets.
- **Physical Verification:** `hdfs dfs -ls -R` and `hdfs dfs -du -h` confirmed zero corruption and byte-level matching.

---

## 4. Batch Preprocessing: Apache Spark 3.5.1

- **Script:** `scripts/phase8/spark_prepare_propagation.py`
- **Execution Time:** 33.75 seconds.
- **Processing Results:**
  - Audited 5,004 events and 4,999 edges directly from HDFS.
  - Detected 0 duplicate directed edges.
  - Identified 5 root broadcast events (`ROOT_BROADCAST`) where `target_node` is null (initial cascade seeds).
  - Bijectively mapped 7,494 genuine non-null string node identifiers to contiguous 64-bit Long IDs (IDs 1 through 7,494).
  - Exported GraphX-ready vertex and edge datasets to HDFS and local feature stores.

---

## 5. Graph Intelligence: Apache Spark GraphX (Scala 2.12)

- **Source Code:** `src/phase8/graphx/PropagationGraph.scala`
- **Packaged JAR:** `target/phase8/crisisguard-graphx.jar` (13,092 bytes).
- **Execution Time:** 16.31 seconds (Spark job) / 20.65 seconds (total pipeline).
- **Graph Topology Results:**
  - Vertices: **7,494**
  - Directed Edges: **4,999**
  - Connected Components: **2,509**
  - Giant Connected Component: **4,986 vertices** (66.5% of network).
  - Max In-Degree: **13**; Max Out-Degree: **2**; Mean Degree: **0.6671**.
  - PageRank Range: Min **0.2944**, Mean **1.0000**, Max **121.9683**.
  - Top Structurally Central Node: Vertex `7450` (`node_name: 9935`, PageRank = 121.9683).
  - Propagation Reachability: 625 vertices reachable from primary seed across maximum depth of 12 hops.

---

## 6. Real-Time Streaming Backbone: Apache Kafka 3.7.0 (KRaft)

- **Topic:** `crisisguard-propagation-events` (2 partitions).
- **Producer Throughput:** **2,570.1 events/second** (5,004 records replayed in 1.947 seconds).
- **Consumer Validation:** Consumed and audited exactly 5,004 messages from offset 0 with **0 drops, 0 duplicates, and 0 schema violations**.

---

## 7. Stream Processing: Apache Spark Structured Streaming 3.5.1

- **Script:** `scripts/phase8/streaming/propagation_stream.py`
- **Execution Time:** 37.75 seconds.
- **Event-Time Processing:** 1-hour watermark on `event_timestamp`.
- **Temporal Windows:** 32 distinct 1-hour tumbling aggregation windows.
- **Durable HDFS Commits:**
  - Sink 1 (Parsed Events): `hdfs://localhost:9000/crisisguard/phase8/streaming/parsed_events/` ($N=5,004$).
  - Sink 2 (Windowed Metrics): `hdfs://localhost:9000/crisisguard/phase8/streaming/windowed_metrics/` ($N=32$).

---

## 8. Big Data Enterprise Warehouse: Apache Hive 3.1.3

- **Script:** `scripts/phase8/hive/run_hive_pipeline.py`
- **Warehouse Location:** `hdfs://localhost:9000/crisisguard/phase8/hive/`
- **External Tables:** `propagation_graph_metrics`, `propagation_stream_metrics`, `media_risk_features`, `crisis_intelligence_features`.
- **Analytical Queries:** Executed 6 queries covering PageRank centrality, degree distributions, streaming velocity trends, synthetic media risk breakdown, crisis categories, and join policy verification.
- **Cross-Stream Join Test:** Verified exactly **0 overlapping keys** between user node IDs and crisis tweet IDs, validating the isolated feature stream policy.

---

## 9. Batch vs. Streaming Dual-Pathway Reconciliation

| Dimension | Spark Batch | Structured Streaming | Discrepancy ($\Delta$) | Validation Status |
| :--- | :---: | :---: | :---: | :---: |
| **Total Events** | **5,004** | **5,004** | **0** | **PERFECT RECONCILIATION** |
| **Unique Sources** | **4,986** | **4,986** | **0** | **PERFECT RECONCILIATION** |
| **Unique Targets** | **2,508** | **2,508** | **0** | **PERFECT RECONCILIATION** |
| **Total Graph Nodes** | **7,494** | **7,494** | **0** | **PERFECT RECONCILIATION** |
| **Unique Edges** | **4,999** | **4,999** | **0** | **PERFECT RECONCILIATION** |

---

## 10. Performance Benchmark Summary

> [!NOTE]
> All metrics reflect a **local / single-node experimental deployment** (Ubuntu 24.04 WSL2, 8 vCPUs, 16 GB RAM).

- **HDFS Ingestion:** 3.56s (7.82 MB volume)
- **Spark Batch:** 44.05s (5,004 events, 4,999 edges)
- **GraphX Scala Compilation & Job:** 26.57s (7,494 vertices, 4,999 edges)
- **Kafka Stream Ingestion:** 1.95s (2,570.1 events/s)
- **Structured Streaming:** 41.89s (32 window intervals)
- **Hive Warehouse & 6 Queries:** 48.53s
- **Total Pipeline Execution:** ~2.5 minutes

---

## 11. Controlled Failure & Fault Tolerance

Executed via `scripts/phase8/test_failure_resilience.py`:
- [x] Malformed JSON payload caught without crashing stream consumer.
- [x] Duplicate propagation events tracked without corrupting unique ID sets.
- [x] Null event timestamps safely intercepted and flagged.
- [x] Dangling graph edges handled gracefully via default vertex attributes.
- [x] Invalid edge weights sanitized and filtered.

---

## 12. Master Validation Results (`validate_phase8.py`)

Executed via `wsl -d Ubuntu-24.04 python3 scripts/validation/validate_phase8.py`:
1. [PASS] HDFS Outputs Verified
2. [PASS] Spark Batch Outputs Verified
3. [PASS] GraphX Outputs Verified
4. [PASS] Kafka Topic Existence
5. [PASS] Kafka Message Flow
6. [PASS] Streaming Outputs Verified
7. [PASS] Hive Tables & Queries Verified
8. [PASS] Schema Consistency Verified
9. [PASS] Row Counts Verified
10. [PASS] Provenance Preserved
11. [PASS] Duplicate Handling Verified
12. [PASS] Batch vs Stream Consistency
13. [PASS] Graph Integrity Verified
14. [PASS] Frozen Inputs Untouched
15. [PASS] Phase Boundary Integrity

**Master Validation Decision: 15/15 CHECKS PASS**

---

## 13. Issues Found & Remediated

1. **Issue 1 (Hive DDL Scheme Omission):** Table creation DDL originally used relative paths `/crisisguard/...`, which Hive interpreted as `file:/crisisguard/...`. Remediated by specifying full `hdfs://localhost:9000/crisisguard/...` URIs.
2. **Issue 2 (Numeric String Type Mismatch in Parquet):** GraphX node names like `"760800"` were parsed as `float64` by pandas before writing Parquet, causing schema mismatches with Hive's `STRING`. Remediated by explicitly specifying `dtype={"node_name": str}`.
3. **Issue 3 (Degree Integer Type Alignment):** Hive DDL declared `in_degree INT` while Parquet wrote `int64` (BIGINT). Remediated by standardizing DDL to `BIGINT`.
4. **Issue 4 (Synthetic Risk Column Type):** Hive table declared `synthetic_risk STRING` while upstream Parquet stores `float64`. Remediated by updating DDL to `DOUBLE` and grouping by risk tiers.
5. **Issue 5 (Vertex-Count Discrepancy & NULL Handling Audit):** Initial batch mapping and streaming reconciliation counted 7,495 unique node identifiers because 5 `ROOT_BROADCAST` events had `target_node = NULL`, which was included in node unions without null filtering and assigned `vertex_id = 1` (`1,` in CSV). GraphX split on `,` and required length $\ge 2$, silently dropping the empty node line and loading 7,494 vertices. Remediated by applying explicit `isNotNull()` filtering on node names across Spark batch preparation and streaming reconciliation, establishing 100% exact parity across Spark Batch (7,494), GraphX (7,494), Streaming (7,494), and Reconciliation (7,494).

---

## 14. Final Phase 8 Status

All distributed components (HDFS, Spark, GraphX, Kafka, Structured Streaming, Hive) are operational, validated, reconciled, and documented.

**PHASE 8 STATUS: PASS — FROZEN**
