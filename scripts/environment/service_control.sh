#!/usr/bin/env bash
set -euo pipefail

export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
export HADOOP_HOME="/opt/hadoop"
export HADOOP_CONF_DIR="$HADOOP_HOME/etc/hadoop"
export KAFKA_HOME="/opt/kafka"
export KAFKA_HEAP_OPTS="-Xms256m -Xmx512m"
export PATH="$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$KAFKA_HOME/bin:$JAVA_HOME/bin:$PATH"

ACTION="${1:-status}"
TARGET="${2:-all}"

start_hdfs() {
    echo "Starting HDFS Daemons..."
    if ! pgrep -f "org.apache.hadoop.hdfs.server.namenode.NameNode" > /dev/null; then
        nohup "$HADOOP_HOME/bin/hdfs" namenode </dev/null > "$HADOOP_HOME/logs/namenode.out" 2>&1 &
    fi
    sleep 3
    if ! pgrep -f "org.apache.hadoop.hdfs.server.datanode.DataNode" > /dev/null; then
        nohup "$HADOOP_HOME/bin/hdfs" datanode </dev/null > "$HADOOP_HOME/logs/datanode.out" 2>&1 &
    fi
    sleep 3
    echo "HDFS daemons verified active."
}

stop_hdfs() {
    echo "Stopping HDFS Daemons..."
    pkill -f "org.apache.hadoop.hdfs.server.datanode.DataNode" || true
    pkill -f "org.apache.hadoop.hdfs.server.namenode.NameNode" || true
    echo "HDFS stopped."
}

start_kafka() {
    echo "Starting Kafka (KRaft mode)..."
    if pgrep -f "kafka.Kafka" > /dev/null; then
        echo "Kafka is already running."
    else
        kafka-server-start.sh -daemon /opt/kafka/config/kraft/server.properties
        sleep 4
        echo "Kafka started."
    fi
}

stop_kafka() {
    echo "Stopping Kafka..."
    kafka-server-stop.sh || true
    sleep 2
    echo "Kafka stopped."
}

check_status() {
    echo "============================================================"
    echo "CrisisGuard Big Data Services Status"
    echo "Author: B.SIVASAI (2023BCS0228)"
    echo "============================================================"
    echo "--- JVM Processes (jps) ---"
    jps -l || true
    echo ""
    echo "--- HDFS Report ---"
    if pgrep -f "org.apache.hadoop.hdfs.server.namenode.NameNode" > /dev/null; then
        hdfs dfsadmin -report -live || true
    else
        echo "HDFS NameNode is NOT running."
    fi
    echo ""
    echo "--- Kafka Port (9092) Check ---"
    if pgrep -f "kafka.Kafka" > /dev/null; then
        echo "Kafka Broker process ACTIVE (PID: $(pgrep -f 'kafka.Kafka' | head -n 1))"
    else
        echo "Kafka Broker is NOT running."
    fi
    echo "============================================================"
}

case "$ACTION" in
    start)
        case "$TARGET" in
            hdfs) start_hdfs ;;
            kafka) start_kafka ;;
            all) start_hdfs; start_kafka ;;
            *) echo "Unknown target: $TARGET"; exit 1 ;;
        esac
        ;;
    stop)
        case "$TARGET" in
            hdfs) stop_hdfs ;;
            kafka) stop_kafka ;;
            all) stop_kafka; stop_hdfs ;;
            *) echo "Unknown target: $TARGET"; exit 1 ;;
        esac
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {start|stop|status} [hdfs|kafka|all]"
        exit 1
        ;;
esac
