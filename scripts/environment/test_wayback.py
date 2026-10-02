import urllib.request

test_urls = [
    ("Wayback Kafka 3.7.0", "https://web.archive.org/web/20240401000000id_/https://archive.apache.org/dist/kafka/3.7.0/kafka_2.12-3.7.0.tgz"),
    ("Wayback Hive 3.1.3", "https://web.archive.org/web/20240401000000id_/https://archive.apache.org/dist/hive/hive-3.1.3/apache-hive-3.1.3-bin.tar.gz"),
]

for name, url in test_urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/8.5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            print(f"{name}: SUCCESS (status={resp.status}, length={resp.headers.get('content-length')})")
    except Exception as e:
        print(f"{name}: FAILED ({e})")
