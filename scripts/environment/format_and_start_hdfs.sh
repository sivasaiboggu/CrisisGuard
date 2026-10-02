#!/usr/bin/env bash
set -euo pipefail

export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
export HADOOP_HOME="/opt/hadoop"
export HADOOP_CONF_DIR="$HADOOP_HOME/etc/hadoop"
export PATH="$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$JAVA_HOME/bin:$PATH"

echo "=== Initializing HDFS NameNode ==="
if [ ! -d "/var/crisisguard/hdfs/namenode/current" ]; then
    echo "Formatting NameNode..."
    hdfs namenode -format -force -nonInteractive
else
    echo "NameNode already formatted."
fi

echo "=== Starting HDFS Daemons ==="
# Stop any existing daemons first
hdfs --daemon stop datanode || true
hdfs --daemon stop namenode || true
sleep 2

hdfs --daemon start namenode
hdfs --daemon start datanode
sleep 5

echo "=== HDFS Daemon Status (jps) ==="
jps | grep -E "NameNode|DataNode" || true

echo "=== HDFS Cluster Report ==="
hdfs dfsadmin -report | head -n 25 || true

echo "=== Creating Logical Directory Structure ==="
hdfs dfs -mkdir -p /crisisguard
hdfs dfs -mkdir -p /crisisguard/raw
hdfs dfs -mkdir -p /crisisguard/processed
hdfs dfs -mkdir -p /crisisguard/test

hdfs dfs -ls -R /crisisguard
echo "HDFS Initialization Complete: PASS"
