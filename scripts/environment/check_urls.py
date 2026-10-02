import urllib.request

urls = [
    ("Hadoop 3.3.6 Archive", "https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz"),
    ("Hadoop 3.3.6 CDN", "https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz"),
    ("Spark 3.5.1 Archive", "https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz"),
    ("Spark 3.5.1 CDN", "https://dlcdn.apache.org/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz"),
    ("Kafka 3.7.0 Archive", "https://archive.apache.org/dist/kafka/3.7.0/kafka_2.12-3.7.0.tgz"),
    ("Hive 3.1.3 Archive", "https://archive.apache.org/dist/hive/hive-3.1.3/apache-hive-3.1.3-bin.tar.gz"),
]

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Wget/1.21.4'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"{name}: status={resp.status}, length={resp.headers.get('content-length')} bytes")
    except Exception as e:
        print(f"{name}: ERROR - {e}")
