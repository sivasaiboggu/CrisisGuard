# Project CrisisGuard: Status & Master Architecture Specification

**Project Title:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course Context:** CSE412 — Big Data & Large-Scale Computing  
**Status Date:** September 2026  

---

## 1. Executive Status & Lifecycle Freeze

```
============================================================
PROJECT LIFECYCLE STATUS: CORE IMPLEMENTATION COMPLETE
============================================================
Phase 4 (Profiling, Ingestion & Preprocessing): FROZEN
Phase 5 (Distributed Environment Setup):        FROZEN
Phase 6 (Synthetic Media Detection Engine):     FROZEN (WITH DOCUMENTED LIMITATIONS)
Phase 7 (Crisis Information Intelligence):     FROZEN (WITH DOCUMENTED LIMITATIONS)
Phase 8 (Big Data Distributed Pipeline):       FROZEN
Phase 9 (Decision Support & Multi-Stream):     FROZEN

Implementation Phases Remaining: 0
============================================================
Current Project State: Core Implementation COMPLETE.
Remaining Work: Final academic report, presentation slides, demo walkthrough, viva defense, and final submission packaging.
(Note: These remaining activities represent documentation and presentation preparation, NOT a new implementation phase.)
============================================================
```

---

## 2. Project Objective & Final Architecture

In acute humanitarian emergencies (e.g., natural disasters, industrial emergencies, civil crises), the viral dissemination of synthetic media (deepfakes, manipulated crisis video, misleading imagery) misdirects disaster relief operations, confuses emergency responders, and accelerates panic.

**CrisisGuard** is an end-to-end distributed Big Data analytics pipeline integrating:
1. **Distributed Event Storage (Hadoop HDFS):** Partitioned, fault-tolerant persistence of propagation events and cascade topology (`hdfs://localhost:9000/crisisguard/...`).
2. **Distributed Batch ETL (Apache Spark):** Bijective node ID indexing and directed edge extraction across 7,494 unique graph nodes.
3. **Iterative Graph Analytics (Spark GraphX):** Distributed PageRank ($maxIter=20, resetProb=0.15$) and Weakly Connected Components across cascade vertices.
4. **Distributed Streaming Message Bus (Apache Kafka):** High-throughput, partitioned stream ingestion (`crisisguard.propagation.events` and `crisisguard.propagation.edges`).
5. **Real-Time Stream Processing (Spark Structured Streaming):** 1-hour tumbling window aggregations and burst velocity scoring with 1-hour event-time watermarking (32 streaming windows).
6. **Analytical Warehousing (Apache Hive):** Schema-enforced relational warehouse backed by Parquet/HDFS (`default.propagation_events`, `default.graphx_vertex_metrics`, `default.propagation_stream_metrics`).
7. **Multi-Stream Analytical Decision Support (Phase 9):** Provenance-preserving integration layer unifying Media Forensics (77 rows), Crisis NLP (104,130 rows), Propagation Graph (7,494 rows), and Spatial Infrastructure (63,660 rows) into a 175,361-record Multi-Stream Analytical Ledger (`phase9_multi_stream_intelligence.parquet`).

---

## 3. High-Level Pipeline Flow

```
[Raw Datasets]
       │
       ▼
[Hadoop HDFS Storage: hdfs://localhost:9000/crisisguard/]
       │
       ▼
[Apache Spark Batch: Node Indexing & Edge Extraction]
       │
       ▼
[Spark GraphX (Scala): PageRank & Connected Components (7,494 vertices)]
       │
       ▼
[Apache Kafka: Topics crisisguard.propagation.events & edges (5,004 & 4,999 msgs)]
       │
       ▼
[Spark Structured Streaming: 1-Hour Tumbling Window Aggregations (32 windows)]
       │
       ▼
[Apache Hive Warehouse: metastore_db/ (3 Analytical Tables)]
       │
       ▼
[Phase 9 Parallel Multi-Stream Ledger: 175,361 Records (Explicit NULLs, Zero EDPI)]
```

---

## 4. Phase-by-Phase Completion Summary

### Phase 4: Data Profiling, Ingestion & Preprocessing [COMPLETED — FROZEN]
- 7 datasets profiled and preprocessed into clean Parquet formats in `data/processed/`.
- CIFAKE (500 preprocessed development records), Google DFD (12 sample frames, 4 media records), HumAID (76,484 records), CrisisMMD (8,079 records), CrisisLex (88,015 records), OpenStreetMap (63,660 road nodes, 146,156 road edges).
- Validation: `scripts/validation/validate_processed_data.py` (PASS).

