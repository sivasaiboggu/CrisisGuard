# CrisisGuard: Phase 5 Version Compatibility & Integration Matrix

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  

---

## 1. Component Compatibility Matrix

| Component | Selected Version | Required Runtime / ABI | Actual WSL2 Runtime | Compatibility Status | Verification Evidence / Test Protocol |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Java** | OpenJDK 11.0.26 LTS | 64-bit Linux JVM | `/usr/lib/jvm/java-11-openjdk-amd64` | **COMPATIBLE** | `java -version` returns OpenJDK 11; bytecode execution smoke test passes. |
| **Python** | 3.12.3 | CPython 3.8–3.12 | Python 3.12.3 (`/usr/bin/python3`) | **COMPATIBLE** | PySpark 3.5.1 worker execution, pandas, and pyarrow integration tests. |
| **Scala** | 2.12.18 | JVM 8/11; matches Spark 3.5.1 | Scala 2.12.18 binary (`/opt/scala`) | **COMPATIBLE** | Binary compatibility with Spark 3.5.1 core and GraphX prebuilt assemblies. |
| **Hadoop** | 3.3.6 | Java 8 or 11; Linux x86_64 | Native POSIX + `/opt/hadoop` | **COMPATIBLE** | Single-node HDFS formatting, NameNode/DataNode launch, file put/get verification. |
| **Spark** | 3.5.1 (Hadoop3 prebuilt) | Java 11, Scala 2.12, Hadoop 3 | `/opt/spark` | **COMPATIBLE** | SparkSession instantiation, PySpark job execution, Parquet read/aggregation. |
| **Kafka** | 3.7.0 (Scala 2.12 build) | Java 11+, KRaft metadata | `/opt/kafka` | **COMPATIBLE** | KRaft controller initialization, broker launch, topic creation, producer/consumer test. |
| **Hive** | 3.1.3 (or Spark-Hive catalog) | Hadoop 3.3.6, Java 11 | `/opt/hive` + Derby/Local Metastore | **COMPATIBLE** | Standard Guava replacement (`guava-27.0-jre.jar`), DDL CREATE TABLE, INSERT/SELECT test. |

---

## 2. Compatibility Risk Analysis & Engineering Mitigations

### 2.1 Java 11 vs. Java 8 Conflict
- **Challenge:** Ubuntu 24.04 had OpenJDK 8 set as the default `java` alternative while Java 11 was also installed.
- **Resolution:** Explicitly export `JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64` in `/etc/profile.d/crisisguard_env.sh` and set `update-alternatives --set java` to Java 11 so that all daemon processes and client shells inherit OpenJDK 11.

### 2.2 Scala 2.12 vs. Scala 2.13 in Spark 3.5.1
- **Challenge:** Spark 3.5.1 releases are compiled against Scala 2.12 by default (`spark-3.5.1-bin-hadoop3.tgz`). GraphX Pregel algorithms in Scala require strict binary compatibility with the runtime Spark core.
- **Resolution:** Frozen Scala version is **2.12.18**. Using `kafka_2.12-3.7.0.tgz` aligns Kafka client libraries with the exact same Scala ABI.

### 2.3 Hive 3.1.3 Guava Mismatch with Hadoop 3.3.x
- **Challenge:** Apache Hive 3.1.3 ships with `guava-19.0.jar`. Hadoop 3.3.6 uses `guava-27.0-jre.jar`. If Hive attempts to load `guava-19.0.jar`, a runtime exception (`NoSuchMethodError: com.google.common.base.Preconditions.checkArgument`) occurs during schema initialization.
- **Resolution:** Remove `guava-19.0.jar` from `$HIVE_HOME/lib/` and symlink `$HADOOP_HOME/share/hadoop/common/lib/guava-27.0-jre.jar` into `$HIVE_HOME/lib/`.

### 2.4 Kafka 3.7.0 Metadata Mode (KRaft)
- **Challenge:** Older Kafka versions required Apache ZooKeeper, requiring an additional daemon process and memory overhead.
- **Resolution:** Kafka 3.7.0 KRaft mode runs without ZooKeeper, saving ~500 MB RAM and drastically simplifying local single-node service management for the 16 GB host constraint.
