# CrisisGuard — Phase 9: End-to-End Intelligence Integration Architecture

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 9 — End-to-End Intelligence Integration, Analytical Validation & Final Decision-Support Layer  
**Date:** September 30, 2026  
**Status:** **PASS — MULTI-STREAM ARCHITECTURAL DESIGN VERIFIED**

---

## 1. Architectural Philosophy: Relational Honesty & Provenance Preservation

In real-world big data systems for disaster response and misinformation intelligence, heterogeneous data sources rarely share universal primary keys:
- **Synthetic Media Forensics (Phase 6):** Evaluates visual manipulation artifacts in controlled benchmark assets (CIFAKE, Google DFD).
- **Crisis Information Intelligence (Phase 7):** Classifies humanitarian requests, damage reports, and casualty reports from real disaster tweet streams (CrisisLex, HumAID, CrisisMMD).
- **Propagation Graph & Streaming (Phase 8):** Simulates cascade diffusion dynamics across a 7,494-node social interaction topology using HDFS, Spark, GraphX, Kafka, and Hive.
- **Spatial Road Infrastructure (Phase 4):** Represents physical geographic road connectivity from OpenStreetMap.

### The Anti-Fabrication Rule:
A common failure mode in academic projects is forcing arbitrary joins (e.g. joining tweet IDs with image IDs or assigning road coordinates to arbitrary social accounts) to manufacture a single wide table. **CrisisGuard strictly prohibits this practice.**

Instead, Phase 9 establishes a **Parallel Feature Stream Architecture**:
```
┌────────────────────────────────────────────────────────────────────────┐
│                   CRISISGUARD MULTI-STREAM ARCHITECTURE                │
└────────────────────────────────────────────────────────────────────────┘

  STREAM A (Synthetic Media)        STREAM B (Crisis Info)
  ┌─────────────────────────┐       ┌─────────────────────────┐
  │ 77 Forensics Assets     │       │ 104,130 Disaster Tweets │
  │ - Image Model (ResNet)  │       │ - CrisisLex (88,015)    │
  │ - Video Model (MesoNet) │       │ - HumAID (15,160)       │
  │ - Bounded Risk Score    │       │ - CrisisMMD (955, Text) │
  └────────────┬────────────┘       └────────────┬────────────┘
               │                                 │
               ▼                                 ▼
    phase9_media_intelligence       phase9_crisis_intelligence
               │                                 │
               └──────────────┬──────────────────┘
                              │
  STREAM C (Propagation Graph)│     STREAM D (Spatial Road Network)
  ┌─────────────────────────┐ │     ┌─────────────────────────┐
  │ 7,494 GraphX Vertices   │ │     │ 63,660 Road Nodes       │
  │ 4,999 Directed Edges    │ │     │ 146,156 Road Edges      │
  │ 32 Streaming Windows    │ │     │ Physical OSM Topologies │
  │ PageRank & Centrality   │ │     │ Lat / Long Coordinates  │
  └────────────┬────────────┘ │     └────────────┬────────────┘
               │              │                  │
               ▼              ▼                  ▼
    phase9_propagation_intelligence   phase9_spatial_intelligence
               │              │                  │
               └──────────────┴──────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │     phase9_multi_stream_intelligence         │
        │     (175,361 Unified Ledger Records)         │
        │     - Explicit Feature Availability Flags    │
        │     - Null-Preserving Representation         │
        │     - Full Provenance & Lineage Tracking     │
        └──────────────────────────────────────────────┘
```

---

## 2. Stream Ingestion & Representation

### Stream A: Synthetic Media Intelligence
- **Input:** `data/features/synthetic_media/unified_media_risk.parquet` ($N=77$)
- **Output:** `data/features/phase9/phase9_media_intelligence.parquet` ($N=77$)
- **Key Fields:** `record_id`, `media_type`, `model_score`, `synthetic_probability`, `synthetic_risk`, `calibration_status` (`UNCALIBRATED`).
- **Epistemic Classification:** Model-estimated synthetic risk feature for downstream prioritization; explicitly uncalibrated.

### Stream B: Crisis Information Intelligence
- **Input:** `data/features/crisis_information/unified_crisis_intelligence.parquet` ($N=104,130$)
- **Output:** `data/features/phase9/phase9_crisis_intelligence.parquet` ($N=104,130$)
- **Key Fields:** `record_id`, `source_dataset`, `crisis_category`, `confidence`, `task_name`, `calibration_status`.
- **Epistemic Classification:** Multiclass humanitarian needs category; CrisisMMD model is strictly unimodal text-based.

### Stream C: Propagation Graph & Streaming Intelligence
- **Input:** `data/features/phase8/graph/graphx_vertex_metrics.csv` ($N=7,494$), `data/processed/propagation/propagation_events.parquet` ($N=5,004$), `data/features/phase8/streaming/propagation_stream_metrics.parquet` ($N=32$)
- **Output:** `data/features/phase9/phase9_propagation_intelligence.parquet` ($N=7,494$)
- **Key Fields:** `record_id`, `vertex_id`, `node_name`, `pagerank`, `in_degree`, `out_degree`, `total_degree`, `component_id`, `total_outbound_events`, `dominant_scenario`.
- **Epistemic Classification:** Observed degree counts and computed random-walk centrality (PageRank); PageRank represents structural authority, not ground-truth causal source origin.

### Stream D: Spatial & Road Network Intelligence
- **Input:** `data/processed/osm/road_nodes.parquet` ($N=63,660$), `data/processed/osm/road_edges.parquet` ($N=146,156$)
- **Output:** `data/features/phase9/phase9_spatial_intelligence.parquet` ($N=63,660$)
- **Key Fields:** `record_id`, `node_id`, `latitude`, `longitude`, `source_dataset`.
- **Epistemic Classification:** Observed geographic coordinate infrastructure available for prospective location-aware dispatch.

---

## 3. Epistemic Integrity & Decision-Support Layer

Rather than compressing these heterogeneous signals into an arbitrary formula, the decision-support layer surfaces a transparent multi-dimensional feature vector:
$$\mathbf{x} = \langle \text{MediaRisk}, \text{CrisisConfidence}, \text{CrisisCategory}, \text{PageRank}, \text{InDegree}, \text{VelocityWindow} \rangle$$

Human incident commanders and automated priority filters evaluate these signals in context with full access to data lineage, calibration flags, and quality status.
