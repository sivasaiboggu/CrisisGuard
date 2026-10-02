# CrisisGuard: Phase 5 Big Data Environment & Integration Final Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase Status:** Phase 5 Completed & Audited (Phase 6 NOT Started)  

---

## 1. Executive Objective

Phase 5 established a stable, verified, reproducible, locally executable Big Data runtime environment for Project CrisisGuard. In strict compliance with the CSE412 applied project specification:
1. All selected Big Data components were empirically validated for binary and runtime compatibility.
2. Genuine data exchange and processing was proven between sequential tools.
3. No premature model training, GraphX implementations, or mock predictions were introduced.
4. Raw data (`data/raw/`) remains completely untouched and immutable.
5. Phase 4 processed data (`data/processed/`) was preserved and utilized exclusively for legitimate integration smoke tests.

---

## 2. Infrastructure & Hardware Profile

* **Host Machine:** AMD Ryzen 7 7445HS (6 Physical Cores / 12 Logical Processors), 16 GB Physical DDR5 RAM, Windows 11 Home Single Language.
* **Virtualization Layer:** WSL2 running Ubuntu 24.04.4 LTS (Noble Numbat) on Linux Kernel 6.6.87.2-microsoft-standard-WSL2.
* **Storage Allocation:** 943 GiB available on Linux native ext4 (`/dev/sdd`), 237 GiB available on Windows `C:\`. All high-throughput Big Data block storage, logs, and scratch directories reside on native Linux ext4 (`/var/crisisguard/`).

---

## 3. Frozen Version Matrix & Compatibility Evidence

| Component | Target Version | Actual Installed Version | Runtime Substrate | Status | Evidence / Test Protocol |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Java** | 11 LTS | OpenJDK 11.0.31 | `/usr/lib/jvm/java-11-openjdk-amd64` | **PASS** | Bytecode compile & execution smoke test (`test_java.sh`). |
| **Scala** | 2.12.18 | Scala 2.12.18 | `/opt/scala` | **PASS** | Interactive expression execution smoke test (`test_scala.sh`). |
| **Python** | 3.12.x | Python 3.12.3 | `/usr/bin/python3` | **PASS** | PySpark worker and PyArrow compatibility verified. |
| **Hadoop** | 3.3.6 | Apache Hadoop 3.3.6 | `/opt/hadoop` (`hdfs://127.0.0.1:9000`) | **PASS** | Single-node HDFS formatted, NameNode/DataNode live (`test_hdfs_smoke.sh`). |
| **Spark** | 3.5.1 | Apache Spark 3.5.1 | `/opt/spark` (PySpark distribution) | **PASS** | SparkSession local execution & dataframe aggregation (`test_spark_local_smoke.py`). |
| **Kafka** | 3.7.0 | Apache Kafka 3.7.0 | `/opt/kafka` (KRaft Metadata Mode) | **PASS** | Topic creation, producer, consumer, and real event stream (`test_kafka_smoke.py`). |
| **Hive** | 3.1.3 | Apache Hive 3.1.3 | `/opt/hive` (Embedded Derby Metastore)| **PASS** | Guava-aligned (`guava-27.0-jre.jar`), DDL/DML, and processed data load (`test_hive_smoke.py`). |

---

## 4. Empirical Tool-to-Tool Integration Data Flows

The core rubric requires genuine tool-to-tool data flow. Phase 5 verified the following real data pipelines:

1. **HDFS Storage Data Flow:**
   * Input: Local verification file containing author credentials (`B.SIVASAI 2023BCS0228`).
   * Ingestion: Uploaded via `hdfs dfs -put` to `/crisisguard/test/hdfs_smoke_test.txt`.
   * Retrieval: Retrieved via `hdfs dfs -cat` and cryptographically validated.

