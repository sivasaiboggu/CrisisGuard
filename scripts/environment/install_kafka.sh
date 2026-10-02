#!/usr/bin/env bash
set -euo pipefail

KAFKA_VERSION="3.7.0"
SCALA_VER="2.12"
KAFKA_PKG="kafka_${SCALA_VER}-${KAFKA_VERSION}"
KAFKA_URL="https://web.archive.org/web/20240401000000id_/https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/${KAFKA_PKG}.tgz"
INSTALL_BASE="/opt"
KAFKA_DIR="${INSTALL_BASE}/${KAFKA_PKG}"
KAFKA_LINK="${INSTALL_BASE}/kafka"
KAFKA_DATA="/var/crisisguard/kafka-logs"

echo "=== Installing Apache Kafka ${KAFKA_VERSION} ==="

mkdir -p "$KAFKA_DATA"
chmod -R 777 "$KAFKA_DATA"

if [ ! -d "$KAFKA_DIR" ]; then
    if [ ! -f "/tmp/${KAFKA_PKG}.tgz" ]; then
        echo "Downloading Kafka ${KAFKA_VERSION}..."
        curl -fsSL "$KAFKA_URL" -o "/tmp/${KAFKA_PKG}.tgz"
    fi
    echo "Extracting Kafka to ${INSTALL_BASE}..."
    tar -xzf "/tmp/${KAFKA_PKG}.tgz" -C "$INSTALL_BASE"
fi

ln -sfn "$KAFKA_DIR" "$KAFKA_LINK"

# Configure KRaft server.properties
KRAFT_CONFIG="${KAFKA_LINK}/config/kraft/server.properties"
sed -i 's|log.dirs=.*|log.dirs=/var/crisisguard/kafka-logs|' "$KRAFT_CONFIG"
sed -i 's|listeners=PLAINTEXT://:9092|listeners=PLAINTEXT://127.0.0.1:9092|' "$KRAFT_CONFIG"

# Symlink binaries
ln -sfn "${KAFKA_LINK}/bin/kafka-server-start.sh" "/usr/local/bin/kafka-server-start.sh"
ln -sfn "${KAFKA_LINK}/bin/kafka-server-stop.sh" "/usr/local/bin/kafka-server-stop.sh"
ln -sfn "${KAFKA_LINK}/bin/kafka-topics.sh" "/usr/local/bin/kafka-topics.sh"
ln -sfn "${KAFKA_LINK}/bin/kafka-console-producer.sh" "/usr/local/bin/kafka-console-producer.sh"
ln -sfn "${KAFKA_LINK}/bin/kafka-console-consumer.sh" "/usr/local/bin/kafka-console-consumer.sh"
ln -sfn "${KAFKA_LINK}/bin/kafka-storage.sh" "/usr/local/bin/kafka-storage.sh"

# Format KRaft cluster storage if meta.properties does not exist
if [ ! -f "${KAFKA_DATA}/meta.properties" ]; then
    echo "Generating KRaft Cluster ID and formatting storage..."
    CLUSTER_ID=$("${KAFKA_LINK}/bin/kafka-storage.sh" random-uuid)
    "${KAFKA_LINK}/bin/kafka-storage.sh" format -t "$CLUSTER_ID" -c "$KRAFT_CONFIG"
fi

echo "Kafka ${KAFKA_VERSION} installed and KRaft initialized at ${KAFKA_LINK}"
