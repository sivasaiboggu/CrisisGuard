import pandas as pd
import numpy as np

def run_audit():
    print("============================================================")
    print("CRISISGUARD — PHASE 8 VERTEX INVESTIGATION SCRIPT")
    print("============================================================")

    # 1. Inspect Phase 4 raw frozen input files
    events_p4 = pd.read_parquet("data/processed/propagation/propagation_events.parquet")
    edges_p4 = pd.read_parquet("data/processed/propagation/propagation_edges.parquet")

    print(f"events_p4 shape: {events_p4.shape}")
    print(f"edges_p4 shape:  {edges_p4.shape}")

    # Dtype inspection
    print(f"events source_node dtype: {events_p4['source_node'].dtype}")
    print(f"events target_node dtype: {events_p4['target_node'].dtype}")
    print(f"edges source_node dtype:  {edges_p4['source_node'].dtype}")
    print(f"edges target_node dtype:  {edges_p4['target_node'].dtype}")
    print(f"edges source sample: {edges_p4['source_node'].head().tolist()} (type: {type(edges_p4['source_node'].iloc[0])})")
    print(f"edges target sample: {edges_p4['target_node'].head().tolist()} (type: {type(edges_p4['target_node'].iloc[0])})")
    print(f"events source sample: {events_p4['source_node'].head().tolist()} (type: {type(events_p4['source_node'].iloc[0])})")
    print(f"events target sample: {events_p4['target_node'].head().tolist()} (type: {type(events_p4['target_node'].iloc[0])})")
    
    # Check string representations as cast by Spark
    src_e_str = set(events_p4["source_node"].dropna().astype(str))
    tgt_e_str = set(events_p4["target_node"].dropna().astype(str))
    print(f"Unique source str in events: {len(src_e_str)}")
    print(f"Unique target str in events: {len(tgt_e_str)}")
    print(f"Union of events (str):       {len(src_e_str.union(tgt_e_str))}")

    # Check numeric IDs (without float string artifacts)
    src_e_int = set(events_p4["source_node"].dropna().astype(np.int64))
    tgt_e_int = set(events_p4["target_node"].dropna().astype(np.int64))
    print(f"Unique source int in events: {len(src_e_int)}")
    print(f"Unique target int in events: {len(tgt_e_int)}")
    print(f"Union of events (int):       {len(src_e_int.union(tgt_e_int))}")
    print(f"Are target ints subset of source ints? {tgt_e_int.issubset(src_e_int)}")
    print(f"Target ints NOT in source ints: {len(tgt_e_int - src_e_int)}")
    print(f"Source ints NOT in target ints: {len(src_e_int - tgt_e_int)}")

    # Calculations
    src_nodes_events = set(events_p4["source_node"].dropna().unique())
    tgt_nodes_events = set(events_p4["target_node"].dropna().unique())

    src_nodes_edges = set(edges_p4["source_node"].dropna().unique())
    tgt_nodes_edges = set(edges_p4["target_node"].dropna().unique())

    union_events = src_nodes_events.union(tgt_nodes_events)
    union_edges = src_nodes_edges.union(tgt_nodes_edges)
    all_union_non_null = union_events.union(union_edges)

    print("\n--- Calculations on Raw Inputs ---")
    print(f"A. Unique source_node in events: {len(src_nodes_events)}")
    print(f"B. Unique target_node in events (non-null): {len(tgt_nodes_events)}")
    print(f"   Union of events source+target (non-null): {len(union_events)}")
    print(f"   Unique source_node in edges: {len(src_nodes_edges)}")
    print(f"   Unique target_node in edges: {len(tgt_nodes_edges)}")
    print(f"   Union of edges source+target: {len(union_edges)}")
    print(f"C. Union of all source & target IDs across events and edges: {len(all_union_non_null)}")

    # Check Root Broadcasts
    root_events = events_p4[events_p4["propagation_type"] == "ROOT_BROADCAST"]
    print(f"\nD. Number of root-broadcast events: {len(root_events)}")
    print(f"   Unique source_node in root broadcasts: {root_events['source_node'].nunique()}")
    print(f"   Root broadcast source nodes: {root_events['source_node'].tolist()}")
    print(f"   Root broadcast target nodes: {root_events['target_node'].tolist()}")

    # 2. Inspect generated vertices.csv and edges.csv
    v_csv = pd.read_csv("data/features/phase8/graph/vertices.csv", dtype=str)
    e_csv = pd.read_csv("data/features/phase8/graph/edges.csv", dtype=str)
    print("\n--- Generated CSVs ---")
    print(f"E. vertices.csv total rows (Mapped IDs): {len(v_csv)}")
    print(f"   vertices.csv non-null node_name: {v_csv['node_name'].notna().sum()}")
    print(f"   vertices.csv null node_name: {v_csv['node_name'].isna().sum()}")
    print(f"   edges.csv rows: {len(e_csv)}")

    # Examine any null rows in vertices.csv
    null_v = v_csv[v_csv["node_name"].isna()]
    if not null_v.empty:
        print("   Found NULL row in vertices.csv:")
        print(null_v)

    has_dot_zero = v_csv["node_name"].astype(str).str.endswith(".0")
    print(f"   Rows with '.0' in node_name: {has_dot_zero.sum()}")
    print(f"   Rows without '.0' in node_name: {(~has_dot_zero).sum()}")
    print("   Sample rows with .0:")
    print(v_csv[has_dot_zero].head(5))
    print("   Sample rows without .0:")
    print(v_csv[~has_dot_zero].head(5))

    # 3. Inspect GraphX output
    gx_csv = pd.read_csv("data/features/phase8/graph/graphx_vertex_metrics.csv")
    print("\n--- GraphX Output ---")
    print(f"F. graphx_vertex_metrics.csv rows (GraphX vertices): {len(gx_csv)}")
    print(f"   gx null vertex_id count: {gx_csv['vertex_id'].isna().sum()}")
    print(f"   gx min vertex_id: {gx_csv['vertex_id'].min()}, max vertex_id: {gx_csv['vertex_id'].max()}")
    gx_dot_zero = gx_csv[gx_csv["node_name"].astype(str).str.endswith(".0")]
    print(f"   gx vertices ending in '.0': {len(gx_dot_zero)}")
    print(f"   gx .0 in-degree sum:  {gx_dot_zero['in_degree'].sum()}")
    print(f"   gx .0 out-degree sum: {gx_dot_zero['out_degree'].sum()}")

    # Vertex set difference (comparing as integers)
    v_ids = set(v_csv["vertex_id"].astype(int))
    gx_ids = set(gx_csv["vertex_id"].astype(int))
    diff_v_minus_gx = v_ids - gx_ids
    diff_gx_minus_v = gx_ids - v_ids
    print(f"   vertex_ids in vertices.csv but NOT in GraphX: {diff_v_minus_gx}")
    print(f"   vertex_ids in GraphX but NOT in vertices.csv: {diff_gx_minus_v}")
    if diff_v_minus_gx:
        for vid in diff_v_minus_gx:
            print("   Missing from GraphX row in vertices.csv:", v_csv[v_csv["vertex_id"].astype(int) == vid].to_dict("records"))

    # 4. Inspect Batch & Streaming Output representations
    # Streaming output:
    stream_files = []
    import glob
    import os
    stream_parts = glob.glob("data/features/phase8/streaming/windowed_propagation/*.parquet")
    print("\n--- Streaming Output ---")
    print(f"   Streaming parquet partition count: {len(stream_parts)}")
    if stream_parts:
        stream_df = pd.concat([pd.read_parquet(f) for f in stream_parts], ignore_index=True)
        print(f"   Streaming windowed records: {len(stream_df)}")
        print(f"   Streaming sum of total_events across windows: {stream_df['total_events'].sum()}")
        print(f"   Streaming columns: {stream_df.columns.tolist()}")

    # Streaming events processed:
    # Let's check how streaming or reconciliation calculated vertices
    # Let's inspect scripts/phase8/reconcile_batch_streaming.py and scripts/validation/validate_phase8.py
    
    # Summary Report A through H
    print("\n" + "=" * 60)
    print("INDEPENDENT METRICS SUMMARY (A - H)")
    print("=" * 60)
    print(f"A. Unique source node IDs (events):           {len(src_nodes_events)}")
    print(f"B. Unique target node IDs (events, non-null): {len(tgt_nodes_events)}")
    print(f"   Unique target node IDs (events, with NaN): {len(tgt_nodes_events) + 1}")
    print(f"C. Union of source and target IDs (non-null): {len(union_events)}")
    print(f"D. Number of root-broadcast IDs:              {len(root_events)}")
    print(f"   Root broadcast source IDs:                 {root_events['source_node'].tolist()}")
    print(f"E. Number of mapped IDs in vertices.csv:      {len(v_csv)}")
    print(f"F. Number of GraphX vertices:                 {len(gx_csv)}")
    
    import json
    with open("docs/phase8/spark_batch_summary.json") as f:
        b_sum = json.load(f)
    with open("docs/phase8/streaming_metrics_summary.json") as f:
        s_sum = json.load(f)
        
    print(f"G. Number of vertices in batch output:        {b_sum.get('total_unique_graph_vertices')}")
    print(f"H. Number represented in streaming output:    {s_sum.get('stream_total_unique_nodes')}")
    print("=" * 60)

if __name__ == "__main__":
    run_audit()
