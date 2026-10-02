import urllib.request

url = "https://web.archive.org/web/20240401000000id_/https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'curl/8.5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"Wayback Spark 3.5.1: SUCCESS (status={resp.status}, length={resp.headers.get('content-length')})")
except Exception as e:
    print(f"Wayback Spark 3.5.1: FAILED ({e})")
