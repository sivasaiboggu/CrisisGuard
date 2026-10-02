import os
import glob
import json
from pathlib import Path
import pandas as pd

def audit_all_inputs():
    print("============================================================")
    print("CRISISGUARD — PHASE 9 INPUT ARTIFACT DISCOVERY & AUDIT")
    print("============================================================")

    root = Path(".")
    
    # 1. Phase 6 Artifacts
    print("\n--- PHASE 6 ARTIFACTS ---")
    p6_feature = root / "data" / "features" / "synthetic_media" / "unified_media_risk.parquet"
    print(f"Phase 6 Feature Parquet: {p6_feature} (exists: {p6_feature.exists()})")
    p6_df = pd.DataFrame()
    if p6_feature.exists():
        p6_df = pd.read_parquet(p6_feature)
        print(f"  Rows: {len(p6_df)}, Columns: {p6_df.columns.tolist()}")
        print(f"  Primary ID column candidates: {[c for c in p6_df.columns if 'id' in c.lower()]}")
        print(f"  Sample row:\n{p6_df.iloc[0].to_dict()}")
        print(f"  Calibration status counts:\n{p6_df['calibration_status'].value_counts() if 'calibration_status' in p6_df.columns else 'N/A'}")
        print(f"  Source dataset counts:\n{p6_df['source_dataset'].value_counts() if 'source_dataset' in p6_df.columns else 'N/A'}")

    p6_schema = root / "schemas" / "synthetic_media" / "media_risk_schema.json"
    print(f"Phase 6 Schema: {p6_schema} (exists: {p6_schema.exists()})")
    
    p6_models = list(glob.glob("models/synthetic_media/**/*", recursive=True))
    print(f"Phase 6 Models ({len(p6_models)} files): {p6_models[:5]}")
    
    p6_registry = root / "models" / "synthetic_media" / "model_registry.json"
    if not p6_registry.exists():
        p6_registry = root / "docs" / "synthetic_media" / "model_registry.json"
    print(f"Phase 6 Registry: {p6_registry} (exists: {p6_registry.exists()})")

    # 2. Phase 7 Artifacts
    print("\n--- PHASE 7 ARTIFACTS ---")
    p7_feature = root / "data" / "features" / "crisis_information" / "unified_crisis_intelligence.parquet"
    print(f"Phase 7 Feature Parquet: {p7_feature} (exists: {p7_feature.exists()})")
    p7_df = pd.DataFrame()
    if p7_feature.exists():
        p7_df = pd.read_parquet(p7_feature)
        print(f"  Rows: {len(p7_df)}, Columns: {p7_df.columns.tolist()}")
        print(f"  Primary ID column candidates: {[c for c in p7_df.columns if 'id' in c.lower()]}")
        print(f"  Sample row:\n{p7_df.iloc[0].to_dict()}")
        print(f"  Calibration status counts:\n{p7_df['calibration_status'].value_counts() if 'calibration_status' in p7_df.columns else 'N/A'}")
        print(f"  Source dataset counts:\n{p7_df['source_dataset'].value_counts() if 'source_dataset' in p7_df.columns else 'N/A'}")

    p7_schema = root / "schemas" / "crisis_intelligence_schema.json"
    if not p7_schema.exists():
        p7_schema = root / "schemas" / "crisis_information" / "crisis_intelligence_schema.json"
    print(f"Phase 7 Schema: {p7_schema} (exists: {p7_schema.exists()})")

    p7_models = list(glob.glob("models/crisis_information/**/*", recursive=True))
    print(f"Phase 7 Models ({len(p7_models)} files): {p7_models[:5]}")

    # 3. Phase 8 Artifacts
    print("\n--- PHASE 8 ARTIFACTS ---")
    p8_events = root / "data" / "processed" / "propagation" / "propagation_events.parquet"
    p8_edges = root / "data" / "processed" / "propagation" / "propagation_edges.parquet"
    p8_vertices_csv = root / "data" / "features" / "phase8" / "graph" / "vertices.csv"
    p8_edges_csv = root / "data" / "features" / "phase8" / "graph" / "edges.csv"
    p8_graphx_csv = root / "data" / "features" / "phase8" / "graph" / "graphx_vertex_metrics.csv"
    p8_stream_pq = root / "data" / "features" / "phase8" / "streaming" / "propagation_stream_metrics.parquet"
    
    print(f"Phase 8 Events: {p8_events} (exists: {p8_events.exists()})")
    p8_ev_df = pd.DataFrame()
    if p8_events.exists():
        p8_ev_df = pd.read_parquet(p8_events)
        print(f"  Events Rows: {len(p8_ev_df)}, Columns: {p8_ev_df.columns.tolist()}")
        print(f"  Sample Event: {p8_ev_df.iloc[0].to_dict()}")
        
    print(f"Phase 8 Edges: {p8_edges} (exists: {p8_edges.exists()})")
    p8_ed_df = pd.DataFrame()
    if p8_edges.exists():
        p8_ed_df = pd.read_parquet(p8_edges)
        print(f"  Edges Rows: {len(p8_ed_df)}, Columns: {p8_ed_df.columns.tolist()}")
        
    print(f"Phase 8 GraphX Vertices Metrics: {p8_graphx_csv} (exists: {p8_graphx_csv.exists()})")
    p8_gx_df = pd.DataFrame()
    if p8_graphx_csv.exists():
        p8_gx_df = pd.read_csv(p8_graphx_csv)
        print(f"  GraphX Rows: {len(p8_gx_df)}, Columns: {p8_gx_df.columns.tolist()}")
        print(f"  Sample GraphX: {p8_gx_df.iloc[0].to_dict()}")

    print(f"Phase 8 Streaming Metrics: {p8_stream_pq} (exists: {p8_stream_pq.exists()})")
    p8_st_df = pd.DataFrame()
    if p8_stream_pq.exists():
        p8_st_df = pd.read_parquet(p8_stream_pq)
        print(f"  Stream Windows Rows: {len(p8_st_df)}, Columns: {p8_st_df.columns.tolist()}")

    # 4. Phase 4 OSM Road Network
    print("\n--- OSM ROAD NETWORK ARTIFACTS ---")
    osm_nodes = root / "data" / "processed" / "osm" / "road_nodes.parquet"
    osm_edges = root / "data" / "processed" / "osm" / "road_edges.parquet"
    print(f"OSM Road Nodes: {osm_nodes} (exists: {osm_nodes.exists()})")
    if osm_nodes.exists():
        osm_n_df = pd.read_parquet(osm_nodes)
        print(f"  OSM Nodes Rows: {len(osm_n_df)}, Columns: {osm_n_df.columns.tolist()}")
        print(f"  Sample OSM Node: {osm_n_df.iloc[0].to_dict()}")
        
    print(f"OSM Road Edges: {osm_edges} (exists: {osm_edges.exists()})")
    if osm_edges.exists():
        osm_e_df = pd.read_parquet(osm_edges)
        print(f"  OSM Edges Rows: {len(osm_e_df)}, Columns: {osm_e_df.columns.tolist()}")

    # 5. Join Feasibility Cross-Checks
    print("\n--- JOIN FEASIBILITY DETAILED AUDIT ---")
    
    # Extract IDs
    p6_content_ids = set(p6_df["content_id"].dropna().astype(str)) if not p6_df.empty else set()
    p7_content_ids = set(p7_df["content_id"].dropna().astype(str)) if not p7_df.empty else set()
    p7_record_ids  = set(p7_df["source_record_id"].dropna().astype(str)) if not p7_df.empty and "source_record_id" in p7_df.columns else set()
    p7_event_ids   = set(p7_df["event_id"].dropna().astype(str)) if not p7_df.empty and "event_id" in p7_df.columns else set()
    p8_content_ids = set(p8_ev_df["content_id"].dropna().astype(str)) if not p8_ev_df.empty else set()
    p8_event_ids   = set(p8_ev_df["event_id"].dropna().astype(str)) if not p8_ev_df.empty else set()
    p8_node_names  = set(p8_gx_df["node_name"].dropna().astype(str)) if not p8_gx_df.empty else set()
    osm_node_ids   = set(osm_n_df["node_id"].dropna().astype(str)) if osm_nodes.exists() and "node_id" in osm_n_df.columns else set()

    print(f"Phase 6 content_ids: {len(p6_content_ids)}")
    print(f"Phase 7 content_ids: {len(p7_content_ids)}")
    print(f"Phase 7 source_record_ids: {len(p7_record_ids)}")
    print(f"Phase 7 event_ids (incident names): {len(p7_event_ids)}")
    print(f"Phase 8 content_ids (simulated cascade topics): {len(p8_content_ids)}")
    print(f"Phase 8 event_ids (transmission instances): {len(p8_event_ids)}")
    print(f"Phase 8 GraphX node_names: {len(p8_node_names)}")
    print(f"OSM node_ids: {len(osm_node_ids)}")

    print("\nChecking Phase 8 content_ids in Phase 6:")
    for cid in p8_content_ids:
        in_p6 = cid in p6_content_ids
        print(f"  '{cid}' in Phase 6: {in_p6}")

    print("\nChecking Phase 8 content_ids in Phase 7:")
    for cid in p8_content_ids:
        in_p7 = cid in p7_content_ids
        in_p7_rec = cid in p7_record_ids
        print(f"  '{cid}' in Phase 7 content_id: {in_p7} | in source_record_id: {in_p7_rec}")

    print("\nChecking Phase 6 content_ids in Phase 7:")
    overlap_6_7 = p6_content_ids.intersection(p7_content_ids)
    print(f"  Direct overlap between Phase 6 content_id and Phase 7 content_id: {len(overlap_6_7)}")

    print("\nChecking Phase 8 event_ids in Phase 7:")
    overlap_ev_7 = p8_event_ids.intersection(p7_content_ids)
    overlap_ev_7_ev = p8_event_ids.intersection(p7_event_ids)
    print(f"  Overlap between Phase 8 event_id and Phase 7 content_id: {len(overlap_ev_7)}")
    print(f"  Overlap between Phase 8 event_id and Phase 7 event_id: {len(overlap_ev_7_ev)}")

    print("\nChecking Phase 8 node_names in OSM node_ids:")
    overlap_osm = p8_node_names.intersection(osm_node_ids)
    print(f"  Overlap between Phase 8 user node_name and OSM road node_id: {len(overlap_osm)}")

    # Null rate checks
    print("\n--- NULL RATE CHECKS ---")
    print(f"Phase 6 content_id nulls: {p6_df['content_id'].isna().sum()} ({p6_df['content_id'].isna().mean():.4f})")
    print(f"Phase 7 content_id nulls: {p7_df['content_id'].isna().sum()} ({p7_df['content_id'].isna().mean():.4f})")
    print(f"Phase 8 event_id nulls:   {p8_ev_df['event_id'].isna().sum()} ({p8_ev_df['event_id'].isna().mean():.4f})")
    print(f"Phase 8 content_id nulls: {p8_ev_df['content_id'].isna().sum()} ({p8_ev_df['content_id'].isna().mean():.4f})")
    print(f"Phase 8 GraphX node_name nulls: {p8_gx_df['node_name'].isna().sum()}")

    print("\nAudit completed.")

if __name__ == "__main__":
    audit_all_inputs()
