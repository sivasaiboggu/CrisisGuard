#!/usr/bin/env python3
"""
CrisisGuard — Phase 6 Input Re-validation Script
Author: B.SIVASAI (2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Independently validates raw and processed media assets for:
- Branch A: Google DFD-derived controlled video sample
- Branch B: CIFAKE image forensics dataset
Checks file existence, integrity, SHA256 uniqueness, dimensions, and zero corruption.
"""

import os
import sys
import hashlib
import json
import pandas as pd
from PIL import Image

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def validate_dfd():
    print("\n--- Validating Branch A: Google DFD-Derived Controlled Sample ---")
    dfd_raw_meta = "data/raw/deepfake_dfd/metadata.json"
    assert os.path.exists(dfd_raw_meta), f"Missing DFD raw metadata: {dfd_raw_meta}"
    with open(dfd_raw_meta, "r") as f:
        meta = json.load(f)
    print(f"Loaded DFD raw metadata: {meta.get('dataset_name')}")
    
    media_proc = "data/processed/deepfake_dfd/media_records.parquet"
    frames_proc = "data/processed/deepfake_dfd/frame_samples.parquet"
    assert os.path.exists(media_proc), f"Missing DFD processed media: {media_proc}"
    assert os.path.exists(frames_proc), f"Missing DFD processed frames: {frames_proc}"
    
    df_media = pd.read_parquet(media_proc)
    df_frames = pd.read_parquet(frames_proc)
    
    print(f"DFD Media records count: {len(df_media)}")
    print(f"DFD Sampled frames count: {len(df_frames)}")
    
    # Check media files
    for idx, row in df_media.iterrows():
        src = row["source_path"]
        assert os.path.exists(src), f"DFD media file missing: {src}"
        assert os.path.getsize(src) > 0, f"DFD media file empty: {src}"
        print(f"  Verified media: {row['content_id']} | Type: {row['media_type']} | Label: {row['label']} ({row['label_name']}) | Path: {src}")
    
    # Check extracted frame files
    for idx, row in df_frames.iterrows():
        frame_idx = int(row['frame_index'])
        src_id = row['source_media_id']
        # Try both patterns: dfd_video_sample_01_frame_000.png or dfd_frame_actor_orig.png
        possible_paths = [
            f"data/processed/deepfake_dfd/frames/{src_id.replace('dfd_dfd_', 'dfd_')}_frame_{frame_idx:03d}.png",
            f"data/processed/deepfake_dfd/frames/{src_id.replace('dfd_dfd_', 'dfd_')}.png",
            f"data/processed/deepfake_dfd/frames/{row['content_id']}.png"
        ]
        found = any(os.path.exists(p) for p in possible_paths)
        assert found, f"Missing frame binary for {row['content_id']}. Checked: {possible_paths}"
        
    print("DFD Controlled Sample Input Validation: PASS")
    return True

def validate_cifake():
    print("\n--- Validating Branch B: CIFAKE Image Forensics Dataset ---")
    cifake_proc = "data/processed/cifake/cifake_records.parquet"
    assert os.path.exists(cifake_proc), f"Missing CIFAKE processed records: {cifake_proc}"
    
    df = pd.read_parquet(cifake_proc)
    print(f"CIFAKE Records Count: {len(df)}")
    assert len(df) == 500, f"Expected 500 CIFAKE records, found {len(df)}"
    
    real_count = (df['label'] == 0).sum()
    synth_count = (df['label'] == 1).sum()
    print(f"Class Balance: Real = {real_count} | Synthetic = {synth_count}")
    assert real_count == 250 and synth_count == 250, f"Expected exact 250/250 balance, got {real_count}/{synth_count}"
    
    hashes = set()
    corrupted_count = 0
    dim_mismatches = 0
    
    for idx, row in df.iterrows():
        p = row['source_path']
        assert os.path.exists(p), f"CIFAKE raw image not found: {p}"
        sha = compute_sha256(p)
        assert sha == row['sha256'], f"SHA256 mismatch for {p}: computed {sha} vs stored {row['sha256']}"
        hashes.add(sha)
        
        # Verify image opens without corruption and dimensions match
        try:
            with Image.open(p) as img:
                w, h = img.size
                if w != row['width'] or h != row['height']:
                    dim_mismatches += 1
                img.verify()
        except Exception as e:
            corrupted_count += 1
            print(f"Corrupted image detected: {p} ({e})")
            
    print(f"Unique SHA256 Hashes: {len(hashes)} / {len(df)}")
    assert len(hashes) == len(df), f"Duplicate images detected! Unique: {len(hashes)}"
    assert corrupted_count == 0, f"Corrupted images found: {corrupted_count}"
    assert dim_mismatches == 0, f"Dimension mismatches found: {dim_mismatches}"
    print("CIFAKE Input Validation: PASS")
    return True

def main():
    print("============================================================")
    print("CRISISGUARD — PHASE 6 INPUT DATASET RE-VALIDATION")
    print("Author: B.SIVASAI (2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("============================================================")
    
    dfd_ok = validate_dfd()
    cifake_ok = validate_cifake()
    
    print("\n============================================================")
    print("PHASE 6 INPUT VALIDATION SUMMARY")
    print("============================================================")
    print(f"Branch A (Google DFD Sample): {'PASS' if dfd_ok else 'FAIL'}")
    print(f"Branch B (CIFAKE Images):     {'PASS' if cifake_ok else 'FAIL'}")
    all_ok = dfd_ok and cifake_ok
    print(f"Overall Input Status:        {'PASS' if all_ok else 'FAIL'}")
    print("============================================================")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
