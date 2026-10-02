import urllib.request

asian_mirrors = [
    "https://mirrors.tuna.tsinghua.edu.cn/apache/",
    "https://mirrors.ustc.edu.cn/apache/",
    "https://mirror.navercorp.com/apache/",
    "https://ftp.jaist.ac.jp/pub/apache/",
    "https://archive.apache.org/",
]

for m in asian_mirrors:
    try:
        req = urllib.request.Request(m, headers={'User-Agent': 'curl/8.5.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f"REACHABLE: {m} (status {resp.status})")
    except Exception as e:
        print(f"FAILED: {m} ({e})")
