# CrisisGuard: End-to-End Data Lineage & Provenance Flow

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Classification Standard:** Strict segregation of REAL DATA, DERIVED DATA, and SEMI-SYNTHETIC DATA.  
**Document Status:** Approved & Audited Baseline (Post-Audit Correction)  

---

## 1. End-to-End Visual Data Lineage

```
+-----------------------------------------------------------------------------------------------------------------------+
|                                                   REAL DATA                                                           |
|                                                                                                                       |
|  [Google DFD-derived Sample]     [CIFAKE Image Benchmark]       [HumAID / CrisisLex]     [CrisisMMD]  [OpenStreetMap] |
|   (Controlled Video Sample)       (Diffusion Synthetic Images)  (Human Crisis Tweets)    (Multimodal)  (Geofabrik PBF)|
+-----------------------------------------------------------------------------------------------------------------------+
             │                                 │                            │                   │              │
             │ [REAL SAMPLE]                   │ [REAL BENCHMARK]           │ [REAL]            │ [REAL]       │ [REAL]
             ▼                                 ▼                            ▼                   ▼              ▼
+-------------------------+       +--------------------------+  +------------------------+ +---------+  +-------------+
| Video Forensics Branch: |       | Image Forensics Branch:  |  | Tokenization, TF-IDF   | | Cross-  |  | OSM PBF     |
| Face Crop & Alignment   |       | Spatial/Frequency Tensors|  | & Urgency Indexing     | | Modal   |  | Node/Edge   |
+-------------------------+       +--------------------------+  +------------------------+ | Align   |  | Topology    |
             │                                 │                            │              +---------+  +-------------+
             │ [DERIVED]                       │ [DERIVED]                  │                   │              │
             ▼                                 ▼                            ▼                   ▼              ▼
+-------------------------+       +--------------------------+  +-------------------------------------+ +-------------+
| Video / Frame Model     |       | Image Model              |  |   Canonical Crisis Emergency Record | | Road Graph  |
| (DFD Deepfake Scoring)  |       | (CIFAKE Diffusion Detect)|  |   (Severity, Urgency, Hazard Tags)  | | (Dijkstra)  |
+-------------------------+       +--------------------------+  +-------------------------------------+ +-------------+
             │                                 │                                    │                          │
             └────────────────┬────────────────┘                                    │                          │
                              ▼                                                     │                          │
              +--------------------------------+                                    │                          │
              |      UNIFIED MEDIA RISK        |                                    │                          │
              | [content_id, media_type,       |                                    │                          │
              |  synthetic_probability,        |                                    │                          │
              |  synthetic_risk, model_ver]    |                                    │                          │
              +--------------------------------+                                    │                          │
                              │                                                     │                          │
                              │ [DERIVED MEDIA FEATURES]                            │ [DERIVED TEXT/DAMAGE]    │
                              └──────────────────────────┬──────────────────────────┘                          │
                                                         ▼                                                     │
                                         +--------------------------------+                                    │
                                         | Anchor Real Content IDs &      |                                    │
                                         | Initial Feature Tuples         |                                    │
                                         +--------------------------------+                                    │
                                                         │                                                     │
                                                         ▼                                                     │
                                         +--------------------------------+                                    │
                                         | Semi-Synthetic Cascade Engine  |                                    │
                                         | (Scale-Free Diffusion Sim)     |                                    │
                                         +--------------------------------+                                    │
                                                         │                                                     │
                                                         │ [SEMI-SYNTHETIC CASCADE]                            │
                                                         ▼                                                     │
                                         +--------------------------------+                                    │
                                         |     Apache Kafka Ingestion     |                                    │
                                         | (Events & Propagation Edges)   |                                    │
                                         +--------------------------------+                                    │
                                                         │                                                     │
                                                         │ [SEMI-SYNTHETIC STREAM]                             │
                                                         ▼                                                     │
                                         +--------------------------------+                                    │
                                         |   Spark Structured Streaming   |                                    │
                                         | (10m Window, Velocity, Bursts) |                                    │
                                         +--------------------------------+                                    │
                                                         │                                                     │
                                                         │ [DERIVED STREAM]                                    │
                          ┌──────────────────────────────┴──────────────────────────────┐                      │
                          ▼                                                             ▼                      │
+----------------------------------------------------+       +------------------------------------+            │
|                Spark GraphX Engine                 |       |            Spark MLlib             |            │
| Cascade Propagation Graph:                         |       | Feature Vector Assembler:          |            │
| - PageRank (Amplifier Spreaders)                   |       | - crisis_severity (CrisisMMD)      |            │
| - Connected Components (Bot Coordinated Rings)     |       | - text_urgency (HumAID)            |            │
+----------------------------------------------------+       | - burst_velocity (Streaming)       |            │
                          │                                  | - pagerank_score (GraphX)          |            │
                          │ [DERIVED GRAPH]                  | - synthetic_media_risk (Unified)   |            │
                          │                                  | - road_reachability (OSM)          |            │
                          │                                  | Classifiers: GBT / Random Forest   |            │
                          │                                  +------------------------------------+            │
                          │                                                             │                      │
                          │                                                             │ [DERIVED ML]         │
                          └──────────────────────────────┬──────────────────────────────┘                      │
                                                         ▼                                                     │
                                      +------------------------------------+                                   │
                                      | GraphX Spatial Routing Join        |<──────────────────────────────────┘
                                      | (Shortest Distance to Depot)       |  [DERIVED ROAD NETWORK]
                                      +------------------------------------+
                                                         │
                                                         │ [DERIVED COMPOSITE]
                                                         ▼
                                      +------------------------------------+
                                      | Emergency Dispatch Priority (EDPI) |
                                      | (Balanced Multi-Criteria Decision) |
                                      +------------------------------------+
                                                         │
                                                         ▼
                                      +------------------------------------+
                                      |      Apache Hive Warehouse         |
                                      | Partitioned SQL Tables (Parquet)   |
                                      +------------------------------------+
```

