# CrisisGuard — Cross-Phase Numerical Consistency Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Audit Scope:** Phases 4 through 9 Numerical Alignment  
**Audit Date:** September 2026  

---

## 1. Executive Summary

This report establishes the single source of empirical truth across the entire CrisisGuard project by systematically cross-checking documented numerical values against the underlying Parquet, CSV, TSV, and JSON artifacts.

Every key numerical metric across datasets, models, graphs, streams, warehouses, and decision ledgers has been extracted directly from disk and compared with documented figures.

---

## 2. Master Numerical Comparison Matrix

| Metric Description | Documented Value | Physical Artifact Value | Match Status | Source Artifact Path | Notes / Audit Observation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CIFAKE Evaluated Test Images** | 72 | 72 | **MATCH** | `data/processed/cifake/cifake_records.parquet` | 36 real photos, 36 diffusion generated |
| **DFD Evaluated Videos** | 5 | 5 | **MATCH** | `data/processed/deepfake_dfd/media_records.parquet` | Google DFD controlled dev subset |
| **DFD Extracted Facial Frames** | 1,714 | 1,714 | **MATCH** | `data/processed/deepfake_dfd/frame_samples.parquet` | Facial bounding-box frame extracts |
| **HumAID Test Partition Records** | 15,160 | 15,160 | **MATCH** | `data/processed/humaid/humaid_records.parquet` | Humanitarian crisis task benchmark |
| **CrisisMMD Total Preprocessed** | 8,079 | 8,079 | **MATCH** | `data/processed/crisismmd/crisismmd_records.parquet` | 6,126 train + 998 dev + 955 test |
| **CrisisMMD Evaluated Test Set** | 955 | 955 | **MATCH** | `data/features/crisis_information/crisismmd_predictions.parquet` | Test split evaluated by NLP models |
| **CrisisLex Ingested Records** | 88,015 | 88,015 | **MATCH** | `data/processed/crisislex/crisislex_records.parquet` | T6 (60,000) + T26 (28,015) |
| **OSM Road Intersections (Nodes)** | 63,660 | 63,660 | **MATCH** | `data/processed/osm/road_nodes.parquet` | Physical spatial routing graph nodes |
| **OSM Road Segments (Edges)** | 146,156 | 146,156 | **MATCH** | `data/processed/osm/road_edges.parquet` | Physical spatial routing graph edges |
| **Phase 6 Unified Media Risk Rows** | 77 | 77 | **MATCH** | `data/features/synthetic_media/unified_media_risk.parquet` | 75 images (72 eval + 3 test) + 2 videos |
| **Phase 6 Image Predictions** | 75 | 75 | **MATCH** | `data/features/synthetic_media/image_predictions.parquet` | Spatial ResNet-18 outputs |
| **Phase 6 Video Predictions** | 2 | 2 | **MATCH** | `data/features/synthetic_media/video_predictions.parquet` | Temporal ResNet-18 outputs |
| **Phase 7 Unified Crisis Rows** | 104,130 | 104,130 | **MATCH** | `data/features/crisis_information/unified_crisis_intelligence.parquet` | 88,015 + 15,160 + 955 |
| **CrisisMMD Baseline Accuracy** | 0.7445 | 0.7445 | **MATCH** | `docs/crisis_information/baseline_audit_data.json` | TF-IDF + Logistic Regression |
| **CrisisMMD Baseline Macro F1** | 0.6171 | 0.6171 | **MATCH** | `docs/crisis_information/baseline_audit_data.json` | Multiclass humanitarian tasks ($N=955$) |
| **CrisisMMD Informativeness Acc.** | 0.8052 | 0.8052 | **MATCH** | `docs/crisis_information/baseline_audit_data.json` | Binary informativeness classification |
| **CrisisMMD Informativeness F1** | 0.8051 | 0.8051 | **MATCH** | `docs/crisis_information/baseline_audit_data.json` | Binary informativeness classification |
| **Phase 8 Propagation Events** | 5,004 | 5,004 | **MATCH** | `data/processed/propagation/propagation_events.parquet` | Semi-synthetic cascade event logs |
| **Phase 8 Propagation Edges** | 4,999 | 4,999 | **MATCH** | `data/processed/propagation/propagation_edges.parquet` | Directed cascade forwarding links |
| **Phase 8 Root Broadcast Events** | 5 | 5 | **MATCH** | `data/processed/propagation/propagation_events.parquet` | Events with `target_node = NULL` |
| **Phase 8 Unique Source Nodes** | 4,986 | 4,986 | **MATCH** | `data/processed/propagation/propagation_events.parquet` | Distinct transmitting accounts |
| **Phase 8 Unique Non-Null Targets**| 2,508 | 2,508 | **MATCH** | `data/processed/propagation/propagation_edges.parquet` | Distinct receiving accounts |
| **Phase 8 Union Graph Vertices** | 7,494 | 7,494 | **MATCH** | `data/features/phase8/graph/graphx_vertex_metrics.csv` | Reconciled non-null union graph nodes |
| **Phase 8 GraphX Output Vertices** | 7,494 | 7,494 | **MATCH** | `data/features/phase8/graph/graphx_vertex_metrics.csv` | GraphX PageRank/Components output rows |
| **Phase 8 Connected Components** | 2,509 | 2,509 | **MATCH** | `docs/phase8/graphx_metrics_summary.json` | GraphX connected components |
| **Phase 8 Giant Component Size** | 4,986 | 4,986 | **MATCH** | `docs/phase8/graphx_metrics_summary.json` | 66.53% of all graph vertices |
| **Phase 8 Streaming Tumbling Windows**| 32 | 32 | **MATCH** | `data/features/phase8/streaming/propagation_stream_metrics.parquet` | 1-minute watermarked aggregations |
| **Phase 8 Hive `propagation_events`**| 5,004 | 5,004 | **MATCH** | Hive metastore external table | Synced with HDFS processed parquet |
| **Phase 8 Hive `graphx_vertex_metrics`**| 7,494 | 7,494 | **MATCH** | Hive metastore external table | Synced with GraphX CSV metrics |
| **Phase 8 Hive `propagation_stream_metrics`**| 32 | 32 | **MATCH** | Hive metastore external table | Synced with streaming parquet |
| **Phase 9 Stream A (Media)** | 77 | 77 | **MATCH** | `data/features/phase9/phase9_media_intelligence.parquet` | Matches Phase 6 unified risk records |
| **Phase 9 Stream B (Crisis)** | 104,130 | 104,130 | **MATCH** | `data/features/phase9/phase9_crisis_intelligence.parquet` | Matches Phase 7 unified crisis records |
| **Phase 9 Stream C (Propagation)**| 7,494 | 7,494 | **MATCH** | `data/features/phase9/phase9_propagation_intelligence.parquet` | Matches Phase 8 GraphX vertex count |
| **Phase 9 Stream D (Spatial)** | 63,660 | 63,660 | **MATCH** | `data/features/phase9/phase9_spatial_intelligence.parquet` | Matches Phase 4 OSM road nodes |
| **Phase 9 Multi-Stream Ledger Total**| **175,361** | **175,361** | **MATCH** | `data/features/phase9/phase9_multi_stream_intelligence.parquet` | Exact additive sum of Streams A, B, C, D |

