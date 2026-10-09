"""
CrisisGuard — Spatial Road Network & Dijkstra Routing Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Ingests OpenStreetMap road network extracts (data/processed/osm/) and computes
exact shortest road paths, distance (km), and travel times (minutes) using Dijkstra's algorithm.
Handles disconnected subgraphs, unreachable nodes, and provides transparent fallback.
"""

import os
import math
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

logger = logging.getLogger("CrisisGuard.Routing")

SPEED_PROFILE_KMH = {
    "motorway": 80.0,
    "trunk": 60.0,
    "primary": 50.0,
    "secondary": 40.0,
    "tertiary": 30.0,
    "residential": 25.0,
    "service": 20.0,
    "unclassified": 30.0,
    "default": 35.0
}

class OSMRoutingEngine:
    def __init__(self, osm_dir: Optional[str] = None):
        if osm_dir is None:
            root = Path(__file__).resolve().parent.parent.parent
            self.osm_dir = root / "data" / "processed" / "osm"
        else:
            self.osm_dir = Path(osm_dir)

        self.nodes_df = None
        self.edges_df = None
        self.kdtree = None
        self.node_id_to_idx = {}
        self.idx_to_node_id = {}
        self.dist_matrix = None
        self.time_matrix = None
        self.initialized = False

        self._load_network()

    def _load_network(self):
        nodes_path = self.osm_dir / "road_nodes.parquet"
        edges_path = self.osm_dir / "road_edges.parquet"

        if not nodes_path.exists() or not edges_path.exists():
            logger.warning(f"OSM parquet files not found in {self.osm_dir}. Falling back to Euclidean routing.")
            return

        try:
            logger.info("Loading OSM road network nodes and edges...")
            self.nodes_df = pd.read_parquet(nodes_path)
            self.edges_df = pd.read_parquet(edges_path)

            # Build node index mappings
            node_ids = self.nodes_df["node_id"].values
            for idx, nid in enumerate(node_ids):
                self.node_id_to_idx[nid] = idx
                self.idx_to_node_id[idx] = nid

            # Build KDTree for nearest node lookups using coordinates
            coords = self.nodes_df[["latitude", "longitude"]].values
            self.kdtree = cKDTree(coords)

            # Build adjacency matrix for distance and travel time
            num_nodes = len(node_ids)
            src_list = []
            dst_list = []
            dist_list = []
            time_list = []

            for _, row in self.edges_df.iterrows():
                u = row["source_node"]
                v = row["target_node"]
                if u not in self.node_id_to_idx or v not in self.node_id_to_idx:
                    continue

                u_idx = self.node_id_to_idx[u]
                v_idx = self.node_id_to_idx[v]
                length_km = max(0.001, float(row["length_m"]) / 1000.0)

                # Determine travel speed
                speed = row.get("speed_if_available")
                if pd.isna(speed) or speed is None or speed <= 0:
                    road_type = str(row.get("road_type", "default")).lower()
                    speed = SPEED_PROFILE_KMH.get(road_type, SPEED_PROFILE_KMH["default"])
                else:
                    speed = float(speed)

                travel_time_min = (length_km / speed) * 60.0

                # Edge u -> v
                src_list.append(u_idx)
                dst_list.append(v_idx)
                dist_list.append(length_km)
                time_list.append(travel_time_min)

                # If bidirectional, add v -> u
                if not bool(row.get("oneway", False)):
                    src_list.append(v_idx)
                    dst_list.append(u_idx)
                    dist_list.append(length_km)
                    time_list.append(travel_time_min)

            self.dist_matrix = sp.csr_matrix(
                (dist_list, (src_list, dst_list)), shape=(num_nodes, num_nodes)
            )
            self.time_matrix = sp.csr_matrix(
                (time_list, (src_list, dst_list)), shape=(num_nodes, num_nodes)
            )
            self.initialized = True
            logger.info(f"OSM Routing Engine initialized with {num_nodes} nodes and {len(src_list)} directed edges.")
        except Exception as e:
            logger.error(f"Failed to load OSM network: {e}")
            self.initialized = False

    def find_nearest_node(self, lat: float, lon: float) -> Optional[int]:
        """Finds the nearest OSM node_id to the given coordinates."""
        if not self.initialized or self.kdtree is None:
            return None
        _, idx = self.kdtree.query([lat, lon])
        return int(self.idx_to_node_id[idx])

    def haversine_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes great-circle distance between two points in km."""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def compute_travel(self,
                       from_node: Optional[int],
                       to_node: Optional[int],
                       from_coords: Optional[Tuple[float, float]] = None,
                       to_coords: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """
        Computes shortest road distance and travel time.
        Distinguishes OSM_DIJKSTRA, EUCLIDEAN_FALLBACK, and UNREACHABLE states.
        """
        # If node IDs not explicitly given, try matching from coordinates
        if from_node is None and from_coords:
            from_node = self.find_nearest_node(from_coords[0], from_coords[1])
        if to_node is None and to_coords:
            to_node = self.find_nearest_node(to_coords[0], to_coords[1])

        # If we have valid network and nodes
        if self.initialized and from_node in self.node_id_to_idx and to_node in self.node_id_to_idx:
            src_idx = self.node_id_to_idx[from_node]
            dst_idx = self.node_id_to_idx[to_node]

            if src_idx == dst_idx:
                return {
                    "distance_km": 0.0,
                    "travel_time_min": 0.0,
                    "routing_method": "OSM_DIJKSTRA",
                    "from_node": from_node,
                    "to_node": to_node
                }

            # Run Dijkstra for travel time
            dist_array, predecessors = dijkstra(
                csgraph=self.time_matrix,
                directed=True,
                indices=src_idx,
                return_predecessors=True
            )
            time_val = float(dist_array[dst_idx])

            if np.isinf(time_val):
                # Disconnected graph components
                return {
                    "distance_km": None,
                    "travel_time_min": None,
                    "routing_method": "UNREACHABLE",
                    "from_node": from_node,
                    "to_node": to_node
                }

            # Compute corresponding road distance
            dist_dijkstra = dijkstra(
                csgraph=self.dist_matrix,
                directed=True,
                indices=src_idx,
                return_predecessors=False
            )
            dist_val = float(dist_dijkstra[dst_idx])

            return {
                "distance_km": round(dist_val, 3),
                "travel_time_min": round(time_val, 2),
                "routing_method": "OSM_DIJKSTRA",
                "from_node": from_node,
                "to_node": to_node
            }

        # Fallback to Euclidean estimation if coordinates available
        if from_coords and to_coords:
            great_circle_km = self.haversine_distance_km(
                from_coords[0], from_coords[1], to_coords[0], to_coords[1]
            )
            # Apply empirical road detour factor 1.35x
            est_dist_km = great_circle_km * 1.35
            est_time_min = (est_dist_km / SPEED_PROFILE_KMH["default"]) * 60.0
            return {
                "distance_km": round(est_dist_km, 3),
                "travel_time_min": round(est_time_min, 2),
                "routing_method": "EUCLIDEAN_FALLBACK",
                "from_node": from_node,
                "to_node": to_node
            }

        # Insufficient spatial information
        return {
            "distance_km": None,
            "travel_time_min": None,
            "routing_method": "NOT_APPLICABLE",
            "from_node": None,
            "to_node": None
        }
