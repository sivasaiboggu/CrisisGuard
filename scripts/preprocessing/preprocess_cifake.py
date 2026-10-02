#!/usr/bin/env python3
"""
CrisisGuard — Phase 4 Preprocessing: CIFAKE AI-Generated Synthetic Images
Author: B.SIVASAI (Roll No: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Processes:
- 500 authentic benchmark images (250 Real CIFAR-10, 250 Stable Diffusion v1.4)
- Verification of labels: label 0 = real, label 1 = synthetic
- Image integrity and SHA256 verification
- Extraction of spatial and frequency-domain artifact features (Laplacian, FFT energy, RGB stats)
- Canonical interim, processed, and feature tables (Parquet & CSV)
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import pandas as pd

SEED = 42

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def preprocess_cifake():
    print("=" * 60)
    print("CrisisGuard Phase 4: Preprocessing CIFAKE Image Forensics Dataset")
    print("=" * 60)

    root = Path(__file__).resolve().parent.parent.parent
    raw_dir = root / "data" / "raw" / "synthetic_media_eval"
    interim_dir = root / "data" / "interim" / "cifake"
    processed_dir = root / "data" / "processed" / "cifake"
    features_dir = root / "data" / "features" / "cifake"

    interim_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    features_dir.mkdir(parents=True, exist_ok=True)

    meta_file = raw_dir / "metadata.json"
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    records = meta.get("records", [])
    print(f"Loaded {len(records)} records from {meta_file.name}")

    canonical_records = []
    feature_records = []
    hash_set = set()
    corrupt_count = 0
    duplicate_count = 0

    for idx, rec in enumerate(records):
        rel_path = rec["file"]
        fp = raw_dir / rel_path
        if not fp.exists():
            print(f"[WARN] Image file missing: {fp}")
            corrupt_count += 1
            continue

        # Integrity & hash check
        f_hash = sha256_file(fp)
        if f_hash in hash_set:
            duplicate_count += 1
        hash_set.add(f_hash)

        try:
            im = Image.open(fp)
            im.verify()  # verify integrity
            im = Image.open(fp)  # reopen after verify
            w, h = im.size
            channels = len(im.getbands())
        except Exception as e:
            print(f"[ERR] Corrupted image {fp}: {e}")
            corrupt_count += 1
            continue

        label = rec["label"]
        generator = rec["generator"]
        source_rec_id = Path(rel_path).stem
        content_id = f"cifake_{'syn' if label == 1 else 'real'}_{source_rec_id.replace(' ', '_').replace('(', '').replace(')', '')}"

        # Canonical interim schema (Step 3)
        canon_item = {
            "content_id": content_id,
            "source_dataset": "cifake_benchmark",
            "source_record_id": source_rec_id,
            "media_type": "image/jpeg",
            "label": label,
            "label_name": "synthetic" if label == 1 else "real",
            "generator": generator,
            "width": w,
            "height": h,
            "channels": channels,
            "file_size_bytes": fp.stat().st_size,
            "sha256": f_hash,
            "source_path": str(fp.relative_to(root)).replace("\\", "/"),
            "governance_type": "REAL"
        }
        canonical_records.append(canon_item)

        # Image feature extraction (spatial & frequency domain)
        im_rgb = im.convert("RGB")
        np_arr = np.array(im_rgb, dtype=np.float32) / 255.0  # normalized [0, 1]
        gray = cv2.cvtColor((np_arr * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)

        # Spatial Laplacian variance (high-frequency artifact indicator)
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # Frequency domain 2D FFT energy
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.log(np.abs(f_shift) + 1e-7)
        fft_mean_energy = float(magnitude_spectrum.mean())
        fft_std_energy = float(magnitude_spectrum.std())

        # Color channel statistics
        r_mean, g_mean, b_mean = [float(x) for x in np_arr.mean(axis=(0, 1))]
        r_std, g_std, b_std = [float(x) for x in np_arr.std(axis=(0, 1))]

        feature_records.append({
            "content_id": content_id,
            "label": label,
            "generator": generator,
            "original_width": w,
            "original_height": h,
            "processed_width": 32,
            "processed_height": 32,
            "channels": channels,
            "normalization_method": "minmax_0_1_rgb",
            "laplacian_variance": round(lap_var, 4),
            "fft_mean_energy": round(fft_mean_energy, 4),
            "fft_std_energy": round(fft_std_energy, 4),
            "mean_r": round(r_mean, 4),
            "mean_g": round(g_mean, 4),
            "mean_b": round(b_mean, 4),
            "std_r": round(r_std, 4),
            "std_g": round(g_std, 4),
            "std_b": round(b_std, 4)
        })

    # Save interim and processed tables
    df_canon = pd.DataFrame(canonical_records)
    df_canon.to_csv(interim_dir / "cifake_catalog.csv", index=False)
    df_canon.to_csv(processed_dir / "cifake_records.csv", index=False)
    df_canon.to_parquet(processed_dir / "cifake_records.parquet", index=False)

    df_feat = pd.DataFrame(feature_records)
    df_feat.to_csv(features_dir / "image_forensics_features.csv", index=False)
    df_feat.to_parquet(features_dir / "image_forensics_features.parquet", index=False)

    print(f"\nCIFAKE Processing Summary:")
    print(f"  Valid Processed Images: {len(df_canon)}")
    print(f"  Real Images (label 0): {sum(df_canon['label'] == 0)}")
    print(f"  Synthetic Images (label 1): {sum(df_canon['label'] == 1)}")
    print(f"  Duplicates Detected: {duplicate_count}")
    print(f"  Corrupt Images: {corrupt_count}")
    print(f"  Feature Dimensions: {df_feat.shape[1]} columns")
    print(f"  Interim Path: {interim_dir}")
    print(f"  Processed Path: {processed_dir}")
    print(f"  Features Path: {features_dir}")

    return len(df_canon) == 500

if __name__ == "__main__":
    success = preprocess_cifake()
    sys.exit(0 if success else 1)
