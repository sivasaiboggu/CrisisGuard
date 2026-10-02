import os
import sys
import subprocess
import shutil
import socket

def check_command(cmd, expected_keyword=None):
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10)
        output = res.stdout
        if res.returncode == 0 or expected_keyword in output:
            if expected_keyword:
                return (expected_keyword in output, output.strip())
            return (True, output.strip())
        return (False, output.strip())
    except Exception as e:
        return (False, str(e))

def check_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except Exception:
        return False

def main():
    print("============================================================")
    print("CRISISGUARD — PHASE 5 ENVIRONMENT VALIDATION")
    print("Author: B.SIVASAI (2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("============================================================")

    # Standardize PATH for Big Data stack binaries
    opt_paths = "/opt/spark/bin:/opt/hadoop/bin:/opt/scala/bin:/opt/kafka/bin:/opt/hive/bin"
    os.environ["PATH"] = f"{opt_paths}:{os.environ.get('PATH', '')}"
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
    os.environ["HADOOP_HOME"] = "/opt/hadoop"
    os.environ["SPARK_HOME"] = "/opt/spark"

    results = {}

    # 1. Java 11
    java_ok, java_out = check_command(["java", "-version"], "11.")
    java_home = os.environ.get("JAVA_HOME", "")
    results["Java 11"] = java_ok and ("11." in java_out or "11." in java_home)
    print(f"Java 11: {'PASS' if results['Java 11'] else 'FAIL'} ({java_out.splitlines()[0] if java_out else 'Missing'})")

    # 2. Python 3.12
    py_ok, py_out = check_command(["python3", "--version"], "3.12")
    results["Python 3.12"] = py_ok
    print(f"Python 3.12: {'PASS' if results['Python 3.12'] else 'FAIL'} ({py_out})")

    # 3. Scala 2.12.18
    scala_ok, scala_out = check_command(["scala", "-version"], "2.12.18")
    results["Scala 2.12.18"] = scala_ok
    print(f"Scala 2.12.18: {'PASS' if results['Scala 2.12.18'] else 'FAIL'} ({scala_out.splitlines()[0] if scala_out else 'Missing'})")

    # 4. Hadoop 3.3.6
    hadoop_ok, hadoop_out = check_command(["hadoop", "version"], "3.3.6")
    results["Hadoop 3.3.6"] = hadoop_ok
    print(f"Hadoop 3.3.6: {'PASS' if results['Hadoop 3.3.6'] else 'FAIL'} ({hadoop_out.splitlines()[0] if hadoop_out else 'Missing'})")

    # 5. Spark 3.5.1
    spark_ok, spark_out = check_command(["spark-submit", "--version"], "3.5.1")
    results["Spark 3.5.1"] = spark_ok
    print(f"Spark 3.5.1: {'PASS' if results['Spark 3.5.1'] else 'FAIL'} ({spark_out.splitlines()[0] if spark_out else 'Missing'})")

    # 6. Kafka 3.7.0
    kafka_dir_ok = os.path.exists("/opt/kafka/bin/kafka-server-start.sh") or os.path.exists("/usr/local/bin/kafka-server-start.sh")
    kafka_jar_ok = any("3.7.0" in f for f in os.listdir("/opt/kafka/libs")) if os.path.exists("/opt/kafka/libs") else False
    results["Kafka 3.7.0"] = kafka_dir_ok and kafka_jar_ok
    print(f"Kafka 3.7.0: {'PASS' if results['Kafka 3.7.0'] else 'FAIL'} (libs verified: {kafka_jar_ok})")

    # 7. Hive 3.1.3
    hive_bin_ok = os.path.exists("/usr/local/bin/hive") or os.path.exists("/opt/hive/bin/hive")
    hive_guava_ok = os.path.exists("/opt/hive/lib/guava-27.0-jre.jar") if os.path.exists("/opt/hive/lib") else False
    results["Hive 3.1.3"] = hive_bin_ok and hive_guava_ok
    print(f"Hive 3.1.3: {'PASS' if results['Hive 3.1.3'] else 'FAIL'} (guava aligned: {hive_guava_ok})")

    # 8. Required Configuration Files
    configs = [
        "config/environment.yaml",
        "config/versions.yaml",
        "docs/environment/PHASE5_PREINSTALL_AUDIT.md",
        "docs/environment/PHASE5_COMPATIBILITY_MATRIX.md",
        "docs/environment/RESOURCE_CONFIGURATION.md",
        "docs/environment/SERVICE_MANAGEMENT.md",
        "docs/environment/ENVIRONMENT_MANIFEST.md",
        "docs/environment/PHASE5_INTEGRATION_TESTS.md",
        "docs/environment/REPRODUCIBILITY_GUIDE.md",
        "docs/environment/PHASE5_FINAL_REPORT.md",
    ]
    missing_configs = [c for c in configs if not os.path.exists(c)]
    results["Configuration & Docs"] = (len(missing_configs) == 0)
    print(f"Configuration & Docs: {'PASS' if results['Configuration & Docs'] else 'FAIL'}")
    if missing_configs:
        print(f"  Missing: {missing_configs}")

    # 9. Storage & Data Preservation
    raw_untouched = os.path.exists("data/raw/deepfake_dfd") and os.path.exists("data/raw/synthetic_media_eval")
    processed_intact = os.path.exists("data/processed/cifake") and os.path.exists("data/processed/humaid")
    results["Data Integrity"] = raw_untouched and processed_intact
    print(f"Data Integrity (Raw Untouched & Processed Intact): {'PASS' if results['Data Integrity'] else 'FAIL'}")

    # 10. Service Availability (HDFS & Kafka)
    hdfs_live = check_port("127.0.0.1", 9000)
    kafka_live = check_port("127.0.0.1", 9092)
    results["HDFS Service (Port 9000)"] = hdfs_live
    results["Kafka Service (Port 9092)"] = kafka_live
    print(f"HDFS Service (Port 9000): {'PASS' if hdfs_live else 'FAIL'}")
    print(f"Kafka Service (Port 9092): {'PASS' if kafka_live else 'FAIL'}")

    all_pass = all(results.values())
    print("\n============================================================")
    print("PHASE 5 DECISION")
    print("============================================================")
    print(f"PHASE 5 STATUS: {'PASS' if all_pass else 'BLOCKED'}")
    print("============================================================")

    sys.exit(0 if all_pass else 1)

if __name__ == "__main__":
    main()
