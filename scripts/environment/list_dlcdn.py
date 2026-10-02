import urllib.request
import re

def list_dlcdn_path(path):
    url = f"https://dlcdn.apache.org/{path}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href="([^"]+)"', html)
            print(f"=== {url} ===")
            print([l for l in links if not l.startswith('?') and not l.startswith('/')][:15])
    except Exception as e:
        print(f"Error {url}: {e}")

list_dlcdn_path("hadoop/common/")
list_dlcdn_path("spark/")
list_dlcdn_path("kafka/")
list_dlcdn_path("hive/")
