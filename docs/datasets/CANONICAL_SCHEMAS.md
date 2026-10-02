# CrisisGuard: Canonical Data Schemas Specification

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Standard:** Heterogeneous Normalized Schemas for Distributed Streaming, GraphX, MLlib, and Hive  

---

## 1. Overview of Canonical Schemas

To ensure genuine data flow and avoid artificial schema merging, CrisisGuard enforces 10 normalized canonical schemas across the pipeline stages:

```
[Media Sources: Google DFD / NIST OpenMFC] ───> 1. media_record ──┐
                                                                  ├──> 3. crisis_media ──> 9. model_prediction ──┐
[Crisis Sources: HumAID / CrisisMMD / Lex] ────> 2. crisis_event ──┘                                               │
                                                                                                                   ├──> 10. emergency_priority (HIVE)
[Semi-Synthetic Cascades Engine] ───────────────> 4. propagation_event & 5. propagation_edge (KAFKA / GRAPHX) ────┤
                                                                                                                   │
[OpenStreetMap Infrastructure] ────────────────> 6. road_node & 7. road_edge & 8. resource_location (GRAPHX) ─────┘
```

---

## 2. Schema Specifications

### 2.1 Schema: `media_record`
* **Role:** Normalized metadata and baseline forensic authenticity signals for incoming video/image media.
* **Primary Producers:** Video Preprocessing / Feature Extractors (Google DFD, NIST MediScore/OpenMFC).

| Field | Data Type | Description | Source Dataset | Required/Optional | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `media_id` | `STRING` | Unique cryptographic hash (SHA256) of media asset | Google DFD / NIST OpenMFC | Required | `"dfd_video_sample_01"` |
| `source_dataset` | `STRING` | Provenance identifier of the source benchmark | Pipeline Metadata | Required | `"Google_DFD"` / `"NIST_OpenMFC"` |
| `media_type` | `STRING` | MIME category of the content (`video/mp4`, `image/jpeg`, `image/gif`) | Source Metadata | Required | `"video/mp4"` |
| `duration_sec` | `DOUBLE` | Video duration in seconds (0.0 for static images) | Video Header | Required | `3.5` |
| `resolution` | `STRING` | Spatial frame dimensions ($W \times H$) | Video Header | Required | `"1920x1080"` |
| `fps` | `DOUBLE` | Frame rate of the video sequence | Video Header | Optional | `29.97` |
| `authenticity_score` | `DOUBLE` | Extracted baseline authenticity probability ($[0.0, 1.0]$, 1.0 = pristine) | Facial Feature Extractor | Required | `0.142` |
| `manipulation_type` | `STRING` | Specific manipulation method if synthetic | Benchmark Ground Truth | Optional | `"deepfake_face_swap"` / `"splicing"` / `"none"` |
| `ground_truth_label` | `INT` | Supervised binary label (0 = pristine/real, 1 = manipulated/fake) | Benchmark Ground Truth | Required | `1` |
| `ingest_timestamp` | `TIMESTAMP` | System ingestion epoch | Pipeline Runtime | Required | `"2026-09-27T00:15:00Z"` |
| `governance_type` | `STRING` | Governance category (`REAL`, `DERIVED`, `SEMI_SYNTHETIC`) | Pipeline Governance | Required | `"REAL"` |


---

### 2.2 Schema: `crisis_event`
* **Role:** Crisis textual and contextual incident reports extracted from humanitarian social streams.
* **Primary Producers:** Crisis Text Ingestors (HumAID, CrisisLex).

| Field | Data Type | Description | Source Dataset | Required/Optional | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | `STRING` | Unique event tweet/message identifier | HumAID / CrisisLex | Required | `"humaid_11749283749284"` |
| `crisis_name` | `STRING` | Named disaster instance | HumAID Metadata | Required | `"Hurricane_Irma_2017"` |
| `disaster_type` | `STRING` | Natural or human-induced category | HumAID / CrisisLex | Required | `"hurricane"` / `"flood"` / `"earthquake"` |
| `text_content` | `STRING` | Raw textual message / tweet content | HumAID / CrisisLex | Required | `"Bridge on Hwy 10 collapsed, families stranded!"` |
| `humanitarian_category` | `STRING` | QCRI gold-standard task category | HumAID Ground Truth | Required | `"infrastructure_and_utility_damage"` |
| `urgency_weight` | `DOUBLE` | Normalized domain urgency factor ($[0.0, 1.0]$) | HumAID Category Mapping | Required | `0.85` |
| `latitude` | `DOUBLE` | Extracted or geocoded latitude coordinate | CrisisLex / Geocoding | Optional | `25.7617` |
| `longitude` | `DOUBLE` | Extracted or geocoded longitude coordinate | CrisisLex / Geocoding | Optional | `-80.1918` |
| `created_at` | `TIMESTAMP` | Original social publication timestamp | Tweet Metadata | Required | `"2017-09-10T14:32:00Z"` |

---

