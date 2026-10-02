import urllib.request

mirrors = [
    "https://dlcdn.apache.org/",
    "https://ftp.osuosl.org/pub/apache/",
    "https://mirrors.gigenet.com/apache/",
    "https://mirror.cogentco.com/pub/apache/",
    "https://mirrors.sonic.net/apache/",
    "https://archive.cloudera.com/",
    "https://repo1.maven.org/maven2/",
]

for m in mirrors:
    try:
        req = urllib.request.Request(m, headers={'User-Agent': 'curl/8.5.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f"REACHABLE: {m} (status {resp.status})")
    except Exception as e:
        print(f"UNREACHABLE: {m} ({e})")
