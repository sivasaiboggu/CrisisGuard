import subprocess
import os
import sys
import pandas as pd

print("============================================================")
print("CrisisGuard Hive Integration Smoke Test")
print("Author: B.SIVASAI")
print("Roll Number: 2023BCS0228")
print("Course: CSE412 — Big Data & Large-Scale Computing")
print("============================================================")

HIVE_BIN = "/opt/hive/bin/hive"

def run_hive(query):
    env = os.environ.copy()
    env["HADOOP_HOME"] = "/opt/hadoop"
    env["HIVE_HOME"] = "/opt/hive"
    env["HADOOP_CONF_DIR"] = "/opt/hadoop/etc/hadoop"
    env["HIVE_CONF_DIR"] = "/opt/hive/conf"
    # Hive 3.1.3 explicitly requires Java 8 runtime due to URLClassLoader casting (HIVE-22415)
    env["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
    env["PATH"] = f"/usr/lib/jvm/java-8-openjdk-amd64/bin:/opt/hive/bin:/opt/hadoop/bin:{env.get('PATH', '')}"
    
    # Run with local execution settings
    hive_cmd = [
        HIVE_BIN,
        "--hiveconf", "hive.fetch.task.conversion=more",
        "--hiveconf", "hive.exec.mode.local.auto=true",
        "-e", query
    ]
    res = subprocess.run(hive_cmd, env=env, text=True, capture_output=True, cwd="/var/crisisguard/hive")
    if res.returncode != 0:
        raise RuntimeError(f"Hive query failed:\nQuery: {query}\nStderr: {res.stderr}\nStdout: {res.stdout}")
    return res.stdout

try:
    print("--- Step 10: Hive DDL & DML Verification ---")
    smoke_csv = "/var/crisisguard/hive/smoke_author_record.csv"
    with open(smoke_csv, "w") as f:
        f.write("1,B.SIVASAI,2023BCS0228,OPERATIONAL\n")
    print(f"Created author verification record at: {smoke_csv}")

    ddl_query = f"""
    DROP TABLE IF EXISTS default.crisisguard_smoke;
    CREATE TABLE default.crisisguard_smoke (
        id INT,
        author STRING,
        roll STRING,
        status STRING
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ',';

    LOAD DATA LOCAL INPATH '{smoke_csv}' OVERWRITE INTO TABLE default.crisisguard_smoke;
    SELECT * FROM default.crisisguard_smoke;
    """
    print("Executing Hive DDL / LOAD / SELECT...")
    out = run_hive(ddl_query)
    print("Hive Output:")
    print(out)
    assert "2023BCS0228" in out, "Hive author record verification failed!"
    print("Step 10 (Hive Core Verification): PASS")

    print("\n--- Step 11: Hive + Phase 4 Processed Data Smoke Test ---")
    parquet_path = "/mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard/data/processed/propagation/propagation_events.parquet"
    print(f"Reading sample records from Phase 4 processed data: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    sample_csv = "/var/crisisguard/hive/propagation_sample.csv"
    sample_df = df[["event_id", "content_id", "scenario_id", "governance_tag"]].head(5)
    sample_df.to_csv(sample_csv, index=False, header=False)
    print(f"Prepared sample CSV at: {sample_csv}")

    data_query = f"""
    DROP TABLE IF EXISTS default.crisisguard_propagation_sample;
    CREATE TABLE default.crisisguard_propagation_sample (
        event_id STRING,
        content_id STRING,
        scenario_id STRING,
        governance_tag STRING
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ',';

    LOAD DATA LOCAL INPATH '{sample_csv}' OVERWRITE INTO TABLE default.crisisguard_propagation_sample;
    SELECT * FROM default.crisisguard_propagation_sample;
    """
    print("Loading processed sample into Hive table and querying records...")
    data_out = run_hive(data_query)
    print("Hive Processed Data Query Output:")
    print(data_out)
    assert "SEMI_SYNTHETIC" in data_out or "ORGANIC" in data_out or "BURST" in data_out, "Hive processed query failed to return records!"
    print("Step 11 (Hive Processed Data Flow): PASS")

    print("\n============================================================")
    print("Hive Smoke Tests: ALL PASS")
    print("============================================================")
    sys.exit(0)

except Exception as e:
    print(f"Hive Smoke Test: FAIL - {e}")
    sys.exit(1)