### 2.3 Schema: `crisis_media`
* **Role:** Association linking multimodal crisis tweets with media assets and damage assessments.
* **Primary Producers:** CrisisMMD Multimodal Pipeline.

| Field | Data Type | Description | Source Dataset | Required/Optional | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `crisis_media_id` | `STRING` | Composite key linking event and media asset | CrisisMMD | Required | `"cmmd_918237491_img01"` |
| `event_id` | `STRING` | Foreign key referencing `crisis_event.event_id` | CrisisMMD | Required | `"cmmd_918237491"` |
| `media_id` | `STRING` | Foreign key referencing `media_record.media_id` | CrisisMMD | Required | `"a4f9b8c2e1d04429"` |
| `damage_severity` | `STRING` | Visual physical damage classification | CrisisMMD Annotations | Required | `"severe_damage"` / `"mild_damage"` |
| `cross_modal_consistent` | `BOOLEAN` | Whether text semantics match visual evidence | Derived Analysis | Required | `false` |
| `provenance_mode` | `STRING` | Governance classification | Pipeline Governance | Required | `"REAL"` |

---

### 2.4 Schema: `propagation_event`
* **Role:** Granular social stream message published to Kafka topic `crisisguard.stream.raw-events`.
* **Primary Producers:** Semi-Synthetic Propagation Engine.

| Field | Data Type | Description | Source Dataset | Required/Optional | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | `STRING` | Unique message diffusion event ID | Propagation Generator | Required | `"prop_evt_00094821"` |
| `content_id` | `STRING` | Identifier binding to real crisis/media item | HumAID / DFDC Key | Required | `"humaid_11749283749284"` |
| `author_id` | `STRING` | Anonymized network user node ID | Simulated Graph Node | Required | `"usr_node_84920"` |
| `parent_event_id` | `STRING` | ID of prior event in the cascade (NULL if seed) | Cascade Tree | Optional | `"prop_evt_00094800"` |
| `timestamp` | `TIMESTAMP` | Logical event time with simulated drift | Cascade Dynamics | Required | `"2026-09-27T00:15:32Z"` |
| `propagation_type` | `STRING` | Diffusion mechanism | Generator Strategy | Required | `"ORGANIC"` / `"BOT_AMPLIFIED"` |
| `synthetic_media_risk` | `DOUBLE` | Inherited or scored synthetic media probability | Derived from `media_record` | Required | `0.858` |
| `crisis_priority` | `DOUBLE` | Initial urgency heuristic | Derived from `crisis_event` | Required | `0.720` |
| `scenario_id` | `STRING` | Controlled simulation test suite tag | Generator Scenario | Required | `"SCENARIO_COORDINATED_BURST"` |
| `governance_tag` | `STRING` | Mandatory compliance tag | Data Policy | Required | `"SEMI_SYNTHETIC"` |

---

### 2.5 Schema: `propagation_edge`
* **Role:** Directed edge stream published to Kafka topic `crisisguard.stream.propagation-edges` for GraphX.
* **Primary Producers:** Semi-Synthetic Propagation Engine.

| Field | Data Type | Description | Source Dataset | Required/Optional | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `edge_id` | `STRING` | Unique identifier for the amplification link | Propagation Engine | Required | `"edge_49201_84920"` |
| `source_node` | `LONG` | 64-bit integer Vertex ID for sender/retweeter | GraphX Vertex ID | Required | `49201L` |
| `target_node` | `LONG` | 64-bit integer Vertex ID for original poster/parent | GraphX Vertex ID | Required | `84920L` |
| `content_id` | `STRING` | Shared media/crisis reference ID | HumAID / DFDC Key | Required | `"humaid_11749283749284"` |
| `timestamp` | `TIMESTAMP` | Timestamp when amplification occurred | Cascade Clock | Required | `"2026-09-27T00:16:01Z"` |
| `edge_weight` | `DOUBLE` | Influence weight / amplification multiplier | Network Generator | Required | `1.0` |
| `governance_tag` | `STRING` | Mandatory compliance label | Data Policy | Required | `"SEMI_SYNTHETIC"` |

---

### 2.6 Schema: `road_node`
* **Role:** Physical road intersection or milestone vertex for GraphX routing.
* **Primary Producers:** OpenStreetMap PBF Ingestor.

| Field | Data Type | Description | Source Dataset | Required/Optional | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `node_id` | `LONG` | Unique 64-bit OpenStreetMap Node Identifier | OpenStreetMap | Required | `249581029L` |
| `latitude` | `DOUBLE` | WGS84 geographic latitude | OpenStreetMap | Required | `12.9716` |
| `longitude` | `DOUBLE` | WGS84 geographic longitude | OpenStreetMap | Required | `77.5946` |
| `elevation_m` | `DOUBLE` | Terrain elevation above sea level in meters | OSM / DEM Model | Optional | `920.0` |
| `is_intersection` | `BOOLEAN` | Flag indicating vertex degree $\ge 3$ | Graph Topologist | Required | `true` |

---

### 2.7 Schema: `road_edge`
* **Role:** Navigable road segment connecting two OSM road nodes.
* **Primary Producers:** OpenStreetMap PBF Ingestor.

