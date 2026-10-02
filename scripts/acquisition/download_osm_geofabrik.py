#!/usr/bin/env python3
"""
CrisisGuard: OpenStreetMap Geofabrik Regional Extract Downloader
Author: B.SIVASAI (Roll No: 2023BCS0228)

Acquires the official Geofabrik Southern Zone India regional road extract (.osm.pbf)
covering the Southern India disaster zones (Kerala, Tamil Nadu, Andhra Pradesh, Karnataka, Telangana).
"""

import os
import sys
import urllib.request
from pathlib import Path

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CrisisGuard-OSM-Downloader'}

def download_osm(target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    base_url = "https://download.geofabrik.de/asia/india/southern-zone-latest.osm.pbf"
    md5_url = "https://download.geofabrik.de/asia/india/southern-zone-latest.osm.pbf.md5"
    
    pbf_dest = target_dir / "southern-zone-latest.osm.pbf"
    md5_dest = target_dir / "southern-zone-latest.osm.pbf.md5"

    # Download MD5 first
    print(f"Downloading MD5 checksum: {md5_url}")
    req = urllib.request.Request(md5_url, headers=headers)
    with urllib.request.urlopen(req) as resp, open(md5_dest, 'wb') as f:
        f.write(resp.read())
    print(f"  [OK] Saved MD5 ({md5_dest.stat().st_size} bytes)")

    if pbf_dest.exists() and pbf_dest.stat().st_size > 500 * 1024 * 1024:
        print(f"  [OK] {pbf_dest.name} already exists ({pbf_dest.stat().st_size} bytes). Skipping re-download.")
        return

    print(f"Downloading regional PBF extract: {base_url} -> {pbf_dest}")
    req = urllib.request.Request(base_url, headers=headers)
    with urllib.request.urlopen(req) as resp, open(pbf_dest, 'wb') as f:
        total = int(resp.headers.get('Content-Length', 0))
        downloaded = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if downloaded % (50 * 1024 * 1024) < chunk_size:
                print(f"  Progress: {round(downloaded / (1024*1024), 1)} MB / {round(total / (1024*1024), 1)} MB ({round(downloaded/total*100, 1)}%)")
                
    print(f"  [OK] Download complete: {pbf_dest} ({pbf_dest.stat().st_size} bytes)")

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    target = root / "data" / "raw" / "osm"
    download_osm(target)
