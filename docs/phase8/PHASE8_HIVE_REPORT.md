# CrisisGuard — Phase 8: Hive Big Data Warehouse & Analytical Queries Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **PASS — HIVE WAREHOUSE & ANALYTICAL SQL VERIFIED**

---

## 1. Executive Summary

Phase 8.7 deployed the enterprise data warehouse layer utilizing Apache Hive Metastore / Spark SQL over Apache Hadoop HDFS (`hdfs://localhost:9000/crisisguard/phase8/hive/`). Four external tables were provisioned mapping directly to the underlying HDFS Parquet stores generated across Phase 6, Phase 7, and Phase 8.

Six analytical SQL queries were formulated and executed against the warehouse via `scripts/phase8/hive/run_hive_pipeline.py`. The queries demonstrated cross-stage data synthesis across GraphX graph centrality, Structured Streaming windowed metrics, synthetic media authenticity risk, and humanitarian crisis taxonomies.

---

## 2. Hive External Tables Provisioning

| Hive Table Name | Underlying HDFS Location | Source Stage | Schema Overview |
| :--- | :--- | :--- | :--- |
| `propagation_graph_metrics` | `/crisisguard/phase8/graph/metrics_parquet/` | Phase 8.4 (GraphX) | `vertex_id`, `node_name`, `pagerank`, `component_id`, `in_degree`, `out_degree` |
| `propagation_stream_metrics` | `/crisisguard/phase8/streaming/windowed_metrics/` | Phase 8.6 (Streaming) | `scenario_id`, `window_event_count`, `unique_sources`, `unique_targets`, `mean_risk`, `window_start`, `window_end`, `rate_per_min` |
| `media_risk_features` | `/crisisguard/phase8/media_risk/` | Phase 6 (Media Risk) | `content_id`, `media_type`, `model_branch`, `model_score`, `synthetic_probability`, `synthetic_risk`, `calibration_status` |
| `crisis_intelligence_features` | `/crisisguard/phase8/crisis_intelligence/` | Phase 7 (Crisis Intel) | `content_id`, `source_dataset`, `source_record_id`, `crisis_category`, `task_name`, `confidence`, `quality_status`, `calibration_status` |

---

## 3. Analytical Query Results & Evidence

### 3.1 Query 1: Top Structurally Central Vertices from PageRank
```sql
SELECT vertex_id, node_name, ROUND(pagerank, 4) AS pagerank_score, in_degree, out_degree, component_id
FROM crisisguard_phase8.propagation_graph_metrics
ORDER BY pagerank DESC LIMIT 5;
```
| Vertex ID | Node Name | PageRank Score | In-Degree | Out-Degree | Component ID |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `7450` | `9935` | **121.9683** | 4 | 0 | 2 |
| `418` | `1409` | **106.2639** | 7 | 0 | 2 |
| `5789` | `7912` | **105.2324** | 7 | 0 | 2 |
| `1996` | `3286` | **101.3225** | 6 | 0 | 2 |
| `3411` | `5012` | **99.8751** | 10 | 0 | 2 |

*Finding:* Top PageRank vertices represent structural sinks receiving multi-hop amplification flow within the primary giant connected component (Component ID 2).

### 3.2 Query 2: Degree Distribution Summary
- Maximum in-degree observed is 13 (PageRank 60.6963), held by high-authority hub node `6456` (`871722`).
- Strong power-law tendency: 333 nodes with in-degree 3, 74 nodes with in-degree 5, decreasing exponentially to single hub nodes at in-degree 11 and 13.

### 3.3 Query 3: Real-Time Stream Progression by Cascade Scenario
| Scenario ID | Active Windows | Total Events | Avg Rate (evt/min) | Peak Rate (evt/min) | Avg Synthetic Risk | Peak Synthetic Risk |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `ORGANIC_DIFFUSION` | 28 | **3,047** | 1.81 | 2.03 | 0.3839 | 1.0000 |
| `COORDINATED_BOT_BURST` | 1 | **1,002** | **16.70** | **16.70** | 0.1247 | 0.1500 |
| `HIGH_VELOCITY_VIRAL` | 3 | **955** | 5.30 | **7.73** | **0.9203** | **0.9699** |

*Finding:* The streaming metrics demonstrate distinct operational signatures:
- `COORDINATED_BOT_BURST` exhibits extreme instantaneous velocity (16.7 events/min) within a single 1-hour window.
- `HIGH_VELOCITY_VIRAL` combines elevated transmission speed (7.73 events/min peak) with catastrophic synthetic media risk ($\mu = 0.9203$, peak $0.9699$).
- `ORGANIC_DIFFUSION` persists over 28 continuous hours at a steady baseline rate (1.81 events/min).

### 3.4 Query 4: Synthetic Media Risk Analysis (Phase 6 Outputs)
- Image Modality: 38 items classified `LOW_RISK` ($\mu_{\text{prob}} = 0.0511$), 33 items `HIGH_RISK` ($\mu_{\text{prob}} = 0.9547$), 4 items `MEDIUM_RISK` ($\mu_{\text{prob}} = 0.5012$).
- Video Modality: 2 items classified `MEDIUM_RISK` ($\mu_{\text{prob}} = 0.4169$).

### 3.5 Query 5: Crisis Intelligence Category Distribution (Phase 7 Outputs)
- Demonstrates preservation of uncalibrated prediction flags (`calibration_status = "UNCALIBRATED"`) for HumAID test predictions and `"NOT_APPLICABLE"` for CrisisLex feature streams.

### 3.6 Query 6: Critical Cross-Stream Join Policy Verification
```sql
SELECT COUNT(g.vertex_id) AS overlapping_keys_count
FROM crisisguard_phase8.propagation_graph_metrics g
JOIN crisisguard_phase8.crisis_intelligence_features c
    ON g.node_name = c.source_record_id;
```
**Result:** Exactly **0** overlapping keys.
*Scientific Conclusion:* Validates the strict architectural rule forbidding synthetic cross-corpus joins. Social propagation cascades and Twitter humanitarian reports exist in disjoint key spaces; preserving separate analytical tables is the only methodologically honest approach.

---

## 4. Performance & Execution Summary

- Total Hive Pipeline Execution Time: **35.88 seconds**
- All 6 queries executed with zero errors.
- Query results saved in machine-readable JSON: `docs/phase8/hive_query_results.json`.

**Hive Status: PASS — COMPLETE PIPELINE END-TO-END VERIFIED**
