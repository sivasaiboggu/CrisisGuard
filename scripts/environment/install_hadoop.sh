#!/usr/bin/env bash
set -euo pipefail

HADOOP_VERSION="3.3.6"
HADOOP_URL="https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"
INSTALL_BASE="/opt"
HADOOP_DIR="${INSTALL_BASE}/hadoop-${HADOOP_VERSION}"
HADOOP_LINK="${INSTALL_BASE}/hadoop"
DATA_DIR="/var/crisisguard"

echo "=== Installing Hadoop ${HADOOP_VERSION} ==="

mkdir -p "$DATA_DIR/hadoop_tmp" "$DATA_DIR/hdfs/namenode" "$DATA_DIR/hdfs/datanode"
chmod -R 777 "$DATA_DIR"

if [ ! -d "$HADOOP_DIR" ]; then
    echo "Downloading Hadoop ${HADOOP_VERSION}..."
    curl -fsSL "$HADOOP_URL" -o "/tmp/hadoop-${HADOOP_VERSION}.tar.gz"
    echo "Extracting Hadoop to ${INSTALL_BASE}..."
    tar -xzf "/tmp/hadoop-${HADOOP_VERSION}.tar.gz" -C "$INSTALL_BASE"
    rm -f "/tmp/hadoop-${HADOOP_VERSION}.tar.gz"
fi

ln -sfn "$HADOOP_DIR" "$HADOOP_LINK"

# Configure hadoop-env.sh
sed -i 's|^# export JAVA_HOME=.*|export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64|' "${HADOOP_LINK}/etc/hadoop/hadoop-env.sh"
if ! grep -q "JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" "${HADOOP_LINK}/etc/hadoop/hadoop-env.sh"; then
    echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> "${HADOOP_LINK}/etc/hadoop/hadoop-env.sh"
fi

# Configure core-site.xml
cat << 'EOF' > "${HADOOP_LINK}/etc/hadoop/core-site.xml"
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://127.0.0.1:9000</value>
    </property>
    <property>
        <name>hadoop.tmp.dir</name>
        <value>/var/crisisguard/hadoop_tmp</value>
    </property>
</configuration>
EOF

# Configure hdfs-site.xml
cat << 'EOF' > "${HADOOP_LINK}/etc/hadoop/hdfs-site.xml"
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///var/crisisguard/hdfs/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///var/crisisguard/hdfs/datanode</value>
    </property>
    <property>
        <name>dfs.permissions.enabled</name>
        <value>false</value>
    </property>
</configuration>
EOF

# Symlink binaries
ln -sfn "${HADOOP_LINK}/bin/hadoop" "/usr/local/bin/hadoop"
ln -sfn "${HADOOP_LINK}/bin/hdfs" "/usr/local/bin/hdfs"

echo "Hadoop ${HADOOP_VERSION} installed and configured successfully at ${HADOOP_LINK}"
