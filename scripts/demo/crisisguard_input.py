#!/usr/bin/env python3
"""
CrisisGuard — Unified Live User Input CLI (Mode A)
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Accepts real-time user input across all modalities:
1. Propagation Cascade Events (--type propagation)
2. Crisis Information Text (--type text)
3. Synthetic Media Image Forensics (--type image)
4. Synthetic Media Video Forensics (--type video)

Publishes validated events to Apache Kafka (default: 'crisisguard-demo-events')
with strict schema enforcement and end-to-end traceability.
"""

import os
import sys
import json
import time
import uuid
import argparse
from datetime import datetime, timezone
from pathlib import Path

def get_kafka_producer(bootstrap_servers="localhost:9092"):
    try:
        from kafka import KafkaProducer
        return KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: str(k).encode("utf-8") if k else None,
            acks="all",
            retries=3,
            linger_ms=10
        )
    except Exception as e:
        print(f"[!] Warning: Could not initialize KafkaProducer: {e}")
        return None

def validate_propagation_event(payload):
    """Strict schema validation for propagation event payload."""
    required = ["event_id", "scenario_id", "propagation_type", "source_node", "target_node", "event_time"]
    for f in required:
        if f not in payload or payload[f] is None:
            raise ValueError(f"Missing required field in propagation event: '{f}'")
    
    # Type checks
    if not isinstance(payload.get("synthetic_media_risk", 0.0), (int, float)):
        raise TypeError("synthetic_media_risk must be numeric (float)")
    risk = float(payload.get("synthetic_media_risk", 0.0))
    if not (0.0 <= risk <= 1.0):
        raise ValueError(f"synthetic_media_risk must be in [0.0, 1.0], got {risk}")
        
    return True

def handle_propagation(args, producer):
    print("\n--- [MODE A: PROPAGATION EVENT INGESTION] ---")
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[ERROR] Specified file not found: {file_path}")
            sys.exit(1)
        with open(file_path, "r") as f:
            payload = json.load(f)
        print(f"Loaded event payload from: {file_path}")
    else:
        # Check if CLI arguments provided or interactive prompt needed
        source = args.source_node
        target = args.target_node
        scenario = args.scenario
        risk = args.risk
        priority = args.priority
        prop_type = args.propagation_type
        
        if not source or not target:
            # Interactive mode if arguments omitted
            print("Entering Interactive Propagation Event Builder:")
            source = source or input("Enter Source Node ID [default: osm_node_1001]: ").strip() or "osm_node_1001"
            target = target or input("Enter Target Node ID [default: osm_node_1002]: ").strip() or "osm_node_1002"
            scenario = scenario or input("Enter Scenario ID [default: flood_evacuation_live]: ").strip() or "flood_evacuation_live"
            risk_in = input(f"Enter Synthetic Media Risk (0.0 - 1.0) [default: {risk or 0.85}]: ").strip()
            risk = float(risk_in) if risk_in else (risk if risk is not None else 0.85)
            priority = priority or input("Enter Priority (LOW, MEDIUM, HIGH, CRITICAL) [default: HIGH]: ").strip() or "HIGH"
            prop_type = prop_type or input("Enter Propagation Type [default: retweet_cascade]: ").strip() or "retweet_cascade"
            
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        event_id = args.event_id or f"demo_evt_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        
        payload = {
            "event_id": event_id,
            "scenario_id": scenario or "flood_evacuation_live",
            "propagation_type": prop_type or "retweet_cascade",
            "content_id": args.content_id or f"media_content_{uuid.uuid4().hex[:8]}",
            "source_node": source,
            "target_node": target,
            "event_time": now_iso,
            "parent_event_id": args.parent_event_id,
            "synthetic_media_risk": float(risk if risk is not None else 0.75),
            "crisis_priority_if_present": priority or "HIGH",
            "governance_tag": "LIVE_USER_INPUT",
            "provenance": "crisisguard_input_cli",
            "producer_timestamp": time.time()
        }

    # Validate
    validate_propagation_event(payload)
    print("\nValidated Propagation Event Payload:")
    print(json.dumps(payload, indent=2))
    
    if args.dry_run:
        print("\n[DRY RUN] Schema validation successful. Event NOT dispatched to Kafka.")
        return payload

    if not producer:
        print("\n[ERROR] Kafka Producer unavailable. Cannot publish event.")
        sys.exit(1)

    topic = args.topic
    key = str(payload["scenario_id"])
    print(f"\nDispatching event to Kafka topic '{topic}' (key='{key}')...")
    
    future = producer.send(topic, key=key, value=payload)
    producer.flush()
    metadata = future.get(timeout=10)
    
    print("=" * 60)
    print("SUCCESS: EVENT CONFIRMED BY KAFKA BROKER")
    print(f"  - Topic:     {metadata.topic}")
    print(f"  - Partition: {metadata.partition}")
    print(f"  - Offset:    {metadata.offset}")
    print(f"  - Event ID:  {payload['event_id']}")
    print(f"  - Timestamp: {payload['event_time']}")
    print("=" * 60)
    return payload

