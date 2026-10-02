# CrisisGuard: Phase 5 Environment Reproducibility Guide

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  

---

## 1. Prerequisites & Host Configuration

1. **Host Operating System:** Windows 11 with WSL2 enabled.
2. **WSL2 Substrate:** Ubuntu 24.04 LTS (`wsl --install -d Ubuntu-24.04`).
3. **Hardware Requirements:** Minimum 16 GB physical RAM, 4 CPU cores, 20 GB available disk space.

---

## 2. Automated Step-by-Step Installation

Clone the repository and execute installation scripts inside WSL2 Ubuntu terminal:

```bash
# 1. Update OS packages and install core build tools
sudo apt update && sudo apt install -y openjdk-11-jdk-headless python3 python3-pip python3-venv curl wget git

# 2. Configure Java 11 Alternatives & Environment
sudo update-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' | sudo tee -a /etc/profile.d/crisisguard_env.sh
echo 'export PATH=$JAVA_HOME/bin:$PATH' | sudo tee -a /etc/profile.d/crisisguard_env.sh
source /etc/profile.d/crisisguard_env.sh

# 3. Install Scala 2.12.18
sudo bash scripts/environment/install_scala.sh

# 4. Install Apache Hadoop 3.3.6 (HDFS)
sudo bash scripts/environment/install_hadoop.sh

# 5. Install Apache Spark 3.5.1
sudo bash scripts/environment/install_spark.sh

# 6. Install Apache Kafka 3.7.0 (KRaft)
sudo bash scripts/environment/install_kafka.sh

# 7. Install Apache Hive 3.1.3
sudo bash scripts/environment/install_hive.sh
```

---

## 3. Environment Variables Reference

Add the following to `/etc/profile.d/crisisguard_env.sh` or `~/.bashrc`:

```bash
export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
export SCALA_HOME="/opt/scala"
export HADOOP_HOME="/opt/hadoop"
export HADOOP_CONF_DIR="$HADOOP_HOME/etc/hadoop"
export SPARK_HOME="/opt/spark"
export KAFKA_HOME="/opt/kafka"
export HIVE_HOME="/opt/hive"
export PATH="$SPARK_HOME/bin:$KAFKA_HOME/bin:$HIVE_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SCALA_HOME/bin:$JAVA_HOME/bin:$PATH"
export KAFKA_HEAP_OPTS="-Xms256m -Xmx512m"
```

---

## 4. Service Lifecycle Operations

```bash
# Start all services (HDFS NameNode/DataNode + Kafka KRaft Broker)
bash scripts/environment/service_control.sh start all

# Check service operational health and ports
bash scripts/environment/service_control.sh status

# Stop all services cleanly
bash scripts/environment/service_control.sh stop all
```

---

## 5. Verification & Smoke Test Execution

Execute all individual and integration smoke tests:

```bash
# 1. Java 11 verification
bash scripts/environment/test_java.sh

# 2. Scala 2.12.18 verification
bash scripts/environment/test_scala.sh

# 3. HDFS single-node block storage verification
bash tests/integration/test_hdfs_smoke.sh

# 4. Spark local dataframe aggregation
python3 tests/integration/test_spark_local_smoke.py

# 5. Spark + HDFS real data integration
python3 tests/integration/test_spark_hdfs_smoke.py

# 6. Kafka producer, consumer, and real event streaming
python3 tests/integration/test_kafka_smoke.py

# 7. Hive DDL, DML, and processed data loading
python3 tests/integration/test_hive_smoke.py

# 8. Master Phase 5 environment validation
python3 scripts/validation/validate_phase5_environment.py
```

---

## 6. Troubleshooting Common Issues

1. **HDFS Port 9000 Connection Refused:**
   * Cause: NameNode failed to start or safe mode is active.
   * Fix: Check logs in `/opt/hadoop/logs/`. Format NameNode if not formatted (`hdfs namenode -format -force`). Wait 10 seconds for DataNode registration.
2. **Hive Guava NoSuchMethodError:**
   * Cause: Hive 3.1.3 ships `guava-19.0.jar` which conflicts with Hadoop 3.3.6.
   * Fix: Run `rm -f /opt/hive/lib/guava-19.0.jar && cp /opt/hadoop/share/hadoop/common/lib/guava-27.0-jre.jar /opt/hive/lib/`.
3. **Kafka Broker Fails to Start:**
   * Cause: Storage directory `/var/crisisguard/kafka-logs` missing meta.properties or port 9092 occupied.
   * Fix: Format cluster ID via `kafka-storage.sh format -t $(kafka-storage.sh random-uuid) -c /opt/kafka/config/kraft/server.properties`.
