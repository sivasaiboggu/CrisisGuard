# CrisisGuard: Phase 5 Resource Configuration & Capacity Allocation

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  

---

## 1. Physical Hardware & WSL2 Virtualization Baseline

The CrisisGuard Big Data environment executes on a single-node development workstation constrained by physical hardware:

* **Host Machine:** AMD Ryzen 7 7445HS (6 Physical Cores / 12 Logical Processors)
* **Host Physical Memory:** 16 GB DDR5 RAM
* **Virtualization Hypervisor:** WSL2 (Hyper-V lightweight VM)
* **WSL2 Allocated Memory Limit:** 7.4 GiB (configured via `.wslconfig` default 50% physical RAM)
* **WSL2 Available Headroom:** ~6.3 GiB unallocated at baseline idle
* **WSL2 Primary Storage:** `/dev/sdd` ext4 native filesystem (943 GiB free space)

---

## 2. Conservative Multi-Daemon Allocation Strategy

To ensure absolute system stability without exhausting physical host RAM or causing out-of-memory (OOM) kernel panics, all Big Data daemons are tuned for lean, single-node development execution:

| Component | Service / Process | Memory Allocation (Min/Max) | vCPU Limit | Native Storage Location |
| :--- | :--- | :---: | :---: | :--- |
| **HDFS NameNode** | Java JVM Daemon | 256 MB / 512 MB | Shared | `/var/crisisguard/hdfs/namenode` |
| **HDFS DataNode** | Java JVM Daemon | 256 MB / 512 MB | Shared | `/var/crisisguard/hdfs/datanode` |
| **Hadoop Tmp / Block Buffer**| Local scratch buffer | In-memory cache + disk | Shared | `/var/crisisguard/hadoop_tmp` |
| **Apache Kafka Broker** | KRaft Combined Broker/Controller | 256 MB / 512 MB | Shared | `/var/crisisguard/kafka-logs` |
| **Apache Hive Metastore** | Embedded Derby Metastore / CLI | 256 MB / 512 MB | Shared | `/var/crisisguard/hive/metastore_db` |
| **Apache Spark Driver** | PySpark / SparkSubmit master | 512 MB / 1024 MB | 2 cores (`local[2]`) | `/tmp/spark-scratch` |
| **Apache Spark Executor** | Local worker thread pool | 512 MB / 1024 MB | 2 threads | In-process execution |
| **Total Peak Footprint** | All services running concurrently | **~3.5 GiB max** | 4 threads max | Native Linux ext4 |

---

## 3. Component-Specific Tuning Directives

### 3.1 Apache Hadoop / HDFS Tuning
* Configuration file: `$HADOOP_HOME/etc/hadoop/hadoop-env.sh`
* Parameters:
  ```bash
  export HADOOP_HEAPSIZE_MAX=512m
  export HADOOP_NAMENODE_OPTS="-Xms256m -Xmx512m"
  export HADOOP_DATANODE_OPTS="-Xms256m -Xmx512m"
  ```
* HDFS block replication is set to `1` (`dfs.replication = 1`) to eliminate inter-node block traffic.

### 3.2 Apache Kafka (KRaft Mode) Tuning
* Configuration file: `$KAFKA_HOME/config/kraft/server.properties`
* Environment variable:
  ```bash
  export KAFKA_HEAP_OPTS="-Xms256m -Xmx512m"
  ```
* ZooKeeper is completely omitted, conserving ~500 MB RAM.
* Single partition per smoke topic (`--partitions 1 --replication-factor 1`).

### 3.3 Apache Spark Tuning
* Configuration file: `$SPARK_HOME/conf/spark-defaults.conf` (or programmatic in `SparkSession.builder`):
  ```properties
  spark.master                     local[2]
  spark.driver.memory              1g
  spark.executor.memory            1g
  spark.sql.shuffle.partitions     4
  spark.default.parallelism        2
  ```
* `spark.sql.shuffle.partitions` is reduced from default `200` to `4` for local micro-batches, preventing JVM garbage collection overhead on small test tables.

### 3.4 Storage Isolation
To avoid Windows 9p filesystem bridge latency (`/mnt/c/`), all runtime logs, block stores, and metastores are located on Linux native ext4 partitions:
* `/var/crisisguard/hdfs/`
* `/var/crisisguard/kafka-logs/`
* `/var/crisisguard/hive/`
* `/var/crisisguard/hadoop_tmp/`
