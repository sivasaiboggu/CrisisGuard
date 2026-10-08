# CrisisGuard — Oral Examination (Viva) Defense & Risk Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Target:** Final Academic Viva / Oral Defense Preparation  
**Audit Date:** September 2026  

---

## 1. Executive Summary

This document prepares factual, evidence-backed answers to the most rigorous theoretical, architectural, and methodological questions likely to be asked by course instructors during the final oral evaluation (Viva).

Every answer is rooted strictly in the physical implementation, avoiding unsupported claims, hypothetical features, or exaggerated real-world performance.

---

## 2. Comprehensive Viva Question & Answer Defense Guide

### Q1: Why does this problem require Big Data tools?
- **Answer:** Crisis analytics operates over orthogonal data modalities that cannot be processed within a single monolithic runtime:
  1. *Unbounded Event Streaming:* Rapid burst dissemination requires distributed partitioning and event-time watermarking (Apache Kafka + Spark Structured Streaming).
  2. *Large-Scale Graph Analytics:* Iterative graph algorithms (PageRank, Connected Components) over social amplification networks are memory-bound and require partition-level graph caching (Spark GraphX).
  3. *Heterogeneous Analytical Warehousing:* Long-term incident auditing requires structured, partitioned SQL querying over petabyte-scale storage (Apache Hive + HDFS).
  Attempting to run real-time streaming, iterative graph matrix operations, and SQL OLAP in a single Python script leads to out-of-memory crashes and state-loss.

### Q2: Why HDFS?
- **Answer:** HDFS provides fault-tolerant, block-level distributed storage with write-once-read-many semantics suitable for immutable disaster incident logging. In CrisisGuard, HDFS stores 5,004 raw propagation events and Parquet partitions, decoupling persistence from compute workers.

### Q3: Why Apache Spark?
- **Answer:** Spark provides unified in-memory distributed compute, eliminating intermediate disk serialization bottlenecks common to legacy MapReduce. In CrisisGuard, Spark handles batch ETL, schema enforcement, and node ID indexing before feeding GraphX.

### Q4: Why Spark GraphX instead of NetworkX?
- **Answer:** NetworkX is an in-memory single-threaded Python library that fails when graph sizes exceed physical workstation RAM. GraphX partitions vertices and edges across distributed RDD partitions, utilizing the Pregel message-passing abstraction to compute iterative PageRank across thousands of nodes efficiently.

### Q5: Why Apache Kafka?
- **Answer:** Kafka acts as a distributed pub/sub commit log that decouples high-velocity data producers from downstream consumers. It absorbs high-velocity bursts (such as coordinated bot attacks) and provides topic partitioning with offset management, guaranteeing that downstream streaming jobs never drop messages during load spikes.

### Q6: Why Spark Structured Streaming?
- **Answer:** Structured Streaming offers native event-time processing, micro-batch engine fault tolerance, and watermark-driven late data handling. In CrisisGuard, a 1-hour event-time watermark and 1-hour tumbling windows aggregate propagation velocity and burst indicators over the 32-hour simulation timeline, producing clean hourly snapshots without race conditions or late-data contamination.

### Q7: Why Apache Hive?
- **Answer:** Hive provides schema-on-read relational abstraction over distributed Parquet files, exposing standard ANSI SQL querying via the Hive Metastore. This allows post-incident crisis analysts to run ad-hoc SQL aggregation queries across propagation events, graph centralities, and streaming metrics without writing custom code.

### Q8: Which datasets are real, and which are semi-synthetic?
- **Answer:**
  - **REAL DATA:**
    1. *HumAID:* Real disaster tweets annotated for humanitarian tasks ($N=15,160$ test).
    2. *CrisisMMD:* Real disaster tweets with damage categories ($N=8,079$).
    3. *CrisisLex:* Real historical disaster tweets from 32 events ($N=88,015$).
    4. *OpenStreetMap:* Real physical road network geometry ($N=63,660$ nodes).
    5. *Google DFD Controlled Sample:* Real manipulated video sequences ($N=5$ videos, 1,714 frames).
    6. *CIFAKE Controlled Sample:* Curated diffusion and photographic images ($N=72$ test).
  - **SEMI-SYNTHETIC DATA:**
    - *Propagation Cascades:* 5,004 diffusion events across 7,494 nodes generated via parameterized stochastic models (`ORGANIC`, `VIRAL`, `BOT_BURST`) to simulate network spread.

### Q9: Why are the datasets not joined directly into one big table?
- **Answer:** Because **no valid common key exists** across disparate academic benchmarks. Forensic media samples (CIFAKE), historical crisis tweets (CrisisLex from 2013), and synthetic cascade graphs possess zero shared entity IDs or coordinates. Manufacturing fuzzy matches or synthetic foreign keys would constitute academic fraud. Instead, CrisisGuard implements a **Parallel Feature Stream Architecture** that preserves complete source provenance.

### Q10: Why is there no Emergency Dispatch Priority Index (EDPI) formula?
- **Answer:** Constructing an ad-hoc linear formula such as $\text{Priority} = 0.4 \times \text{MediaRisk} + 0.3 \times \text{CrisisScore} + 0.3 \times \text{PageRank}$ assigns arbitrary, unvalidated weights to disparate domains without empirical ground truth. In an emergency setting, arbitrary weighting leads to dangerous, ungrounded dispatch decisions. Phase 9 provides transparent multi-attribute feature representations for qualified human responders rather than an ungrounded automated index.

### Q11: What does "synthetic risk" actually mean?
- **Answer:** In CrisisGuard, `synthetic_risk` is an analytical feature derived from the deep learning classifier's output logit. It represents the model's assessment of visual tampering artifacts. **It is NOT proof of malicious intent, disinformation, or physical falsity.**

### Q12: Are the deep learning model probabilities calibrated?
- **Answer:** **NO.** Both Phase 6 models are audited as `calibration_status = UNCALIBRATED`. They output raw sigmoid activations that must not be interpreted as Bayesian posterior probabilities.

### Q13: What is the modality of CrisisMMD in CrisisGuard?
- **Answer:** CrisisMMD is modeled strictly as **TEXT-ONLY** crisis classification with multimodal metadata tracking. No local image binaries were present, and no fake image embeddings were fabricated.

### Q14: How was correctness validated across tools?
- **Answer:** Every phase incorporates automated validation scripts verifying cryptographic SHA-256 hashes, exact row counts, schema conformity, duplicate IDs, bounded confidence ranges, and zero arbitrary weights. Additionally, independent consistency auditors verify that tests do not simply call themselves.

### Q15: How does data flow between tools in Phase 8?
- **Answer:**
  1. Events are written to **HDFS**.
  2. **Spark Batch** reads HDFS, maps node IDs, and outputs edge lists.
  3. **GraphX** reads edge lists, computes PageRank/Components, and writes CSV metrics.
  4. Events and edges are published to **Kafka** topics.
  5. **Spark Structured Streaming** reads Kafka topics and computes tumbling window aggregations.
  6. **Apache Hive** tables are created over the persistent sinks for analytical SQL querying.

---

*Viva defense preparation completed: All responses factually substantiated by code and artifacts.*
