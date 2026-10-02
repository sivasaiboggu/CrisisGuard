import urllib.request

test_urls = [
    ("Hadoop 3.3.6 dlcdn", "https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz"),
    ("Spark archive HTTP", "http://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz"),
    ("Spark archive HTTPS", "https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz"),
    ("Kafka 3.7.0 archive HTTP", "http://archive.apache.org/dist/kafka/3.7.0/kafka_2.12-3.7.0.tgz"),
    ("Hive 3.1.3 archive HTTP", "http://archive.apache.org/dist/hive/hive-3.1.3/apache-hive-3.1.3-bin.tar.gz"),
]

for name, url in test_urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/8.5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"{name}: SUCCESS (status={resp.status}, length={resp.headers.get('content-length')})")
    except Exception as e:
        print(f"{name}: FAILED ({e})")