def handle_text(args, producer):
    print("\n--- [MODE A: CRISIS TEXT INTELLIGENCE] ---")
    root = Path(__file__).resolve().parent.parent.parent
    
    text = args.text
    if args.file:
        with open(args.file, "r") as f:
            data = json.load(f)
            text = data[0]["text"] if isinstance(data, list) else data.get("text", "")
            
    if not text:
        text = input("Enter Crisis Text/Tweet to analyze:\n> ").strip()
        if not text:
            text = "CRITICAL: Embankment collapsed in Sector 5! Need urgent rescue boats and evacuation assistance."

    print(f"\nInput Text: \"{text}\"")
    
    # Load Phase 7 CrisisMMD Model
    import joblib
    vec_path = root / "models" / "crisis_information" / "crisismmd" / "crisismmd_tfidf_vectorizer.joblib"
    model_path = root / "models" / "crisis_information" / "crisismmd" / "crisismmd_baseline_logistic.joblib"
    
    if not vec_path.exists() or not model_path.exists():
        print(f"[ERROR] Phase 7 model files missing: {model_path}")
        sys.exit(1)
        
    t0 = time.time()
    vectorizer = joblib.load(vec_path)
    model = joblib.load(model_path)
    
    categories = [
        "affected_individuals",
        "infrastructure_and_utility_damage",
        "not_humanitarian",
        "other_relevant_information",
        "rescue_volunteering_or_donation_effort"
    ]
    
    X = vectorizer.transform([text])
    pred_idx = int(model.predict(X)[0])
    probs = model.predict_proba(X)[0]
    latency_ms = (time.time() - t0) * 1000
    
    predicted_cat = categories[pred_idx] if pred_idx < len(categories) else str(pred_idx)
    confidence = float(probs[pred_idx])
    
    print("\n--- Classification Results ---")
    print(f"  Predicted Category: {predicted_cat}")
    print(f"  Confidence:         {confidence * 100:.2f}%")
    print(f"  Inference Latency:  {latency_ms:.2f} ms")
    print("\nProbability Distribution:")
    for cat_name, prob in zip(categories, probs):
        bar = "#" * int(prob * 30)
        print(f"  - {cat_name:40s}: {prob*100:5.2f}% | {bar}")
        
    if args.publish:
        content_id = f"text_{uuid.uuid4().hex[:8]}"
        record = {
            "content_id": content_id,
            "source_dataset": "crisismmd_multimodal",
            "source_record_id": f"live_input_{int(time.time())}",
            "event_id": f"evt_live_{int(time.time())}",
            "text_available": True,
            "image_available": False,
            "crisis_category": predicted_cat,
            "task_name": "humanitarian_text_classification",
            "model_score": round(confidence, 4),
            "confidence": round(confidence, 4),
            "quality_status": "HIGH",
            "calibration_status": "UNCALIBRATED",
            "provenance": "crisisguard_live_cli_input",
            "model_version": "v1.0_tfidf_logistic",
            "prediction_timestamp": datetime.now(timezone.utc).isoformat()
        }
        if producer and not args.dry_run:
            producer.send(args.topic, key=content_id, value=record)
            producer.flush()
            print(f"\n[+] Published Crisis Intelligence Record to '{args.topic}'")

def handle_image(args, producer):
    print("\n--- [MODE A: SYNTHETIC MEDIA IMAGE FORENSICS] ---")
    root = Path(__file__).resolve().parent.parent.parent
    
    img_path = args.path
    if not img_path:
        default_img = root / "data" / "demo" / "input" / "sample_image.jpg"
        img_path = str(default_img)
        print(f"No image path specified. Using default demo asset: {img_path}")
        
    img_file = Path(img_path)
    if not img_file.exists():
        print(f"[ERROR] Image file does not exist: {img_file}")
        sys.exit(1)
        
    # Execute image inference using Unified Engine or direct ResNet-18
    sys.path.append(str(root / "scripts" / "synthetic_media"))
    from infer_media import UnifiedMediaInferenceEngine
    
    t0 = time.time()
    engine = UnifiedMediaInferenceEngine(config_path=str(root / "config" / "synthetic_media.yaml"))
    result = engine.infer_image(str(img_file), content_id=f"img_{uuid.uuid4().hex[:8]}")
    latency_ms = (time.time() - t0) * 1000
    
    synth_risk = result.get('synthetic_risk', result.get('synthetic_probability', 0.0))
    model_score = result.get('model_score', 0.0)
    print("\n--- Forensics Analysis Result ---")
    print(f"  Content ID:            {result['content_id']}")
    print(f"  Input File:            {img_file.name}")
    print(f"  Synthetic Media Risk:  {synth_risk:.4f}")
    print(f"  Raw Score (Logits):    {model_score:.4f}")
    cal_desc = "Platt Logistic Scaling / ResNet-18" if result.get("calibration_status") == "CALIBRATED_PLATT" else "Standard Sigmoid / Uncalibrated"
    print(f"  Calibration Status:    {result.get('calibration_status', 'UNCALIBRATED')} ({cal_desc})")
    print(f"  Inference Latency:     {latency_ms:.2f} ms")
    
    if args.publish and producer and not args.dry_run:
        producer.send(args.topic, key=result["content_id"], value=result)
        producer.flush()
        print(f"\n[+] Published Synthetic Media Risk Record to '{args.topic}'")

