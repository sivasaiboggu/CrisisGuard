"""
CrisisGuard — Emergency Resource Inventory Module
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Manages emergency resource inventories, depot locations, capacities, and availability states.
Note: Configured as a clearly labeled synthetic demonstration inventory adhering to Section 4.2.
Does NOT represent actual emergency service assets.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import copy

VALID_RESOURCE_TYPES = [
    "AMBULANCE",
    "RESCUE_BOAT",
    "FIRE_TENDER",
    "INFRASTRUCTURE_REPAIR_CREW",
    "RELIEF_SUPPLY_TRUCK"
]

CATEGORY_RESOURCE_COMPATIBILITY = {
    "affected_individuals": ["AMBULANCE", "RESCUE_BOAT", "RELIEF_SUPPLY_TRUCK"],
    "infrastructure_and_utility_damage": ["INFRASTRUCTURE_REPAIR_CREW", "FIRE_TENDER"],
    "rescue_volunteering_or_donation_effort": ["RESCUE_BOAT", "RELIEF_SUPPLY_TRUCK", "AMBULANCE"],
    "other_relevant_information": ["RELIEF_SUPPLY_TRUCK", "INFRASTRUCTURE_REPAIR_CREW"]
}

DEFAULT_DEMONSTRATION_INVENTORY = [
    {
        "resource_id": "RES_BOAT_01",
        "depot_id": "DEPOT_YAMUNA_EAST",
        "resource_type": "RESCUE_BOAT",
        "total_capacity": 6,
        "allocated_quantity": 0,
        "location": {
            "latitude": 6.716976,
            "longitude": 72.948632,
            "osm_node_id": 208413043
        },
        "supported_categories": ["affected_individuals", "rescue_volunteering_or_donation_effort"],
        "status": "AVAILABLE",
        "is_synthetic_demonstration": True
    },
    {
        "resource_id": "RES_BOAT_02",
        "depot_id": "DEPOT_RIVER_NORTH",
        "resource_type": "RESCUE_BOAT",
        "total_capacity": 4,
        "allocated_quantity": 0,
        "location": {
            "latitude": 6.717420,
            "longitude": 72.948196,
            "osm_node_id": 208413047
        },
        "supported_categories": ["affected_individuals", "rescue_volunteering_or_donation_effort"],
        "status": "AVAILABLE",
        "is_synthetic_demonstration": True
    },
    {
        "resource_id": "RES_AMB_01",
        "depot_id": "DEPOT_CIVIL_HOSPITAL",
        "resource_type": "AMBULANCE",
        "total_capacity": 8,
        "allocated_quantity": 0,
        "location": {
            "latitude": 6.771809,
            "longitude": 73.127137,
            "osm_node_id": 208410771
        },
        "supported_categories": ["affected_individuals", "rescue_volunteering_or_donation_effort"],
        "status": "AVAILABLE",
        "is_synthetic_demonstration": True
    },
    {
        "resource_id": "RES_AMB_02",
        "depot_id": "DEPOT_METRO_TRAUMA",
        "resource_type": "AMBULANCE",
        "total_capacity": 5,
        "allocated_quantity": 0,
        "location": {
            "latitude": 6.717345,
            "longitude": 72.944424,
            "osm_node_id": 208413068
        },
        "supported_categories": ["affected_individuals", "rescue_volunteering_or_donation_effort"],
        "status": "AVAILABLE",
        "is_synthetic_demonstration": True
    },
    {
        "resource_id": "RES_FIRE_01",
        "depot_id": "DEPOT_CENTRAL_FIRE",
        "resource_type": "FIRE_TENDER",
        "total_capacity": 4,
        "allocated_quantity": 0,
        "location": {
            "latitude": 6.717694,
            "longitude": 72.944479,
            "osm_node_id": 208413073
        },
        "supported_categories": ["infrastructure_and_utility_damage", "affected_individuals"],
        "status": "AVAILABLE",
        "is_synthetic_demonstration": True
    },
    {
        "resource_id": "RES_REPAIR_01",
        "depot_id": "DEPOT_GRID_SERVICES",
        "resource_type": "INFRASTRUCTURE_REPAIR_CREW",
        "total_capacity": 5,
        "allocated_quantity": 0,
        "location": {
            "latitude": 6.771809,
            "longitude": 73.127137,
            "osm_node_id": 208410771
        },
        "supported_categories": ["infrastructure_and_utility_damage", "other_relevant_information"],
        "status": "AVAILABLE",
        "is_synthetic_demonstration": True
    },
    {
        "resource_id": "RES_TRUCK_01",
        "depot_id": "DEPOT_CIVIL_SUPPLIES",
        "resource_type": "RELIEF_SUPPLY_TRUCK",
        "total_capacity": 10,
        "allocated_quantity": 0,
        "location": {
            "latitude": 6.717420,
            "longitude": 72.948196,
            "osm_node_id": 208413047
        },
        "supported_categories": ["affected_individuals", "rescue_volunteering_or_donation_effort", "other_relevant_information"],
        "status": "AVAILABLE",
        "is_synthetic_demonstration": True
    }
]

class ResourceInventoryManager:
    def __init__(self, initial_inventory: Optional[List[Dict[str, Any]]] = None):
        if initial_inventory is not None:
            self._inventory = copy.deepcopy(initial_inventory)
        else:
            self._inventory = copy.deepcopy(DEFAULT_DEMONSTRATION_INVENTORY)

    def get_all_resources(self) -> List[Dict[str, Any]]:
        """Returns deep copy of all registered resource records."""
        return copy.deepcopy(self._inventory)

    def get_available_resources(self, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns available resources with remaining capacity > 0."""
        available = []
        for r in self._inventory:
            rem = r["total_capacity"] - r["allocated_quantity"]
            if rem > 0 and r["status"] != "EXHAUSTED":
                if resource_type is None or r["resource_type"] == resource_type:
                    rec = copy.deepcopy(r)
                    rec["available_quantity"] = rem
                    available.append(rec)
        return available

    def allocate_quantity(self, resource_id: str, quantity: int) -> bool:
        """
        Allocates specified quantity of resource.
        Guarantees conservation constraint: cannot allocate more than remaining capacity.
        """
        if quantity <= 0:
            return False

        for r in self._inventory:
            if r["resource_id"] == resource_id:
                rem = r["total_capacity"] - r["allocated_quantity"]
                if quantity > rem:
                    return False  # Over-allocation prohibited
                r["allocated_quantity"] += quantity
                if r["allocated_quantity"] == r["total_capacity"]:
                    r["status"] = "EXHAUSTED"
                else:
                    r["status"] = "PARTIALLY_ALLOCATED"
                return True
        return False

    def release_quantity(self, resource_id: str, quantity: int) -> bool:
        """Releases previously allocated resources back into inventory."""
        if quantity <= 0:
            return False

        for r in self._inventory:
            if r["resource_id"] == resource_id:
                if quantity > r["allocated_quantity"]:
                    return False
                r["allocated_quantity"] -= quantity
                if r["allocated_quantity"] == 0:
                    r["status"] = "AVAILABLE"
                else:
                    r["status"] = "PARTIALLY_ALLOCATED"
                return True
        return False

    def reset_inventory(self):
        """Resets all allocations to baseline."""
        self._inventory = copy.deepcopy(DEFAULT_DEMONSTRATION_INVENTORY)
