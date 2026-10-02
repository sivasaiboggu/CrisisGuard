#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: Kafka Consumer & Stream Validation Tooling
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Consumes records from Kafka topic 'crisisguard-propagation-events',
audits message schema integrity, measures counts, duplicates, and invalid payloads.
"""

import sys
import os
import json
import time
from pathlib import Path
from kafka import KafkaConsumer, TopicPartition

def validate_stream():
    print("=" * 70)
    print("CRISISGUARD — PHASE 8 KAFKA STREAM CONSUMPTION & VALIDATION")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    print("=" * 70)
    
    root = Path(__file__).resolve().parent.parent.parent.parent
    topic = "crisisguard-propagation-events"
    bootstrap_servers = ["localhost:9092"]
    
    print(f"\n[1] Initializing Kafka Consumer on {topic}...")
    consumer = KafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=5000,
        group_id="crisisguard-validation-group"
    )
    
    # Assign all partitions explicitly to ensure reading from offset 0
    partitions = consumer.partitions_for_topic(topic)
    if not partitions:
        print(f"ERROR: No partitions found for topic {topic}")
        return False
        
    tps = [TopicPartition(topic, p) for p in partitions]
    consumer.assign(tps)
    consumer.seek_to_beginning()
    
    print(f"Assigned partitions: {tps}")
    print("Beginning stream consumption and schema validation...")
    
    consumed_count = 0
    duplicate_count = 0
    invalid_count = 0
    seen_event_ids = set()
    
    mandatory_fields = [
        "event_id", "scenario_id", "propagation_type", "content_id",
        "source_node", "event_time", "synthetic_media_risk", "governance_tag"
    ]
    
    t0 = time.time()
    for message in consumer:
        val = message.value
        consumed_count += 1
        
        # Check mandatory fields
        missing = [f for f in mandatory_fields if f not in val]
        if missing:
            invalid_count += 1
            if invalid_count <= 5:
                print(f"  Invalid record (missing {missing}): {val}")
            continue
            
        eid = val["event_id"]
        if eid in seen_event_ids:
            duplicate_count += 1
        else:
            seen_event_ids.add(eid)
            
        if (consumed_count % 1000) == 0:
            print(f"  Consumed & validated {consumed_count:,} events...")
            
    duration = time.time() - t0
    consumer.close()
    
    print("\n[2] Stream Consumption Results:")
    print(f"  - Total Consumed Events: {consumed_count:,}")
    print(f"  - Unique Event IDs:     {len(seen_event_ids):,}")
    print(f"  - Duplicate Events:     {duplicate_count}")
    print(f"  - Invalid Events:       {invalid_count}")
    print(f"  - Consumption Time:     {duration:.3f} seconds")
    
    c_count = (consumed_count >= 5004)
    c_dups = (duplicate_count == 0)
    c_valid = (invalid_count == 0)
    
    all_ok = c_count and c_dups and c_valid
    
    summary = {
        "topic": topic,
        "consumed_count": consumed_count,
        "unique_event_ids": len(seen_event_ids),
        "duplicate_count": duplicate_count,
        "invalid_count": invalid_count,
        "consumption_duration_sec": round(duration, 3),
        "validation_passed": all_ok
    }
    
    docs_dir = root / "docs" / "phase8"
    docs_dir.mkdir(parents=True, exist_ok=True)
    with open(docs_dir / "kafka_validation_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved validation summary to: {docs_dir / 'kafka_validation_summary.json'}")
    
    print("\n" + "=" * 70)
    print(f"OVERALL KAFKA STREAM STATUS: {'PASS' if all_ok else 'FAIL'}")
    print("=" * 70)
    return all_ok

if __name__ == "__main__":
    ok = validate_stream()
    sys.exit(0 if ok else 1)