def handle_video(args, producer):
    print("\n--- [MODE A: SYNTHETIC MEDIA VIDEO FORENSICS] ---")
    root = Path(__file__).resolve().parent.parent.parent
    
    vid_path = args.path
    if not vid_path:
        default_vid = root / "data" / "demo" / "input" / "sample_video.gif"
        vid_path = str(default_vid)
        print(f"No video path specified. Using default demo asset: {vid_path}")
        
    vid_file = Path(vid_path)
    if not vid_file.exists():
        print(f"[ERROR] Video asset does not exist: {vid_file}")
        sys.exit(1)
        
    sys.path.append(str(root / "scripts" / "synthetic_media"))
    from infer_media import UnifiedMediaInferenceEngine
    
    t0 = time.time()
    engine = UnifiedMediaInferenceEngine(config_path=str(root / "config" / "synthetic_media.yaml"))
    result = engine.infer_video(str(vid_file), content_id=f"vid_{uuid.uuid4().hex[:8]}")
    latency_ms = (time.time() - t0) * 1000
    
    synth_risk = result.get('synthetic_risk', result.get('synthetic_probability', 0.0))
    model_score = result.get('model_score', 0.0)
    print("\n--- Video Temporal Forensics Result ---")
    print(f"  Content ID:            {result['content_id']}")
    print(f"  Input File:            {vid_file.name}")
    print(f"  Synthetic Media Risk:  {synth_risk:.4f}")
    print(f"  Raw Score (Logits):    {model_score:.4f}")
    print(f"  Classification:        {'SYNTHETIC / MANIPULATED' if synth_risk >= 0.5 else 'AUTHENTIC / REAL'}")
    print(f"  Calibration Status:    {result['calibration_status']} (Frozen Temporal Checkpoint)")
    print(f"  Inference Latency:     {latency_ms:.2f} ms")

def main():
    parser = argparse.ArgumentParser(
        description="CrisisGuard — Unified Live User Input CLI (Mode A)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--type", choices=["propagation", "text", "image", "video"], default="propagation",
                        help="Input modality type (default: propagation)")
    parser.add_argument("--topic", default="crisisguard-demo-events",
                        help="Kafka destination topic (default: crisisguard-demo-events)")
    parser.add_argument("--bootstrap-servers", default="localhost:9092",
                        help="Kafka bootstrap server address (default: localhost:9092)")
    parser.add_argument("--file", help="Path to input JSON / payload file")
    parser.add_argument("--dry-run", action="store_true", help="Validate without publishing to Kafka")
    parser.add_argument("--publish", action="store_true", help="Publish multimodal inferences to Kafka")
    
    # Propagation specific args
    parser.add_argument("--source-node", help="Source node ID (e.g. osm_node_1001)")
    parser.add_argument("--target-node", help="Target node ID (e.g. osm_node_1002)")
    parser.add_argument("--scenario", help="Scenario ID (e.g. flood_evacuation_live)")
    parser.add_argument("--risk", type=float, help="Synthetic media risk (0.0 to 1.0)")
    parser.add_argument("--priority", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], help="Crisis priority")
    parser.add_argument("--propagation-type", default="retweet_cascade", help="Propagation cascade type")
    parser.add_argument("--content-id", help="Associated media content ID")
    parser.add_argument("--parent-event-id", help="Parent event ID for cascades")
    parser.add_argument("--event-id", help="Explicit event ID (auto-generated if omitted)")
    
    # Text / Media specific args
    parser.add_argument("--text", help="Text or tweet content for crisis intelligence")
    parser.add_argument("--path", help="Path to image or video file for media forensics")
    
    args = parser.parse_args()
    
    producer = None
    if not args.dry_run and args.type == "propagation":
        producer = get_kafka_producer(args.bootstrap_servers)
    elif args.publish:
        producer = get_kafka_producer(args.bootstrap_servers)
        
    if args.type == "propagation":
        handle_propagation(args, producer)
    elif args.type == "text":
        handle_text(args, producer)
    elif args.type == "image":
        handle_image(args, producer)
    elif args.type == "video":
        handle_video(args, producer)
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
