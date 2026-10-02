#!/usr/bin/env python3
"""
CrisisGuard — Dedicated Image Forensics Demo Runner
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run Phase 6 Image Forensics on arbitrary image")
    parser.add_argument("image_path", nargs="?", default="data/demo/input/sample_image.jpg",
                        help="Path to input image file (default: data/demo/input/sample_image.jpg)")
    parser.add_argument("--publish", action="store_true", help="Publish record to Kafka demo topic")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent.parent
    cli = root / "scripts" / "demo" / "crisisguard_input.py"
    cmd = [sys.executable, str(cli), "--type", "image", "--path", args.image_path]
    if args.publish:
        cmd.append("--publish")
        
    import subprocess
    sys.exit(subprocess.run(cmd).returncode)

if __name__ == "__main__":
    main()
