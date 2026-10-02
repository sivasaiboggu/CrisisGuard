#!/usr/bin/env python3
"""
CrisisGuard: Semi-Synthetic Propagation Cascade Generator
Author: B.SIVASAI (Roll No: 2023BCS0228)

Generates controlled, reproducible social media diffusion cascades binding
authentic crisis/synthetic-media content IDs with scale-free and small-world
amplification topologies.

STRICT GOVERNANCE PROTOCOL:
All generated records are explicitly labeled with `governance_tag: "SEMI_SYNTHETIC"`.
Under no circumstances are these represented as real historical Twitter/X logs.
"""

import os
import sys
import json
import csv
import random
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Seed anchor content IDs derived from official datasets
AUTHENTIC_CONTENT_SEEDS = [
    {
        "content_id": "humaid_irma_2017_001928",
        "dataset_origin": "HumAID",
        "hazard_type": "hurricane",
        "category": "infrastructure_and_utility_damage",
        "base_urgency": 0.88,
        "base_synthetic_risk": 0.05  # Authentic ground truth
    },
    {
        "content_id": "dfdc_syn_bridge_collapse_84920",
        "dataset_origin": "DFDC",
        "hazard_type": "infrastructure_sabotage",
        "category": "rescue_volunteering_effort",
        "base_urgency": 0.95,
        "base_synthetic_risk": 0.92  # Weaponized deepfake
    },
    {
        "content_id": "crisismmd_harvey_img_49102",
        "dataset_origin": "CrisisMMD",
        "hazard_type": "flood",
        "category": "severe_damage",
        "base_urgency": 0.82,
        "base_synthetic_risk": 0.12
    },
    {
        "content_id": "ff_face2face_mayoral_evac_0091",
        "dataset_origin": "FaceForensics++",
        "hazard_type": "civil_unrest",
        "category": "caution_and_advice",
        "base_urgency": 0.90,
        "base_synthetic_risk": 0.96  # Manipulated official statement
    },
    {
        "content_id": "crisislex_california_fire_81729",
        "dataset_origin": "CrisisLex",
        "hazard_type": "wildfire",
        "category": "injured_or_dead_people",
        "base_urgency": 0.93,
        "base_synthetic_risk": 0.08
    }
]

SCENARIO_PROFILES = [
    "ORGANIC_DIFFUSION",
    "COORDINATED_BOT_BURST",
    "HIGH_VELOCITY_VIRAL",
    "LOW_VELOCITY_LOCAL",
    "MULTI_SOURCE_COLLUSION"
]

