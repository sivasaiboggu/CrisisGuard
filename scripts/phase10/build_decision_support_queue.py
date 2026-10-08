#!/usr/bin/env python3
"""
CrisisGuard — Phase 10 Decision-Support Queue & Evidence Aggregator
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard — Scientific Hardening Pass

Builds an evidence-aware, non-autonomous human review queue:
1. Aggregates multi-stream evidence (Media risk, Crisis text category, Graph centrality, Spatial context).
2. Assigns rule-based, interpretable Review Priority Tiers without arbitrary linear weighting formulas (No EDPI):
   - TIER_1_URGENT_HUMAN_TRIAGE: High synthetic risk (>=0.80) OR Critical Humanitarian Need (rescue / infrastructure)
   - TIER_2_ELEVATED_VERIFICATION: Moderate synthetic risk (0.50 <= r < 0.80) OR high-degree propagation hub
   - TIER_3_ROUTINE_MONITORING: Standard information / low synthetic risk
3. Enforces strict Human-in-the-Loop Governance:
   - Flag: human_verification_required = True
   - Operational Scope: STRICTLY DECISION SUPPORT — NOT AUTONOMOUS DISPATCH
   - Explicitly records uncertainty and calibration status (CALIBRATED_PLATT vs UNCALIBRATED).
4. Saves queue to data/features/phase10/human_review_queue.parquet and docs/phase10/decision_support_summary.json.
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np

def build_decision_support():
    print("=" * 75)
    print("CRISISGUARD — PHASE 10 DECISION-SUPPORT & HUMAN TRIAGE QUEUE")
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("=" * 75)

    root = Path(__file__).resolve().parent.parent.parent
    p6_cal = root / "models" / "synthetic_media" / "calibration" / "calibrated_image_predictions.parquet"
    p6_raw = root / "data" / "features" / "synthetic_media" / "unified_media_risk.parquet"
    p7_file = root / "data" / "features" / "crisis_information" / "unified_crisis_intelligence.parquet"
    p8_gx = root / "data" / "features" / "phase8" / "graph" / "graphx_vertex_metrics.csv"
    
    out_feat = root / "data" / "features" / "phase10"
    out_docs = root / "docs" / "phase10"
    out_feat.mkdir(parents=True, exist_ok=True)
    out_docs.mkdir(parents=True, exist_ok=True)

    print("\n[1] Aggregating Cross-Stream Evidence Records...")
    # Load calibrated images if present, fallback to raw
    if p6_cal.exists():
        df_media = pd.read_parquet(p6_cal)
        print(f"  Loaded calibrated image predictions: N={len(df_media)}")
    else:
        df_media = pd.read_parquet(p6_raw)
        print(f"  Loaded baseline media risks: N={len(df_media)}")

    df_crisis = pd.read_parquet(p7_file)
    df_graph = pd.read_csv(p8_gx)

    now_iso = datetime.now(timezone.utc).isoformat()
    triage_records = []

    # 1. Process Stream A: Synthetic Media Risk Items
    print("\n[2] Triaging Stream A (Synthetic Media Forensics)...")
    for _, r in df_media.iterrows():
        risk = float(r.get("synthetic_risk", 0.5))
        cal_status = str(r.get("calibration_status", "UNCALIBRATED"))
        cid = str(r["content_id"])
        
        if risk >= 0.80:
            priority = "TIER_1_URGENT_HUMAN_TRIAGE"
            rationale = f"Elevated synthetic media risk ({risk:.4f} >= 0.80). Forensic verification required to avert false crisis dissemination."
        elif risk >= 0.50:
            priority = "TIER_2_ELEVATED_VERIFICATION"
            rationale = f"Moderate synthetic media risk ({risk:.4f}). Secondary verification recommended."
        else:
            priority = "TIER_3_ROUTINE_MONITORING"
            rationale = f"Low synthetic media risk ({risk:.4f}). Consistent with authentic media baseline."

        triage_records.append({
            "queue_id": f"triage_media_{cid}",
            "stream_source": "STREAM_A_SYNTHETIC_MEDIA",
            "entity_identifier": cid,
            "evidence_summary": rationale,
            "synthetic_media_risk": round(risk, 4),
            "crisis_category": None,
            "topological_pagerank": None,
            "calibration_status": cal_status,
            "review_priority": priority,
            "human_verification_required": True,
            "dispatch_scope": "DECISION_SUPPORT_ONLY_NO_AUTONOMOUS_DISPATCH",
            "provenance": str(r.get("provenance", "CrisisGuard_Phase6")),
            "triage_timestamp": now_iso
        })

    # 2. Process Stream B: High-Priority Crisis Information Items (Sampling critical alerts)
    print("[3] Triaging Stream B (Disaster Response Intelligence)...")
    urgent_categories = {
        "rescue_volunteering_or_donation_effort",
        "infrastructure_and_utility_damage",
        "affected_individuals",
        "injured_or_dead_people",
        "requests_or_urgent_needs"
    }

    # Take a representative stratified sample of crisis records for the human triage queue
    sample_crisis = df_crisis.sample(n=min(500, len(df_crisis)), random_state=42)
    for idx, r in sample_crisis.iterrows():
        cat = str(r.get("crisis_category", "other_relevant_information"))
        conf = float(r.get("confidence", 0.5)) if pd.notna(r.get("confidence")) else 0.5
        rid = str(r.get("source_record_id", idx))
        
        if cat in urgent_categories and conf >= 0.60:
            priority = "TIER_1_URGENT_HUMAN_TRIAGE"
            rationale = f"High-confidence alert in urgent category '{cat}' (Confidence: {conf:.2%}). Human operator validation required for relief prioritization."
        elif cat in urgent_categories:
            priority = "TIER_2_ELEVATED_VERIFICATION"
            rationale = f"Humanitarian alert in urgent category '{cat}' with moderate confidence ({conf:.2%})."
        else:
            priority = "TIER_3_ROUTINE_MONITORING"
            rationale = f"Informational or non-urgent report: '{cat}'."

        triage_records.append({
            "queue_id": f"triage_crisis_{idx}",
            "stream_source": "STREAM_B_CRISIS_INFORMATION",
            "entity_identifier": rid,
            "evidence_summary": rationale,
            "synthetic_media_risk": None,
            "crisis_category": cat,
            "topological_pagerank": None,
            "calibration_status": str(r.get("calibration_status", "UNCALIBRATED")),
            "review_priority": priority,
            "human_verification_required": True,
            "dispatch_scope": "DECISION_SUPPORT_ONLY_NO_AUTONOMOUS_DISPATCH",
            "provenance": str(r.get("provenance", "CrisisGuard_Phase7")),
            "triage_timestamp": now_iso
        })

    # 3. Process Stream C: Top Topological Propagation Hubs
    print("[4] Triaging Stream C (Propagation Network Hubs)...")
    top_hubs = df_graph.sort_values(by="pagerank", ascending=False).head(50)
    for _, r in top_hubs.iterrows():
        pr_val = float(r["pagerank"])
        tot_deg = int(r["in_degree"] + r["out_degree"])
        v_name = str(r["node_name"])
        
        if pr_val >= 10.0:
            priority = "TIER_1_URGENT_HUMAN_TRIAGE"
            rationale = f"Extreme topological structural hub (PageRank={pr_val:.2f}, Degree={tot_deg}). Dissemination bottleneck with high broadcast reach."
        else:
            priority = "TIER_2_ELEVATED_VERIFICATION"
            rationale = f"Prominent propagation node (PageRank={pr_val:.2f}, Degree={tot_deg}). Network diffusion monitor recommended."

        triage_records.append({
            "queue_id": f"triage_hub_{int(r['vertex_id'])}",
            "stream_source": "STREAM_C_PROPAGATION_GRAPH",
            "entity_identifier": v_name,
            "evidence_summary": rationale,
            "synthetic_media_risk": None,
            "crisis_category": None,
            "topological_pagerank": round(pr_val, 4),
            "calibration_status": "NOT_APPLICABLE",
            "review_priority": priority,
            "human_verification_required": True,
            "dispatch_scope": "DECISION_SUPPORT_ONLY_NO_AUTONOMOUS_DISPATCH",
            "provenance": "CrisisGuard_Phase8_GraphX",
            "triage_timestamp": now_iso
        })

    # Convert to DataFrame
    df_queue = pd.DataFrame(triage_records)
    queue_parquet = out_feat / "human_review_queue.parquet"
    df_queue.to_parquet(queue_parquet, index=False)
    print(f"\n[5] Serialized {len(df_queue)} human review items to: {queue_parquet}")

    # Summary Statistics
    priority_counts = df_queue["review_priority"].value_counts().to_dict()
    stream_counts = df_queue["stream_source"].value_counts().to_dict()

    print("\nReview Priority Distribution:")
    for p, c in priority_counts.items():
        print(f"  - {p:32s}: {c:4d} ({c/len(df_queue)*100:5.2f}%)")

    summary_payload = {
        "title": "Decision Support & Human Review Queue Summary",
        "author": "B.SIVASAI (Roll Number: 2023BCS0228)",
        "course": "CSE412 — Big Data & Large-Scale Computing",
        "date": "2026-10-02",
        "total_queue_items": len(df_queue),
        "priority_breakdown": priority_counts,
        "stream_breakdown": stream_counts,
        "governance_guarantees": {
            "human_in_the_loop_enforced": True,
            "zero_arbitrary_dispatch_weights": True,
            "autonomous_dispatch_forbidden": True,
            "uncertainty_surfacing": "Calibrated probabilities (Platt) and uncalibrated scores strictly flagged."
        }
    }

    summary_file = out_docs / "decision_support_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary_payload, f, indent=2)
    print(f"Serialized summary report to: {summary_file}")
    print("=" * 75)
    return 0

if __name__ == "__main__":
    sys.exit(build_decision_support())
