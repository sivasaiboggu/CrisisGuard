#!/usr/bin/env python3
"""
CrisisGuard — Phase 6 Image Preprocessing & Partitioning
Author: B.SIVASAI (2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Prepares CIFAKE images for the image forensics model:
- Deterministic 70/15/15 stratified train/val/test partitioning (seed 42).
- Standardized image tensor transformations (resizing to 64x64, normalization).
- Preserves content_id, label, SHA256 hash, and provenance metadata.
- Serializes feature partition metadata and preprocessed tensor dataset.
"""

import os
import sys
import yaml
import torch
import torchvision.transforms as transforms
import pandas as pd
from PIL import Image
from sklearn.model_selection import StratifiedShuffleSplit

def load_config():
    with open("config/synthetic_media.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    print("============================================================")
    print("CRISISGUARD — IMAGE PREPROCESSING & PARTITIONING")
    print("Author: B.SIVASAI (2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("============================================================")
    
    cfg = load_config()
    seed = cfg['reproducibility']['global_seed']
    img_size = cfg['image_branch']['image_size']
    out_dir = cfg['paths']['features_output_dir']
    os.makedirs(out_dir, exist_ok=True)
    
    proc_parquet = cfg['paths']['cifake_processed_parquet']
    df = pd.read_parquet(proc_parquet)
    print(f"Loaded {len(df)} records from {proc_parquet}")
    
    # 1. Deterministic Stratified Train / Val / Test Partitioning
    # 70% Train (350), 15% Val (75), 15% Test (75)
    sss_test = StratifiedShuffleSplit(n_splits=1, test_size=0.15, random_state=seed)
    train_val_idx, test_idx = next(sss_test.split(df, df['label']))
    
    df_train_val = df.iloc[train_val_idx].copy()
    df_test = df.iloc[test_idx].copy()
    df_test['split'] = 'test'
    
    # Split train_val into train (70/85) and val (15/85)
    val_rel_size = 0.15 / 0.85
    sss_val = StratifiedShuffleSplit(n_splits=1, test_size=val_rel_size, random_state=seed)
    train_idx, val_idx = next(sss_val.split(df_train_val, df_train_val['label']))
    
    df_train = df_train_val.iloc[train_idx].copy()
    df_val = df_train_val.iloc[val_idx].copy()
    df_train['split'] = 'train'
    df_val['split'] = 'val'
    
    df_partitioned = pd.concat([df_train, df_val, df_test]).sort_values('content_id').reset_index(drop=True)
    
    print("\n--- Partition Distribution Summary ---")
    for s in ['train', 'val', 'test']:
        sub = df_partitioned[df_partitioned['split'] == s]
        r_c = (sub['label'] == 0).sum()
        s_c = (sub['label'] == 1).sum()
        print(f"Split: {s.upper():<6} | Total: {len(sub):<3} | Real (0): {r_c:<3} | Synthetic (1): {s_c:<3}")
        
    # 2. Tensor Transformation
    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    image_tensors = []
    labels = []
    splits = []
    content_ids = []
    
    print(f"\nProcessing {len(df_partitioned)} images into {img_size}x{img_size} normalized tensors...")
    for idx, row in df_partitioned.iterrows():
        p = row['source_path']
        with Image.open(p) as img:
            rgb_img = img.convert('RGB')
            tensor = transform(rgb_img)
            image_tensors.append(tensor)
            labels.append(int(row['label']))
            splits.append(row['split'])
            content_ids.append(row['content_id'])
            
    stacked_tensors = torch.stack(image_tensors)  # (500, 3, 64, 64)
    tensor_labels = torch.tensor(labels, dtype=torch.long)
    
    print(f"Stacked Tensor Shape: {stacked_tensors.shape}")
    print(f"Tensor Mean: {stacked_tensors.mean():.4f} | Std: {stacked_tensors.std():.4f}")
    
    # 3. Serialization
    partitions_parquet = os.path.join(out_dir, "cifake_partitions.parquet")
    tensors_pt = os.path.join(out_dir, "cifake_tensors.pt")
    
    df_partitioned.to_parquet(partitions_parquet, index=False)
    torch.save({
        "tensors": stacked_tensors,
        "labels": tensor_labels,
        "splits": splits,
        "content_ids": content_ids,
        "image_size": img_size,
        "normalization": {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]}
    }, tensors_pt)
    
    print("\n============================================================")
    print("IMAGE PREPROCESSING COMPLETE")
    print("============================================================")
    print(f"Partitions Parquet: {partitions_parquet} ({len(df_partitioned)} records)")
    print(f"Serialized Tensors: {tensors_pt}")
    print("Status: PASS")
    print("============================================================")

if __name__ == "__main__":
    main()
