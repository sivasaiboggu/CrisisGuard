#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: Test Spark Structured Streaming Kafka Ingestion
"""

import sys
import time
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, TimestampType
)

def test_stream():
    print("Testing Spark Structured Streaming with Kafka package...")
    spark = SparkSession.builder \
        .appName("TestSparkKafka") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("WARN")
    print("SparkSession created, reading Kafka stream...")
    
    df_kafka = spark.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "crisisguard-propagation-events") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()
        
    count = df_kafka.count()
    print(f"Read {count} records from Kafka topic!")
    df_kafka.printSchema()
    
    spark.stop()
    return count >= 5004

if __name__ == "__main__":
    ok = test_stream()
    sys.exit(0 if ok else 1)
