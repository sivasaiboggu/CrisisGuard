# CrisisGuard — Phase 9: Unified Intelligence Feature Contract

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 9 — End-to-End Intelligence Integration, Analytical Validation & Final Decision-Support Layer  
**Date:** September 30, 2026  
**Status:** **PASS — FORMAL SCHEMA & FEATURE CONTRACT GOVERNED**

---

## 1. Feature Contract Specification

The Phase 9 Unified Intelligence contract governs the schema, semantic types, allowable ranges, null semantics, and epistemic boundaries of all analytical features in the multi-stream ledger (`schemas/phase9/crisisguard_intelligence_schema.json`).

| Field Name | Type | Range / Domain | Nullable? | Availability Flag | Epistemic Classification | Description |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `stream_id` | `STRING` | Enum (4 Streams) | No | N/A | **OBSERVED** | Originating stream (`STREAM_A` through `STREAM_D`) |
| `record_id` | `STRING` | Unique string | No | N/A | **OBSERVED** | Globally unique canonical identifier |
| `source_dataset` | `STRING` | Valid dataset name | No | N/A | **OBSERVED** | Original corpus (e.g. `CIFAKE`, `humaid_all_combined`) |
| `event_id` | `STRING` | Event tag / incident | Yes | N/A | **OBSERVED** | Disaster incident or cascade transmission tag |
| `node_id` | `INTEGER` | $\ge 1$ | Yes | N/A | **OBSERVED** | Network node ID (social user or OSM road vertex) |
| `timestamp` | `STRING` | ISO-8601 UTC | Yes | N/A | **OBSERVED** | Prediction, transmission, or capture timestamp |
| `media_risk` | `DOUBLE` | $[0.0, 1.0]$ | Yes | `media_risk_available` | **INFERRED** | Continuous bounded model-derived synthetic media risk |
| `media_risk_available` | `BOOLEAN` | `{True, False}` | No | Self | **OBSERVED** | Explicit flag: True if genuine media risk is present |
| `crisis_model_score` | `DOUBLE` | $[0.0, 1.0]$ | Yes | `crisis_intelligence_available` | **INFERRED** | Uncalibrated model confidence score for crisis category |
| `crisis_confidence` | `DOUBLE` | $[0.0, 1.0]$ | Yes | `crisis_intelligence_available` | **INFERRED** | Category probability/confidence metric |
| `crisis_prediction` | `STRING` | Valid category | Yes | `crisis_intelligence_available` | **INFERRED** | Predicted humanitarian category (e.g. `rescue_efforts`) |
| `crisis_intelligence_available` | `BOOLEAN` | `{True, False}` | No | Self | **OBSERVED** | Explicit flag: True if crisis features are present |
| `pagerank` | `DOUBLE` | $\ge 0.0$ | Yes | `propagation_intelligence_available` | **COMPUTED** | Stationary probability distribution under random walk |
| `degree` | `INTEGER` | $\ge 0$ | Yes | `propagation_intelligence_available` | **OBSERVED** | Total network degree ($k_{in} + k_{out}$) |
| `component_id` | `INTEGER` | $\ge 1$ | Yes | `propagation_intelligence_available` | **COMPUTED** | Weakly connected component identifier from GraphX |
| `propagation_activity` | `STRING` | Enum scenarios | Yes | `propagation_intelligence_available` | **INFERRED** | Dominant cascade diffusion regime |
| `propagation_intelligence_available`| `BOOLEAN` | `{True, False}` | No | Self | **OBSERVED** | Explicit flag: True if graph features are present |
| `spatial_intelligence_available` | `BOOLEAN` | `{True, False}` | No | Self | **OBSERVED** | Explicit flag: True if spatial road coordinates exist |
| `quality_status` | `STRING` | `VALID`, `DEGRADED` | No | N/A | **OBSERVED** | Input asset quality assessment |
| `calibration_status` | `STRING` | `CALIBRATED_EMPIRICAL`, `UNCALIBRATED`, `NOT_APPLICABLE` | No | N/A | **OBSERVED** | Statistical calibration validity of probabilities |
| `provenance` | `STRING` | Free-text lineage | No | N/A | **OBSERVED** | End-to-end data lineage tracing |
| `governance_type` | `STRING` | `REAL`, `SYNTHETIC`, `SEMI_SYNTHETIC` | No | N/A | **OBSERVED** | Data veracity classification |

---

## 2. Epistemic Classification Rules

To prevent cognitive overclaiming and scientific misinterpretation:
1. **OBSERVED:** Features that are directly recorded from the raw physical or social data stream without model transformations (e.g. `in_degree`, `timestamp`, `source_dataset`, `node_id`).
2. **COMPUTED:** Deterministic mathematical transformations of the graph topology via verified algorithms (e.g. GraphX `pagerank` computed via 20 power-iteration steps; `component_id` computed via label propagation).
3. **INFERRED:** Probabilistic or statistical model outputs that reflect model inductive bias and are subject to estimation error (e.g. `media_risk`, `crisis_prediction`, `crisis_confidence`, `dominant_scenario`).
4. **UNKNOWN:** Concepts that cannot be legitimately determined from available data (e.g., ground-truth malicious intent behind a deepfake; causal injection origin of an unobserved account).

---

## 3. Strict Null Handling & Availability Flags

- **Zero-Value Prohibition:** An unavailable metric MUST be populated as `NULL` (Python `None` / SQL `NULL`). It MUST NOT be replaced with `0.0`. In disaster management, a confidence of `0.0` denotes complete certainty of non-membership, whereas `NULL` denotes absence of measurement.
- **Dual Verification:** Downstream query engines MUST check the corresponding boolean availability flag (e.g. `WHERE media_risk_available = TRUE`) before accessing continuous risk features.