2. **Spark + HDFS Pipeline:**
   * Input: Legitimate Phase 4 processed Parquet dataset (`data/processed/cifake/cifake_canonical.parquet`).
   * Ingestion: Uploaded to `hdfs://127.0.0.1:9000/crisisguard/processed/cifake/`.
   * Processing: PySpark 3.5.1 connected directly to HDFS URI, deserialized Parquet schema, and performed distributed aggregation (`groupBy("label").count()`).

3. **Kafka Real Event Streaming Data Flow:**
   * Input: Legitimate Phase 4 propagation event records (`data/processed/propagation/propagation_events.parquet`).
   * Serialization: Converted to canonical event JSON payloads tagged with `governance_tag: SEMI_SYNTHETIC`.
   * Streaming: Produced to topic `crisisguard.phase5.events` on broker `127.0.0.1:9092`.
   * Consumption: Consumed via Kafka console consumer and validated in Python.

4. **Hive Analytical Warehousing Data Flow:**
   * Input: Phase 4 processed propagation sample CSV.
   * Ingestion: `LOAD DATA LOCAL INPATH` into Hive table `default.crisisguard_propagation_sample`.
   * Warehousing Query: Executed SQL aggregation `SELECT scenario_id, COUNT(*) GROUP BY scenario_id;`.

---

## 5. Resource Management & Operational Stability

* **RAM Constraints:** Machine has 16 GB physical RAM. Total concurrent daemon footprint is capped at ~3.5 GiB max:
  * HDFS NameNode / DataNode: 512 MB max heap.
  * Kafka Broker: 512 MB max heap.
  * Hive Embedded Metastore: 512 MB max heap.
  * Spark Driver / Executor: 1 GB memory limit, 2 local cores (`local[2]`).
* **Service Control:** Automated lifecycle script `scripts/environment/service_control.sh` provides deterministic `start`, `stop`, and `status` controls.

---

## 6. Problems Encountered & Resolved

1. **Java Alternative Mismatch:**
   * *Problem:* Ubuntu 24.04 had Java 8 configured as default despite Java 11 being present.
   * *Resolution:* Set `update-alternatives --set java` to Java 11 and exported `JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64` in `/etc/profile.d/crisisguard_env.sh`.
2. **Hive 3.1.3 Guava Incompatibility:**
   * *Problem:* Hive 3.1.3 ships `guava-19.0.jar` while Hadoop 3.3.6 requires `guava-27.0-jre.jar`.
   * *Resolution:* Replaced Hive's `guava-19.0.jar` with Hadoop's `guava-27.0-jre.jar` in `$HIVE_HOME/lib/`.
3. **Archive.apache.org SSL Timeout:**
   * *Problem:* Direct connections to Hetzner-hosted Apache archive servers timed out over SSL from local ISP.
   * *Resolution:* Sourced Hadoop 3.3.6 from Apache Fastly CDN (`dlcdn.apache.org`), and verified cryptographic release tarballs for Kafka 3.7.0 and Hive 3.1.3 via the Internet Archive Wayback Machine.

---

## 7. Known Scope Boundaries Strictly Maintained

* **Machine Learning:** Zero ML models trained; no synthetic-media classifiers trained or evaluated.
* **GraphX / Streaming:** No Pregel algorithms or streaming applications executed; only single-node service smoke tests.
* **EDPI:** Zero heuristic emergency priority calculations or arbitrary weights.
* **Dashboard:** No UI or dashboard implemented.

---

## 8. Master Phase 5 Validation Decision

```
============================================================
CRISISGUARD — PHASE 5 ENVIRONMENT VALIDATION
============================================================
Java 11: PASS
Python 3.12: PASS
Scala 2.12.18: PASS
Hadoop 3.3.6: PASS
Spark 3.5.1: PASS
Kafka 3.7.0: PASS
Hive 3.1.3: PASS
Configuration & Docs: PASS
Data Integrity: PASS
HDFS Service (Port 9000): PASS
Kafka Service (Port 9092): PASS
============================================================
PHASE 5 DECISION
============================================================
PHASE 5 STATUS: PASS
============================================================
```
