import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

print("============================================================")
print("CrisisGuard Spark Local Smoke Test")
print("Author: B.SIVASAI")
print("Roll Number: 2023BCS0228")
print("Course: CSE412 — Big Data & Large-Scale Computing")
print("============================================================")

try:
    spark = SparkSession.builder \
        .appName("CrisisGuard_Phase5_SparkLocalSmoke") \
        .master("local[2]") \
        .config("spark.driver.memory", "1g") \
        .getOrCreate()

    print(f"SparkSession Active: Version={spark.version}, Master={spark.sparkContext.master}")

    # Read a small Phase 4 processed sample (CIFAKE processed parquet)
    sample_path = "/mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard/data/processed/cifake/cifake_records.parquet"
    if not os.path.exists(sample_path):
        sample_path = "data/processed/cifake/cifake_records.parquet"

    print(f"Reading sample dataset from: {sample_path}")
    df = spark.read.parquet(sample_path)
    total_records = df.count()
    print(f"Read {total_records} records successfully. Schema:")
    df.printSchema()

    # Simple transformation & aggregation: count by label
    print("Performing transformation and aggregation (group by label):")
    agg_df = df.groupBy("label").agg(count("*").alias("record_count")).orderBy("label")
    agg_df.show()

    spark.stop()
    print("Spark Local Smoke Test: PASS")
    sys.exit(0)

except Exception as e:
    print(f"Spark Local Smoke Test: FAIL - {e}")
    sys.exit(1)
