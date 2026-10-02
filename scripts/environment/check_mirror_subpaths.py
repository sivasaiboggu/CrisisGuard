import urllib.request
import re

for base in ["https://mirrors.sonic.net/apache/", "https://mirror.cogentco.com/pub/apache/"]:
    for sub in ["hadoop/common/hadoop-3.3.6/", "spark/spark-3.5.1/", "kafka/3.7.0/", "hive/hive-3.1.3/"]:
        url = base + sub
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'curl/8.5.0'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                print(f"FOUND: {url}")
        except Exception as e:
            print(f"NOT FOUND: {url} ({e})")
