import urllib.request
import re

for base in ["https://mirror.cogentco.com/pub/apache/"]:
    for proj in ["spark/", "kafka/", "hive/"]:
        url = base + proj
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'curl/8.5.0'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                links = [l for l in re.findall(r'href="([^"]+)"', html) if not l.startswith('?') and not l.startswith('/')]
                print(f"=== {url} ===")
                print(links[:15])
        except Exception as e:
            print(f"Error {url}: {e}")
