# CrisisGuard — Phase 9.1: Complete Input Artifact Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 9 — End-to-End Intelligence Integration, Analytical Validation & Final Decision-Support Layer  
**Date:** September 30, 2026  
**Status:** **PASS — ALL UPSTREAM FROZEN ARTIFACTS VERIFIED ON DISK**

---

## 1. Executive Summary

In accordance with Phase 9.1 control protocols, this document records an exhaustive, evidence-based audit of all frozen upstream input artifacts from Phase 4, Phase 6, Phase 7, and Phase 8. No file paths or column names have been assumed; every entry below was physically verified on the active filesystem.

---

## 2. Phase 6: Synthetic Media Intelligence Artifacts

| Attribute | Verified Value | Description / Evidence |
| :--- | :--- | :--- |
| **Artifact Path** | `data/features/synthetic_media/unified_media_risk.parquet` | Canonical feature store table |
| **Row Count** | **77** | Verified exact row count |
| **Columns ($D=12$)** | `content_id`, `media_type`, `model_branch`, `model_version`, `model_score`, `synthetic_probability`, `synthetic_risk`, `calibration_status`, `prediction_timestamp`, `source_dataset`, `quality_status`, `provenance` | Governed schema contract |
| **Primary Key** | `content_id` | Unique identifier (e.g., `cifake_real_0000_4`) |
| **Source Datasets** | `CIFAKE` (75 assets), `Google_DFD_Controlled_Sample` (2 assets) | Controlled multi-modal forensics |
| **Calibration Status** | `UNCALIBRATED` (**77** / 77 assets) | Strictly reported as uncalibrated raw scores |
| **Quality Status** | `VALID` (**77** / 77 assets) | All assets pass image/video ingestion integrity |
| **Model Registry** | `models/synthetic_media/model_registry.yaml` | ResNet-18 (image) & MesoNet-4 (video) |
| **Model Weights** | `image_model_best.pt`, `video_model_best.pt` | Trained and frozen model checkpoints |
| **Schema Contract** | `schemas/media_risk_schema.json` | JSON Schema draft 2020-12 |

---

## 3. Phase 7: Crisis Information Intelligence Artifacts

| Attribute | Verified Value | Description / Evidence |
| :--- | :--- | :--- |
| **Artifact Path** | `data/features/crisis_information/unified_crisis_intelligence.parquet` | Canonical feature store table |
| **Row Count** | **104,130** | Verified exact row count |
| **Columns ($D=18$)** | `content_id`, `source_dataset`, `source_record_id`, `event_id`, `text_available`, `image_available`, `crisis_category`, `task_name`, `model_score`, `confidence`, `quality_status`, `calibration_status`, `temporal_features`, `context_features`, `provenance`, `model_version`, `prediction_timestamp`, `governance_type` | Unified multi-source crisis schema |
| **Primary Key** | `content_id` | Prefixed unique identifier (e.g., `humaid_721630546711986178`) |
| **Source Datasets** | `crisislex_t6_and_t26` (88,015), `humaid_all_combined` (15,160), `crisismmd_multimodal` (955) | Multi-corpus disaster intelligence |
| **Calibration Status** | `NOT_APPLICABLE` (88,015: CrisisLex), `UNCALIBRATED` (16,115: HumAID + CrisisMMD) | Statistically sound calibration tracking |
| **Confidence Field** | `confidence` | Model confidence in $[0.0, 1.0]$ where available |
| **Text Availability** | Text available for CrisisLex and CrisisMMD; unhydrated for HumAID official test split | Handled transparently without fabrication |
| **Image Availability** | Text-only model for CrisisMMD (images not used in baseline model) | Strict text-only scientific boundary |
| **Model Registry** | `models/crisis_information/model_registry.yaml` | CrisisMMD Logistic, HumAID Stratified Baseline |
| **Schema Contract** | `schemas/crisis_intelligence_schema.json` | JSON Schema draft 2020-12 |

---

## 4. Phase 8: Propagation Graph & Streaming Intelligence Artifacts

| Attribute | Verified Value | Description / Evidence |
| :--- | :--- | :--- |
| **Events Parquet** | `data/processed/propagation/propagation_events.parquet` | **5,004** rows, 11 columns |
| **Edges Parquet** | `data/processed/propagation/propagation_edges.parquet` | **4,999** rows, 6 columns |
| **Vertex CSV** | `data/features/phase8/graph/vertices.csv` | **7,494** rows (clean Long IDs 1 to 7,494) |
| **Edge CSV** | `data/features/phase8/graph/edges.csv` | **4,999** rows |
| **GraphX Metrics CSV** | `data/features/phase8/graph/graphx_vertex_metrics.csv` | **7,494** rows (`vertex_id`, `node_name`, `pagerank`, `component_id`, `in_degree`, `out_degree`) |
| **Streaming Parquet** | `data/features/phase8/streaming/propagation_stream_metrics.parquet` | **32** 1-hour tumbling temporal windows |
| **Root Broadcast Events** | **5** events | Cascade seeds (`target_node = NULL`) |
| **Unique Source Nodes** | **4,986** | Verified non-null sources |
| **Unique Target Nodes** | **2,508** | Verified non-null targets |
| **GraphX Executable** | `target/phase8/crisisguard-graphx.jar` | Compiled Scala 2.12 JAR (13,092 bytes) |
| **Hive Warehouse** | `hdfs://localhost:9000/crisisguard/phase8/hive/` | 4 External tables, 6 analytical queries executed |

---

## 5. Phase 4: Spatial / Road Network Artifacts

| Attribute | Verified Value | Description / Evidence |
| :--- | :--- | :--- |
| **Road Nodes** | `data/processed/osm/road_nodes.parquet` | **63,660** rows (`node_id`, `latitude`, `longitude`, `source_dataset`, `governance_type`) |
| **Road Edges** | `data/processed/osm/road_edges.parquet` | **146,156** rows (`edge_id`, `way_id`, `source_node`, `target_node`, `road_type`, `length_m`, `oneway`, `speed_if_available`, `governance_type`) |
| **Geographic Scope** | Regional road network extracted from OpenStreetMap Geofabrik PBF | Real physical spatial infrastructure |

---

## 6. Audit Decision

- [x] All Phase 6 feature parquets, schemas, and model registries verified.
- [x] All Phase 7 feature parquets, schemas, and model registries verified.
- [x] All Phase 8 propagation datasets, GraphX tables, and streaming outputs verified.
- [x] All Phase 4 spatial tables verified.
- [x] Zero missing upstream dependencies detected.

**PHASE 9.1 DECISION: PASS — READY FOR JOIN FEASIBILITY AUDIT**
