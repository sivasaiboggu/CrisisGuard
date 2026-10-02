import urllib.request

url = "https://downloads.apache.org/kafka/3.7.0/kafka_2.12-3.7.0.tgz"
print(f"Testing {url}...")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"SUCCESS: status={resp.status}, length={resp.headers.get('content-length')}")
except Exception as e:
    print(f"FAILED: {e}")
