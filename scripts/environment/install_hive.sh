#!/usr/bin/env bash
set -euo pipefail

HIVE_VERSION="3.1.3"
HIVE_PKG="apache-hive-${HIVE_VERSION}-bin"
HIVE_URL="https://web.archive.org/web/20240401000000id_/https://archive.apache.org/dist/hive/hive-${HIVE_VERSION}/${HIVE_PKG}.tar.gz"
INSTALL_BASE="/opt"
HIVE_DIR="${INSTALL_BASE}/${HIVE_PKG}"
HIVE_LINK="${INSTALL_BASE}/hive"
HIVE_DATA="/var/crisisguard/hive"

echo "=== Installing Apache Hive ${HIVE_VERSION} ==="

mkdir -p "$HIVE_DATA"
chmod -R 777 "$HIVE_DATA"

TARBALL="/var/crisisguard/downloads/${HIVE_PKG}.tar.gz"

if [ ! -d "$HIVE_DIR" ]; then
    if [ ! -f "$TARBALL" ]; then
        echo "Downloading Hive ${HIVE_VERSION}..."
        curl -fsSL "$HIVE_URL" -o "$TARBALL"
    fi
    echo "Extracting Hive to ${INSTALL_BASE}..."
    tar -xzf "$TARBALL" -C "$INSTALL_BASE"
fi

ln -sfn "$HIVE_DIR" "$HIVE_LINK"

# Fix Guava conflict: Hive 3.1.3 ships guava-19.0, Hadoop 3.3.6 requires guava-27.0-jre
if [ -f "${HIVE_LINK}/lib/guava-19.0.jar" ]; then
    echo "Replacing guava-19.0.jar with Hadoop 3.3.6 guava-27.0-jre.jar..."
    rm -f "${HIVE_LINK}/lib/guava-19.0.jar"
    if [ -f "/opt/hadoop/share/hadoop/common/lib/guava-27.0-jre.jar" ]; then
        cp "/opt/hadoop/share/hadoop/common/lib/guava-27.0-jre.jar" "${HIVE_LINK}/lib/"
    fi
fi

# Configure hive-site.xml
cat << 'EOF' > "${HIVE_LINK}/conf/hive-site.xml"
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:derby:;databaseName=/var/crisisguard/hive/metastore_db;create=true</value>
        <description>JDBC connect string for a JDBC metastore</description>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionDriverName</name>
        <value>org.apache.derby.jdbc.EmbeddedDriver</value>
        <description>Driver class name for a JDBC metastore</description>
    </property>
    <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>/crisisguard/warehouse</value>
        <description>location of default database for the warehouse</description>
    </property>
    <property>
        <name>hive.metastore.schema.verification</name>
        <value>false</value>
    </property>
    <property>
        <name>datanucleus.schema.autoCreateAll</name>
        <value>true</value>
    </property>
</configuration>
EOF

# Symlink binaries
ln -sfn "${HIVE_LINK}/bin/hive" "/usr/local/bin/hive"
ln -sfn "${HIVE_LINK}/bin/schematool" "/usr/local/bin/schematool"
ln -sfn "${HIVE_LINK}/bin/beeline" "/usr/local/bin/beeline"

echo "Hive ${HIVE_VERSION} installed successfully at ${HIVE_LINK}"
