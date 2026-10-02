# CrisisGuard — Phase 8: HDFS Ingestion & Namespace Verification Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 8 — Real-Time Propagation Analysis and Graph-Based Crisis Intelligence  
**Date:** September 28, 2026  
**Status:** **PASS — HDFS NAMESPACE INITIALIZED & INGESTED**

---

## 1. Executive Summary

In fulfillment of the distributed storage requirement of Phase 8, a dedicated HDFS namespace (`/crisisguard/phase8/`) was created and populated with approved upstream inputs. Live execution on Apache Hadoop HDFS 3.3.6 (NameNode port 9000 / DataNode local cluster) verified directory creation, file transfer, size integrity, and storage distribution without modifying or overwriting frozen local datasets.

---

## 2. HDFS Directory Hierarchy

The following subdirectories were created under `/crisisguard/phase8/`:
- `/crisisguard/phase8/propagation/`: Ingested propagation events and edge lists for Spark batch and streaming.
- `/crisisguard/phase8/media_risk/`: Phase 6 synthetic media risk predictions.
- `/crisisguard/phase8/crisis_intelligence/`: Phase 7 unified crisis features (HumAID, CrisisMMD, CrisisLex).
- `/crisisguard/phase8/osm/`: OpenStreetMap regional infrastructure road network (nodes and edges).
- `/crisisguard/phase8/graph/`: Destination directory for Spark GraphX vertices, edges, and PageRank outputs.
- `/crisisguard/phase8/streaming/`: Destination directory for Spark Structured Streaming checkpointing and parquet sinks.
- `/crisisguard/phase8/hive/`: Warehouse destination for Hive external tables.

---

## 3. Ingestion Manifest & Size Verification

| HDFS Destination Path | Ingested Source File | Source Size | HDFS Verified Size | Ingestion Status |
| :--- | :--- | :---: | :---: | :---: |
| `/crisisguard/phase8/propagation/propagation_events.parquet` | `data/processed/propagation/propagation_events.parquet` | 232,713 B | **232,713 B** | PASS |
| `/crisisguard/phase8/propagation/propagation_edges.parquet` | `data/processed/propagation/propagation_edges.parquet` | 99,922 B | **99,922 B** | PASS |
| `/crisisguard/phase8/media_risk/unified_media_risk.parquet` | `data/features/synthetic_media/unified_media_risk.parquet` | 11,100 B | **11,100 B** | PASS |
| `/crisisguard/phase8/crisis_intelligence/unified_crisis_intelligence.parquet` | `data/features/crisis_information/unified_crisis_intelligence.parquet` | 3,445,876 B | **3,445,876 B** | PASS |
| `/crisisguard/phase8/osm/road_nodes.parquet` | `data/processed/osm/road_nodes.parquet` | 1,587,382 B | **1,587,382 B** | PASS |
| `/crisisguard/phase8/osm/road_edges.parquet` | `data/processed/osm/road_edges.parquet` | 2,448,753 B | **2,448,753 B** | PASS |

Total HDFS Ingested Volume: **7.82 MB** across 6 core Parquet datasets.

---

## 4. Physical Evidence (`hdfs dfs -ls -R` and `hdfs dfs -du -h`)

### 4.1 Recursive Listing Evidence
```
drwxr-xr-x   - sivasai supergroup          0 2026-09-27 19:21 /crisisguard/phase8/crisis_intelligence
-rw-r--r--   1 sivasai supergroup    3445876 2026-09-27 19:21 /crisisguard/phase8/crisis_intelligence/unified_crisis_intelligence.parquet
drwxr-xr-x   - sivasai supergroup          0 2026-09-27 19:21 /crisisguard/phase8/graph
drwxr-xr-x   - sivasai supergroup          0 2026-09-27 19:21 /crisisguard/phase8/hive
drwxr-xr-x   - sivasai supergroup          0 2026-09-27 19:21 /crisisguard/phase8/media_risk
-rw-r--r--   1 sivasai supergroup      11100 2026-09-27 19:21 /crisisguard/phase8/media_risk/unified_media_risk.parquet
drwxr-xr-x   - sivasai supergroup          0 2026-09-27 19:21 /crisisguard/phase8/osm
-rw-r--r--   1 sivasai supergroup    2448753 2026-09-27 19:21 /crisisguard/phase8/osm/road_edges.parquet
-rw-r--r--   1 sivasai supergroup    1587382 2026-09-27 19:21 /crisisguard/phase8/osm/road_nodes.parquet
drwxr-xr-x   - sivasai supergroup          0 2026-09-27 19:21 /crisisguard/phase8/propagation
-rw-r--r--   1 sivasai supergroup      99922 2026-09-27 19:21 /crisisguard/phase8/propagation/propagation_edges.parquet
-rw-r--r--   1 sivasai supergroup     232713 2026-09-27 19:21 /crisisguard/phase8/propagation/propagation_events.parquet
drwxr-xr-x   - sivasai supergroup          0 2026-09-27 19:21 /crisisguard/phase8/streaming
```

### 4.2 Disk Usage Breakdown
```
3.3 M    3.3 M    /crisisguard/phase8/crisis_intelligence
0        0        /crisisguard/phase8/graph
0        0        /crisisguard/phase8/hive
10.8 K   10.8 K   /crisisguard/phase8/media_risk
3.8 M    3.8 M    /crisisguard/phase8/osm
324.8 K  324.8 K  /crisisguard/phase8/propagation
0        0        /crisisguard/phase8/streaming
```

---

## 5. Verification Conclusion

All HDFS operations completed cleanly with zero exit code errors, exact byte matching, and valid permissions. Upstream local frozen files remain unchanged.

**HDFS Status: PASS — FROZEN FOR PHASE 8 SPARK PROCESSING**
