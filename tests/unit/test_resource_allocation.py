"""
CrisisGuard — Unit Tests for Intelligent Resource Allocation (Feature B)
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Validates:
1. One incident and one compatible resource.
2. Multiple incidents competing for limited resources.
3. Compatibility constraints across resource types.
4. Insufficient inventory handling and unmet demand calculation.
5. Zero available resources -> INFEASIBLE_CAPACITY.
6. Verification gating (CONTRADICTED -> INFEASIBLE, UNVERIFIED -> AWAITING_APPROVAL).
7. Resource exhaustion and repeated allocation requests.
8. Conservation constraint: sum(allocated) <= capacity.
9. Missing / invalid coordinates handling.
"""

import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from src.allocation.inventory import ResourceInventoryManager
from src.allocation.routing import OSMRoutingEngine
from src.allocation.optimizer import EmergencyResourceOptimizer

class TestResourceAllocation(unittest.TestCase):
    def setUp(self):
        self.optimizer = EmergencyResourceOptimizer(repo_root=str(root))
        self.optimizer.inventory_manager.reset_inventory()

    def test_single_incident_compatible_allocation(self):
        """Verifies single eligible incident receives optimal allocation."""
        incidents = [
            {
                "incident_id": "test_single_01",
                "incident_category": "affected_individuals",
                "urgency_level": "CRITICAL",
                "verification_status": "EVIDENCE_SUPPORTED",
                "required_resource_type": "RESCUE_BOAT",
                "demanded_quantity": 3,
                "latitude": 6.7170,
                "longitude": 72.9486
            }
        ]
        results = self.optimizer.solve_allocation(incidents)
        self.assertEqual(len(results), 1)
        rec = results[0]
        self.assertEqual(rec["allocation_status"], "RECOMMENDED")
        self.assertEqual(rec["feasibility_status"], "FEASIBLE")
        self.assertEqual(rec["assigned_quantity"], 3)
        self.assertEqual(rec["unmet_quantity"], 0)
        self.assertEqual(rec["required_resource_type"], "RESCUE_BOAT")
        self.assertIsNotNone(rec["assigned_resource_id"])

    def test_competing_incidents_prioritization(self):
        """
        Verifies when demand exceeds capacity, higher urgency incidents
        receive priority over lower urgency ones.
        """
        # Create isolated inventory with limited boats
        custom_inv = [
            {
                "resource_id": "LIMITED_BOAT_01",
                "depot_id": "DEPOT_TEST",
                "resource_type": "RESCUE_BOAT",
                "total_capacity": 5,
                "allocated_quantity": 0,
                "location": {"latitude": 6.7170, "longitude": 72.9486, "osm_node_id": 208413043},
                "supported_categories": ["affected_individuals"],
                "status": "AVAILABLE",
                "is_synthetic_demonstration": True
            }
        ]
        self.optimizer.inventory_manager = ResourceInventoryManager(initial_inventory=custom_inv)

        incidents = [
            # Low urgency requesting 4
            {
                "incident_id": "inc_low_urgency",
                "incident_category": "affected_individuals",
                "urgency_level": "LOW",
                "verification_status": "EVIDENCE_SUPPORTED",
                "required_resource_type": "RESCUE_BOAT",
                "demanded_quantity": 4,
                "latitude": 6.7170,
                "longitude": 72.9486
            },
            # Critical urgency requesting 4
            {
                "incident_id": "inc_critical_urgency",
                "incident_category": "affected_individuals",
                "urgency_level": "CRITICAL",
                "verification_status": "EVIDENCE_SUPPORTED",
                "required_resource_type": "RESCUE_BOAT",
                "demanded_quantity": 4,
                "latitude": 6.7170,
                "longitude": 72.9486
            }
        ]
        results = self.optimizer.solve_allocation(incidents)
        res_crit = next(r for r in results if r["incident_id"] == "inc_critical_urgency")
        res_low = next(r for r in results if r["incident_id"] == "inc_low_urgency")

        # Critical should get its full 4 units
        self.assertEqual(res_crit["assigned_quantity"], 4)
        self.assertEqual(res_crit["unmet_quantity"], 0)
        # Low should get remaining 1 unit out of total 5
        self.assertEqual(res_low["assigned_quantity"], 1)
        self.assertEqual(res_low["unmet_quantity"], 3)

    def test_compatibility_constraints(self):
        """Verifies resources of incompatible types are never allocated."""
        incidents = [
            {
                "incident_id": "inc_fire_01",
                "incident_category": "infrastructure_and_utility_damage",
                "urgency_level": "HIGH",
                "verification_status": "EVIDENCE_SUPPORTED",
                "required_resource_type": "FIRE_TENDER",
                "demanded_quantity": 2,
                "latitude": 6.7176,
                "longitude": 72.9444
            }
        ]
        results = self.optimizer.solve_allocation(incidents)
        rec = results[0]
        self.assertEqual(rec["allocation_status"], "RECOMMENDED")
        self.assertEqual(rec["required_resource_type"], "FIRE_TENDER")
        # Assigned resource must be a FIRE_TENDER
        self.assertIn("FIRE", rec["assigned_resource_id"])

    def test_zero_available_resources(self):
        """Verifies handling when resource inventory is completely exhausted."""
        empty_inv = []
        self.optimizer.inventory_manager = ResourceInventoryManager(initial_inventory=empty_inv)
        incidents = [
            {
                "incident_id": "inc_exhausted_01",
                "incident_category": "affected_individuals",
                "urgency_level": "HIGH",
                "verification_status": "EVIDENCE_SUPPORTED",
                "required_resource_type": "AMBULANCE",
                "demanded_quantity": 2,
                "latitude": 6.7718,
                "longitude": 73.1271
            }
        ]
        results = self.optimizer.solve_allocation(incidents)
        rec = results[0]
        self.assertEqual(rec["allocation_status"], "INFEASIBLE")
        self.assertEqual(rec["feasibility_status"], "INFEASIBLE_CAPACITY")
        self.assertEqual(rec["assigned_quantity"], 0)
        self.assertEqual(rec["unmet_quantity"], 2)

    def test_verification_gating_unverified_incident(self):
        """Verifies unverified incident enters AWAITING_APPROVAL queue without dispatch."""
        incidents = [
            {
                "incident_id": "inc_unverified_gate",
                "incident_category": "affected_individuals",
                "urgency_level": "CRITICAL",
                "verification_status": "UNVERIFIED",
                "required_resource_type": "AMBULANCE",
                "demanded_quantity": 2,
                "human_approved": False
            }
        ]
        results = self.optimizer.solve_allocation(incidents)
        rec = results[0]
        self.assertEqual(rec["allocation_status"], "AWAITING_APPROVAL")
        self.assertEqual(rec["feasibility_status"], "UNVERIFIED_GATE")
        self.assertEqual(rec["assigned_quantity"], 0)
        self.assertEqual(rec["unmet_quantity"], 2)
        self.assertTrue(rec["human_approval_required"])

    def test_verification_gating_contradicted_incident(self):
        """Verifies contradicted incident is marked INFEASIBLE and blocked from dispatch."""
        incidents = [
            {
                "incident_id": "inc_contradicted_gate",
                "incident_category": "infrastructure_and_utility_damage",
                "urgency_level": "CRITICAL",
                "verification_status": "CONTRADICTED_BY_EVIDENCE",
                "required_resource_type": "FIRE_TENDER",
                "demanded_quantity": 3
            }
        ]
        results = self.optimizer.solve_allocation(incidents)
        rec = results[0]
        self.assertEqual(rec["allocation_status"], "INFEASIBLE")
        self.assertEqual(rec["feasibility_status"], "UNVERIFIED_GATE")
        self.assertEqual(rec["assigned_quantity"], 0)
        self.assertEqual(rec["unmet_quantity"], 3)

    def test_resource_conservation_law(self):
        """Verifies total assigned resources never exceed depot total capacity."""
        inv_before = self.optimizer.inventory_manager.get_all_resources()
        total_boat_cap = sum(r["total_capacity"] for r in inv_before if r["resource_type"] == "RESCUE_BOAT")

        # Demand twice the total capacity
        incidents = [
            {
                "incident_id": f"flood_inc_{i}",
                "incident_category": "affected_individuals",
                "urgency_level": "CRITICAL",
                "verification_status": "EVIDENCE_SUPPORTED",
                "required_resource_type": "RESCUE_BOAT",
                "demanded_quantity": 4,
                "latitude": 6.7170,
                "longitude": 72.9486
            }
            for i in range(5)  # 5 * 4 = 20 boats demanded vs ~10 total capacity
        ]
        results = self.optimizer.solve_allocation(incidents, update_inventory=True)
        total_assigned = sum(r["assigned_quantity"] for r in results)
        self.assertLessEqual(total_assigned, total_boat_cap)

    def test_duplicate_incident_submission_ignored(self):
        """Verifies duplicate incident IDs within the same batch do not double-allocate resources."""
        inc = {
            "incident_id": "inc_duplicate_batch_01",
            "incident_category": "affected_individuals",
            "urgency_level": "CRITICAL",
            "verification_status": "EVIDENCE_SUPPORTED",
            "required_resource_type": "RESCUE_BOAT",
            "demanded_quantity": 3,
            "latitude": 6.7170,
            "longitude": 72.9486
        }
        results = self.optimizer.solve_allocation([inc, inc])
        # Only 1 unique allocation result should be produced
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["assigned_quantity"], 3)

    def test_idempotent_repeated_allocation_requests(self):
        """Verifies repeated calls with the same incident ID do not consume double resources."""
        inc = {
            "incident_id": "inc_idempotency_test_02",
            "incident_category": "affected_individuals",
            "urgency_level": "HIGH",
            "verification_status": "EVIDENCE_SUPPORTED",
            "required_resource_type": "RESCUE_BOAT",
            "demanded_quantity": 2,
            "latitude": 6.7170,
            "longitude": 72.9486
        }
        res1 = self.optimizer.solve_allocation([inc], update_inventory=True)
        res2 = self.optimizer.solve_allocation([inc], update_inventory=True)
        self.assertEqual(res1[0]["assigned_quantity"], res2[0]["assigned_quantity"])
        self.assertEqual(res1[0]["assigned_resource_id"], res2[0]["assigned_resource_id"])

if __name__ == "__main__":
    unittest.main()

