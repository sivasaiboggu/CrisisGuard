import urllib.request
import re

for proj in ["spark/", "kafka/", "hive/"]:
    url = f"https://dlcdn.apache.org/{proj}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/8.5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href="([^"]+)"', html)
            print(f"=== {url} ===")
            print([l for l in links if not l.startswith('?') and not l.startswith('/')])
    except Exception as e:
        print(f"Error {url}: {e}")
