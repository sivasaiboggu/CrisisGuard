# CrisisGuard: Phase 5 Service Management & Operational Runbook

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  

---

## 1. Service Architecture & Dependencies

The CrisisGuard local single-node Big Data environment consists of four interconnected service tiers:

```
[HDFS NameNode (9000)] & [HDFS DataNode (9866)]
                       ▲
                       │ Storage & Block Management
                       │
             [Apache Spark 3.5.1]
             (Local Driver/Executors)
                       ▲
                       │ Ingestion & Streaming
                       │
         [Apache Kafka 3.7.0 Broker (9092)]
         (KRaft Controller Quorum: 9093)
                       ▲
                       │ Warehousing
                       │
       [Apache Hive 3.1.3 Embedded Metastore]
```

### Dependency Ordering:
1. **Startup Order:**
   - Step 1: HDFS (NameNode then DataNode)
   - Step 2: Kafka Broker (KRaft mode; self-managed metadata)
   - Step 3: Spark Session / Jobs (connects to HDFS `hdfs://127.0.0.1:9000` and Kafka `127.0.0.1:9092`)
   - Step 4: Hive Metastore / Spark-Hive Warehouse
2. **Shutdown Order:**
   - Step 1: Spark Jobs / Client sessions
   - Step 2: Kafka Broker (`kafka-server-stop.sh`)
   - Step 3: HDFS Daemons (`hdfs --daemon stop datanode; hdfs --daemon stop namenode`)

---

## 2. Service Management Operations

### 2.1 Automated Service Control Script
A centralized service management script is located at `scripts/environment/service_control.sh`.

```bash
# Start all services (HDFS + Kafka)
bash scripts/environment/service_control.sh start all

# Check operational status of all services
bash scripts/environment/service_control.sh status

# Stop all services cleanly
bash scripts/environment/service_control.sh stop all
```

### 2.2 Granular Manual Service Commands

| Component | Operation | Exact CLI Command | Process Name (jps) | Ports |
| :--- | :--- | :--- | :--- | :---: |
| **HDFS NameNode** | Start | `hdfs --daemon start namenode` | `NameNode` | 9000 (IPC), 9870 (Web UI) |
| | Stop | `hdfs --daemon stop namenode` | — | — |
| | Status | `hdfs dfsadmin -report` | — | — |
| **HDFS DataNode** | Start | `hdfs --daemon start datanode` | `DataNode` | 9866 (Data), 9864 (Web UI) |
| | Stop | `hdfs --daemon stop datanode` | — | — |
| **Apache Kafka** | Start | `kafka-server-start.sh -daemon /opt/kafka/config/kraft/server.properties` | `Kafka` | 9092 (PLAINTEXT), 9093 (KRaft) |
| | Stop | `kafka-server-stop.sh` | — | — |
| | Status | `kafka-topics.sh --bootstrap-server 127.0.0.1:9092 --list` | — | — |
| **Apache Hive** | Metastore Init | `schematool -dbType derby -initSchema` | — | Embedded JDBC Derby |
| | CLI Interactive| `hive` | `CliDriver` | — |
| | Query Test | `hive -e "SHOW TABLES;"` | — | — |

---

## 3. Storage and Log Cleanup

Temporary and diagnostic logs are segregated to avoid disk pollution:
* Hadoop Logs: `/opt/hadoop/logs/`
* Kafka Logs: `/var/crisisguard/kafka-logs/`
* Hive Metastore: `/var/crisisguard/hive/metastore_db/`
* Spark Scratch: `/tmp/spark-scratch/`
