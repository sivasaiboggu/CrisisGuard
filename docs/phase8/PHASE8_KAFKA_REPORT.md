# CrisisGuard — Phase 8: Apache Kafka Ingestion & Stream Replay Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **PASS — KAFKA STREAM REPLAY & AUDIT VERIFIED**

---

## 1. Executive Summary

Phase 8.5 deployed an Apache Kafka streaming infrastructure (Kafka 3.7.0 running in KRaft metadata mode on `localhost:9092`). Topic `crisisguard-propagation-events` was provisioned with 2 partitions. The dedicated producer (`scripts/phase8/kafka/produce_propagation_events.py`) replayed all 5,004 validated real Phase 4 propagation events without fabricating synthetic events or corrupting timestamps.

Consumer validation tooling (`scripts/phase8/kafka/consume_and_validate.py`) connected to the broker, assigned all partitions from offset 0, and audited payload schemas, counting exactly 5,004 events with zero dropped records, zero duplicates, and zero schema violations.

---

## 2. Topic Configuration & Broker Topology

- **Broker Address:** `localhost:9092`
- **Metadata Management:** Apache Kafka KRaft (Kafka Raft Metadata mode, zero external Zookeeper dependency)
- **Topic Name:** `crisisguard-propagation-events`
- **Partitions:** 2
- **Replication Factor:** 1 (Single-node local cluster deployment)
- **Message Serialization:** UTF-8 Encoded JSON
- **Partition Key Strategy:** Keyed by `scenario_id` to guarantee strictly ordered delivery per cascade scenario.

---

## 3. Producer Throughput & Transmission Metrics

| Metric | Measured Value | Unit / Benchmark |
| :--- | :---: | :--- |
| **Input Source Dataset** | `data/processed/propagation/propagation_events.parquet` | Frozen Phase 4 cascade dataset |
| **Total Events Produced** | **5,004** | 100.0% completion rate |
| **Invalid / Dropped Records** | **0** | Strict zero-loss guarantee |
| **Elapsed Publishing Time** | **1.947** | Seconds |
| **Ingestion Throughput** | **2,570.1** | Events / Second |
| **Producer Acks Configuration** | `all` (-1) | Durability guarantee |
| **Compression / Batching** | Batch size: 16 KB, Linger: 10ms | Efficient I/O packing |

---

## 4. Consumer Audit & Integrity Results

| Consumer Criterion | Verification Metric | Status |
| :--- | :---: | :---: |
| **Total Consumed Messages** | **5,004** | PASS |
| **Unique Event IDs** | **5,004** | PASS (Zero collision) |
| **Duplicate Messages** | **0** | PASS |
| **Malformed / Invalid Messages** | **0** | PASS (All mandatory fields valid) |
| **Payload Schema Conformance** | 100% | PASS (`event_id`, `source_node`, `target_node`, `event_time`, `governance_tag`) |
| **Consumer Elapsed Time** | **6.838 seconds** | PASS |

---

## 5. Artifact & Verification Checklist

- [x] Topic creation script: Provisioned `crisisguard-propagation-events`
- [x] Kafka producer: `scripts/phase8/kafka/produce_propagation_events.py`
- [x] Producer statistics: `docs/phase8/kafka_producer_stats.json`
- [x] Consumer validation tooling: `scripts/phase8/kafka/consume_and_validate.py`
- [x] Stream audit summary: `docs/phase8/kafka_validation_summary.json`
- [x] Broker verification: Verified live partition offsets on `localhost:9092`.

**Kafka Status: PASS — READY FOR SPARK STRUCTURED STREAMING**
