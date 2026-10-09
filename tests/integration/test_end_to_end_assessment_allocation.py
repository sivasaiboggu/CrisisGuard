"""
CrisisGuard — End-to-End Integration Tests (Features A & B)
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Validates full workflow:
Raw Reports -> Extraction -> Misinformation Assessment -> Candidate Incident Formation
-> Resource Optimization -> Human Approval Audit Logging.
"""

import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from src.assessment.misinformation_assessor import MisinformationAssessor
from src.allocation.optimizer import EmergencyResourceOptimizer

class TestEndToEndAssessmentAllocation(unittest.TestCase):
    def setUp(self):
        self.assessor = MisinformationAssessor(repo_root=str(root))
        self.optimizer = EmergencyResourceOptimizer(repo_root=str(root))
        self.optimizer.inventory_manager.reset_inventory()

    def test_full_pipeline_flow(self):
        # 1. Raw multi-incident crisis stream
        raw_stream = [
            # Event 1: Real flood in Sector 5 (corroborated by NDMA Sitrep)
            {
                "claim_id": "stream_evt_01",
                "text": "Yamuna embankment breached in Sector 5! Urgent rescue boats needed for trapped families.",
                "location": "Sector 5",
                "coordinates": {"latitude": 6.7170, "longitude": 72.9486},
                "source_type": "CITIZEN_REPORT",
                "timestamp": "2026-10-09T10:00:00Z"
            },
            # Event 2: Fake bridge collapse (contradicted by CWC water gauge telemetry)
            {
                "claim_id": "stream_evt_02",
                "text": "Downtown bridge collapsed! All railway tracks destroyed by raging water!",
                "location": "Downtown bridge",
                "coordinates": {"latitude": 6.7176, "longitude": 72.9444},
                "source_type": "ANONYMOUS_TWITTER",
                "timestamp": "2026-10-09T10:02:00Z"
            },
            # Event 3: Unverified isolated claim
            {
                "claim_id": "stream_evt_03",
                "text": "Transformer burst in Sector 88, medical assistance required.",
                "location": "Sector 88",
                "coordinates": {"latitude": 6.7718, "longitude": 73.1271},
                "source_type": "TELEGRAM_CHANNEL",
                "timestamp": "2026-10-09T10:05:00Z"
            }
        ]

        # 2. Phase A: Evidence-Aware Assessment
        assessments = []
        for report in raw_stream:
            asmt = self.assessor.assess_claim(report)
            assessments.append(asmt)

        self.assertEqual(len(assessments), 3)
        self.assertEqual(assessments[0]["assessment_outcome"], "EVIDENCE_SUPPORTED")
        self.assertEqual(assessments[1]["assessment_outcome"], "CONTRADICTED_BY_EVIDENCE")
        self.assertIn(assessments[2]["assessment_outcome"], ["UNVERIFIED", "INSUFFICIENT_EVIDENCE"])

        # 3. Form Candidate Incidents for Resource Allocation
        candidate_incidents = []
        for asmt, raw in zip(assessments, raw_stream):
            # Extract requested resource type or default by category
            cand = {
                "incident_id": f"inc_{asmt['claim_id']}",
                "incident_category": asmt["crisis_category"],
                "urgency_level": "CRITICAL" if "breached" in raw["text"].lower() or "collapsed" in raw["text"].lower() else "MEDIUM",
                "verification_status": asmt["assessment_outcome"],
                "required_resource_type": "RESCUE_BOAT" if "boat" in raw["text"].lower() else "AMBULANCE",
                "demanded_quantity": 3 if "boat" in raw["text"].lower() else 1,
                "coordinates": raw.get("coordinates"),
                "human_approved": False
            }
            candidate_incidents.append(cand)

        # 4. Phase B: Optimization & Allocation
        allocations = self.optimizer.solve_allocation(candidate_incidents)
        self.assertEqual(len(allocations), 3)

        alloc_map = {a["incident_id"]: a for a in allocations}

        # Check Event 1 (Evidence Supported) -> RECOMMENDED
        a1 = alloc_map["inc_stream_evt_01"]
        self.assertEqual(a1["allocation_status"], "RECOMMENDED")
        self.assertEqual(a1["feasibility_status"], "FEASIBLE")
        self.assertEqual(a1["assigned_quantity"], 3)
        self.assertEqual(a1["unmet_quantity"], 0)
        self.assertEqual(a1["required_resource_type"], "RESCUE_BOAT")
        self.assertIn(a1["routing_method"], ["OSM_DIJKSTRA", "EUCLIDEAN_FALLBACK"])

        # Check Event 2 (Contradicted by Telemetry) -> INFEASIBLE (Blocked at Gate)
        a2 = alloc_map["inc_stream_evt_02"]
        self.assertEqual(a2["allocation_status"], "INFEASIBLE")
        self.assertEqual(a2["feasibility_status"], "UNVERIFIED_GATE")
        self.assertEqual(a2["assigned_quantity"], 0)
        self.assertIn("prohibited", a2["priority_rationale"].lower())

        # Check Event 3 (Unverified) -> AWAITING_APPROVAL
        a3 = alloc_map["inc_stream_evt_03"]
        self.assertEqual(a3["allocation_status"], "AWAITING_APPROVAL")
        self.assertEqual(a3["feasibility_status"], "UNVERIFIED_GATE")
        self.assertEqual(a3["assigned_quantity"], 0)

        # 5. Human-in-the-Loop Approval Test
        # Dispatcher manually verifies Event 3 via police radio and approves it
        candidate_incidents[2]["human_approved"] = True
        re_alloc = self.optimizer.solve_allocation([candidate_incidents[2]])
        self.assertEqual(re_alloc[0]["allocation_status"], "RECOMMENDED")
        self.assertEqual(re_alloc[0]["feasibility_status"], "FEASIBLE")
        self.assertEqual(re_alloc[0]["assigned_quantity"], 1)

if __name__ == "__main__":
    unittest.main()
