#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: Kafka Propagation Events Producer
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Replays validated real Phase 4 propagation events (5,004 events) into Kafka
topic 'crisisguard-propagation-events' preserving all metadata, timestamps,
source/target nodes, and governance provenance.
"""

import sys
import os
import json
import time
from pathlib import Path
import pandas as pd
from kafka import KafkaProducer

def produce_events():
    print("=" * 70)
    print("CRISISGUARD — PHASE 8 KAFKA PROPAGATION PRODUCER")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    print("=" * 70)
    
    root = Path(__file__).resolve().parent.parent.parent.parent
    events_pq = root / "data" / "processed" / "propagation" / "propagation_events.parquet"
    
    if not events_pq.exists():
        print(f"ERROR: Events parquet file not found at {events_pq}")
        return False
        
    df_events = pd.read_parquet(events_pq)
    total_records = len(df_events)
    print(f"Loaded {total_records:,} real propagation events from {events_pq.name}")
    
    # Configure KafkaProducer
    topic = "crisisguard-propagation-events"
    bootstrap_servers = ["localhost:9092"]
    
    print(f"Connecting Kafka Producer to {bootstrap_servers} for topic: {topic}...")
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: str(k).encode("utf-8") if k else None,
        acks="all",
        retries=3,
        batch_size=16384,
        linger_ms=10
    )
    
    t0 = time.time()
    produced_count = 0
    invalid_count = 0
    
    print(f"Publishing {total_records} events to Kafka topic '{topic}'...")
    for idx, row in df_events.iterrows():
        try:
            # Construct standard event payload
            event_id = str(row["event_id"])
            source_node = str(row["source_node"]) if pd.notna(row["source_node"]) else None
            target_node = str(row["target_node"]) if pd.notna(row["target_node"]) else None
            
            # Timestamp formatting (ISO 8601 string)
            ts_raw = row["timestamp"]
            ts_str = str(ts_raw) if pd.notna(ts_raw) else None
            
            payload = {
                "event_id": event_id,
                "scenario_id": str(row["scenario_id"]) if pd.notna(row["scenario_id"]) else "UNKNOWN",
                "propagation_type": str(row["propagation_type"]) if pd.notna(row["propagation_type"]) else "UNKNOWN",
                "content_id": str(row["content_id"]) if pd.notna(row["content_id"]) else "UNKNOWN",
                "source_node": source_node,
                "target_node": target_node,
                "event_time": ts_str,
                "parent_event_id": str(row["parent_event_id"]) if pd.notna(row["parent_event_id"]) else None,
                "synthetic_media_risk": float(row["synthetic_media_risk"]) if pd.notna(row["synthetic_media_risk"]) else 0.0,
                "crisis_priority_if_present": str(row["crisis_priority_if_present"]) if pd.notna(row["crisis_priority_if_present"]) else "NORMAL",
                "governance_tag": str(row.get("governance_tag", "SEMI_SYNTHETIC")),
                "provenance": "crisisguard_phase4_propagation_stream",
                "producer_timestamp": time.time()
            }
            
            # Key by scenario_id or source_node to maintain ordering within partitions
            key = str(row.get("scenario_id", "default"))
            producer.send(topic, key=key, value=payload)
            produced_count += 1
            
            if (produced_count % 1000) == 0:
                print(f"  Published {produced_count:,} / {total_records:,} events...")
                
        except Exception as e:
            print(f"  Error encoding row {idx}: {e}")
            invalid_count += 1
            
    print("Flushing Kafka producer buffer...")
    producer.flush()
    duration = time.time() - t0
    throughput = produced_count / duration if duration > 0 else 0
    
    print(f"\nPublishing Complete:")
    print(f"  - Topic:              {topic}")
    print(f"  - Total Produced:     {produced_count:,}")
    print(f"  - Invalid/Dropped:    {invalid_count}")
    print(f"  - Elapsed Time:       {duration:.3f} seconds")
    print(f"  - Ingestion Rate:     {throughput:.1f} events/sec")
    
    producer.close()
    
    stats = {
        "topic": topic,
        "bootstrap_servers": bootstrap_servers,
        "input_records": total_records,
        "produced_count": produced_count,
        "invalid_count": invalid_count,
        "duration_seconds": round(duration, 3),
        "throughput_eps": round(throughput, 1),
        "status": "PASS" if produced_count == total_records else "FAIL"
    }
    
    docs_dir = root / "docs" / "phase8"
    docs_dir.mkdir(parents=True, exist_ok=True)
    with open(docs_dir / "kafka_producer_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"Saved producer statistics to: {docs_dir / 'kafka_producer_stats.json'}")
    
    return produced_count == total_records

if __name__ == "__main__":
    ok = produce_events()
    sys.exit(0 if ok else 1)
