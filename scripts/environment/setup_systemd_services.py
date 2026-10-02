import os

hdfs_nn = """[Unit]
Description=Hadoop HDFS NameNode
After=network.target

[Service]
Type=simple
User=sivasai
Environment=JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
Environment=HADOOP_HOME=/opt/hadoop
Environment=HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ExecStart=/opt/hadoop/bin/hdfs namenode
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

hdfs_dn = """[Unit]
Description=Hadoop HDFS DataNode
After=hdfs-namenode.service

[Service]
Type=simple
User=sivasai
Environment=JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
Environment=HADOOP_HOME=/opt/hadoop
Environment=HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ExecStart=/opt/hadoop/bin/hdfs datanode
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

kafka_svc = """[Unit]
Description=Apache Kafka Distributed Message Broker (KRaft)
After=network.target

[Service]
Type=simple
User=sivasai
Environment=JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
Environment=KAFKA_HEAP_OPTS=-Xms256m -Xmx512m
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/kraft/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

with open("/etc/systemd/system/hdfs-namenode.service", "w") as f:
    f.write(hdfs_nn)
with open("/etc/systemd/system/hdfs-datanode.service", "w") as f:
    f.write(hdfs_dn)
with open("/etc/systemd/system/kafka.service", "w") as f:
    f.write(kafka_svc)

print("Systemd service files written successfully.")
