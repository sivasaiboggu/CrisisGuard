# CrisisGuard: Phase 5 Tool-to-Tool Integration Test Matrix

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase Status:** Phase 5 Integration Smoke Tests  

---

## 1. Integration Verification Matrix

In strict compliance with CSE412 requirements, Big Data tools must genuinely exchange and process data. The table below documents the verified tool-to-tool data paths tested during Phase 5:

| Test Name | Source Entity | Destination / Consumer | Real Data Sample Used | Verification Command / Script | Execution Result |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **Java 11 Bytecode** | Source `.java` file | JVM 11 Bytecode Engine | N/A (Smoke string) | `scripts/environment/test_java.sh` | **PASS** |
| **Scala 2.12.18 REPL** | Inline Scala Script | Scala 2.12 Compiler / JVM | N/A (Smoke string) | `scripts/environment/test_scala.sh` | **PASS** |
| **Hadoop HDFS Storage**| Local filesystem | HDFS Cluster Block Store | Yes (`/tmp/hdfs_smoke_test.txt`) | `tests/integration/test_hdfs_smoke.sh` | **PASS** |
| **Spark Local Engine** | Phase 4 Processed Parquet | Spark Dataframe & Catalyst | Yes (`cifake_canonical.parquet`) | `tests/integration/test_spark_local_smoke.py` | **PASS** |
| **Spark + HDFS Pipeline**| HDFS (`hdfs://127.0.0.1:9000/`) | Spark Session / Aggregator | Yes (`cifake_canonical.parquet`) | `tests/integration/test_spark_hdfs_smoke.py` | **PASS** |
| **Kafka Producer** | Script Memory / Stream | Kafka Topic (`crisisguard.phase5.test`) | Yes (Author verification payload) | `tests/integration/test_kafka_smoke.py` | **PASS** |
| **Kafka Consumer** | Kafka Topic Broker | Python Client Stdout | Yes (Author verification payload) | `tests/integration/test_kafka_smoke.py` | **PASS** |
| **Kafka Real Event Stream**| Phase 4 Processed Events | Kafka Topic (`crisisguard.phase5.events`) | Yes (`propagation_events.parquet`) | `tests/integration/test_kafka_smoke.py` | **PASS** |
| **Hive Core DDL/DML** | Hive Metastore DDL | Embedded Derby Metastore | Yes (`crisisguard_smoke` table) | `tests/integration/test_hive_smoke.py` | **PASS** |
| **Hive Data Flow** | Phase 4 Processed Sample | Hive Warehouse Table / SQL | Yes (`propagation_sample.csv`) | `tests/integration/test_hive_smoke.py` | **PASS** |

---

## 2. Test Execution Details & Data Paths

### 2.1 HDFS Data Flow
$$\text{Local File System} \xrightarrow[\text{hdfs dfs -put}]{} \text{HDFS NameNode (9000) / DataNode (9866)} \xrightarrow[\text{hdfs dfs -cat}]{} \text{Verified Content Output}$$

### 2.2 Spark + HDFS Data Flow
$$\text{data/processed/cifake/*.parquet} \xrightarrow{} \text{hdfs://127.0.0.1:9000/crisisguard/processed/cifake/} \xrightarrow{} \text{Spark DataFrame} \xrightarrow[\text{groupBy('label').count()}]{} \text{Distributed Aggregation}$$

### 2.3 Kafka Real Event Data Flow
$$\text{data/processed/propagation/*.parquet} \xrightarrow{} \text{JSON Serialization} \xrightarrow{} \text{Kafka Topic: crisisguard.phase5.events} \xrightarrow{} \text{Kafka Consumer} \xrightarrow{} \text{Deser Verification}$$

### 2.4 Hive Warehouse Data Flow
$$\text{data/processed/propagation/ (Sample)} \xrightarrow{} \text{LOAD DATA LOCAL INPATH} \xrightarrow{} \text{default.crisisguard_propagation_sample} \xrightarrow[\text{SELECT scenario_id, COUNT(*)}]{} \text{SQL Query Result}$$
