# CrisisGuard — Comprehensive Viva & Examination Preparation (30+ Questions & Answers)

**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  

---

## Table of Categories
1. [Big Data Architecture & Distributed Computing](#1-big-data-architecture--distributed-computing)
2. [Apache Kafka & Stream Ingestion](#2-apache-kafka--stream-ingestion)
3. [Apache Spark Structured Streaming & Watermarking](#3-apache-spark-structured-streaming--watermarking)
4. [Apache Spark GraphX & Network Analytics](#4-apache-spark-graphx--network-analytics)
5. [Hadoop HDFS & Apache Hive Warehouse](#5-hadoop-hdfs--apache-hive-warehouse)
6. [Machine Learning Forensics & Calibration](#6-machine-learning-forensics--calibration)
7. [Data Governance, Relational Integrity & Schema Design](#7-data-governance-relational-integrity--schema-design)
8. [Failure Resilience & Production Engineering](#8-failure-resilience--production-engineering)

---

## 1. Big Data Architecture & Distributed Computing

### Q1: What architectural pattern does CrisisGuard follow: Lambda, Kappa, or a hybrid?
**Answer:** CrisisGuard employs a **hybrid architecture** that combines the strengths of both Lambda and Kappa:
- For **stream processing (Phase 8)**, it uses a **Kappa-style log-centric architecture** where Apache Kafka serves as the single source of truth for real-time propagation cascades, consumed continuously by Spark Structured Streaming.
- For **graph analytics and historical feature unification (Phases 4, 8, 9)**, it applies **batch computing** (GraphX iterative graph algorithms and Spark SQL) to generate authoritative PageRank scores, connected components, and the Phase 9 Multi-Stream Ledger of 175,361 rows.

### Q2: Why did you separate Kafka ingestion from Spark streaming rather than writing directly from producers to HDFS?
**Answer:** Direct writes from high-velocity edge producers to HDFS suffer from two major flaws:
1. **The Small Files Problem in HDFS:** High-frequency small network requests cause NameNode heap exhaustion because every file/block consumes ~150 bytes of NameNode memory.
2. **Backpressure and Decoupling:** Kafka acts as an elastic shock absorber. If downstream Spark consumers experience transient latency or crash, Kafka's distributed commit log safely buffers messages for the duration of the retention policy without data loss.

### Q3: How does the pipeline scale horizontally if event volume grows by 100x?
**Answer:**
- **Kafka:** Increase topic partitions from 1 to $N$. Kafka automatically distributes partitions across broker nodes, enabling parallel ingestion.
- **Spark:** Scale worker executors horizontally. Spark automatically assigns each Kafka partition to a dedicated Spark task, maintaining 1:1 parallel consumption.
- **HDFS:** Add DataNodes to distribute block placement and scale aggregate I/O throughput.

---

## 2. Apache Kafka & Stream Ingestion

### Q4: What message delivery semantic does CrisisGuard provide (at-most-once, at-least-once, exactly-once)?
**Answer:** CrisisGuard provides **end-to-end at-least-once delivery with idempotent downstream sinks (effectively exactly-once)**:
- The Kafka producer is configured with `acks="all"` and `retries=3`, ensuring data is replicated before acknowledgement.
- Spark Structured Streaming tracks read offsets via write-ahead transaction logs and commits output micro-batches to deterministic Parquet paths with checkpointing.
- Downstream deduplication on `event_id` ensures idempotent processing.

### Q5: What partitioning key strategy is used in Kafka and why?
**Answer:** Events are keyed by `scenario_id` (or `source_node`). In Kafka, all messages with the same partition key are guaranteed to land on the same partition. This guarantees **strict temporal and causal ordering** within a given disaster scenario or network cascade, avoiding race conditions during windowed aggregations.

### Q6: What happens if the Kafka broker crashes during stream consumption?
**Answer:** Spark Structured Streaming maintains persistent state checkpoints (including consumed partition offsets) in HDFS / local storage. When the broker recovers, Spark resumes consumption from the exact offset recorded in the last successful commit log, ensuring zero message loss and no reprocessing of stale offsets.

---

## 3. Apache Spark Structured Streaming & Watermarking

### Q7: Explain the purpose and operation of the 1-hour watermark in your streaming engine.
**Answer:** A watermark defines how long the streaming engine will wait for late-arriving events before dropping them or closing the aggregation window:
```python
parsed_stream_df.withColumn("event_timestamp", F.to_timestamp(F.col("event_time"))) \
    .withWatermark("event_timestamp", "1 hour")
```
- Let the maximum observed event time be $T_{max}$. The watermark is computed as $T_{max} - 1\text{ hour}$.
- Any incoming event whose timestamp is older than the current watermark is dropped from the aggregation state store.
- **Critical benefit:** Prevents unbounded state growth in the Spark driver/executor memory by garbage-collecting closed tumbling windows.

### Q8: What windowing model is implemented in Phase 8?
**Answer:** A **1-hour Tumbling Window** on `event_timestamp`. Tumbling windows are fixed-duration, non-overlapping, contiguous time intervals. Each event falls into exactly one window, computed as:
$$\text{Window Start} = \lfloor \text{timestamp} / 1\text{ hr} \rfloor \times 1\text{ hr}$$
$$\text{Window End} = \text{Window Start} + 1\text{ hr}$$
Across the 32-hour simulation of Phase 8, this generated exactly **32 distinct temporal windows**.

### Q9: Why did you use `availableNow=True` trigger during Phase 8 batch reconciliation?
**Answer:** `Trigger(availableNow=True)` processes all available data in the Kafka topic across multiple micro-batches until the queue is completely drained, and then cleanly terminates. This provides identical computation to a continuous streaming job while allowing deterministic end-to-end reconciliation against batch ground truth.

---

## 4. Apache Spark GraphX & Network Analytics

### Q10: How many vertices and edges does your propagation network have?
**Answer:**
- **Vertices:** 7,494 unique vertices (representing source nodes, target nodes, and cascade origins).
- **Edges:** 4,999 directed propagation edges.
- **Events:** 5,004 raw propagation events (including 5 root seed events with null parent targets).

### Q11: What graph algorithms did you execute with GraphX and what are their computational complexities?
**Answer:**
1. **Dynamic PageRank:** Computes the structural influence and information propagation likelihood of each node. PageRank runs iteratively with complexity $\mathcal{O}(I \times (V + E))$, where $I$ is iterations, converging when error $\epsilon < 0.001$.
2. **Connected Components:** Identifies disconnected subgraphs and isolated cascade clusters using label propagation, running in $\mathcal{O}(D \times (V + E))$, where $D$ is the graph diameter.
3. **In-Degree and Out-Degree:** Aggregates incoming and outgoing edges per vertex in $\mathcal{O}(E)$.

### Q12: Why compile GraphX in Scala rather than using PySpark GraphFrames?
**Answer:** GraphX is part of core Spark written natively in Scala. Executing iterative graph algorithms (like PageRank) in Scala avoids the heavy serialization overhead and Python-JVM IPC context switching that plagues PySpark graph operations, yielding ~3–5x higher execution throughput and lower memory footprint. Our assembly JAR is located at `target/phase8/crisisguard-graphx.jar` (13,092 bytes).

---

## 5. Hadoop HDFS & Apache Hive Warehouse

### Q13: What is the block size and replication factor configured for HDFS in CrisisGuard?
**Answer:**
- **Replication Factor:** 3 (standard Hadoop default for enterprise fault tolerance).
- **Block Size:** 128 MB. For files smaller than 128 MB, HDFS allocates only the physical file size plus metadata in the NameNode.

### Q14: How does Apache Hive interact with HDFS and Parquet in your architecture?
**Answer:** Hive tables are defined as **EXTERNAL TABLES** pointing directly to HDFS and local Parquet directories:
- Schema-on-Read: Hive does not move or copy data; it creates schema metadata in the Derby metastore pointing to the storage paths.
- Columnar Efficiency: Hive queries read only the necessary columns (e.g. `scenario_id`, `mean_synthetic_risk`), skipping unreferenced columns via Parquet's columnar projection and Snappy block compression.

### Q15: What are the 4 external Hive tables created in Phase 8?
**Answer:**
1. `propagation_events`: Raw cascade events (5,004 records).
2. `graph_pagerank`: Vertex PageRank scores (7,494 vertices).
3. `graph_components`: Connected components and subgraph IDs.
4. `streaming_window_metrics`: 1-hour windowed aggregations (32 windows).

---

## 6. Machine Learning Forensics & Calibration

### Q16: What neural network backbone is used for synthetic media detection in Phase 6?
**Answer:** A modified **ResNet-18** architecture:
- **Image Forensics:** ResNet-18 binary classifier trained on the CIFAKE dataset, fine-tuned with a custom fully-connected classification head.
- **Video Forensics:** A two-stage architecture comprising a ResNet-18 frame-level spatial feature extractor (512-dim embedding) followed by a temporal classifier modeling cross-frame artifacts.

### Q17: Why are your model confidence scores explicitly labeled "UNCALIBRATED"?
**Answer:** Neural networks with Sigmoid or Softmax outputs produce scores that are often overconfident and do not represent true empirical probabilities. True calibration requires post-processing techniques such as **Platt Scaling (logistic calibration)**, **Isotonic Regression**, or **Temperature Scaling** evaluated against an independent calibration set with Brier Score or Expected Calibration Error (ECE). In CrisisGuard, because post-hoc calibration was not performed, academic honesty demands labeling the outputs as `UNCALIBRATED`.

### Q18: What text classification architecture is used in Phase 7?
**Answer:**
- **CrisisMMD:** TF-IDF feature extraction with sublinear term frequency scaling coupled with a multi-class Logistic Regression classifier evaluated on official splits across 5 humanitarian classes.
- **HumAID:** Stratified prior distribution baseline on official train/dev/test splits (76,484 records), reflecting that text was unhydrated locally due to Twitter API v2 academic policy changes.

---

## 7. Data Governance, Relational Integrity & Schema Design

### Q19: Explain the "NO_VALID_JOIN" finding and why it is scientifically significant.
**Answer:** In multi-source disaster response systems, engineers often attempt to join disparate datasets (e.g., joining tweets with OpenStreetMap road segments). We conducted an empirical **Key Overlap Audit** across all 7 project datasets and proved that key overlap is **0.00%**. Performing arbitrary outer joins would create billions of meaningless Cartesian products. Instead, CrisisGuard preserves relational integrity by implementing an **additive multi-stream ledger** where each stream retains its native keys, explicit NULLs are enforced for absent attributes, and no synthetic relationships are fabricated.

### Q20: What is the size and composition of the Phase 9 Multi-Stream Ledger?
**Answer:** Exactly **175,361 rows**, comprised of:
- **Stream A (Synthetic Media Forensics):** 77 rows
- **Stream B (Crisis Information Intelligence):** 104,130 rows
- **Stream C (Propagation & Graph Intelligence):** 7,494 rows
- **Stream D (Spatial Road Network Nodes):** 63,660 rows
- **Total:** $77 + 104,130 + 7,494 + 63,660 = 175,361$ rows.

### Q21: Why does CrisisGuard reject "EDPI" (Emergency Disaster Priority Index)?
**Answer:** EDPI was an ad-hoc heuristic that computed a weighted sum of heterogeneous scores (e.g. $0.4 \times \text{risk} + 0.3 \times \text{PageRank} + 0.3 \times \text{damage}$). This creates arbitrary, non-reproducible rankings without statistical validation. CrisisGuard replaces arbitrary weights with unadulterated evidence streams and explicit schema contracts.

---

## 8. Failure Resilience & Production Engineering

### Q22: What controlled failure resilience tests were designed and validated?
**Answer:** Five tests were systematically implemented and passed:
1. **Malformed JSON Injection:** Ingestion of malformed payloads is safely caught by schema validation and routed to dead-letter queues.
2. **Duplicate Event Handling:** Kafka replay of already processed event IDs produces idempotent output without double-counting.
3. **Null Timestamp Resilience:** Events with missing timestamps are quarantined rather than crashing the watermarking engine.
4. **Dangling Edge Tolerance:** Edges referencing non-existent nodes are safely filtered without breaking GraphX vertex unions.
5. **Out-of-Bounds Risk Scores:** Media scores outside $[0.0, 1.0]$ are rejected by schema assertion.

### Q23: How do you verify that your live demo did not alter frozen computational outputs?
**Answer:** All demo outputs are strictly sandboxed:
- Ingestion targets `crisisguard-demo-events` (never `crisisguard-propagation-events`).
- Storage targets `data/demo/` and `/crisisguard/demo/` (never `data/features/`).
- Running `scripts/validation/validate_final_project.py` performs MD5, row count, and schema checks across all 15 frozen artifacts, guaranteeing 10/10 PASS.

### Q24: What is the difference between event time and processing time?
**Answer:**
- **Processing Time:** The system clock time of the machine executing the Spark task.
- **Event Time:** The actual time when the disaster event or tweet occurred, embedded within the event payload.
- **CrisisGuard Choice:** CrisisGuard strictly uses **Event Time** with watermarking because social media messages often experience network delays, and aggregating by processing time would scramble chronological cascade dynamics.

---

## Summary Checklist for Viva Presentation
- [x] All 7 datasets identified and row counts memorized (CIFAKE=500, DFD=4/12, HumAID=76,484, CrisisMMD=8,079, CrisisLex=88,015, OSM Nodes=63,660, Edges=146,156, Prop Events=5,004).
- [x] Exact Phase 9 ledger count known: **175,361**.
- [x] Master Validator & Acceptance Suite verified: **10/10 PASS**.
- [x] Both Demo Modes (A and B) tested and ready to execute live on demand.
