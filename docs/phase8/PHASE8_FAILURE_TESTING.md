# CrisisGuard — Phase 8: Controlled Failure & Quality Resilience Testing Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **PASS — FAULT TOLERANCE & EDGE-CASE HANDLING VERIFIED**

---

## 1. Executive Summary

Phase 8.11 subjected the big data ingestion, streaming, and graph computation pipelines to controlled failure and quality stress tests (`scripts/phase8/test_failure_resilience.py`). In strict adherence to laboratory policy, zero upstream frozen datasets were modified; tests were conducted using temporary Kafka topics (`crisisguard-test-failure-events`) and isolated in-memory fixtures.

Five specific failure modes were simulated and validated:
1. Malformed JSON message payloads on Kafka streams.
2. Duplicate event transmissions.
3. Missing / null timestamps.
4. Dangling edges referencing unknown graph vertices.
5. Non-finite / negative edge weights.

---

## 2. Failure Testing Matrix & Observations

| Test ID | Failure Mode Simulated | Test Fixture | Expected Pipeline Behavior | Observed Behavior | Test Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TEST-01** | **Malformed JSON Payload** | Unparsable raw byte string `INVALID_RAW_JSON_{event_id...` | Intercept decode exception, quarantine message, keep consumer alive | Safely caught `JSONDecodeError`, zero consumer crashes | **PASS** |
| **TEST-02** | **Duplicate Event Replay** | Identical `event_id` transmitted twice in succession | Stream validator flags duplicate without double-counting | Duplicate detected, count incremented, unique ID set preserved | **PASS** |
| **TEST-03** | **Missing Event Timestamp** | Event payload with `event_time: null` | Flag invalid timestamp, prevent watermark corruption | Correctly flagged for fallback / quarantine | **PASS** |
| **TEST-04** | **Dangling Graph Edge** | Directed edge $(1, 9999)$ where vertex $9999$ is unknown | Assign GraphX `defaultUser` attribute (`UNKNOWN_NODE`) | Graph constructed without null pointer exceptions | **PASS** |
| **TEST-05** | **Invalid Edge Weight** | Weights $[-0.5, +\infty, \text{NaN}]$ | Sanitize / filter non-finite and negative weights | All 3 invalid weights caught and rejected | **PASS** |

---

## 3. Failure Policy & Recovery Procedures

1. **Stream Corruption Prevention:** The Spark Structured Streaming pipeline parses Kafka records with `.option("failOnDataLoss", "false")` and handles nulls using explicit type casting, ensuring malformed records cannot stall the distributed micro-batch cycle.
2. **Deduplication:** Event IDs are uniquely tracked across window partitions, preventing artificial inflation of cascade propagation velocity.
3. **Graph Integrity:** GraphX utilizes default vertex attributes to gracefully assimilate edges that reference newly appearing or unindexed nodes during dynamic streaming.

**Failure Testing Status: PASS — 5/5 RESILIENCE CRITERIA VERIFIED**
