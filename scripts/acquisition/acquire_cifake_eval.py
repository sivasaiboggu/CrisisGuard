#!/usr/bin/env python3
"""
CrisisGuard — Independent Synthetic-Media Evaluation Dataset Acquisition (Fast Concurrent)
Acquires a controlled, reproducible subset of the CIFAKE benchmark
(Bird & Lotfi, IEEE Access 2024) directly from the official project repository:
https://github.com/jordan-bird/CIFAKE-Real-and-AI-Generated-Synthetic-Images

Dataset: CIFAKE (Real photographic CIFAR-10 vs Stable Diffusion v1.4 Synthetic)
License: Creative Commons Attribution 4.0 International (CC BY 4.0)
Sampling: Deterministic pseudo-random selection with seed=42.
Total Target: 250 REAL + 250 FAKE = 500 images (~1.5 MB total footprint).
"""

import os
import sys
import json
import random
import hashlib
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def download_single_image(args):
    raw_url, out_path, headers = args
    if not os.path.exists(out_path):
        req = urllib.request.Request(raw_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp, open(out_path, "wb") as f:
            f.write(resp.read())
    return out_path

def acquire_cifake_subset(target_dir="data/raw/synthetic_media_eval", sample_size_per_class=250, seed=42):
    print("=" * 60)
    print("CrisisGuard: Acquiring Independent Synthetic-Media Evaluation Dataset")
    print("Dataset: CIFAKE (Bird & Lotfi, IEEE Access 2024)")
    print(f"Target Directory: {target_dir}")
    print(f"Sample Size: {sample_size_per_class} Real + {sample_size_per_class} Synthetic = {sample_size_per_class * 2} Total")
    print(f"Selection Seed: {seed}")
    print("=" * 60)

    real_dir = os.path.join(target_dir, "real")
    fake_dir = os.path.join(target_dir, "fake")
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)

    base_raw_url = "https://raw.githubusercontent.com/jordan-bird/CIFAKE-Real-and-AI-Generated-Synthetic-Images/main/DATASET/test"
    base_api_url = "https://api.github.com/repos/jordan-bird/CIFAKE-Real-and-AI-Generated-Synthetic-Images/contents/DATASET/test"

    metadata = {
        "dataset_name": "CIFAKE: Real and AI-Generated Synthetic Images",
        "official_source": "Nottingham Trent University / IEEE Access 2024",
        "authors": "Jordan J. Bird and Ahmad Lotfi",
        "citation": "Bird, J.J. and Lotfi, A., 2024. CIFAKE: Image Classification and Explainable Identification of AI-Generated Synthetic Images. IEEE Access.",
        "official_repository": "https://github.com/jordan-bird/CIFAKE-Real-and-AI-Generated-Synthetic-Images",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "provenance_mode": "REAL DATA (Authentic Academic Benchmark Release)",
        "selection_method": f"Deterministic uniform random sampling without replacement (seed={seed})",
        "selection_seed": seed,
        "sample_size_per_class": sample_size_per_class,
        "total_samples": sample_size_per_class * 2,
        "records": []
    }

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    classes = [
        {"class_name": "REAL", "out_dir": real_dir, "label": 0, "label_name": "pristine", "generator": "none (CIFAR-10 photographic)"},
        {"class_name": "FAKE", "out_dir": fake_dir, "label": 1, "label_name": "synthetic", "generator": "Stable Diffusion v1.4"}
    ]

    all_download_tasks = []
    file_metadata_map = {}

    for cls_info in classes:
        cls_name = cls_info["class_name"]
        print(f"\nFetching index for {cls_name}...")
        api_url = f"{base_api_url}/{cls_name}"
        req = urllib.request.Request(api_url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                file_list = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"Error accessing GitHub API for {cls_name}: {e}")
            file_list = [{"name": f"{i:04d} (2).jpg"} for i in range(sample_size_per_class)]

        img_names = [item["name"] for item in file_list if item.get("name", "").endswith(".jpg")]
        print(f"Found {len(img_names)} candidates in {cls_name} index.")

        rng = random.Random(seed)
        if len(img_names) >= sample_size_per_class:
            selected_names = sorted(rng.sample(img_names, sample_size_per_class))
        else:
            selected_names = sorted(img_names)

        for fname in selected_names:
            out_path = os.path.join(cls_info["out_dir"], fname)
            quoted_fname = urllib.parse.quote(fname)
            raw_url = f"{base_raw_url}/{cls_name}/{quoted_fname}"
            all_download_tasks.append((raw_url, out_path, headers))
            file_metadata_map[out_path] = (cls_info, fname)

    print(f"\nDownloading {len(all_download_tasks)} images concurrently with 20 workers...")
    completed = 0
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(download_single_image, task): task for task in all_download_tasks}
        for future in as_completed(futures):
            try:
                out_path = future.result()
                completed += 1
                if completed % 100 == 0 or completed == len(all_download_tasks):
                    print(f"  Downloaded [{completed}/{len(all_download_tasks)}] images...")
            except Exception as exc:
                print(f"  Download error: {exc}")

    # Build metadata records
    print("\nComputing SHA256 checksums and building metadata catalog...")
    for out_path, (cls_info, fname) in file_metadata_map.items():
        if os.path.exists(out_path):
            file_hash = sha256_file(out_path)
            file_size = os.path.getsize(out_path)
            rel_path = os.path.relpath(out_path, target_dir).replace("\\", "/")

            metadata["records"].append({
                "file": rel_path,
                "label": cls_info["label"],
                "label_name": cls_info["label_name"],
                "generator": cls_info["generator"],
                "resolution": "32x32x3",
                "format": "JPEG",
                "size_bytes": file_size,
                "sha256": file_hash
            })

    # Sort records deterministically by file path
    metadata["records"].sort(key=lambda x: x["file"])

    meta_path = os.path.join(target_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    total_downloaded = len(metadata["records"])
    real_count = sum(1 for r in metadata["records"] if r["label"] == 0)
    fake_count = sum(1 for r in metadata["records"] if r["label"] == 1)
    total_size = sum(r["size_bytes"] for r in metadata["records"])

    print("\n" + "=" * 60)
    print("CIFAKE Acquisition Summary:")
    print(f"  Total Valid Records: {total_downloaded}")
    print(f"  Pristine / Real: {real_count}")
    print(f"  Synthetic (Stable Diffusion): {fake_count}")
    print(f"  Total Size: {total_size / 1024:.2f} KB ({total_size / (1024*1024):.2f} MB)")
    print(f"  Metadata Path: {meta_path}")
    print("=" * 60)

    return total_downloaded == (sample_size_per_class * 2)

if __name__ == "__main__":
    success = acquire_cifake_subset()
    sys.exit(0 if success else 1)
