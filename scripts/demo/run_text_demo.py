#!/usr/bin/env python3
"""
CrisisGuard — Dedicated Crisis Text Intelligence Demo Runner
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run Phase 7 Crisis Text Classification on arbitrary tweet/message")
    parser.add_argument("text", nargs="?", default="URGENT: Flash flood breached river embankment near downtown bridge, families need immediate evacuation and rescue boats!",
                        help="Crisis text or tweet string to classify")
    parser.add_argument("--publish", action="store_true", help="Publish intelligence record to Kafka demo topic")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent.parent
    cli = root / "scripts" / "demo" / "crisisguard_input.py"
    cmd = [sys.executable, str(cli), "--type", "text", "--text", args.text]
    if args.publish:
        cmd.append("--publish")
        
    import subprocess
    sys.exit(subprocess.run(cmd).returncode)

if __name__ == "__main__":
    main()
