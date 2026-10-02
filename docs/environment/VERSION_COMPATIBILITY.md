# CrisisGuard: Big Data Toolchain Version Compatibility Matrix

**Baseline Date:** 2026-09-27  
**Host Platform:** Windows 11 (Host) / WSL2 Ubuntu 24.04 LTS (Primary Big Data Runtime)  
**Status:** Frozen & Approved for Phase 2  

---

## 1. Version Compatibility Matrix

| Component | Selected Version | Java Requirement | Python Requirement | Reason | Compatibility Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Operating System / Kernel** | Ubuntu 24.04.4 LTS (WSL2, Kernel 6.6.87.2) | N/A | 3.12.3 preinstalled | Official POSIX substrate for Hadoop/Spark/Kafka | Native ext4 disk has 943 GB free; zero Windows path/permission quirks |
| **Java Development Kit** | OpenJDK 11 LTS (11.0.x) / OpenJDK 8 LTS | Self | N/A | Both already installed in `/usr/lib/jvm/`; OpenJDK 11 is the universal intersection | Hadoop 3.3.6, Spark 3.5.x, Kafka 3.7.x all support Java 11 LTS cleanly |
| **Python** | Python 3.12.3 | N/A | Self | System Python in Ubuntu 24.04 | Fully supported by PySpark 3.5.x; avoids Windows Python 3.14 incompatibilities |
| **Apache Spark** | 3.5.1 / 3.5.2 (Pre-built for Apache Hadoop 3.3+) | Java 8/11/17 | Python 3.8 – 3.12 | Current stable LTS release; includes Structured Streaming, MLlib, GraphX | Pre-built with Scala 2.12; supports direct PySpark 3.5 integration |
| **Spark GraphX** | Included with Spark 3.5.x | Java 8/11/17 | Scala 2.12 / Python via GraphFrames | Course requirement for relational graph and Pregel algorithms | Requires Scala 2.12 bytecode for native GraphX execution |
| **Spark MLlib** | Included with Spark 3.5.x | Java 8/11/17 | Python 3.12 (PySpark ML) | Distributed ML algorithms (GBT, RF, Logistic Regression, VectorAssembler) | Native integration with Spark Structured Streaming micro-batches |
| **Apache Kafka** | 3.7.0 (Scala 2.12 binary) | Java 11/17 | Python client (kafka-python / confluent-kafka) | Modern Kafka release supporting KRaft (Zookeeper-less) | Operates reliably on Java 11 with $\le 512$ MB memory footprint |
| **Apache Hive** | Spark SQL Hive Metastore (v2.3.9 / v3.1.3 client) | Java 8/11 | Python / SQL | Standard Spark-Hive integration without requiring full MapReduce daemons | Provides partitioned external/managed Parquet/ORC warehouse tables |
| **Apache Hadoop / Storage Layer** | Hadoop 3.3.6 Client / Local FS / HDFS | Java 8/11 | N/A | Distributed storage layer for checkpoints and warehouse files | Compatible with Spark 3.5.x and Java 11 |
| **Scala** | 2.12.18 | Java 8/11/17 | N/A | Exact compiler version used by Spark 3.5.x | Strictly required if building custom GraphX Scala tasks |

---

## 2. Cross-Component Verification Rationale

1. **Java 11 as the Universal Standard:**
   - Spark 3.5.x officially deprecates Java 8 and recommends Java 11 or 17.
   - Kafka 3.7.0 runs natively on Java 11.
   - Hadoop 3.3.6 has complete production support for Java 11.
   - Both OpenJDK 8 and OpenJDK 11 are already pre-installed in `/usr/lib/jvm/` in the WSL2 Ubuntu environment. Setting `JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64` creates zero disruption and requires no third-party PPA installation.

2. **Python 3.12 Compatibility:**
   - Host Windows runs Python 3.14.3, which causes syntax and worker serialization failures in PySpark 3.5.x.
   - WSL2 Ubuntu 24.04 ships with Python 3.12.3, which is 100% compatible with PySpark 3.5.x.

3. **Apache Kafka KRaft Mode:**
   - In Kafka 3.x, KRaft (Kafka Raft Metadata mode) is production-ready.
   - Eliminates Apache ZooKeeper, reducing JVM processes from 2 to 1 and saving $\ge 512$ MB RAM on the host.

4. **Hive Integration via Spark SQL:**
   - Rather than launching a full Apache Hive daemon with YARN and Tez, Spark 3.5.x includes built-in Hive Metastore support.
   - Allows full SQL DDL/DML, partition pruning, and Parquet/ORC table management conforming strictly to the course Hive warehouse requirement with zero daemon instability.