def generate_cascades(output_dir: Path, num_events: int = 5000, seed: int = 42):
    random.seed(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    events_file = output_dir / "events.jsonl"
    edges_file = output_dir / "edges.csv"
    summary_file = output_dir / "generator_summary.json"

    base_time = datetime(2026, 9, 27, 0, 0, 0, tzinfo=timezone.utc)
    
    events = []
    edges = []
    
    # Active cascade trees tracked per seed content
    active_trees = {}
    for item in AUTHENTIC_CONTENT_SEEDS:
        cid = item["content_id"]
        scenario = random.choice(SCENARIO_PROFILES)
        root_user = random.randint(1000, 9999)
        root_event_id = f"evt_{cid[:10]}_0000"
        
        root_event = {
            "event_id": root_event_id,
            "content_id": cid,
            "source_node": root_user,
            "target_node": None,
            "timestamp": base_time.isoformat(),
            "parent_event_id": None,
            "propagation_type": "ROOT_BROADCAST",
            "synthetic_media_risk": item["base_synthetic_risk"],
            "crisis_priority": item["base_urgency"],
            "scenario_id": scenario,
            "governance_tag": "SEMI_SYNTHETIC"
        }
        events.append(root_event)
        active_trees[cid] = {
            "meta": item,
            "scenario": scenario,
            "nodes": [root_user],
            "event_ids": [root_event_id],
            "current_time": base_time,
            "edge_count": 0
        }

    # Generate cascade steps using preferential attachment and burst dynamics
    event_idx = 1
    cids = list(active_trees.keys())
    
    while event_idx < num_events:
        cid = random.choice(cids)
        tree = active_trees[cid]
        scenario = tree["scenario"]
        
        # Determine time delta based on scenario velocity
        if scenario == "COORDINATED_BOT_BURST":
            dt_seconds = random.uniform(0.1, 2.5)  # Automated burst within seconds
            prop_type = "BOT_AMPLIFIED"
            risk_noise = random.uniform(-0.02, +0.03)
        elif scenario == "HIGH_VELOCITY_VIRAL":
            dt_seconds = random.uniform(1.0, 15.0)
            prop_type = "HIGH_VELOCITY_SHARE"
            risk_noise = random.uniform(-0.05, +0.05)
        elif scenario == "MULTI_SOURCE_COLLUSION":
            dt_seconds = random.uniform(0.5, 5.0)
            prop_type = "COLLUSIVE_AMPLIFICATION"
            risk_noise = random.uniform(-0.03, +0.04)
        else: # ORGANIC / LOW_VELOCITY
            dt_seconds = random.uniform(10.0, 180.0)
            prop_type = "ORGANIC_RETWEET"
            risk_noise = random.uniform(-0.08, +0.08)

        tree["current_time"] += timedelta(seconds=dt_seconds)
        event_time_str = tree["current_time"].isoformat()
        
        # Preferential attachment: higher probability to amplify super-spreader nodes
        target_node = random.choice(tree["nodes"])
        parent_event_id = random.choice(tree["event_ids"])
        new_user_id = random.randint(10000, 999999)
        tree["nodes"].append(new_user_id)
        
        event_id = f"evt_{cid[:10]}_{event_idx:05d}"
        tree["event_ids"].append(event_id)
        
        # Clamp risks between 0.0 and 1.0
        syn_risk = max(0.0, min(1.0, round(tree["meta"]["base_synthetic_risk"] + risk_noise, 4)))
        urgency = max(0.0, min(1.0, round(tree["meta"]["base_urgency"] + random.uniform(-0.05, 0.05), 4)))

        event = {
            "event_id": event_id,
            "content_id": cid,
            "source_node": new_user_id,
            "target_node": target_node,
            "timestamp": event_time_str,
            "parent_event_id": parent_event_id,
            "propagation_type": prop_type,
            "synthetic_media_risk": syn_risk,
            "crisis_priority": urgency,
            "scenario_id": scenario,
            "governance_tag": "SEMI_SYNTHETIC"
        }
        events.append(event)
        
        # Edge representation for GraphX
        edge_id = f"edge_{new_user_id}_{target_node}_{event_idx}"
        edge = {
            "edge_id": edge_id,
            "source_node": new_user_id,
            "target_node": target_node,
            "content_id": cid,
            "timestamp": event_time_str,
            "edge_weight": 1.0,
            "governance_tag": "SEMI_SYNTHETIC"
        }
        edges.append(edge)
        tree["edge_count"] += 1
        event_idx += 1

    # Write events to JSON Lines (Kafka payload format)
    with open(events_file, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    # Write edges to CSV (GraphX edge format)
    with open(edges_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["edge_id", "source_node", "target_node", "content_id", "timestamp", "edge_weight", "governance_tag"])
        writer.writeheader()
        writer.writerows(edges)

    summary = {
        "generator_version": "1.0.0",
        "timestamp_generated": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "total_events": len(events),
        "total_edges": len(edges),
        "seed_content_count": len(AUTHENTIC_CONTENT_SEEDS),
        "scenarios_simulated": SCENARIO_PROFILES,
        "governance_classification": "SEMI_SYNTHETIC",
        "output_files": [
            str(events_file.relative_to(output_dir.parent.parent)),
            str(edges_file.relative_to(output_dir.parent.parent))
        ]
    }

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Generated {len(events)} propagation events and {len(edges)} cascade edges in: {output_dir}")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CrisisGuard Semi-Synthetic Propagation Generator")
    parser.add_argument("--events", type=int, default=5000, help="Number of propagation events to simulate")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")
    parser.add_argument("--output", type=str, default="data/generated/propagation", help="Output directory")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent
    target_out = project_root / args.output
    generate_cascades(target_out, num_events=args.events, seed=args.seed)
