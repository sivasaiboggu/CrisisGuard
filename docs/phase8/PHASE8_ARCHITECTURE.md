# CrisisGuard — Phase 8: Distributed Big Data Pipeline Architecture

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **PASS — ARCHITECTURE VERIFIED & DEPLOYED**

---

## 1. Architectural Mission & Course Requirement

The primary mandate of Phase 8 is to implement and validate an end-to-end, multi-stage distributed Big Data architecture where real data flows sequentially across major distributed tools:

$$\text{HDFS} \longrightarrow \text{Spark} \longrightarrow \text{GraphX} \longrightarrow \text{Kafka} \longrightarrow \text{Spark Structured Streaming} \longrightarrow \text{Hive}$$

Rather than creating isolated or toy scripts, each stage consumes the physical output produced by its upstream predecessor:
1. **HDFS 3.3.6:** Serves as the primary distributed storage namespace (`/crisisguard/phase8/`) hosting frozen cascade and contextual Parquet datasets.
2. **Apache Spark 3.5.1 (Batch):** Ingests raw Parquet from HDFS, normalizes schemas, enforces types, extracts vertices, audits duplicate edges, and formats GraphX-compatible vertex and edge files.
3. **Apache Spark GraphX (Scala 2.12):** Directly ingests the HDFS graph topology, constructs the distributed graph, executes PageRank (20 iterations), extracts connected components, and estimates diffusion reachability.
4. **Apache Kafka 3.7.0 (KRaft):** Serves as the real-time event streaming backbone (`crisisguard-propagation-events`), replaying 5,004 verified cascade events with strict partition ordering.
5. **Spark Structured Streaming 3.5.1:** Ingests the live Kafka stream, enforces event-time processing with a 1-hour watermark, aggregates temporal metrics over 32 tumbling windows, and commits raw and windowed outputs back to HDFS.
6. **Apache Hive 3.1.3:** Provisions external warehouse tables over HDFS Parquet stores and executes cross-stage analytical queries synthesizing graph centrality, stream velocity, and media risk.

---

## 2. End-to-End Data Flow Diagram

```mermaid
flowchart TD
    subgraph S1["1. Distributed Storage Layer"]
        HDFS["Hadoop HDFS 3.3.6<br/>/crisisguard/phase8/"]
        P_EV["propagation_events.parquet<br/>(5,004 events)"]
        P_ED["propagation_edges.parquet<br/>(4,999 edges)"]
        HDFS --> P_EV
        HDFS --> P_ED
    end

    subgraph S2["2. Batch Ingestion & Graph Preparation"]
        SPARK_BATCH["Apache Spark 3.5.1 Batch<br/>spark_prepare_propagation.py"]
        P_EV --> SPARK_BATCH
        P_ED --> SPARK_BATCH
        GX_VERT["vertices.csv / parquet<br/>(7,494 vertices)"]
        GX_EDGE["edges.csv / parquet<br/>(4,999 edges)"]
        SPARK_BATCH --> GX_VERT
        SPARK_BATCH --> GX_EDGE
    end

    subgraph S3["3. Graph Intelligence Layer"]
        GRAPHX["Apache Spark GraphX (Scala 2.12)<br/>PropagationGraph.scala"]
        GX_VERT --> GRAPHX
        GX_EDGE --> GRAPHX
        GX_RES["graphx_vertex_metrics.csv<br/>(PageRank, CC, Degrees)"]
        GRAPHX --> GX_RES
        GX_RES -->|Persist to HDFS| HDFS
    end

    subgraph S4["4. Real-Time Streaming Backbone"]
        KAFKA_PROD["Kafka Producer<br/>produce_propagation_events.py"]
        P_EV --> KAFKA_PROD
        KAFKA["Apache Kafka 3.7.0 (KRaft)<br/>crisisguard-propagation-events"]
        KAFKA_PROD -->|2,570 evt/s| KAFKA
    end

    subgraph S5["5. Stream Processing Engine"]
        STREAM["Spark Structured Streaming<br/>propagation_stream.py"]
        KAFKA --> STREAM
        WATERMARK["1-Hour Event-Time Watermark<br/>32 Tumbling Windows"]
        STREAM --> WATERMARK
        STREAM_SINK["HDFS Streaming Sinks<br/>parsed_events & windowed_metrics"]
        WATERMARK --> STREAM_SINK
        STREAM_SINK -->|Commit to HDFS| HDFS
    end

    subgraph S6["6. Big Data Enterprise Warehouse"]
        HIVE["Apache Hive Metastore / Spark SQL<br/>crisisguard_phase8"]
        HDFS --> HIVE
        HIVE_T1["propagation_graph_metrics"]
        HIVE_T2["propagation_stream_metrics"]
        HIVE_T3["media_risk_features"]
        HIVE_T4["crisis_intelligence_features"]
        HIVE --> HIVE_T1
        HIVE --> HIVE_T2
        HIVE --> HIVE_T3
        HIVE --> HIVE_T4
        QUERIES["Analytical SQL Queries 1 to 6"]
        HIVE_T1 --> QUERIES
        HIVE_T2 --> QUERIES
        HIVE_T3 --> QUERIES
        HIVE_T4 --> QUERIES
    end
```

---

## 3. Disjoint Stream Policy & Schema Boundaries

A foundational architectural constraint in Phase 8 is the **rejection of unvalidated synthetic joins**:
- **Social Propagation Space:** Vertices are user identifiers (e.g., `760800`, `871722`) propagating semi-synthetic cascades.
- **Humanitarian Crisis Space:** Identifiers are Twitter Snowflake IDs (`source_record_id`) reporting physical disaster observations.
- **Media Risk Space:** Identifiers are synthetic image/video asset tags (`cifake_real_...`).

Because pairwise intersection across these key domains is strictly **0.00%**, Phase 8 stores and queries them as distinct external tables. Hive queries aggregate within domains and synthesize macroscopic trends without inventing false foreign key linkages.

---

## 4. Phase Boundary Enforcements

- **No EDPI:** No Emergency Dispatch Priority Index was computed.
- **No Dispatch Weighting:** No heuristic emergency priority formulas were applied.
- **No Dashboard:** Dashboard visualization is deferred to Phase 9.
- **Frozen Inputs Intact:** Phase 4, Phase 6, and Phase 7 source files remain unaltered.

**Architecture Status: PASS — FULLY DEPLOYED & TESTED**