### Phase 5: Distributed Environment & Infrastructure Setup [COMPLETED — FROZEN]
- Standardized Hadoop 3.3.6 (HDFS), Apache Spark 3.5.1, Apache Kafka 3.6.0, Apache Hive 3.1.3 on WSL2 Ubuntu 24.04 with Java 11.
- Configuration artifacts verified in `config/hadoop/`, `config/spark/`, `config/kafka/`, `config/hive/`.
- Validation: `scripts/validation/validate_phase5_environment.py` (PASS).

### Phase 6: Synthetic Media Detection Engine [COMPLETED — FROZEN WITH LIMITATIONS]
- Spatial ResNet-18 image classifier trained on CIFAKE; Temporal ResNet-18 video classifier evaluated on Google DFD controlled sample.
- Output: `unified_media_risk.parquet` (77 records).
- All records formally audited as `calibration_status = UNCALIBRATED`. `synthetic_risk` strictly treated as an analytical feature without proof of malicious intent.
- Validation: `scripts/validation/validate_phase6_final.py` (11/11 PASS).

### Phase 7: Crisis Information Intelligence Engine [COMPLETED — FROZEN WITH LIMITATIONS]
- Fine-tuned DistilBERT transformer and classical TF-IDF + Logistic Regression baselines on CrisisMMD; prior baselines on HumAID; contextual lexicon features on CrisisLex.
- Output: `unified_crisis_intelligence.parquet` (104,130 records: 88,015 CrisisLex + 15,160 HumAID test + 955 CrisisMMD test).
- Modality: Strictly text-only crisis modeling with multimodal metadata tracking; zero local images; zero claims of multimodal visual classification.
- Validation: `scripts/validation/validate_phase7_models.py` (15/15 PASS), `audit_phase7_consistency.py` (12/12 PASS).

### Phase 8: Big Data Propagation & Graph Streaming Pipeline [COMPLETED — FROZEN]
- End-to-end distributed execution: HDFS $\to$ Spark $\to$ GraphX $\to$ Kafka $\to$ Streaming $\to$ Hive.
- Final Reconciled Graph: 5,004 propagation events, 4,999 directed edges, 5 root broadcast events, 4,986 unique sources, 2,508 unique non-null targets, 7,494 GraphX vertices, 2,509 connected components, 32 streaming tumbling windows.
- Reconciled historical NULL-target bug: intermediate 7,495 mapped nodes reconciled to authoritative **7,494** non-null graph vertices.
- Validation: `scripts/validation/validate_phase8.py` (15/15 PASS).

### Phase 9: End-to-End Decision Support & Multi-Stream Integration [COMPLETED — FROZEN]
- Parallel Feature Stream Architecture (`STREAM_A` through `STREAM_D`):
  - `phase9_media_intelligence.parquet`: 77 records
  - `phase9_crisis_intelligence.parquet`: 104,130 records
  - `phase9_propagation_intelligence.parquet`: 7,494 records
  - `phase9_spatial_intelligence.parquet`: 63,660 records
  - `phase9_multi_stream_intelligence.parquet`: **175,361 records** (Unified Multi-Stream Ledger)
- Strict Epistemic Governance: Zero arbitrary priority weights (NO EDPI, NO Danger Score); zero forced joins (`NO_VALID_JOIN`); explicit NULL semantics for unavailable stream attributes.
- Validation: `scripts/validation/validate_phase9.py` (14/14 PASS), `audit_phase9_consistency.py` (10/10 PASS).

---

## 5. Master Validation Summary

All automated test suites execute locally and confirm 100% compliance:
- **Master Final Project Validator (`validate_final_project.py`):** **10 / 10 CHECKS PASSED**
- **Independent Final Project Auditor (`audit_final_project.py`):** **6 / 6 CHECKS PASSED**
- **Blocking Technical Issues:** **0**
- **Unverified Items:** **0**

---

## 6. Remaining Work Checklist (Documentation & Presentation)

- [x] Correct README.md to reflect final Phases 4–9 architecture and eliminate legacy Phase 0 text.
- [x] Update Phase 8 documentation references to the reconciled 7,494 vertex count.
- [x] Refresh PROJECT_STATUS.md to reflect all phases frozen.
- [ ] Compile final 6–10 page Academic/Technical Course Report using verified sections in `docs/final_audit/FINAL_REPORT_READINESS.md`.
- [ ] Prepare final presentation slide deck (PPT).
- [ ] Record / rehearse 10-minute live demonstration according to `docs/final_audit/DEMO_READINESS.md`.
- [ ] Review Viva Defense Q&A in `docs/final_audit/VIVA_RISK_AUDIT.md`.
- [ ] Package final submission archive.
