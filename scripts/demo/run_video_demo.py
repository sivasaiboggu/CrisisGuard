#!/usr/bin/env python3
"""
CrisisGuard — Dedicated Video Forensics Demo Runner
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run Phase 6 Temporal Video Forensics on arbitrary video")
    parser.add_argument("video_path", nargs="?", default="data/demo/input/sample_video.gif",
                        help="Path to input video or animated gif (default: data/demo/input/sample_video.gif)")
    parser.add_argument("--publish", action="store_true", help="Publish record to Kafka demo topic")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent.parent
    cli = root / "scripts" / "demo" / "crisisguard_input.py"
    cmd = [sys.executable, str(cli), "--type", "video", "--path", args.video_path]
    if args.publish:
        cmd.append("--publish")
        
    import subprocess
    sys.exit(subprocess.run(cmd).returncode)

if __name__ == "__main__":
    main()