---

## 2. Provenance Classification Protocol

Every record flowing through the pipeline is explicitly tagged with its classification tier:

### 2.1 REAL DATA
* **Definition:** Data originating directly from external, verified research organizations without synthetic alteration.
* **Entities:**
  * **Google DFD-Derived Controlled Development Sample:** 9 authentic sequence files, frames, and TUM splits (`data/raw/deepfake_dfd/`).
  * **CIFAKE AI-Generated Image Benchmark:** 500 authentic photographic and Stable Diffusion test images (`data/raw/synthetic_media_eval/`).
  * **HumAID:** Disaster tweets and humanitarian consensus annotations (`data/raw/humaid/`).
  * **CrisisMMD:** Image-text pairs and physical damage ratings (`data/raw/crisismmd/`).
  * **CrisisLex:** Disaster tweet corpora and lexicons (`data/raw/crisislex/`).
  * **OpenStreetMap:** Raw regional road network PBF extract (`data/raw/osm/`).

### 2.2 DERIVED DATA
* **Definition:** Deterministic mathematical, statistical, or machine learning transformations computed from REAL DATA.
* **Entities:**
  * Video forensics facial landmark tensors and deepfake classification probabilities.
  * Image forensics frequency/spatial tensors and diffusion classification probabilities.
  * **Unified Media Schema:** Canonical records (`content_id`, `media_type`, `synthetic_probability`, `synthetic_risk`, `model_version`, `prediction_timestamp`).
  * TF-IDF word vectors and lexical crisis urgency scores.
  * Spark Streaming windowed event counters and burst velocities.
  * GraphX PageRank scores and connected component IDs.
  * Spark MLlib inference predictions and Emergency Dispatch Priority Index (EDPI) scores.

### 2.3 SEMI-SYNTHETIC DATA
* **Definition:** Artificially generated social repost/retweet cascades constructed by binding authentic content IDs with simulated graph diffusion dynamics.
* **Entities:**
  * `propagation_event` streams generated by `scripts/generation/generate_propagation_cascades.py`.
  * `propagation_edge` retweet/mention link streams.
* **Ethical Boundary:** **Under no circumstances is semi-synthetic cascade data claimed to represent authentic historical social media log histories.** Quarantined in `data/generated/propagation/` with `governance_tag: "SEMI_SYNTHETIC"`.

---

## 3. Operational Principle: Emergency Priority Separation

**Synthetic media risk is a FEATURE, not an arbiter of truth.**
* In the CrisisGuard architecture, `synthetic_media_risk` informs the system about the probability and severity of media tampering, but **does not directly decide whether a crisis event is genuine or fabricated**.
* Real-world emergencies often involve misattributed, recycled, or manipulated imagery alongside critical true needs.
* The Emergency Dispatch Priority Index (EDPI) balances:
  $$\text{EDPI} = f(\text{Severity}, \text{Urgency}, \text{Velocity}, \text{PageRank}, \text{SyntheticRisk}, \text{RoadAccessibility}, \text{Proximity})$$
  ensuring responders prioritize actionable, reach-accessible humanitarian emergencies while discounting coordinated synthetic disinformation.