---

## 3. Contradictions & Legacy Numbers Analysis

### 3.1 The 7,495 vs 7,494 Graph Vertex Discrepancy
- **Audit Finding:** In early Phase 8 batch preprocessing (`spark_prepare_propagation.py`), unioning source and target nodes without filtering `NULL` generated 7,495 entries ($7,494 \text{ user IDs} + 1 \text{ NULL entity}$), where `NULL` was assigned `vertex_id = 1` (`1,` in CSV). GraphX dropped this empty record, constructing a graph of exactly **7,494** vertices.
- **Remediation Status:** Explicit `isNotNull()` filtering was applied, unifying the count at **7,494**.
- **Documentation Anomaly:** Several Phase 8 reports (`PHASE8_SPARK_REPORT.md`, `PHASE8_STREAMING_REPORT.md`, `PHASE8_ARCHITECTURE.md`, `PHASE8_REPRODUCIBILITY.md`) still mention the historical `7,495` count. These are flagged in `STALE_ARTIFACT_AUDIT.md` for cleanup.

### 3.2 HumAID Global ID Uniqueness vs Cross-Corpus Duplication
- **Audit Finding:** HumAID contains 5 tweet IDs cross-posted across 2 disaster sub-corpora (10 rows sharing 5 IDs).
- **Remediation Status:** Phase 9 correctly assigned synthetic primary record keys (`record_id = "crisis_" + index`) to ensure 100% uniqueness (0 duplicates) across the 175,361-row multi-stream ledger.

---

*Numerical consistency conclusion: 100% of physical data artifacts match their documented mathematical targets.*
