#!/usr/bin/env bash
set -euo pipefail

export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
export HADOOP_HOME="/opt/hadoop"
export HADOOP_CONF_DIR="$HADOOP_HOME/etc/hadoop"
export PATH="$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$JAVA_HOME/bin:$PATH"

TEST_FILE="/tmp/hdfs_smoke_test.txt"
HDFS_TARGET="/crisisguard/test/hdfs_smoke_test.txt"

echo "=== Preparing Local Test File ==="
cat << 'EOF' > "$TEST_FILE"
CrisisGuard HDFS Integration Smoke Test
Author: B.SIVASAI
Roll Number: 2023BCS0228
Course: CSE412 Big Data & Large-Scale Computing
Timestamp: $(date -u)
Payload: HDFS Block Storage Operational
EOF

echo "=== Uploading to HDFS: $HDFS_TARGET ==="
hdfs dfs -rm -f "$HDFS_TARGET" 2>/dev/null || true
hdfs dfs -put "$TEST_FILE" "$HDFS_TARGET"

echo "=== Listing HDFS File Metadata ==="
hdfs dfs -ls "$HDFS_TARGET"

echo "=== Reading Content from HDFS ==="
READ_OUTPUT=$(hdfs dfs -cat "$HDFS_TARGET")
echo "$READ_OUTPUT"

if echo "$READ_OUTPUT" | grep -q "2023BCS0228"; then
    echo "HDFS Smoke Test: PASS"
else
    echo "HDFS Smoke Test: FAIL (Author roll number not found in read output)"
    exit 1
fi

rm -f "$TEST_FILE"
