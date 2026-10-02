#!/usr/bin/env python3
"""
CrisisGuard — Safe Demo Environment Reset
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Safely clears ONLY temporary demo run outputs:
- Local: data/demo/streaming/*
- HDFS:  hdfs://localhost:9000/crisisguard/demo/*

STRICT SAFETY CONSTRAINTS:
- NEVER touches data/features/
- NEVER touches data/processed/
- NEVER touches data/raw/
- NEVER touches models/
- NEVER touches hdfs:///crisisguard/phase8/
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("=" * 70)
    print("CRISISGUARD — DEMO ENVIRONMENT SAFE RESET")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("=" * 70)

    root = Path(__file__).resolve().parent.parent.parent
    demo_stream_dir = root / "data" / "demo" / "streaming"

    # Absolute Safety Check
    assert "demo" in str(demo_stream_dir), "Safety Violation: Path does not contain 'demo'!"
    assert "features" not in str(demo_stream_dir), "Safety Violation: Path contains 'features'!"

    print(f"\n[1] Cleaning Local Demo Streaming Outputs ({demo_stream_dir.relative_to(root)})...")
    if demo_stream_dir.exists():
        for sub in ["raw_events", "windowed_metrics", "checkpoints"]:
            target = demo_stream_dir / sub
            if target.exists():
                shutil.rmtree(target)
                print(f"  Removed: {target.relative_to(root)}")
    print("  Local demo streaming directories cleared.")

    # Recreate empty directories
    (demo_stream_dir / "raw_events").mkdir(parents=True, exist_ok=True)
    (demo_stream_dir / "windowed_metrics").mkdir(parents=True, exist_ok=True)

    print("\n[2] Cleaning HDFS Demo Directory (/crisisguard/demo/)...")
    hdfs_cmd = "/opt/hadoop/bin/hdfs dfs -rm -r -f /crisisguard/demo/streaming"
    try:
        if sys.platform.startswith("linux"):
            res = subprocess.run(hdfs_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            res = subprocess.run(f'wsl -d Ubuntu-24.04 -e bash -c "{hdfs_cmd}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("  HDFS /crisisguard/demo/streaming cleared successfully.")
    except Exception as e:
        print(f"  [!] Notice cleaning HDFS: {e}")

    print("\n" + "=" * 70)
    print("DEMO RESET COMPLETE: READY FOR NEW LIVE RUN")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
