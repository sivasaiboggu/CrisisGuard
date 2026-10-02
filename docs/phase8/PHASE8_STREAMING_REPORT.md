# CrisisGuard — Phase 8: Apache Spark Structured Streaming Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **PASS — STRUCTURED STREAMING & TEMPORAL WINDOWING VERIFIED**

---

## 1. Executive Summary

Phase 8.6 implemented and executed the real-time stream processing pipeline using Apache Spark Structured Streaming 3.5.1 (`scripts/phase8/streaming/propagation_stream.py`). The streaming engine connected directly to Apache Kafka topic `crisisguard-propagation-events`, ingested all 5,004 live cascade events, enforced event-time semantics with a 1-hour watermark, computed windowed temporal aggregations, and committed dual streaming sinks to durable HDFS Parquet storage (`/crisisguard/phase8/streaming/`) and local feature stores.

---

## 2. Stream Architecture & Event-Time Semantics

- **Source Connector:** `spark-sql-kafka-0-10_2.12:3.5.1`
- **Topic Ingested:** `crisisguard-propagation-events` (2 partitions)
- **Offset Strategy:** `earliest` to `latest` (Micro-batch with `availableNow=True`)
- **Event-Time Field:** `event_timestamp` parsed from event payload
- **Watermark Specification:** `.withWatermark("event_timestamp", "1 hour")`
- **Tumbling Windows:** 1-hour non-overlapping event-time intervals
- **Sink 1 (Raw Events):** `hdfs://localhost:9000/crisisguard/phase8/streaming/parsed_events/` (Parquet)
- **Sink 2 (Windowed Metrics):** `hdfs://localhost:9000/crisisguard/phase8/streaming/windowed_metrics/` (Parquet)

---

## 3. Streaming Metrics & Window Aggregations

Total Time Windows Computed: **32 distinct 1-hour temporal windows**.

### Sample Window Aggregations (Top Cascades):
| Window Interval (Event-Time) | Cascade Scenario | Event Volume | Unique Sources | Unique Targets | Mean Synthetic Risk | Propagation Rate (Events/min) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `2026-09-27 00:00:00 - 01:00:00` | `COORDINATED_BOT_BURST` | **1,002** | 1,002 | 505 | 0.1247 | **16.70** |
| `2026-09-27 00:00:00 - 01:00:00` | `HIGH_VELOCITY_VIRAL` | **447** | 447 | 231 | 0.9179 | **7.45** |
| `2026-09-27 00:00:00 - 01:00:00` | `ORGANIC_DIFFUSION` | **119** | 119 | 57 | 0.3786 | **1.98** |
| `2026-09-27 01:00:00 - 02:00:00` | `HIGH_VELOCITY_VIRAL` | **464** | 464 | 353 | 0.9205 | **7.73** |
| `2026-09-27 01:00:00 - 02:00:00` | `ORGANIC_DIFFUSION` | **113** | 113 | 76 | 0.3906 | **1.88** |
| `2026-09-27 02:00:00 - 03:00:00` | `HIGH_VELOCITY_VIRAL` | **44** | 44 | 42 | 0.9224 | **0.73** |
| `2026-09-27 02:00:00 - 03:00:00` | `ORGANIC_DIFFUSION` | **114** | 114 | 94 | 0.3412 | **1.90** |

---

## 4. Reconciliation Baseline

| Dimension | Measured Streaming Metric | Expected Target | Status |
| :--- | :---: | :---: | :---: |
| **Total Processed Events** | **5,004** | 5,004 | PASS |
| **Unique Event Sources** | **4,986** | 4,986 | PASS |
| **Unique Non-Null Event Targets** | **2,508** | 2,508 (historical 2,509 incl. NULL) | PASS |
| **Total Unique Graph Nodes** | **7,494** | 7,494 (reconciled from historical 7,495) | PASS |
| **Unique Transmission Edges** | **4,999** | 4,999 | PASS |
| **Execution Duration** | **37.75s** | < 60s | PASS |

---

## 5. Artifact Checklist

- [x] Streaming Script: `scripts/phase8/streaming/propagation_stream.py`
- [x] Stream Summary JSON: `docs/phase8/streaming_metrics_summary.json`
- [x] Parquet Feature Output: `data/features/phase8/streaming/propagation_stream_metrics.parquet`
- [x] HDFS Sink 1: `hdfs://localhost:9000/crisisguard/phase8/streaming/parsed_events/` ($N=5,004$)
- [x] HDFS Sink 2: `hdfs://localhost:9000/crisisguard/phase8/streaming/windowed_metrics/` ($N=32$)

**Structured Streaming Status: PASS — PROCEED TO HIVE WAREHOUSE**
