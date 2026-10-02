#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: Input Audit Script
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Audits frozen inputs for Phase 8:
1. Primary Phase 4 propagation data (5,004 events, 4,999 edges, SEMI_SYNTHETIC)
2. Phase 6 unified media-risk outputs (77 prediction records)
3. Phase 7 unified crisis intelligence (104,130 records)
4. OSM road network (63,660 road nodes, 146,156 edges)
"""

import sys
import os
import json
import hashlib
from pathlib import Path
import pandas as pd

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def audit_inputs():
    print("=" * 70)
    print("CRISISGUARD — PHASE 8 INPUT AUDIT & FROZEN BASELINE")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    print("=" * 70)
    
    root = Path(__file__).resolve().parent.parent.parent
    audit_results = {}
    
    # -------------------------------------------------------------
    # 1. Primary Phase 4 Propagation Data
    # -------------------------------------------------------------
    prop_events_p = root / "data" / "processed" / "propagation" / "propagation_events.parquet"
    prop_edges_p = root / "data" / "processed" / "propagation" / "propagation_edges.parquet"
    
    if not prop_events_p.exists() or not prop_edges_p.exists():
        # Search for alternative paths
        candidates = list(root.glob("**/propagation_*.parquet"))
        print(f"Propagation candidates found: {candidates}")
        return False
        
    df_events = pd.read_parquet(prop_events_p)
    df_edges = pd.read_parquet(prop_edges_p)
    
    n_events = len(df_events)
    n_edges = len(df_edges)
    events_hash = sha256_file(prop_events_p)
    edges_hash = sha256_file(prop_edges_p)
    
    print(f"\n[1] Primary Propagation Data:")
    print(f"  - Events File: {prop_events_p.relative_to(root)} ({n_events} rows, {len(df_events.columns)} cols)")
    print(f"    Columns: {df_events.columns.tolist()}")
    print(f"    SHA256:  {events_hash}")
    print(f"  - Edges File:  {prop_edges_p.relative_to(root)} ({n_edges} rows, {len(df_edges.columns)} cols)")
    print(f"    Columns: {df_edges.columns.tolist()}")
    print(f"    SHA256:  {edges_hash}")
    
    governance_tags = df_events["governance_type"].unique().tolist() if "governance_type" in df_events.columns else []
    print(f"    Governance Tags: {governance_tags}")
    
    audit_results["propagation_events"] = {
        "file": str(prop_events_p.relative_to(root)),
        "rows": n_events,
        "cols": len(df_events.columns),
        "columns": df_events.columns.tolist(),
        "sha256": events_hash,
        "governance": governance_tags
    }
    audit_results["propagation_edges"] = {
        "file": str(prop_edges_p.relative_to(root)),
        "rows": n_edges,
        "cols": len(df_edges.columns),
        "columns": df_edges.columns.tolist(),
        "sha256": edges_hash
    }
    
    # -------------------------------------------------------------
    # 2. Phase 6 Unified Media-Risk Outputs
    # -------------------------------------------------------------
    mr_p = root / "data" / "features" / "synthetic_media" / "unified_media_risk.parquet"
    if not mr_p.exists():
        print(f"ERROR: Media risk parquet not found at {mr_p}")
        return False
    df_mr = pd.read_parquet(mr_p)
    n_mr = len(df_mr)
    mr_hash = sha256_file(mr_p)
    print(f"\n[2] Phase 6 Unified Media-Risk Outputs:")
    print(f"  - File:    {mr_p.relative_to(root)} ({n_mr} rows, {len(df_mr.columns)} cols)")
    print(f"    Columns: {df_mr.columns.tolist()}")
    print(f"    SHA256:  {mr_hash}")
    
    audit_results["media_risk"] = {
        "file": str(mr_p.relative_to(root)),
        "rows": n_mr,
        "cols": len(df_mr.columns),
        "columns": df_mr.columns.tolist(),
        "sha256": mr_hash
    }
    
    # -------------------------------------------------------------
    # 3. Phase 7 Unified Crisis Intelligence
    # -------------------------------------------------------------
    ci_p = root / "data" / "features" / "crisis_information" / "unified_crisis_intelligence.parquet"
    if not ci_p.exists():
        print(f"ERROR: Unified crisis intelligence parquet not found at {ci_p}")
        return False
    df_ci = pd.read_parquet(ci_p)
    n_ci = len(df_ci)
    ci_hash = sha256_file(ci_p)
    print(f"\n[3] Phase 7 Unified Crisis Intelligence:")
    print(f"  - File:    {ci_p.relative_to(root)} ({n_ci} rows, {len(df_ci.columns)} cols)")
    print(f"    Columns: {df_ci.columns.tolist()}")
    print(f"    SHA256:  {ci_hash}")
    
    audit_results["crisis_intelligence"] = {
        "file": str(ci_p.relative_to(root)),
        "rows": n_ci,
        "cols": len(df_ci.columns),
        "columns": df_ci.columns.tolist(),
        "sha256": ci_hash
    }
    
    # -------------------------------------------------------------
    # 4. OpenStreetMap (OSM) Road Network
    # -------------------------------------------------------------
    osm_nodes_p = root / "data" / "processed" / "osm" / "road_nodes.parquet"
    osm_edges_p = root / "data" / "processed" / "osm" / "road_edges.parquet"
    
    n_nodes = 0
    n_osm_edges = 0
    if osm_nodes_p.exists() and osm_edges_p.exists():
        df_nodes = pd.read_parquet(osm_nodes_p)
        df_oedges = pd.read_parquet(osm_edges_p)
        n_nodes = len(df_nodes)
        n_osm_edges = len(df_oedges)
        nodes_hash = sha256_file(osm_nodes_p)
        oedges_hash = sha256_file(osm_edges_p)
        print(f"\n[4] OpenStreetMap (OSM) Road Network:")
        print(f"  - Nodes:   {osm_nodes_p.relative_to(root)} ({n_nodes} rows, {len(df_nodes.columns)} cols)")
        print(f"    Columns: {df_nodes.columns.tolist()}")
        print(f"    SHA256:  {nodes_hash}")
        print(f"  - Edges:   {osm_edges_p.relative_to(root)} ({n_osm_edges} rows, {len(df_oedges.columns)} cols)")
        print(f"    Columns: {df_oedges.columns.tolist()}")
        print(f"    SHA256:  {oedges_hash}")
        
        audit_results["osm_nodes"] = {
            "file": str(osm_nodes_p.relative_to(root)),
            "rows": n_nodes,
            "cols": len(df_nodes.columns),
            "columns": df_nodes.columns.tolist(),
            "sha256": nodes_hash
        }
        audit_results["osm_edges"] = {
            "file": str(osm_edges_p.relative_to(root)),
            "rows": n_osm_edges,
            "cols": len(df_oedges.columns),
            "columns": df_oedges.columns.tolist(),
            "sha256": oedges_hash
        }
    else:
        candidates = list(root.glob("**/osm*.*"))
        print(f"OSM candidates found: {candidates}")
        
    # Verification assertions
    c1 = (n_events == 5004)
    c2 = (n_edges == 4999)
    c3 = (n_mr == 77)
    c4 = (n_ci == 104130)
    c5 = (n_nodes == 63660)
    c6 = (n_osm_edges == 146156)
    
    print("\n" + "=" * 70)
    print("FROZEN INPUT VERIFICATION STATUS:")
    print(f"  - Propagation Events (5,004)    : {'PASS' if c1 else 'FAIL'} ({n_events})")
    print(f"  - Propagation Edges (4,999)     : {'PASS' if c2 else 'FAIL'} ({n_edges})")
    print(f"  - Media Risk Records (77)       : {'PASS' if c3 else 'FAIL'} ({n_mr})")
    print(f"  - Crisis Intelligence (104,130) : {'PASS' if c4 else 'FAIL'} ({n_ci})")
    print(f"  - OSM Road Nodes (63,660)       : {'PASS' if c5 else 'FAIL'} ({n_nodes})")
    print(f"  - OSM Road Edges (146,156)      : {'PASS' if c6 else 'FAIL'} ({n_osm_edges})")
    
    all_pass = c1 and c2 and c3 and c4 and c5 and c6
    print(f"\nOVERALL INPUT AUDIT: {'PASS — ALL INPUTS VERIFIED' if all_pass else 'FAIL — MISMATCH DETECTED'}")
    print("=" * 70)
    
    out_dir = root / "docs" / "phase8"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "input_audit_data.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)
    print(f"Saved audit data to: {out_dir / 'input_audit_data.json'}")
    
    return all_pass

if __name__ == "__main__":
    ok = audit_inputs()
    sys.exit(0 if ok else 1)
