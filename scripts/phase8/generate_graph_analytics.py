#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: Graph Analytics & Visualization Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Produces analytical figures and tables for:
1. Degree distribution (In-degree power-law tail)
2. PageRank structural centrality distribution
3. Cascade size & connected components decomposition
4. Temporal propagation rate progression across scenarios
"""

import sys
import os
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def generate_analytics():
    print("=" * 70)
    print("CRISISGUARD — PHASE 8 GRAPH ANALYTICS & VISUALIZATION")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    print("=" * 70)
    
    root = Path(__file__).resolve().parent.parent.parent
    graph_metrics_csv = root / "data" / "features" / "phase8" / "graph" / "graphx_vertex_metrics.csv"
    stream_metrics_parquet = root / "data" / "features" / "phase8" / "streaming" / "propagation_stream_metrics.parquet"
    
    figs_dir = root / "docs" / "phase8" / "figures"
    figs_dir.mkdir(parents=True, exist_ok=True)
    
    if not graph_metrics_csv.exists() or not stream_metrics_parquet.exists():
        print("Missing required metric files.")
        return False
        
    df_graph = pd.read_csv(graph_metrics_csv)
    df_stream = pd.read_parquet(stream_metrics_parquet)
    
    # -------------------------------------------------------------
    # Plot 1: In-Degree Distribution
    # -------------------------------------------------------------
    print("\n[1] Generating In-Degree Distribution plot...")
    plt.figure(figsize=(8, 5))
    in_deg_counts = df_graph["in_degree"].value_counts().sort_index()
    plt.bar(in_deg_counts.index, in_deg_counts.values, color="#1f77b4", edgecolor="black", alpha=0.85)
    plt.yscale("log")
    plt.xlabel("In-Degree (Inbound Forwarding Transmissions)", fontsize=11, fontweight="bold")
    plt.ylabel("Vertex Count (Log Scale)", fontsize=11, fontweight="bold")
    plt.title("CrisisGuard Phase 8: In-Degree Distribution (GraphX)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plot1_path = figs_dir / "degree_distribution.png"
    plt.savefig(plot1_path, dpi=200)
    plt.close()
    print(f"  Saved: {plot1_path}")
    
    # -------------------------------------------------------------
    # Plot 2: PageRank Distribution
    # -------------------------------------------------------------
    print("\n[2] Generating PageRank Centrality Distribution plot...")
    plt.figure(figsize=(8, 5))
    plt.hist(df_graph["pagerank"], bins=40, color="#ff7f0e", edgecolor="black", alpha=0.85)
    plt.yscale("log")
    plt.xlabel("PageRank Structural Centrality Score", fontsize=11, fontweight="bold")
    plt.ylabel("Vertex Count (Log Scale)", fontsize=11, fontweight="bold")
    plt.title("CrisisGuard Phase 8: PageRank Score Distribution", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plot2_path = figs_dir / "pagerank_distribution.png"
    plt.savefig(plot2_path, dpi=200)
    plt.close()
    print(f"  Saved: {plot2_path}")
    
    # -------------------------------------------------------------
    # Plot 3: Temporal Propagation Rate Across Scenarios
    # -------------------------------------------------------------
    print("\n[3] Generating Temporal Propagation Rate plot...")
    plt.figure(figsize=(10, 5))
    scenarios = df_stream["scenario_id"].unique()
    colors = {"COORDINATED_BOT_BURST": "#d62728", "HIGH_VELOCITY_VIRAL": "#9467bd", "ORGANIC_DIFFUSION": "#2ca02c"}
    
    for sc in scenarios:
        sub = df_stream[df_stream["scenario_id"] == sc].sort_values("window_start")
        # Extract hours from start
        times = [i for i in range(len(sub))]
        rates = sub["propagation_rate_per_min"].values
        plt.plot(times, rates, marker="o", label=sc, color=colors.get(sc, "blue"), linewidth=2)
        
    plt.xlabel("Active Time Window Index (1-Hour Intervals)", fontsize=11, fontweight="bold")
    plt.ylabel("Propagation Rate (Events / Minute)", fontsize=11, fontweight="bold")
    plt.title("CrisisGuard Phase 8: Real-Time Stream Propagation Velocity", fontsize=12, fontweight="bold")
    plt.legend(frameon=True, facecolor="white", loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plot3_path = figs_dir / "temporal_propagation_rate.png"
    plt.savefig(plot3_path, dpi=200)
    plt.close()
    print(f"  Saved: {plot3_path}")
    
    # -------------------------------------------------------------
    # Plot 4: Connected Components Decomposition
    # -------------------------------------------------------------
    print("\n[4] Generating Connected Components Decomposition plot...")
    plt.figure(figsize=(8, 5))
    cc_counts = df_graph["component_id"].value_counts().values
    plt.plot(range(1, min(51, len(cc_counts) + 1)), cc_counts[:50], color="#8c564b", linewidth=2.5)
    plt.yscale("log")
    plt.xlabel("Component Rank (Top 50)", fontsize=11, fontweight="bold")
    plt.ylabel("Component Size (Vertices, Log Scale)", fontsize=11, fontweight="bold")
    plt.title("CrisisGuard Phase 8: Connected Components Size Rank", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plot4_path = figs_dir / "component_sizes.png"
    plt.savefig(plot4_path, dpi=200)
    plt.close()
    print(f"  Saved: {plot4_path}")
    
    print("\nAll Graph Analytics visualizations generated successfully.")
    return True

if __name__ == "__main__":
    ok = generate_analytics()
    sys.exit(0 if ok else 1)
