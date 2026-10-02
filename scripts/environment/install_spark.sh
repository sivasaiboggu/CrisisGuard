#!/usr/bin/env bash
set -euo pipefail

SPARK_VERSION="3.5.1"
INSTALL_BASE="/opt"
SPARK_VENV="${INSTALL_BASE}/spark_env"
SPARK_LINK="${INSTALL_BASE}/spark"

TARBALL="/var/crisisguard/downloads/pyspark-${SPARK_VERSION}.tar.gz"

echo "=== Installing Apache Spark ${SPARK_VERSION} via PySpark Distribution ==="

if [ -f "$TARBALL" ]; then
    echo "Installing from local archive: $TARBALL..."
    pip install "$TARBALL" --break-system-packages
else
    echo "Installing pyspark==${SPARK_VERSION} via pip..."
    pip install "pyspark==${SPARK_VERSION}" --break-system-packages
fi

PYSPARK_PKG_DIR=$(python3 -c "import pyspark, os; print(os.path.dirname(pyspark.__file__))")
echo "Found PySpark distribution at: ${PYSPARK_PKG_DIR}"

ln -sfn "$PYSPARK_PKG_DIR" "$SPARK_LINK"

# Symlink binaries to /usr/local/bin
ln -sfn "$SPARK_LINK/bin/spark-submit" "/usr/local/bin/spark-submit"
ln -sfn "$SPARK_LINK/bin/pyspark" "/usr/local/bin/pyspark"
ln -sfn "$SPARK_LINK/bin/spark-shell" "/usr/local/bin/spark-shell"

echo "Apache Spark ${SPARK_VERSION} successfully linked to ${SPARK_LINK}"