| Field | Data Type | Description | Source Dataset | Required/Optional | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `edge_id` | `STRING` | Composite key of connected road nodes | OpenStreetMap | Required | `"osm_way_8492019_1"` |
| `src_node` | `LONG` | Start vertex node ID | OpenStreetMap | Required | `249581029L` |
| `dst_node` | `LONG` | End vertex node ID | OpenStreetMap | Required | `249581035L` |
| `length_km` | `DOUBLE` | Haversine or projected road distance | Derived from coordinates | Required | `0.452` |
| `road_type` | `STRING` | Highway classification tag | OpenStreetMap | Required | `"primary"` / `"secondary"` / `"trunk"` |
| `max_speed_kph` | `INT` | Posted speed limit in km/h | OpenStreetMap | Optional | `60` |
| `is_passable` | `BOOLEAN` | Dynamic passability flag (simulated flood cuts) | Dynamic Status | Required | `true` |

---

### 2.8 Schema: `resource_location`
* **Role:** Physical coordinates and capacity of emergency response centers, fire stations, and depots.
* **Primary Producers:** OSM Emergency POIs / Municipal GIS.

| Field | Data Type | Description | Source Dataset | Required/Optional | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `resource_id` | `STRING` | Unique emergency depot / hospital identifier | OSM / Municipal Open Data | Required | `"depot_blr_central_01"` |
| `resource_name` | `STRING` | Name of the facility | OSM Name Tag | Required | `"District Emergency Operations Center"` |
| `resource_type` | `STRING` | Operational service type | OSM Amenity Tag | Required | `"hospital"` / `"fire_station"` / `"rescue_hub"` |
| `nearest_road_node` | `LONG` | Nearest routable vertex on the road graph | Spatial Nearest-Neighbor | Required | `249581029L` |
| `available_teams` | `INT` | Number of active dispatch units available | Operational State | Required | `8` |

---

### 2.9 Schema: `model_prediction`
* **Role:** Machine learning classification and anomaly outputs computed across feature vectors.
* **Primary Producers:** Spark MLlib GBTClassifier / RandomForest.

| Field | Data Type | Description | Source Dataset | Required/Optional | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `prediction_id` | `STRING` | Unique inference execution key | Spark MLlib | Required | `"pred_20260927_00192"` |
| `content_id` | `STRING` | Foreign key referencing crisis/media record | Real Content ID | Required | `"humaid_11749283749284"` |
| `predicted_class` | `INT` | 0 = Genuine Urgent Crisis, 1 = Coordinated Synthetic Disinformation | MLlib Model Output | Required | `1` |
| `disinfo_probability` | `DOUBLE` | Softmax confidence score ($[0.0, 1.0]$) | MLlib GBT Probability | Required | `0.912` |
| `model_version` | `STRING` | Serialized model checkpoint tag | Model Metadata | Required | `"mllib_gbt_v1.0"` |
| `inference_time_ms` | `DOUBLE` | Spark inference latency per record | Pipeline Monitor | Required | `4.2` |

---

### 2.10 Schema: `emergency_priority`
* **Role:** Consolidated warehouse table in Apache Hive providing the actionable **Emergency Dispatch Priority Index (EDPI)** for incident commanders.
* **Primary Producers:** Spark MLlib + GraphX joined sink into Hive.

| Field | Data Type | Description | Source Dataset | Required/Optional | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `incident_id` | `STRING` | Canonical incident tracking key | Consolidated Key | Required | `"inc_20260927_0001"` |
| `content_id` | `STRING` | Originating message/content reference | HumAID / DFDC | Required | `"humaid_11749283749284"` |
| `disaster_type` | `STRING` | Hazard category | `crisis_event` | Required | `"hurricane"` |
| `authenticity_score` | `DOUBLE` | Visual media verification score ($0.0 = \text{fake}$) | `media_record` | Required | `0.142` |
| `urgency_weight` | `DOUBLE` | Linguistic urgency factor ($1.0 = \text{critical}$) | `crisis_event` | Required | `0.850` |
| `max_pagerank` | `DOUBLE` | GraphX super-spreader amplifier centrality | GraphX Cascade Graph | Required | `0.0482` |
| `share_velocity` | `DOUBLE` | Spark Streaming 10-minute windowed burst velocity | Spark Streaming | Required | `142.5` |
| `shortest_distance_km` | `DOUBLE` | GraphX shortest route to nearest dispatch depot | GraphX Road Graph | Required | `3.82` |
| `edpi_score` | `DOUBLE` | **Emergency Dispatch Priority Index** ($[0.0, 100.0]$) | Spark MLlib / Logic | Required | `87.4` |
| `dispatch_action` | `STRING` | Recommended decision | Decision Logic | Required | `"DISPATCH_HIGH_PRIORITY"` / `"HOLD_VERIFICATION_REQUIRED"` |
| `record_date` | `STRING` | Hive partition key (`YYYY-MM-DD`) | Hive Partitioner | Required | `"2026-09-27"` |
