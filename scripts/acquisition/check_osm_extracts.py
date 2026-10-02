import urllib.request
import re

url = "https://download.geofabrik.de/asia/india.html"
headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request(url, headers=headers)
html = urllib.request.urlopen(req).read().decode('utf-8')
links = re.findall(r'href=[\'"](.*?-latest\.osm\.pbf)[\'"]', html)
for l in sorted(set(links)):
    print(l)
