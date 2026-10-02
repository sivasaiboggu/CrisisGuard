#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: HDFS Ingestion Script
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Creates the Phase 8 HDFS namespace and copies validated upstream inputs into HDFS:
- /crisisguard/phase8/propagation/
- /crisisguard/phase8/media_risk/
- /crisisguard/phase8/crisis_intelligence/
- /crisisguard/phase8/osm/
- /crisisguard/phase8/graph/
- /crisisguard/phase8/streaming/
- /crisisguard/phase8/hive/
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path

def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    t0 = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    if res.returncode != 0:
        print(f"ERROR ({res.returncode}):\n{res.stderr}")
    return res.returncode == 0, res.stdout, res.stderr, dt

def hdfs_ingest():
    print("=" * 70)
    print("CRISISGUARD — PHASE 8 HDFS INGESTION & NAMESPACE SETUP")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    print("=" * 70)
    
    hdfs_bin = "/opt/hadoop/bin/hdfs"
    if not Path(hdfs_bin).exists():
        hdfs_bin = "hdfs"
        
    root = Path(__file__).resolve().parent.parent.parent
    base_hdfs = "/crisisguard/phase8"
    
    subdirs = [
        f"{base_hdfs}/propagation",
        f"{base_hdfs}/media_risk",
        f"{base_hdfs}/crisis_intelligence",
        f"{base_hdfs}/osm",
        f"{base_hdfs}/graph",
        f"{base_hdfs}/streaming",
        f"{base_hdfs}/hive"
    ]
    
    # 1. Create HDFS directories
    print("\n[1] Creating Phase 8 HDFS directories...")
    ok, out, err, _ = run_cmd([hdfs_bin, "dfs", "-mkdir", "-p"] + subdirs)
    if not ok:
        print("Failed to create HDFS directories.")
        return False
        
    # 2. Copy approved inputs to HDFS
    copies = [
        (root / "data" / "processed" / "propagation" / "propagation_events.parquet", f"{base_hdfs}/propagation/"),
        (root / "data" / "processed" / "propagation" / "propagation_edges.parquet", f"{base_hdfs}/propagation/"),
        (root / "data" / "features" / "synthetic_media" / "unified_media_risk.parquet", f"{base_hdfs}/media_risk/"),
        (root / "data" / "features" / "crisis_information" / "unified_crisis_intelligence.parquet", f"{base_hdfs}/crisis_intelligence/"),
        (root / "data" / "processed" / "osm" / "road_nodes.parquet", f"{base_hdfs}/osm/"),
        (root / "data" / "processed" / "osm" / "road_edges.parquet", f"{base_hdfs}/osm/"),
    ]
    
    print("\n[2] Ingesting validated files to HDFS...")
    ingest_timings = {}
    for local_f, hdfs_d in copies:
        if not local_f.exists():
            print(f"ERROR: Local file does not exist: {local_f}")
            return False
        print(f"  - Ingesting {local_f.name} ({local_f.stat().st_size:,} bytes) -> {hdfs_d}")
        ok, out, err, dt = run_cmd([hdfs_bin, "dfs", "-put", "-f", str(local_f), hdfs_d])
        if not ok:
            print(f"Failed to put {local_f.name} to {hdfs_d}")
            return False
        ingest_timings[local_f.name] = {
            "size_bytes": local_f.stat().st_size,
            "hdfs_destination": hdfs_d,
            "duration_seconds": round(dt, 3)
        }
        
    # 3. Verify HDFS files using -ls -R and -du -h
    print("\n[3] Verifying HDFS files (hdfs dfs -ls -R /crisisguard/phase8)...")
    ok, ls_out, err, _ = run_cmd([hdfs_bin, "dfs", "-ls", "-R", base_hdfs])
    print(ls_out)
    
    print("\n[4] Verifying HDFS storage (hdfs dfs -du -h /crisisguard/phase8)...")
    ok, du_out, err, _ = run_cmd([hdfs_bin, "dfs", "-du", "-h", base_hdfs])
    print(du_out)
    
    # Save HDFS audit evidence
    evidence = {
        "hdfs_namespace": base_hdfs,
        "subdirectories": subdirs,
        "ingest_timings": ingest_timings,
        "ls_output": ls_out,
        "du_output": du_out
    }
    
    docs_dir = root / "docs" / "phase8"
    docs_dir.mkdir(parents=True, exist_ok=True)
    with open(docs_dir / "hdfs_ingest_evidence.json", "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
    print(f"\nSaved HDFS audit evidence to {docs_dir / 'hdfs_ingest_evidence.json'}")
    
    print("\n" + "=" * 70)
    print("OVERALL HDFS STATUS: PASS — NAMESPACE INITIALIZED & INGESTED")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = hdfs_ingest()
    sys.exit(0 if success else 1)
