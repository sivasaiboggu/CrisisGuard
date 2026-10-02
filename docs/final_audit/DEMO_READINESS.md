# CrisisGuard — 10-Minute Live Demo Readiness Plan

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Target Duration:** 10 Minutes Total  
**Audit Date:** September 2026  

---

## 1. Executive Summary

This document structures a clear, compelling, 10-minute live demonstration of the CrisisGuard Big Data pipeline. Every demonstration step is supported by concrete, existing terminal commands, physical artifacts, database tables, and analytical visualizations.

No mock data or fake screenshots are utilized. All demonstrated tools operate over the actual local cluster environment.

---

## 2. 10-Minute Demonstration Timeline & Script

```
[00:00 - 01:30] Part 1: Problem, Datasets & Architecture
[01:30 - 03:00] Part 2: AI Intelligence Engines (Phases 6 & 7)
[03:00 - 05:30] Part 3: Distributed Pipeline Execution (HDFS, Spark, GraphX)
[05:30 - 07:30] Part 4: Real-Time Streaming & Warehousing (Kafka, Structured Streaming, Hive)
[07:30 - 09:15] Part 5: Phase 9 Analytical Decision Support & Multi-Stream Ledger
[09:15 - 10:00] Part 6: Validation, Scientific Epistemics & Q&A Transition
```

---

## 3. Demonstration Step-by-Step Breakdown & Evidence

### Part 1: Problem, Datasets & Architecture Overview (0:00 – 1:30)
- **Narrative:** Introduce how viral synthetic media corrupts humanitarian disaster response and why single-node systems fail.
- **Evidence / Screen:** Display architecture diagram (`docs/phase8/PHASE8_ARCHITECTURE.md`) and dataset inventory (`data/processed/`).
- **Command:**
  ```bash
  ls -lh data/processed/*/
  ```
- **Key Talking Point:** Transparent provenance across 7 real and semi-synthetic datasets.

### Part 2: AI Intelligence Engines (1:30 – 3:00)
- **Narrative:** Demonstrate Phase 6 (Synthetic Media) and Phase 7 (Crisis Information).
- **Evidence / Screen:**
  - Show ResNet-18 Grad-CAM explainability heatmaps (`outputs/synthetic_media/explainability/`).
  - Inspect `unified_media_risk.parquet` (77 rows, uncalibrated) and `unified_crisis_intelligence.parquet` (104,130 rows, text-only).
- **Command:**
  ```bash
  python3 scripts/validation/validate_phase6_final.py
  python3 scripts/validation/validate_phase7_models.py
  ```

### Part 3: Distributed Pipeline Execution: HDFS, Spark, GraphX (3:00 – 5:30)
- **Narrative:** Show genuine distributed data flow from HDFS into Spark and GraphX.
- **Evidence / Screen:**
  - HDFS file listing: `hdfs://localhost:9000/crisisguard/data/processed/propagation/events.jsonl` (5,004 events).
  - GraphX PageRank output on 7,494 vertices.
  - Display PageRank log-distribution plot (`docs/phase8/figures/pagerank_distribution.png`).
- **Command:**
  ```bash
  head -n 5 data/features/phase8/graph/graphx_vertex_metrics.csv
  ```
- **Key Talking Point:** Reconciled 7,494 non-null vertices, Spearman $\rho = 0.9920$ with in-degree.

### Part 4: Real-Time Streaming & Warehousing: Kafka, Streaming, Hive (5:30 – 7:30)
- **Narrative:** Show live Kafka publishing, Spark Structured Streaming with watermarking, and Hive warehouse tables.
- **Evidence / Screen:**
  - Kafka topic partitions (`crisisguard.propagation.events`, 5,004 messages).
  - Spark Structured Streaming 1-minute tumbling windows (32 windows).
  - Hive Metastore query receipts.
- **Command:**
  ```bash
  python3 scripts/validation/validate_phase8.py
  ```

### Part 5: Phase 9 Analytical Decision Support & Multi-Stream Ledger (7:30 – 9:15)
- **Narrative:** Present the culminating decision-support layer. Emphasize the scientific refusal to create arbitrary joins or fake emergency priority scores (NO EDPI).
- **Evidence / Screen:**
  - Inspect 175,361-row unified multi-stream ledger (`phase9_multi_stream_intelligence.parquet`).
  - Demonstrate explicit NULL semantics and boolean availability flags.
- **Command:**
  ```bash
  python3 scripts/validation/validate_phase9.py
  ```

### Part 6: Validation, Epistemics & Wrap-Up (9:15 – 10:00)
- **Narrative:** Run the independent consistency auditor confirming zero contradictions across all phases.
- **Command:**
  ```bash
  python3 scripts/validation/audit_phase9_consistency.py
  ```
- **Key Conclusion:** CrisisGuard delivers a mathematically verified, distributed Big Data architecture that preserves scientific provenance at every tier.

---

## 4. Demo Readiness Checklist

| Element | Prepared Artifact | Test Status |
| :--- | :--- | :--- |
| **All Services Up** | Hadoop HDFS, Kafka broker, Hive metastore | Tested and verified |
| **Data Artifacts Ready** | All 5 Parquet files in `data/features/phase9/` | Verified on disk |
| **Visual Plots Ready** | 4 figures in `docs/phase8/figures/` + Grad-CAM heatmaps | Verified present |
| **Validation Commands** | Fast-executing test suites (< 15 seconds) | 100% PASS |
| **Backup Receipts** | Pre-generated execution logs in `docs/phase8/` and `docs/phase9/` | Complete fallback available |

---

*Demo readiness verdict: 100% READY FOR LIVE 10-MINUTE PRESENTATION.*
