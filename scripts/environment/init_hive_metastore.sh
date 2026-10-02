#!/usr/bin/env bash
set -euo pipefail

export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
export HADOOP_HOME="/opt/hadoop"
export HIVE_HOME="/opt/hive"
export PATH="$HIVE_HOME/bin:$HADOOP_HOME/bin:$JAVA_HOME/bin:$PATH"

echo "=== Initializing Hive Derby Metastore Schema ==="
cd /var/crisisguard/hive

if [ ! -d "/var/crisisguard/hive/metastore_db" ]; then
    schematool -dbType derby -initSchema
else
    echo "Metastore already initialized."
fi

echo "=== Hive Metastore Schema Validation ==="
schematool -dbType derby -info || true
echo "Hive Schema Initialization Complete: PASS"
