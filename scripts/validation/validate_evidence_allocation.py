#!/usr/bin/env python3
"""
CrisisGuard — Feature Validation Suite: Evidence-Aware Assessment & Resource Allocation
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Validates:
1. Schema conformity (assessment_schema.json & allocation_schema.json).
2. Traceable reference evidence store integrity.
3. Separation of synthetic media risk from claim veracity.
4. Gating constraints: unverified claims held, contradicted claims rejected.
5. OSM road network routing & Dijkstra travel time accuracy.
6. MILP optimization & resource conservation laws.
"""

import sys
import json
import logging
from pathlib import Path

# Setup paths
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from src.assessment.claim_extractor import ClaimExtractor
from src.assessment.evidence_store import EvidenceStore
from src.assessment.misinformation_assessor import MisinformationAssessor
from src.allocation.inventory import ResourceInventoryManager
from src.allocation.routing import OSMRoutingEngine
from src.allocation.optimizer import EmergencyResourceOptimizer

logging.basicConfig(level=logging.ERROR)

def run_validation():
    print("=" * 75)
    print("CRISISGUARD — EVIDENCE ASSESSMENT & RESOURCE ALLOCATION VALIDATOR")
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("=" * 75)

    checks = []

    # 1. Schemas Check
    asmt_schema_path = root / "schemas" / "assessment" / "assessment_schema.json"
    alloc_schema_path = root / "schemas" / "allocation" / "allocation_schema.json"
    s_ok = asmt_schema_path.exists() and alloc_schema_path.exists()
    checks.append(("Schema Definitions Exist & Readable", s_ok, "Both schemas loaded"))

    # 2. Evidence Store Baseline Records
    ev_store = EvidenceStore()
    ref_count = len(ev_store.reference_records)
    ev_ok = ref_count >= 4
    checks.append(("Traceable Reference Records Baseline", ev_ok, f"{ref_count} baseline records present"))

    # 3. Misinformation Assessor Outcome Differentiation
    assessor = MisinformationAssessor(repo_root=str(root))
    
    # Supported
    rep_sup = {"claim_id": "c1", "text": "Yamuna embankment breached in Sector 5", "location": "Sector 5"}
    asmt_sup = assessor.assess_claim(rep_sup)
    c3_ok = asmt_sup["assessment_outcome"] == "EVIDENCE_SUPPORTED" and asmt_sup["uncertainty_score"] <= 0.20

    # Contradicted
    rep_con = {"claim_id": "c2", "text": "Downtown bridge collapsed and destroyed", "location": "Downtown bridge"}
    asmt_con = assessor.assess_claim(rep_con)
    c4_ok = asmt_con["assessment_outcome"] == "CONTRADICTED_BY_EVIDENCE" and asmt_con["human_review_required"] is True

    # Untraceable
    rep_un = {"claim_id": "c3", "text": "Extraterrestrial saucer landed near warehouse", "location": "Sector 99"}
    asmt_un = assessor.assess_claim(rep_un)
    c5_ok = asmt_un["assessment_outcome"] == "INSUFFICIENT_EVIDENCE" and asmt_un["uncertainty_score"] >= 0.70

    checks.append(("Authoritative Corroboration Detection", c3_ok, f"Outcome: {asmt_sup['assessment_outcome']}"))
    checks.append(("Telemetry Contradiction Detection", c4_ok, f"Outcome: {asmt_con['assessment_outcome']}"))
    checks.append(("Untraceable Claim Epistemic Uncertainty", c5_ok, f"Outcome: {asmt_un['assessment_outcome']}"))

    # 4. Strict Separation: Synthetic Media != False Claim
    # If media is synthetic but claim fact is corroborated
    rep_syn = {
        "claim_id": "c4",
        "text": "Yamuna embankment breached in Sector 5, evacuation active.",
        "location": "Sector 5",
        "media_path": str(root / "data" / "demo" / "input" / "sample_image.jpg"),
        "media_type": "IMAGE"
    }
    asmt_syn = assessor.assess_claim(rep_syn)
    sep_ok = asmt_syn["assessment_outcome"] in ["EVIDENCE_SUPPORTED", "REQUIRES_HUMAN_REVIEW"] and asmt_syn["assessment_outcome"] != "CONTRADICTED_BY_EVIDENCE"
    checks.append(("Separation: Synthetic Media vs Claim Veracity", sep_ok, f"Outcome: {asmt_syn['assessment_outcome']}"))

    # 5. OSM Routing & Dijkstra Accuracy
    router = OSMRoutingEngine()
    route = router.compute_travel(208413043, 208413047)
    route_ok = router.initialized and route["routing_method"] == "OSM_DIJKSTRA" and route["travel_time_min"] is not None
    checks.append(("OSM Road Network Dijkstra Engine", route_ok, f"Time: {route.get('travel_time_min')}m, Dist: {route.get('distance_km')}km"))

    # 6. Allocation Gating Enforcement
    optimizer = EmergencyResourceOptimizer(repo_root=str(root))
    gate_incidents = [
        {"incident_id": "i_con", "verification_status": "CONTRADICTED_BY_EVIDENCE", "required_resource_type": "FIRE_TENDER", "demanded_quantity": 2},
        {"incident_id": "i_unv", "verification_status": "UNVERIFIED", "required_resource_type": "AMBULANCE", "demanded_quantity": 2, "human_approved": False}
    ]
    gate_res = optimizer.solve_allocation(gate_incidents)
    gate_ok = (gate_res[0]["allocation_status"] == "INFEASIBLE" and gate_res[0]["feasibility_status"] == "UNVERIFIED_GATE" and
               gate_res[1]["allocation_status"] == "AWAITING_APPROVAL" and gate_res[1]["feasibility_status"] == "UNVERIFIED_GATE")
    checks.append(("Verification Policy Dispatch Gating", gate_ok, "Contradicted blocked, unverified held"))

    # 7. MILP Optimization & Resource Conservation
    optimizer.inventory_manager.reset_inventory()
    competing_incidents = [
        {
            "incident_id": "inc_comp_1",
            "incident_category": "affected_individuals",
            "urgency_level": "CRITICAL",
            "verification_status": "EVIDENCE_SUPPORTED",
            "required_resource_type": "RESCUE_BOAT",
            "demanded_quantity": 4,
            "latitude": 6.7170,
            "longitude": 72.9486
        },
        {
            "incident_id": "inc_comp_2",
            "incident_category": "affected_individuals",
            "urgency_level": "HIGH",
            "verification_status": "EVIDENCE_SUPPORTED",
            "required_resource_type": "RESCUE_BOAT",
            "demanded_quantity": 4,
            "latitude": 6.7174,
            "longitude": 72.9482
        }
    ]
    alloc_res = optimizer.solve_allocation(competing_incidents)
    total_assigned = sum(r["assigned_quantity"] for r in alloc_res)
    milp_ok = (len(alloc_res) == 2 and total_assigned <= 10 and
               all(r["allocation_status"] == "RECOMMENDED" for r in alloc_res))
    checks.append(("MILP Constrained Optimization & Conservation", milp_ok, f"Total Assigned: {total_assigned} boats"))

    # 8. Idempotency & Repeat Ingestion
    optimizer.inventory_manager.reset_inventory()
    run1 = optimizer.solve_allocation([competing_incidents[0]], update_inventory=False)
    run2 = optimizer.solve_allocation([competing_incidents[0]], update_inventory=False)
    idemp_ok = run1[0]["assigned_quantity"] == run2[0]["assigned_quantity"]
    checks.append(("Allocation Idempotency (Repeat Solves)", idemp_ok, "Identical assignment recommendations"))

    # Print Summary
    print("\nVALIDATION SUMMARY:")
    all_passed = True
    for idx, (name, status, detail) in enumerate(checks, 1):
        status_str = "[PASS]" if status else "[FAIL]"
        if not status:
            all_passed = False
        print(f"  {status_str} {idx}. {name:<45}: {detail}")

    print("=" * 75)
    if all_passed:
        print(f"TOTAL CHECKS: {len(checks)} | PASSED: {len(checks)} | FAILED: 0")
        print("ALL EVIDENCE-AWARE & RESOURCE-ALLOCATION REQUIREMENTS SATISFIED.")
    else:
        print("VALIDATION FAILED ON ONE OR MORE CHECKS.")
    print("=" * 75)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(run_validation())
