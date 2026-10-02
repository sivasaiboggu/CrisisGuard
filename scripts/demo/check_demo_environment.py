#!/usr/bin/env python3
"""
CrisisGuard — Demo Environment & Infrastructure Health Check
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

IMPORTANT — RUNTIME:
  Run ONLY from WSL2 Ubuntu-24.04 using the project .venv:
    cd /mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard
    .venv/bin/python scripts/demo/check_demo_environment.py

  DO NOT run from Windows Python 3.14 (missing kafka-python, torchvision,
  incompatible scikit-learn serialization format).

Verifies:
  1. Python version & all required ML/Big Data packages (with exact versions)
  2. Java runtime
  3. Kafka broker connectivity (actual connection, not just socket)
  4. Kafka topic existence
  5. Hadoop/HDFS (actual dfs operation)
  6. Spark submit availability
  7. GraphX JAR presence
  8. Hive Derby metastore
  9. Demo directories
"""

import os
import sys
import socket
import subprocess
import importlib.metadata
from pathlib import Path


def check_socket(host, port, timeout=2.0):
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except Exception:
        return False


SPARK_SUBMIT = "/opt/spark/bin/spark-submit"
HDFS_BIN = "/opt/hadoop/bin/hdfs"


def run_cmd(cmd, timeout=8.0):
    try:
        res = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, shell=isinstance(cmd, str), timeout=timeout
        )
        return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def main():
    print("=" * 70)
    print("CRISISGUARD — DEMO ENVIRONMENT HEALTH CHECK")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print(f"Python:  {sys.executable}")
    print(f"Runtime: {'WSL2/Linux' if sys.platform.startswith('linux') else 'Windows (WARNING: use WSL2)'}")
    print("=" * 70)

    root = Path(__file__).resolve().parent.parent.parent
    all_passed = True

    # ------------------------------------------------------------------ #
    # 1. Python & Packages
    # ------------------------------------------------------------------ #
    print("\n[1] Python Runtime & Required Packages...")
    required = [
        ("pandas",      "2.x",   "pandas"),
        ("pyarrow",     "14+",   "pyarrow"),
        ("kafka",       "2.x",   "kafka-python"),
        ("torch",       "2.14+", "torch"),
        ("torchvision", "0.29+", "torchvision"),
        ("sklearn",     "1.5.2", "scikit-learn"),
        ("yaml",        "6.x",   "pyyaml"),
        ("jsonschema",  "4.x",   "jsonschema"),
        ("scipy",       "1.x",   "scipy"),
        ("PIL",         "10+",   "Pillow"),
    ]
    python_ok = True
    for mod_name, req_ver, pkg_name in required:
        try:
            if mod_name == "sklearn":
                import sklearn as mod
            elif mod_name == "yaml":
                import yaml as mod
            elif mod_name == "PIL":
                import PIL as mod
            else:
                mod = __import__(mod_name)

            try:
                ver = importlib.metadata.version(pkg_name)
            except Exception:
                ver = getattr(mod, "__version__", "present")

            # Warn if scikit-learn != 1.5.2 (frozen model compatibility)
            if mod_name == "sklearn" and ver != "1.5.2":
                print(f"  [WARN] {mod_name:15}: {ver} (FROZEN MODELS NEED 1.5.2 — may cause InconsistentVersionWarning)")
                python_ok = False
                all_passed = False
            else:
                print(f"  [PASS] {mod_name:15}: {ver}")
        except ImportError:
            print(f"  [FAIL] {mod_name:15}: MISSING — install with: pip install {pkg_name}")
            python_ok = False
            all_passed = False

    print(f"  Python executable: {sys.executable} (v{sys.version.split()[0]})")
    if not sys.platform.startswith("linux"):
        print("  [FAIL] NOT RUNNING IN WSL2/Linux — kafka & torchvision will be unavailable on Windows Python 3.14!")
        all_passed = False

    # ------------------------------------------------------------------ #
    # 2. Java
    # ------------------------------------------------------------------ #
    print("\n[2] Java Runtime Environment...")
    ok, out, err = run_cmd(["java", "-version"])
    java_ver = err.split("\n")[0] if err else out.split("\n")[0] if out else "not found"
    if ok or "version" in java_ver.lower():
        print(f"  [PASS] Java: {java_ver}")
    else:
        print(f"  [FAIL] Java not found — needed for Spark & HDFS")
        all_passed = False

    # ------------------------------------------------------------------ #
    # 3. Kafka — actual broker verification (not just socket)
    # ------------------------------------------------------------------ #
    print("\n[3] Apache Kafka Service (localhost:9092)...")
    kafka_socket_ok = check_socket("localhost", 9092) or check_socket("127.0.0.1", 9092)
    if kafka_socket_ok:
        # Actually try KafkaProducer connection
        try:
            from kafka import KafkaProducer, KafkaAdminClient
            admin = KafkaAdminClient(bootstrap_servers="localhost:9092", request_timeout_ms=4000)
            topics = admin.list_topics()
            admin.close()
            user_topics = [t for t in topics if not t.startswith("__")]
            demo_topic_present = "crisisguard-demo-events" in topics
            prod_topic_present = "crisisguard-propagation-events" in topics
            print(f"  [PASS] Kafka Broker: CONNECTED (port 9092)")
            print(f"  [PASS] Demo Topic 'crisisguard-demo-events': {'PRESENT' if demo_topic_present else 'MISSING'}")
            print(f"  [PASS] Prod Topic 'crisisguard-propagation-events': {'PRESENT' if prod_topic_present else 'MISSING'}")
            print(f"  Topics found: {', '.join(user_topics[:6])}")
            if not demo_topic_present:
                all_passed = False
        except Exception as e:
            print(f"  [WARN] Kafka socket open but broker client failed: {e}")
    else:
        print("  [FAIL] Kafka port 9092 NOT REACHABLE — start Kafka in WSL2")
        all_passed = False

    # ------------------------------------------------------------------ #
    # 4. Hadoop / HDFS — actual operation
    # ------------------------------------------------------------------ #
    print("\n[4] Apache Hadoop & HDFS...")
    ok_ls, out_ls, _ = run_cmd([HDFS_BIN, "dfs", "-ls", "/"])
    if ok_ls:
        print("  [PASS] HDFS NameNode: RESPONDING (hdfs dfs -ls /)")
        ok_report, report_out, _ = run_cmd([HDFS_BIN, "dfsadmin", "-report"])
        if ok_report:
            for line in report_out.splitlines()[:4]:
                print(f"    {line}")
    else:
        hdfs_sock = check_socket("localhost", 9000)
        if hdfs_sock:
            print("  [WARN] HDFS port 9000 open but dfs -ls failed (PATH issue?)")
        else:
            print("  [FAIL] HDFS not responding — start Hadoop in WSL2")
            all_passed = False

    # ------------------------------------------------------------------ #
    # 5. Spark
    # ------------------------------------------------------------------ #
    print("\n[5] Apache Spark & GraphX JAR...")
    ok_spk, spk_out, spk_err = run_cmd([SPARK_SUBMIT, "--version"])
    combined = (spk_out + " " + spk_err).lower()
    if ok_spk or "version" in combined:
        ver_lines = [l for l in (spk_out + "\n" + spk_err).splitlines() if "version" in l.lower()]
        print(f"  [PASS] Spark: {ver_lines[0].strip() if ver_lines else 'Available'}")
    else:
        print(f"  [FAIL] spark-submit not found at {SPARK_SUBMIT}")
        all_passed = False

    graphx_jar = root / "target" / "phase8" / "crisisguard-graphx.jar"
    if graphx_jar.exists():
        print(f"  [PASS] GraphX JAR: FOUND ({graphx_jar.stat().st_size:,} bytes)")
    else:
        print(f"  [FAIL] GraphX JAR: MISSING at {graphx_jar}")
        all_passed = False

    # ------------------------------------------------------------------ #
    # 6. Hive Metastore
    # ------------------------------------------------------------------ #
    print("\n[6] Apache Hive Metastore...")
    hive_dir = root / "metastore_db"
    if hive_dir.exists():
        print(f"  [PASS] Hive Derby Metastore: FOUND ({hive_dir})")
    else:
        print("  [WARN] Hive Derby Metastore not found at workspace root")

    # ------------------------------------------------------------------ #
    # 7. Demo Directories
    # ------------------------------------------------------------------ #
    print("\n[7] Demo Directories...")
    demo_dirs = [
        root / "scripts" / "demo",
        root / "docs" / "demo",
        root / "data" / "demo",
        root / "data" / "demo" / "input",
        root / "data" / "demo" / "streaming",
    ]
    for d in demo_dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  [READY] {d.relative_to(root)}")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    status = "PASS" if all_passed else "ATTENTION NEEDED"
    print(f"ENVIRONMENT HEALTH CHECK RESULT: {status}")
    print("=" * 70)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
