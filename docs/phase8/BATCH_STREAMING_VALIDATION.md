# CrisisGuard — Phase 8: Batch vs. Streaming Reconciliation & Validation Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **PASS — 100% RECONCILIATION BETWEEN SPARK BATCH AND STRUCTURED STREAMING**

---

## 1. Executive Summary

A mandatory big data engineering requirement of Phase 8 is the formal dual-pathway reconciliation between **Spark Batch Preprocessing** (Phase 8.3) and **Spark Structured Streaming** (Phase 8.6). Both pipelines independently processed the propagation cascade universe:
- Batch path: Ingested `propagation_events.parquet` from HDFS in bulk.
- Streaming path: Ingested events published to Apache Kafka topic `crisisguard-propagation-events` via micro-batching with event-time watermarking.

This audit cross-validates total event counts, unique source nodes, unique target nodes, total unique graph nodes, and unique transmission edges across both computational paradigms.

---

## 2. Reconciliation Matrix

| Analytical Metric | Spark Batch Processing | Spark Structured Streaming | Discrepancy ($\Delta$) | Reconciliation Status |
| :--- | :---: | :---: | :---: | :---: |
| **Total Event Count** | **5,004** | **5,004** | **0** (0.00%) | **PERFECT MATCH** |
| **Unique Source Nodes** | **4,986** | **4,986** | **0** (0.00%) | **PERFECT MATCH** |
| **Unique Target Nodes** | **2,508** | **2,508** | **0** (0.00%) | **PERFECT MATCH** |
| **Total Unique Graph Vertices** | **7,494** | **7,494** | **0** (0.00%) | **PERFECT MATCH** |
| **Unique Transmission Edges** | **4,999** | **4,999** | **0** (0.00%) | **PERFECT MATCH** |

---

## 3. Discrepancy & Root Cause Analysis

### Forensic Vertex-Count Consistency Audit (7,495 vs. 7,494 Reconciled):
A rigorous forensic audit was conducted on the reported vertex counts across the pipeline:
1. **Initial Discrepancy Mechanism:** In the initial pipeline run, Spark batch mapping and streaming reconciliation reported **7,495** unique node identifiers, while GraphX constructed a graph of **7,494** vertices ($4,999$ directed edges).
2. **Underlying Cause:** Exactly 5 propagation events represent `ROOT_BROADCAST` cascades (unparented injection seeds where `target_node = NULL`). In initial preprocessing, unioning `source_node` and `target_node` without null filtering included `NULL` as a distinct entity ($7,494 + 1 = 7,495$), which Spark sorted first and mapped to `vertex_id = 1` (`1,` in CSV).
3. **GraphX Filter Behavior:** GraphX's Scala parser (`PropagationGraph.scala`) split lines by comma and required `parts.length >= 2`. Since Java's `String.split(",")` drops trailing empty strings, line `1,` returned length 1 and was excluded, leaving 7,494 valid user vertices.
4. **Remediation & Hardening:** Explicit `.filter(F.col("node_name").isNotNull())` and `.filter(F.col("target_node").isNotNull())` guards were implemented in both Spark batch preparation and streaming reconciliation. The graph vertex universe is now rigorously unified across Spark batch (**7,494**), GraphX (**7,494**), Structured Streaming (**7,494**), and Reconciliation (**7,494**).
5. **Exact Message Flow Parity:**
   - Every Kafka message (5,004 events) was acknowledged and processed without drops or duplicate retries.
   - The 1-hour event-time watermark correctly encompassed the entire temporal span of the cascades.
   - The 5 root broadcast events ($5,004 - 4,999 = 5$) are recognized as genuine unparented root injections with null target vertices, correctly generating no spurious graph nodes.

---

## 4. Architectural Implications

This exact parity confirms that:
1. The Kafka producer and broker did not lose, truncate, or duplicate any cascade records.
2. Spark Structured Streaming guarantees exactly-once processing semantics through HDFS write-ahead logging and checkpointing.
3. Downstream emergency analysis can transition seamlessly between historical batch profiling and real-time streaming ingestion with zero data divergence.

**Reconciliation Status: PASS — DUAL ENGINE INTEGRITY CONFIRMED**
