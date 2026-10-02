import os
import sys
import subprocess
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg

print("============================================================")
print("CrisisGuard Spark + HDFS Integration Smoke Test")
print("Author: B.SIVASAI")
print("Roll Number: 2023BCS0228")
print("Course: CSE412 — Big Data & Large-Scale Computing")
print("============================================================")

local_sample = "/mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard/data/processed/cifake/cifake_records.parquet"
if not os.path.exists(local_sample):
    local_sample = "data/processed/cifake/cifake_records.parquet"
hdfs_target_dir = "/crisisguard/processed/cifake"
hdfs_url = f"hdfs://127.0.0.1:9000{hdfs_target_dir}/cifake_records.parquet"

env = os.environ.copy()
env["HADOOP_HOME"] = "/opt/hadoop"
env["PATH"] = f"/opt/hadoop/bin:{env.get('PATH', '')}"
env["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"

try:
    print(f"Step 1: Uploading legitimate Phase 4 processed sample to HDFS: {hdfs_url}...")
    subprocess.run(["/opt/hadoop/bin/hdfs", "dfs", "-mkdir", "-p", hdfs_target_dir], check=True, env=env)
    subprocess.run(["/opt/hadoop/bin/hdfs", "dfs", "-rm", "-f", f"{hdfs_target_dir}/cifake_records.parquet"], check=False, env=env)
    subprocess.run(["/opt/hadoop/bin/hdfs", "dfs", "-put", "-f", local_sample, f"{hdfs_target_dir}/cifake_records.parquet"], check=True, env=env)
    print("Step 1 Complete: Sample uploaded to HDFS.")

    print("Step 2: Initializing SparkSession configured for HDFS access...")
    spark = SparkSession.builder \
        .appName("CrisisGuard_Phase5_SparkHDFS_Integration") \
        .master("local[2]") \
        .config("spark.driver.memory", "1g") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://127.0.0.1:9000") \
        .getOrCreate()

    print(f"Step 3: Reading Parquet data directly from HDFS URI: {hdfs_url}")
    df = spark.read.parquet(hdfs_url)
    total_count = df.count()
    print(f"Verified {total_count} records retrieved from HDFS.")

    print("Step 4: Inspecting Schema...")
    df.printSchema()

    print("Step 5: Executing distributed aggregation (file_size_bytes stats grouped by label):")
    summary_df = df.groupBy("label").agg(
        count("*").alias("image_count"),
        avg("file_size_bytes").alias("mean_bytes")
    ).orderBy("label")
    summary_df.show()

    spark.stop()
    print("Spark + HDFS Integration Smoke Test: PASS")
    sys.exit(0)

except Exception as e:
    print(f"Spark + HDFS Integration Smoke Test: FAIL - {e}")
    sys.exit(1)
