#!/usr/bin/env python3
"""
CrisisGuard — Phase 4 Preprocessing: Google DFD-Derived Controlled Development Sample
Author: B.SIVASAI (Roll No: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Processes:
- Canonical media records for Google DFD-derived sample
- Controlled keyframe extraction (without overwhelming storage)
- Spatial artifact feature extraction (Laplacian variance, RGB statistics)
- Output: data/interim/deepfake_dfd/ and data/processed/deepfake_dfd/
"""

import os
import sys
import json
import csv
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
import cv2
import pandas as pd

SEED = 42

def preprocess_dfd():
    print("=" * 60)
    print("CrisisGuard Phase 4: Preprocessing Google DFD-Derived Sample")
    print("=" * 60)

    root = Path(__file__).resolve().parent.parent.parent
    raw_dir = root / "data" / "raw" / "deepfake_dfd"
    interim_dir = root / "data" / "interim" / "deepfake_dfd"
    processed_dir = root / "data" / "processed" / "deepfake_dfd"
    features_dir = root / "data" / "features" / "deepfake_dfd"

    interim_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    features_dir.mkdir(parents=True, exist_ok=True)
    (interim_dir / "frames").mkdir(exist_ok=True)
    (processed_dir / "frames").mkdir(exist_ok=True)

    meta_file = raw_dir / "metadata.json"
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Load official TUM FaceForensics sequence splits
    splits = {}
    for split_name in ["train", "val", "test"]:
        sp_file = raw_dir / "splits" / f"{split_name}.json"
        if sp_file.exists():
            with open(sp_file, "r", encoding="utf-8") as sf:
                splits[split_name] = json.load(sf)

    media_records = []
    frame_samples = []
    feature_records = []

    # Process items in sample_media
    for item in meta.get("sample_media", []):
        media_id = item["media_id"]
        rel_file = item["file"]
        fp = raw_dir / rel_file
        label = item["label"]
        label_name = item["label_name"]
        manip_type = item.get("manipulation_type", "none")

        if not fp.exists():
            print(f"[WARN] File missing: {fp}")
            continue

        file_size = fp.stat().st_size
        ext = fp.suffix.lower()

        if ext == ".gif":
            im = Image.open(fp)
            n_frames = getattr(im, "n_frames", 1)
            w, h = im.size
            media_type = "video/gif"
            # Assign split based on media_id
            split = "test" if "01" in media_id else "val"
            actor_id = "actor_dfd_pair_01" if "01" in media_id else "actor_dfd_pair_02"
        else:
            im = Image.open(fp)
            n_frames = 1
            w, h = im.size
            media_type = "image/png"
            split = "train" if "orig" in media_id else "test"
            actor_id = "actor_dfd_071" if "orig" in media_id else "actor_dfd_054"

        # 1. Canonical media catalog record (Step 2 schema)
        canonical_record = {
            "content_id": f"dfd_{media_id}",
            "source_dataset": "google_dfd_controlled_sample",
            "source_record_id": media_id,
            "media_type": media_type,
            "label": label,
            "label_name": label_name,
            "split": split,
            "actor_id_if_available": actor_id,
            "manipulation_type_if_available": manip_type,
            "width": w,
            "height": h,
            "frame_count": n_frames,
            "file_size_bytes": file_size,
            "source_path": str(fp.relative_to(root)).replace("\\", "/"),
            "governance_type": "REAL"
        }
        media_records.append(canonical_record)

        # 2. Controlled Keyframe Sampling (Step 14)
        if ext == ".gif":
            # Sample up to 5 evenly spaced keyframes
            step = max(1, n_frames // 5)
            sampled_indices = list(range(0, n_frames, step))[:5]
            for idx in sampled_indices:
                im.seek(idx)
                frame_rgb = im.convert("RGB")
                frame_fname = f"{media_id}_frame_{idx:03d}.png"
                interim_frame_path = interim_dir / "frames" / frame_fname
                processed_frame_path = processed_dir / "frames" / frame_fname
                frame_rgb.save(interim_frame_path)
                frame_rgb.save(processed_frame_path)

                # Feature extraction: Laplacian variance (sharpness/blur) & color stats
                np_frame = np.array(frame_rgb)
                gray = cv2.cvtColor(np_frame, cv2.COLOR_RGB2GRAY)
                lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
                mean_r, mean_g, mean_b = [float(x) for x in np_frame.mean(axis=(0, 1))]
                std_r, std_g, std_b = [float(x) for x in np_frame.std(axis=(0, 1))]

                frame_meta = {
                    "content_id": f"dfd_{media_id}_f{idx:03d}",
                    "source_media_id": f"dfd_{media_id}",
                    "source_video": rel_file,
                    "frame_index": idx,
                    "frame_position_sec": round(idx / 25.0, 3),
                    "width": w,
                    "height": h,
                    "label": label,
                    "split": split,
                    "governance_type": "DERIVED"
                }
                frame_samples.append(frame_meta)

                feature_records.append({
                    "content_id": f"dfd_{media_id}_f{idx:03d}",
                    "source_media_id": f"dfd_{media_id}",
                    "label": label,
                    "laplacian_variance": lap_var,
                    "mean_r": mean_r,
                    "mean_g": mean_g,
                    "mean_b": mean_b,
                    "std_r": std_r,
                    "std_g": std_g,
                    "std_b": std_b,
                    "split": split
                })
        else:
            frame_fname = f"{media_id}.png"
            im_rgb = im.convert("RGB")
            im_rgb.save(interim_dir / "frames" / frame_fname)
            im_rgb.save(processed_dir / "frames" / frame_fname)
            np_frame = np.array(im_rgb)
            gray = cv2.cvtColor(np_frame, cv2.COLOR_RGB2GRAY)
            lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            mean_r, mean_g, mean_b = [float(x) for x in np_frame.mean(axis=(0, 1))]
            std_r, std_g, std_b = [float(x) for x in np_frame.std(axis=(0, 1))]

            frame_samples.append({
                "content_id": f"dfd_{media_id}",
                "source_media_id": f"dfd_{media_id}",
                "source_video": rel_file,
                "frame_index": 0,
                "frame_position_sec": 0.0,
                "width": w,
                "height": h,
                "label": label,
                "split": split,
                "governance_type": "DERIVED"
            })
            feature_records.append({
                "content_id": f"dfd_{media_id}",
                "source_media_id": f"dfd_{media_id}",
                "label": label,
                "laplacian_variance": lap_var,
                "mean_r": mean_r,
                "mean_g": mean_g,
                "mean_b": mean_b,
                "std_r": std_r,
                "std_g": std_g,
                "std_b": std_b,
                "split": split
            })

    # Save media records
    df_media = pd.DataFrame(media_records)
    df_media.to_csv(interim_dir / "media_catalog.csv", index=False)
    df_media.to_csv(processed_dir / "media_records.csv", index=False)
    df_media.to_parquet(processed_dir / "media_records.parquet", index=False)

    # Save frame samples
    df_frames = pd.DataFrame(frame_samples)
    df_frames.to_csv(interim_dir / "frame_samples.csv", index=False)
    df_frames.to_csv(processed_dir / "frame_samples.csv", index=False)
    df_frames.to_parquet(processed_dir / "frame_samples.parquet", index=False)

    # Save features
    df_feat = pd.DataFrame(feature_records)
    df_feat.to_csv(features_dir / "video_features.csv", index=False)
    df_feat.to_parquet(features_dir / "video_features.parquet", index=False)

    print(f"DFD Processing Complete:")
    print(f"  Canonical media records: {len(df_media)}")
    print(f"  Sampled keyframes: {len(df_frames)}")
    print(f"  Feature records: {len(df_feat)}")
    print(f"  Interim directory: {interim_dir}")
    print(f"  Processed directory: {processed_dir}")
    print(f"  Features directory: {features_dir}")
    return True

if __name__ == "__main__":
    success = preprocess_dfd()
    sys.exit(0 if success else 1)
