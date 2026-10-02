# CrisisGuard: Feature Contracts Specification (Phase 4 Freeze)

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Document Standard:** Interface & Schema Contract for Downstream Distributed Processing  
**Status:** Pre-Modeling Contract (No Fabricated Predictions / No Arbitrary Weights)  

---

## 1. Context & Operational Governance

Phase 4 strictly prepares data structures and defines feature contracts.
* **No Fabricated Model Predictions:** Machine learning models are **not** trained during Phase 4. 
* **No Arbitrary Heuristic Weights:** The Emergency Dispatch Priority Index (EDPI) weights and functional forms will be determined through empirical methodology design and evaluation in Phase 6 (Spark MLlib).

---

## 2. Media Risk Feature Contract (Step 20)

Downstream distributed streaming (Kafka, Spark Structured Streaming) and machine learning (Spark MLlib) consume canonical media inference outputs conforming to this contract:

### 2.1 Schema Definition

| Field Name | Data Type | Nullable | Range / Format | Description |
| :--- | :--- | :---: | :--- | :--- |
| `content_id` | `STRING` | No | Alphanumeric unique ID | Globally unique media identifier (e.g. `cifake_syn_0010`, `dfd_video_sample_01`) |
| `media_type` | `STRING` | No | MIME type string | Asset modality (`video/mp4`, `video/gif`, `image/jpeg`, `image/png`) |
| `synthetic_media_probability` | `DOUBLE` | No | $[0.0, 1.0]$ | Classifier confidence score indicating synthetic manipulation |
| `synthetic_media_risk` | `DOUBLE` | No | $[0.0, 1.0]$ | Calibrated risk score reflecting potential emergency disinformation impact |
| `model_version` | `STRING` | No | Semantic version | Model identifier and checkpoint name |
| `prediction_timestamp` | `TIMESTAMP`| No | ISO 8601 UTC | Exact time of inference generation |

### 2.2 Operational Contract Rules
1. Both the **Video Forensics Branch** and **Image Forensics Branch** output identical record structures.
2. `synthetic_media_risk` serves strictly as a **predictive feature**, never as an autonomous binary filter.

---

## 3. Crisis Priority Feature Contract (Step 21)

The composite Emergency Dispatch Priority Index (EDPI) evaluated in Phase 6 consumes an assembled 8-dimensional feature vector combining cross-modal signals:

### 3.1 Schema Definition

| Feature Identifier | Data Type | Source Component | Operational Range | Role in Emergency Dispatch Prioritization |
| :--- | :--- | :--- | :---: | :--- |
| **`crisis_severity`** | `DOUBLE` | CrisisMMD Multimodal | $[0.0, 1.0]$ | Normalized physical infrastructure damage rating |
| **`urgency`** | `DOUBLE` | HumAID Text Urgency | $[0.0, 1.0]$ | Life-safety humanitarian urgency rating |
| **`propagation_velocity`** | `DOUBLE` | Spark Streaming Windows | $[0.0, \infty)$ | Retweet/repost rate per 10-minute sliding window |
| **`propagation_volume`** | `BIGINT` | Spark Streaming Windows | $[0, \infty)$ | Cumulative cascade event volume |
| **`graph_influence`** | `DOUBLE` | Spark GraphX PageRank | $[0.0, 1.0]$ | Viral amplifier centrality score in propagation network |
| **`synthetic_media_risk`** | `DOUBLE` | Unified Media Contract | $[0.0, 1.0]$ | Probability of fabricated/manipulated media weaponization |
| **`road_accessibility`** | `DOUBLE` | GraphX Shortest Path | $[0.0, 1.0]$ | Topological road network reachability to incident node |
| **`resource_distance`** | `DOUBLE` | OpenStreetMap Network | $[0.0, \infty)$ | Geodesic network distance in meters to nearest depot |

### 3.2 Formal Constraint
* **No Heuristic Weight Assignment in Phase 4:** The exact mathematical formulation and weights:
  $$\text{EDPI} = f(\mathbf{x}, \mathbf{w})$$
  will be trained and evaluated using Spark MLlib classifiers and ranking evaluators in Phase 6. No arbitrary constant weights are assigned in Phase 4.
