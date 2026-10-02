#!/usr/bin/env bash
set -euo pipefail

SCALA_VERSION="2.12.18"
SCALA_URL="https://downloads.lightbend.com/scala/${SCALA_VERSION}/scala-${SCALA_VERSION}.tgz"
INSTALL_BASE="/opt"
SCALA_DIR="${INSTALL_BASE}/scala-${SCALA_VERSION}"
SCALA_LINK="${INSTALL_BASE}/scala"

if [ ! -d "$SCALA_DIR" ]; then
    echo "Downloading Scala ${SCALA_VERSION}..."
    curl -fsSL "$SCALA_URL" -o "/tmp/scala-${SCALA_VERSION}.tgz"
    echo "Extracting to ${INSTALL_BASE}..."
    tar -xzf "/tmp/scala-${SCALA_VERSION}.tgz" -C "$INSTALL_BASE"
    rm -f "/tmp/scala-${SCALA_VERSION}.tgz"
fi

ln -sfn "$SCALA_DIR" "$SCALA_LINK"
ln -sfn "$SCALA_LINK/bin/scala" "/usr/local/bin/scala"
ln -sfn "$SCALA_LINK/bin/scalac" "/usr/local/bin/scalac"

echo "Scala ${SCALA_VERSION} installed successfully at ${SCALA_LINK}"
