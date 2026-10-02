# CrisisGuard: Phase 5 Big Data Environment Manifest

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  

---

## 1. Specification & Topology Summary

| Dimension | Specification Parameter | Configured Value |
| :--- | :--- | :--- |
| **Host System** | Operating System | Microsoft Windows 11 Home Single Language (Build 10.0.26200) |
| | Physical Processor | AMD Ryzen 7 7445HS (6 Cores / 12 Threads) |
| | Host RAM / Windows Disk | 16 GB DDR5 / 237 GB Free on `C:\` |
| **Virtualization** | WSL2 Linux Distribution | Ubuntu 24.04.4 LTS (Noble Numbat) |
| | Kernel Version | Linux 6.6.87.2-microsoft-standard-WSL2 x86_64 |
| | WSL Memory / Disk Space | 7.4 GiB Allocated (6.3 GiB Free) / 943 GiB Free on `/dev/sdd` |
| **Core Runtimes** | Java Development Kit | OpenJDK 11.0.31 (`/usr/lib/jvm/java-11-openjdk-amd64`) |
| | Python Runtime | Python 3.12.3 (`/usr/bin/python3`) |
| | Scala Runtime | Scala 2.12.18 (`/opt/scala`, binary compatible with Spark 3.5.1) |
| **Big Data Platform** | Distributed Storage | Apache Hadoop 3.3.6 HDFS (`hdfs://127.0.0.1:9000`) |
| | Stream & Batch Processing | Apache Spark 3.5.1 (`/opt/spark`, `local[2]`, PySpark 3.5.1) |
| | Distributed Messaging | Apache Kafka 3.7.0 (`127.0.0.1:9092`, KRaft Metadata Mode) |
| | Analytical Data Warehouse | Apache Hive 3.1.3 (`/opt/hive`, Embedded Derby Metastore) |

---

## 2. Port & Network Protocol Allocations

| Component | Port | Interface | Protocol | Description |
| :--- | :---: | :---: | :---: | :--- |
| **HDFS NameNode IPC** | `9000` | `127.0.0.1` | Protobuf / RPC | Primary HDFS client filesystem access |
| **HDFS NameNode Web UI** | `9870` | `0.0.0.0` | HTTP | Cluster health and NameNode diagnostics |
| **HDFS DataNode Transfer** | `9866` | `127.0.0.1` | TCP Streaming | Block data read / write streaming |
| **HDFS DataNode Web UI** | `9864` | `0.0.0.0` | HTTP | Local block health diagnostics |
| **Kafka Broker PLAINTEXT**| `9092` | `127.0.0.1` | Kafka TCP Wire | Producer and consumer streaming event exchange |
| **Kafka KRaft Controller** | `9093` | `127.0.0.1` | Kafka Raft RPC | Metadata quorum consensus |
| **Spark Driver UI** | `4040` | `0.0.0.0` | HTTP | Spark active job, stage, and task visualization |
