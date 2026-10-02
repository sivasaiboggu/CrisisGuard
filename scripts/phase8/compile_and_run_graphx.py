#!/usr/bin/env python3
"""
CrisisGuard — Phase 8: Compile and Execute GraphX Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Compiles PropagationGraph.scala using scalac against Spark GraphX jars,
packages the class files into a JAR, executes via spark-submit,
and pushes generated graph metrics back into HDFS.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run():
    print("=" * 70)
    print("CRISISGUARD — PHASE 8 GRAPHX COMPILATION & EXECUTION")
    print("=" * 70)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    print("=" * 70)
    
    root = Path(__file__).resolve().parent.parent.parent
    src_file = root / "src" / "phase8" / "graphx" / "PropagationGraph.scala"
    build_dir = root / "target" / "phase8" / "classes"
    jar_file = root / "target" / "phase8" / "crisisguard-graphx.jar"
    
    build_dir.mkdir(parents=True, exist_ok=True)
    
    spark_jars_glob = "/usr/local/lib/python3.12/dist-packages/pyspark/jars/*"
    
    # 1. Compile with scalac
    print(f"\n[1] Compiling {src_file.name} with scalac 2.12.18...")
    t0 = time.time()
    compile_cmd = f'scalac -cp "{spark_jars_glob}" -d "{build_dir}" "{src_file}"'
    res = os.system(compile_cmd)
    if res != 0:
        print(f"Compilation failed with exit code {res}")
        return False
    print(f"Compilation succeeded in {time.time() - t0:.2f}s")
    
    # 2. Package into JAR using jar tool
    print(f"\n[2] Packaging classes into JAR: {jar_file.relative_to(root)}...")
    jar_cmd = f'jar -cf "{jar_file}" -C "{build_dir}" .'
    res_jar = os.system(jar_cmd)
    if res_jar != 0:
        print(f"JAR packaging failed with exit code {res_jar}")
        return False
    print(f"Created JAR: {jar_file} ({jar_file.stat().st_size:,} bytes)")
    
    # 3. Execute via spark-submit
    print(f"\n[3] Executing Spark GraphX job via spark-submit...")
    t1 = time.time()
    submit_cmd = (
        f'spark-submit '
        f'--class crisisguard.phase8.graphx.PropagationGraph '
        f'--master "local[2]" '
        f'--driver-memory 2g '
        f'"{jar_file}" '
        f'"hdfs://localhost:9000/crisisguard/phase8/graph/vertices.csv" '
        f'"hdfs://localhost:9000/crisisguard/phase8/graph/edges.csv" '
        f'"{root}/data/features/phase8/graph"'
    )
    print(f"Running: {submit_cmd}")
    res_submit = os.system(submit_cmd)
    if res_submit != 0:
        print(f"GraphX execution failed with exit code {res_submit}")
        return False
        
    execution_time = time.time() - t1
    print(f"GraphX job completed in {execution_time:.2f}s")
    
    # 4. Upload results to HDFS
    print(f"\n[4] Uploading GraphX results to HDFS (/crisisguard/phase8/graph/)...")
    local_csv = root / "data" / "features" / "phase8" / "graph" / "graphx_vertex_metrics.csv"
    if local_csv.exists():
        put_cmd = f'/opt/hadoop/bin/hdfs dfs -put -f "{local_csv}" /crisisguard/phase8/graph/'
        os.system(put_cmd)
        print(f"Uploaded {local_csv.name} to HDFS.")
        
    # Also verify HDFS
    os.system('/opt/hadoop/bin/hdfs dfs -ls /crisisguard/phase8/graph/')
    
    print("\n" + "=" * 70)
    print(f"OVERALL GRAPHX PIPELINE: PASS ({execution_time:.2f}s)")
    print("=" * 70)
    return True

if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
