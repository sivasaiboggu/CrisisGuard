# CrisisGuard: Data Quality & Governance Rules

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Standard:** Rigorous Quality Validation, Invariant Checks, and Leakage Prevention  

---

## 1. Core Data Quality Invariants

Every dataset and interim feature pipeline must adhere to the following 10 invariant validation rules:

### 1. Missing Value Policies (`DQ-01`)
* **Identifiers & Foreign Keys:** `media_id`, `event_id`, `node_id`, `content_id` MUST NEVER be null, empty, or whitespace. Records violating this are quarantined immediately to `data/interim/quarantine/`.
* **Numerical Metrics:** `authenticity_score`, `urgency_weight`, `length_km` must not contain `NaN` or `Inf`. Missing numeric signals default to deterministic median values computed strictly over the training partition.
* **Text Content:** Blank or null text strings are rejected.

### 2. Duplicate Detection & Deduplication (`DQ-02`)
* Exact duplicate event IDs or content hashes are dropped at the ingestion boundary.
* Retweets or cascade events must have distinct `event_id` keys even when referencing the same `content_id`.

### 3. Timestamp Validity & Monotonicity (`DQ-03`)
* All timestamps must conform to ISO-8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`).
* Cascade timestamps must satisfy $T_{\text{child}} \ge T_{\text{parent}}$. Out-of-order events arriving beyond the Spark Structured Streaming watermark threshold (10 minutes) are handled via stateful late-arrival buffers or logged to drop tables.

### 4. Coordinate Validity (`DQ-04`)
* Geographic coordinates must satisfy WGS84 bounds:
  $$\text{Latitude} \in [-90.0, +90.0], \quad \text{Longitude} \in [-180.0, +180.0]$$
* Road graph nodes and crisis events outside the active regional bounding box are flagged as out-of-bounds.

### 5. Categorical & Label Invariants (`DQ-05`)
* Binary labels for synthetic media must strictly be $\in \{0, 1\}$.
* Humanitarian categories must conform to the closed QCRI HumAID taxonomy (`rescue_volunteering_effort`, `infrastructure_and_utility_damage`, `caution_and_advice`, etc.).
* Unrecognized labels are mapped to `other_relevant_information`.

### 6. Media Integrity & Header Validation (`DQ-06`)
* Media assets must have valid headers verifiable by standard decoders (e.g., `ffprobe` / `cv2` for video, `Pillow` for imagery).
* Video resolution must satisfy $W \ge 320, H \ge 240$.
* Videos with 0 bytes or unreadable frames are quarantined.

### 7. ID Consistency & Referential Integrity (`DQ-07`)
* In the semi-synthetic propagation generator, every `content_id` referenced in an edge or event MUST resolve to an authentic entity present in `media_record` or `crisis_event`.
* Dangling foreign keys are strictly prohibited.

### 8. Corrupted File Quarantine (`DQ-08`)
* Corrupted archives or truncated files must fail with descriptive exceptions and never be silently bypassed.
* Checksum verification (SHA256) is mandatory prior to ingestion.

### 9. Class Imbalance Mitigation (`DQ-09`)
* Deepfake benchmarks frequently contain 4:1 to 10:1 fake-to-real ratios.
* The evaluation subset must be explicitly stratified to achieve a 1:1 or 2:1 balanced class distribution to ensure unbiased ROC-AUC and F1-score computation.

---

## 2. Train / Test Leakage Prevention Protocol (`DQ-10`)

**CRITICAL MANDATE: No information from the test set may leak into the training process.**

1. **Partitioning by Video / Subject Identity:**
   - In Google DFD and NIST OpenMFC, train/test splits must be stratified by **subject / original video identity**, NEVER by random frame sampling.
   - All frames or crops originating from a single video (or actor) must strictly belong to either the training set OR the test set, never both.
2. **Feature Scaler & Transformer Fitting:**
   - Spark MLlib `StandardScaler`, `VectorAssembler`, `StringIndexer`, and `IDF` models must be fitted EXCLUSIVELY on the training DataFrame:
     $$\text{Scaler.fit}(DF_{\text{train}}) \rightarrow \text{Scaler.transform}(DF_{\text{train}}), \quad \text{Scaler.transform}(DF_{\text{test}})$$
   - Never fit transformers on the combined dataset.
3. **Graph Feature Isolation:**
   - Graph centrality metrics (PageRank) computed over test-window cascades must not be leaked into training feature stores.
