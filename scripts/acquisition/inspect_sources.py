import urllib.request
import urllib.parse
import re

url = "https://crisisnlp.qcri.org/humaid_dataset.html"
headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request(url, headers=headers)
html = urllib.request.urlopen(req).read().decode('utf-8')

for m in re.finditer(r'<a\s+[^>]*?href=[\'"](.*?)[\'"][^>]*?>(.*?)</a>', html, re.I):
    href, text = m.group(1), m.group(2)
    if any(k in href.lower() for k in ['zip', 'tar', 'gz', 'humaid']):
        full = urllib.parse.urljoin(url, href)
        try:
            r = urllib.request.Request(full, headers=headers, method='HEAD')
            with urllib.request.urlopen(r, timeout=5) as resp:
                print(f"[FOUND {resp.status}] {full} ({resp.headers.get('Content-Length')} bytes)")
        except Exception as e:
            print(f"[ERR] {full} -> {e}")
