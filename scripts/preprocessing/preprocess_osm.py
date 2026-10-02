#!/usr/bin/env python3
"""
CrisisGuard — Phase 4 Preprocessing: OpenStreetMap Regional Road Network
Author: B.SIVASAI (Roll No: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Processes:
- Ingests data/raw/osm/regional_extract.osm.pbf
- Extracts canonical road_node (node_id, latitude, longitude)
- Extracts canonical road_edge (edge_id, source_node, target_node, road_type, length_m, oneway, speed_if_available)
- Computes geodesic haversine length in meters
- Strictly stores NULL for speed_if_available when unrecorded (no invented values)
- Output: data/interim/osm/ and data/processed/osm/ (CSV and Parquet)
"""

import os
import sys
import re
import math
from pathlib import Path
import osmium
import pandas as pd

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)

class WayScanner(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.ways = []
        self.referenced_nodes = set()

    def way(self, w):
        if "highway" in w.tags:
            nodes = [n.ref for n in w.nodes]
            if len(nodes) >= 2:
                hw_type = w.tags["highway"]
                oneway_tag = w.tags.get("oneway", "no").lower()
                is_oneway = oneway_tag in ["yes", "1", "true"]
                maxspeed_tag = w.tags.get("maxspeed")
                speed_val = None
                if maxspeed_tag:
                    m = re.search(r"(\d+(\.\d+)?)", maxspeed_tag)
                    if m:
                        speed_val = float(m.group(1))

                self.ways.append({
                    "way_id": w.id,
                    "road_type": hw_type,
                    "oneway": is_oneway,
                    "speed_if_available": speed_val,
                    "node_refs": nodes
                })
                self.referenced_nodes.update(nodes)

class NodeCollector(osmium.SimpleHandler):
    def __init__(self, target_ids):
        super().__init__()
        self.target_ids = target_ids
        self.node_coords = {}

    def node(self, n):
        if n.id in self.target_ids:
            self.node_coords[n.id] = (round(n.location.lat, 6), round(n.location.lon, 6))

def preprocess_osm():
    print("=" * 60)
    print("CrisisGuard Phase 4: Preprocessing OpenStreetMap Road Topology")
    print("=" * 60)

    root = Path(__file__).resolve().parent.parent.parent
    pbf_file = root / "data" / "raw" / "osm" / "regional_extract.osm.pbf"
    interim_dir = root / "data" / "interim" / "osm"
    processed_dir = root / "data" / "processed" / "osm"

    interim_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    if not pbf_file.exists():
        print(f"[ERR] OSM PBF file missing: {pbf_file}")
        return False

    print(f"Scanning ways and highway tags from {pbf_file.name}...")
    way_scanner = WayScanner()
    way_scanner.apply_file(str(pbf_file))
    print(f"Found {len(way_scanner.ways)} road ways referencing {len(way_scanner.referenced_nodes)} distinct nodes.")

    print("Collecting node geographic coordinates...")
    node_collector = NodeCollector(way_scanner.referenced_nodes)
    node_collector.apply_file(str(pbf_file))
    print(f"Captured coordinates for {len(node_collector.node_coords)} road nodes.")

    # 1. Build canonical road_node records
    node_records = []
    for nid, (lat, lon) in node_collector.node_coords.items():
        node_records.append({
            "node_id": nid,
            "latitude": lat,
            "longitude": lon,
            "source_dataset": "openstreetmap_geofabrik",
            "governance_type": "REAL"
        })

    # 2. Build canonical road_edge records
    edge_records = []
    edge_idx = 0
    missing_coords = 0

    for w in way_scanner.ways:
        way_id = w["way_id"]
        hw_type = w["road_type"]
        is_oneway = w["oneway"]
        speed = w["speed_if_available"]
        refs = w["node_refs"]

        for i in range(len(refs) - 1):
            u, v = refs[i], refs[i + 1]
            if u not in node_collector.node_coords or v not in node_collector.node_coords:
                missing_coords += 1
                continue

            lat1, lon1 = node_collector.node_coords[u]
            lat2, lon2 = node_collector.node_coords[v]
            length_m = haversine_distance(lat1, lon1, lat2, lon2)

            edge_idx += 1
            edge_records.append({
                "edge_id": f"osm_e_{edge_idx}",
                "way_id": way_id,
                "source_node": u,
                "target_node": v,
                "road_type": hw_type,
                "length_m": length_m,
                "oneway": is_oneway,
                "speed_if_available": speed,
                "governance_type": "REAL"
            })

            # If bidirectional, add reverse traversal edge
            if not is_oneway:
                edge_idx += 1
                edge_records.append({
                    "edge_id": f"osm_e_{edge_idx}",
                    "way_id": way_id,
                    "source_node": v,
                    "target_node": u,
                    "road_type": hw_type,
                    "length_m": length_m,
                    "oneway": is_oneway,
                    "speed_if_available": speed,
                    "governance_type": "REAL"
                })

    df_nodes = pd.DataFrame(node_records)
    df_edges = pd.DataFrame(edge_records)

    print(f"\nOSM Road Preprocessing Summary:")
    print(f"  Canonical Road Nodes: {len(df_nodes)}")
    print(f"  Canonical Road Edges: {len(df_edges)}")
    print(f"  Missing Coordinate Pairs: {missing_coords}")
    print(f"  Speed Availability: {df_edges['speed_if_available'].notna().sum()} edges with explicit speed tag, {df_edges['speed_if_available'].isna().sum()} NULL")
    print(f"  Top Road Types:")
    for rt, cnt in df_edges["road_type"].value_counts().head(5).items():
        print(f"    - {rt}: {cnt} edges")

    # Save to interim and processed
    df_nodes.to_csv(interim_dir / "road_nodes.csv", index=False)
    df_edges.to_csv(interim_dir / "road_edges.csv", index=False)
    df_nodes.to_parquet(processed_dir / "road_nodes.parquet", index=False)
    df_edges.to_parquet(processed_dir / "road_edges.parquet", index=False)

    print(f"  Saved nodes to {interim_dir / 'road_nodes.csv'} and {processed_dir / 'road_nodes.parquet'}")
    print(f"  Saved edges to {interim_dir / 'road_edges.csv'} and {processed_dir / 'road_edges.parquet'}")
    return len(df_nodes) > 0 and len(df_edges) > 0

if __name__ == "__main__":
    success = preprocess_osm()
    sys.exit(0 if success else 1)
