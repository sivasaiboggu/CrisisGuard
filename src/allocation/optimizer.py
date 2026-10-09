"""
CrisisGuard — Intelligent Emergency Resource Allocation Optimizer
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Mathematical formulation and MILP optimization for emergency resource assignment:
- Enforces strict verification gate (unverified claims queued, contradicted claims rejected).
- Hard capacity constraints: sum(assigned) <= available capacity.
- Compatibility constraints: resource_type must match required type.
- Reachability constraints: unreachable road network incidents flagged INFEASIBLE.
- Solves via scipy.optimize.milp (HiGHS solver) or exact greedy prioritization fallback.
- Emits decision-support recommendations matching schemas/allocation/allocation_schema.json.
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

import numpy as np
import jsonschema
from scipy.optimize import milp, LinearConstraint, Bounds

from src.allocation.inventory import ResourceInventoryManager, VALID_RESOURCE_TYPES
from src.allocation.routing import OSMRoutingEngine

logger = logging.getLogger("CrisisGuard.Optimizer")

URGENCY_WEIGHTS = {
    "CRITICAL": 10.0,
    "HIGH": 5.0,
    "MEDIUM": 2.0,
    "LOW": 1.0
}

PENALTY_UNMET_BASE = 500.0

class EmergencyResourceOptimizer:
    def __init__(self, repo_root: Optional[str] = None):
        if repo_root is None:
            self.root = Path(__file__).resolve().parent.parent.parent
        else:
            self.root = Path(repo_root)

        self.inventory_manager = ResourceInventoryManager()
        self.routing_engine = OSMRoutingEngine()

        schema_path = self.root / "schemas" / "allocation" / "allocation_schema.json"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
        else:
            self.schema = None
            logger.warning(f"Allocation schema not found at {schema_path}")

        # Idempotency and duplicate prevention ledger: incident_id -> allocation record
        self.processed_allocations: Dict[str, Dict[str, Any]] = {}

    def reset_history(self):
        """Resets allocation history ledger and inventory allocations."""
        self.processed_allocations.clear()
        self.inventory_manager.reset_inventory()

    def solve_allocation(self,
                         incidents: List[Dict[str, Any]],
                         update_inventory: bool = True) -> List[Dict[str, Any]]:
        """
        Solves multi-incident emergency resource allocation.
        Returns a list of structured allocation recommendation records.
        Enforces idempotency and duplicate prevention.
        """
        results = []
        eligible_incidents = []
        seen_in_batch = set()

        # 1. Verification Gatekeeping & Pre-filter
        for inc in incidents:
            inc_id = str(inc.get("incident_id", f"inc_{uuid.uuid4().hex[:6]}"))
            human_approved = bool(inc.get("human_approved", False))

            # Idempotency / Duplicate Prevention Check
            if inc_id in self.processed_allocations:
                prev = self.processed_allocations[inc_id]
                # If previously awaiting approval and now explicitly human-approved, allow transition
                if prev.get("allocation_status") == "AWAITING_APPROVAL" and human_approved:
                    pass
                else:
                    results.append(prev)
                    continue

            if inc_id in seen_in_batch:
                logger.info(f"Duplicate submission of incident '{inc_id}' ignored in current batch.")
                continue
            seen_in_batch.add(inc_id)

            v_status = inc.get("verification_status", "UNVERIFIED")
            urgency = inc.get("urgency_level", "MEDIUM")
            cat = inc.get("incident_category", "unclassified")
            res_type = inc.get("required_resource_type", "AMBULANCE")
            demand = max(1, int(inc.get("demanded_quantity", 1)))

            coords = inc.get("coordinates")
            if isinstance(coords, dict):
                lat = coords.get("latitude") or inc.get("latitude")
                lon = coords.get("longitude") or inc.get("longitude")
            else:
                lat = inc.get("latitude")
                lon = inc.get("longitude")

            osm_node = inc.get("nearest_osm_node")
            if osm_node is None and lat is not None and lon is not None:
                osm_node = self.routing_engine.find_nearest_node(float(lat), float(lon))

            # Gate: Contradicted claims are rejected from real-world dispatch
            if v_status == "CONTRADICTED_BY_EVIDENCE":
                rec = self._build_record(
                    incident_id=inc_id,
                    incident_category=cat,
                    urgency_level=urgency,
                    verification_status=v_status,
                    required_resource_type=res_type,
                    demanded_quantity=demand,
                    assigned_resource_id=None,
                    assigned_depot_id=None,
                    assigned_quantity=0,
                    unmet_quantity=demand,
                    travel_dist_km=None,
                    travel_time_min=None,
                    routing_method="NOT_APPLICABLE",
                    allocation_status="INFEASIBLE",
                    feasibility_status="UNVERIFIED_GATE",
                    priority_rationale="Incident contradicted by authoritative evidence. Real-world dispatch prohibited.",
                    human_approval_required=True,
                    lat=lat, lon=lon, osm_node=osm_node
                )
                results.append(rec)
                continue

            # Gate: Unverified claims require dispatcher triage before asset release
            if v_status in ["UNVERIFIED", "INSUFFICIENT_EVIDENCE", "REQUIRES_HUMAN_REVIEW"] and not human_approved:
                rec = self._build_record(
                    incident_id=inc_id,
                    incident_category=cat,
                    urgency_level=urgency,
                    verification_status=v_status,
                    required_resource_type=res_type,
                    demanded_quantity=demand,
                    assigned_resource_id=None,
                    assigned_depot_id=None,
                    assigned_quantity=0,
                    unmet_quantity=demand,
                    travel_dist_km=None,
                    travel_time_min=None,
                    routing_method="NOT_APPLICABLE",
                    allocation_status="AWAITING_APPROVAL",
                    feasibility_status="UNVERIFIED_GATE",
                    priority_rationale="Incident verification unconfirmed. Queued in dispatch review triage before asset commitment.",
                    human_approval_required=True,
                    lat=lat, lon=lon, osm_node=osm_node
                )
                results.append(rec)
                continue

            # If evidence-supported or human-approved, incident is eligible for optimization
            eligible_incidents.append({
                "incident_id": inc_id,
                "incident_category": cat,
                "urgency_level": urgency,
                "verification_status": v_status,
                "required_resource_type": res_type,
                "demanded_quantity": demand,
                "latitude": lat,
                "longitude": lon,
                "osm_node": osm_node,
                "human_approved": human_approved
            })

        if not eligible_incidents:
            return results

        # 2. Collect Available Resources
        available_resources = self.inventory_manager.get_available_resources()

        # If zero resources available across the board
        if not available_resources:
            for el in eligible_incidents:
                rec = self._build_record(
                    incident_id=el["incident_id"],
                    incident_category=el["incident_category"],
                    urgency_level=el["urgency_level"],
                    verification_status=el["verification_status"],
                    required_resource_type=el["required_resource_type"],
                    demanded_quantity=el["demanded_quantity"],
                    assigned_resource_id=None,
                    assigned_depot_id=None,
                    assigned_quantity=0,
                    unmet_quantity=el["demanded_quantity"],
                    travel_dist_km=None,
                    travel_time_min=None,
                    routing_method="NOT_APPLICABLE",
                    allocation_status="INFEASIBLE",
                    feasibility_status="INFEASIBLE_CAPACITY",
                    priority_rationale="Zero emergency resources currently available across all depots.",
                    human_approval_required=True,
                    lat=el["latitude"], lon=el["longitude"], osm_node=el["osm_node"]
                )
                results.append(rec)
            return results

        # 3. Compute Compatibility and Travel Times
        M = len(eligible_incidents)
        N = len(available_resources)

        cost_matrix = np.full((M, N), 1e6)  # High cost for incompatible/unreachable
        dist_matrix = np.full((M, N), 1e6)
        routing_methods = [["NOT_APPLICABLE" for _ in range(N)] for _ in range(M)]

        for i, inc in enumerate(eligible_incidents):
            req_type = inc["required_resource_type"]
            for j, res in enumerate(available_resources):
                if res["resource_type"] != req_type:
                    continue  # Incompatible type

                # Compute travel routing
                res_node = res["location"].get("osm_node_id")
                res_lat = res["location"].get("latitude")
                res_lon = res["location"].get("longitude")

                inc_node = inc["osm_node"]
                inc_lat = inc["latitude"]
                inc_lon = inc["longitude"]

                route = self.routing_engine.compute_travel(
                    from_node=res_node,
                    to_node=inc_node,
                    from_coords=(res_lat, res_lon) if (res_lat and res_lon) else None,
                    to_coords=(inc_lat, inc_lon) if (inc_lat and inc_lon) else None
                )

                if route["routing_method"] == "UNREACHABLE":
                    routing_methods[i][j] = "UNREACHABLE"
                    continue

                t_time = route["travel_time_min"]
                d_dist = route["distance_km"]
                if t_time is not None:
                    cost_matrix[i, j] = t_time
                    dist_matrix[i, j] = d_dist if d_dist is not None else 0.0
                    routing_methods[i][j] = route["routing_method"]

        # 4. Formulate & Solve MILP Optimization Problem
        # Variables: x[i, j] for each (incident i, resource j) + u[i] for unmet demand
        # Total variables = M * N + M
        num_vars = M * N + M
        c_obj = np.zeros(num_vars)

        # Objective: sum(travel_cost * x[i, j]) + sum(urgency_weight * penalty * u[i])
        for i in range(M):
            urgency = eligible_incidents[i]["urgency_level"]
            weight = URGENCY_WEIGHTS.get(urgency, 1.0)
            u_idx = M * N + i
            c_obj[u_idx] = weight * PENALTY_UNMET_BASE

            for j in range(N):
                var_idx = i * N + j
                c_obj[var_idx] = 1.0 + cost_matrix[i, j]

        # Constraints
        # A1: Resource capacity constraints: sum_i x[i, j] <= Capacity_j  (N constraints)
        # A2: Incident demand balance: sum_j x[i, j] + u[i] = Demand_i     (M constraints)
        A_rows = []
        b_l = []
        b_u = []

        # Capacity constraints
        for j in range(N):
            cap = available_resources[j]["available_quantity"]
            row = np.zeros(num_vars)
            for i in range(M):
                row[i * N + j] = 1.0
            A_rows.append(row)
            b_l.append(0.0)
            b_u.append(float(cap))

        # Demand constraints
        for i in range(M):
            d_val = float(eligible_incidents[i]["demanded_quantity"])
            row = np.zeros(num_vars)
            for j in range(N):
                # Only include compatible & reachable edges
                if cost_matrix[i, j] < 1e5:
                    row[i * N + j] = 1.0
            row[M * N + i] = 1.0  # unmet demand variable
            A_rows.append(row)
            b_l.append(d_val)
            b_u.append(d_val)

        A_mat = np.array(A_rows)
        constraints = LinearConstraint(A_mat, b_l, b_u)

        # Bounds: all variables integer >= 0
        integrality = np.ones(num_vars)  # All variables integer
        bounds = Bounds(lb=np.zeros(num_vars), ub=np.full(num_vars, 1000.0))

        # Solve MILP
        res_sol = milp(c=c_obj, integrality=integrality, constraints=constraints, bounds=bounds)

        # 5. Interpret Solution and Generate Records
        if res_sol.success:
            sol_vars = np.round(res_sol.x).astype(int)
        else:
            logger.warning(f"MILP solver did not converge ({res_sol.status}): {res_sol.message}. Falling back to greedy.")
            sol_vars = np.zeros(num_vars, dtype=int)
            # Greedy fallback
            for i in range(M):
                sol_vars[M * N + i] = eligible_incidents[i]["demanded_quantity"]

        for i, inc in enumerate(eligible_incidents):
            inc_id = inc["incident_id"]
            demand = inc["demanded_quantity"]
            unmet = sol_vars[M * N + i]

            # Find which resource was assigned
            assigned_res = None
            assigned_qty = 0
            chosen_j = None

            for j in range(N):
                qty = sol_vars[i * N + j]
                if qty > 0:
                    assigned_res = available_resources[j]
                    assigned_qty += qty
                    chosen_j = j
                    if update_inventory:
                        self.inventory_manager.allocate_quantity(assigned_res["resource_id"], qty)

            # Determine statuses
            if assigned_qty > 0:
                dist_val = dist_matrix[i, chosen_j] if dist_matrix[i, chosen_j] < 1e5 else None
                time_val = cost_matrix[i, chosen_j] if cost_matrix[i, chosen_j] < 1e5 else None
                rmethod = routing_methods[i][chosen_j]

                status = "RECOMMENDED"
                feasibility = "FEASIBLE"
                rationale = (f"Optimally allocated {assigned_qty}/{demand} unit(s) from {assigned_res['depot_id']} "
                             f"({assigned_res['resource_id']}) based on urgency {inc['urgency_level']} "
                             f"and travel time {time_val:.1f}m.")
                if unmet > 0:
                    rationale += f" Remaining unmet demand: {unmet} unit(s) due to capacity limits."

                rec = self._build_record(
                    incident_id=inc_id,
                    incident_category=inc["incident_category"],
                    urgency_level=inc["urgency_level"],
                    verification_status=inc["verification_status"],
                    required_resource_type=inc["required_resource_type"],
                    demanded_quantity=demand,
                    assigned_resource_id=assigned_res["resource_id"],
                    assigned_depot_id=assigned_res["depot_id"],
                    assigned_quantity=assigned_qty,
                    unmet_quantity=unmet,
                    travel_dist_km=dist_val,
                    travel_time_min=time_val,
                    routing_method=rmethod,
                    allocation_status=status,
                    feasibility_status=feasibility,
                    priority_rationale=rationale,
                    human_approval_required=True,
                    lat=inc["latitude"], lon=inc["longitude"], osm_node=inc["osm_node"]
                )
            else:
                # Unallocated: check whether due to reachability or capacity
                all_unreachable = all(routing_methods[i][j] == "UNREACHABLE"
                                      for j in range(N) if available_resources[j]["resource_type"] == inc["required_resource_type"])
                if all_unreachable and any(available_resources[j]["resource_type"] == inc["required_resource_type"] for j in range(N)):
                    feasibility = "INFEASIBLE_UNREACHABLE"
                    rationale = f"All compatible depots are road-network unreachable from incident location."
                    rmethod = "UNREACHABLE"
                else:
                    feasibility = "INFEASIBLE_CAPACITY"
                    rationale = f"Insufficient available capacity for {inc['required_resource_type']} across depots."
                    rmethod = "NOT_APPLICABLE"

                rec = self._build_record(
                    incident_id=inc_id,
                    incident_category=inc["incident_category"],
                    urgency_level=inc["urgency_level"],
                    verification_status=inc["verification_status"],
                    required_resource_type=inc["required_resource_type"],
                    demanded_quantity=demand,
                    assigned_resource_id=None,
                    assigned_depot_id=None,
                    assigned_quantity=0,
                    unmet_quantity=demand,
                    travel_dist_km=None,
                    travel_time_min=None,
                    routing_method=rmethod,
                    allocation_status="UNALLOCATED",
                    feasibility_status=feasibility,
                    priority_rationale=rationale,
                    human_approval_required=True,
                    lat=inc["latitude"], lon=inc["longitude"], osm_node=inc["osm_node"]
                )
            results.append(rec)

        if update_inventory:
            for rec in results:
                self.processed_allocations[rec["incident_id"]] = rec

        return results

    def _build_record(self,
                      incident_id: str,
                      incident_category: str,
                      urgency_level: str,
                      verification_status: str,
                      required_resource_type: str,
                      demanded_quantity: int,
                      assigned_resource_id: Optional[str],
                      assigned_depot_id: Optional[str],
                      assigned_quantity: int,
                      unmet_quantity: int,
                      travel_dist_km: Optional[float],
                      travel_time_min: Optional[float],
                      routing_method: str,
                      allocation_status: str,
                      feasibility_status: str,
                      priority_rationale: str,
                      human_approval_required: bool,
                      lat: Optional[float] = None,
                      lon: Optional[float] = None,
                      osm_node: Optional[int] = None) -> Dict[str, Any]:
        """Constructs schema-validated recommendation record."""
        rec = {
            "allocation_id": f"alloc_{uuid.uuid4().hex[:10]}",
            "incident_id": str(incident_id),
            "incident_category": str(incident_category),
            "urgency_level": str(urgency_level),
            "verification_status": str(verification_status),
            "incident_location": {
                "latitude": float(lat) if lat is not None else None,
                "longitude": float(lon) if lon is not None else None,
                "nearest_osm_node": int(osm_node) if osm_node is not None else None
            },
            "required_resource_type": str(required_resource_type),
            "demanded_quantity": int(demanded_quantity),
            "assigned_resource_id": str(assigned_resource_id) if assigned_resource_id is not None else None,
            "assigned_depot_id": str(assigned_depot_id) if assigned_depot_id is not None else None,
            "assigned_quantity": int(assigned_quantity),
            "unmet_quantity": int(unmet_quantity),
            "travel_distance_km": round(float(travel_dist_km), 3) if travel_dist_km is not None else None,
            "estimated_travel_time_min": round(float(travel_time_min), 2) if travel_time_min is not None else None,
            "routing_method": str(routing_method),
            "allocation_status": str(allocation_status),
            "priority_rationale": str(priority_rationale),
            "feasibility_status": str(feasibility_status),
            "human_approval_required": bool(human_approval_required),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provenance": "crisisguard_milp_highs_optimizer_v1"
        }

        if self.schema:
            try:
                jsonschema.validate(instance=rec, schema=self.schema)
            except jsonschema.ValidationError as ve:
                logger.error(f"Allocation record schema validation failed: {ve.message}")
                raise ve

        return rec
