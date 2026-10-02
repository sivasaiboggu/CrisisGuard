import os
import json
import time
import sys
import subprocess
import pandas as pd

print("============================================================")
print("CrisisGuard Kafka Integration Smoke Test")
print("Author: B.SIVASAI")
print("Roll Number: 2023BCS0228")
print("Course: CSE412 — Big Data & Large-Scale Computing")
print("============================================================")

TOPIC = "crisisguard.phase5.test"
DATA_TOPIC = "crisisguard.phase5.events"
BOOTSTRAP_SERVER = "127.0.0.1:9092"
KAFKA_BIN = "/opt/kafka/bin"

def run_cmd(cmd, input_text=None):
    env = os.environ.copy()
    env["PATH"] = f"{KAFKA_BIN}:{env.get('PATH', '')}"
    env["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
    res = subprocess.run(cmd, input=input_text, text=True, capture_output=True, env=env)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd)}\nStderr: {res.stderr}\nStdout: {res.stdout}")
    return res.stdout

try:
    print(f"Step 1: Creating Kafka topics: {TOPIC}, {DATA_TOPIC}...")
    run_cmd(["kafka-topics.sh", "--bootstrap-server", BOOTSTRAP_SERVER, "--create", "--if-not-exists", "--topic", TOPIC, "--partitions", "1", "--replication-factor", "1"])
    run_cmd(["kafka-topics.sh", "--bootstrap-server", BOOTSTRAP_SERVER, "--create", "--if-not-exists", "--topic", DATA_TOPIC, "--partitions", "1", "--replication-factor", "1"])
    print("Topics created successfully.")

    # Step 2: Test message with Author and Roll Number
    test_msg = "CrisisGuard Kafka Smoke Verification | Author: B.SIVASAI | Roll: 2023BCS0228 | Status: OK"
    print(f"Step 2: Producing verification message to topic '{TOPIC}': {test_msg}")
    run_cmd(["kafka-console-producer.sh", "--bootstrap-server", BOOTSTRAP_SERVER, "--topic", TOPIC], input_text=f"{test_msg}\n")

    print(f"Step 3: Consuming message from '{TOPIC}'...")
    consume_res = run_cmd(["kafka-console-consumer.sh", "--bootstrap-server", BOOTSTRAP_SERVER, "--topic", TOPIC, "--from-beginning", "--max-messages", "1", "--timeout-ms", "10000"])
    print(f"Consumer Output:\n{consume_res.strip()}")
    assert "2023BCS0228" in consume_res and "B.SIVASAI" in consume_res, "Verification message mismatch!"
    print("Step 8 (Author Message Test): PASS")

    # Step 4: Step 9 Real Data Smoke Test
    print("\n--- Step 9: Real Data Event Smoke Test ---")
    parquet_path = "/mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard/data/processed/propagation/propagation_events.parquet"
    print(f"Reading 3 sample records from Phase 4 processed data: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    sample_records = df.head(3).to_dict(orient="records")

    produced_events = []
    producer_input = ""
    for r in sample_records:
        event = {
            "content_id": str(r.get("content_id", "N/A")),
            "event_type": str(r.get("propagation_type", "CASCADE_EVENT")),
            "scenario_id": str(r.get("scenario_id", "UNKNOWN")),
            "timestamp": str(r.get("timestamp", "2026-09-27T00:00:00Z")),
            "governance_tag": str(r.get("governance_tag", "SEMI_SYNTHETIC"))
        }
        event_str = json.dumps(event)
        producer_input += event_str + "\n"
        produced_events.append(event)
        print(f"Formed Event: {event_str}")

    print(f"Sending 3 event records to '{DATA_TOPIC}'...")
    run_cmd(["kafka-console-producer.sh", "--bootstrap-server", BOOTSTRAP_SERVER, "--topic", DATA_TOPIC], input_text=producer_input)

    print(f"Consuming 3 event records from '{DATA_TOPIC}'...")
    consumed_events_raw = run_cmd(["kafka-console-consumer.sh", "--bootstrap-server", BOOTSTRAP_SERVER, "--topic", DATA_TOPIC, "--from-beginning", "--max-messages", "3", "--timeout-ms", "10000"])
    print("Consumed Records:")
    print(consumed_events_raw.strip())

    lines = [l for l in consumed_events_raw.strip().split("\n") if l.strip()]
    assert len(lines) >= 3, f"Expected at least 3 events, received {len(lines)}"
    print("Step 9 (Real Data Event Smoke Test): PASS")

    print("\n============================================================")
    print("Kafka Smoke Tests: ALL PASS")
    print("============================================================")
    sys.exit(0)

except Exception as e:
    print(f"Kafka Smoke Test: FAIL - {e}")
    sys.exit(1)
