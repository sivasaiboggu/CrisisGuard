#!/usr/bin/env python3
"""
CrisisGuard — Phase 6 Video Preprocessing & Feature Extraction
Author: B.SIVASAI (2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Extracts uniform temporal keyframes from Google DFD-derived controlled samples,
processes frames into standardized tensors, extracts deep feature representations,
and serializes video-atomic features for video-level evaluation.
"""

import os
import sys
import yaml
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import pandas as pd
from PIL import Image

def load_config():
    with open("config/synthetic_media.yaml", "r") as f:
        return yaml.safe_load(f)

def extract_uniform_frames_from_gif(gif_path, num_frames=5):
    """Deterministically extracts num_frames uniformly spaced from an animated GIF."""
    frames = []
    with Image.open(gif_path) as img:
        total_frames = getattr(img, 'n_frames', 1)
        if total_frames <= num_frames:
            step = 1
            indices = list(range(total_frames))
        else:
            step = total_frames / num_frames
            indices = [int(i * step) for i in range(num_frames)]
            
        for idx in indices:
            img.seek(idx)
            frame = img.convert('RGB')
            frames.append((idx, frame.copy()))
    return frames, total_frames

def main():
    print("============================================================")
    print("CRISISGUARD — VIDEO PREPROCESSING & FEATURE EXTRACTION")
    print("Author: B.SIVASAI (2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("============================================================")
    
    cfg = load_config()
    seed = cfg['reproducibility']['global_seed']
    torch.manual_seed(seed)
    
    out_dir = cfg['paths']['dfd_features_dir']
    os.makedirs(out_dir, exist_ok=True)
    
    # Standardize image transformation
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Load ResNet18 feature extractor
    print("Loading pretrained ResNet-18 feature extraction backbone...")
    weights = models.ResNet18_Weights.DEFAULT
    backbone = models.resnet18(weights=weights)
    # Strip final classification head to output 512-dim embedding
    backbone.fc = torch.nn.Identity()
    backbone.eval()
    
    dfd_proc_media = cfg['paths']['dfd_processed_dir'] + "media_records.parquet"
    df_media = pd.read_parquet(dfd_proc_media)
    print(f"Loaded {len(df_media)} media records from {dfd_proc_media}")
    
    video_records = []
    frame_records = []
    video_tensors = {}
    
    with torch.no_grad():
        for idx, row in df_media.iterrows():
            content_id = row['content_id']
            src_path = row['source_path']
            media_type = row['media_type']
            label = int(row['label'])
            split = row['split']
            actor_id = row.get('actor_id_if_available', 'unknown')
            
            print(f"\nProcessing media: {content_id} ({media_type}) | Split: {split} | Path: {src_path}")
            
            if "gif" in media_type or src_path.endswith(".gif"):
                raw_frames, total_f = extract_uniform_frames_from_gif(src_path, num_frames=5)
            else:
                # Single keyframe image
                with Image.open(src_path) as img:
                    raw_frames = [(0, img.convert('RGB'))]
                total_f = 1
                
            frame_tensors = []
            frame_features = []
            
            for f_idx, f_img in raw_frames:
                t = transform(f_img).unsqueeze(0)  # (1, 3, 224, 224)
                feat = backbone(t).squeeze(0)      # (512,)
                frame_tensors.append(t.squeeze(0))
                frame_features.append(feat)
                
                frame_id = f"{content_id}_f{f_idx:03d}"
                frame_records.append({
                    "frame_id": frame_id,
                    "content_id": content_id,
                    "frame_index": f_idx,
                    "label": label,
                    "split": split,
                    "actor_id": actor_id,
                    "feature_norm": float(torch.norm(feat).item()),
                    "governance_type": "DERIVED_FEATURE"
                })
                
            stacked_feats = torch.stack(frame_features)  # (N_frames, 512)
            # Temporal mean pooling
            video_feat = torch.mean(stacked_feats, dim=0)  # (512,)
            video_tensors[content_id] = {
                "frame_tensors": torch.stack(frame_tensors),
                "frame_features": stacked_feats,
                "video_feature": video_feat,
                "label": label,
                "split": split
            }
            
            video_records.append({
                "content_id": content_id,
                "source_path": src_path,
                "media_type": "video" if ("gif" in media_type or total_f > 1) else "image",
                "sampled_frames_count": len(raw_frames),
                "total_frames_count": total_f,
                "label": label,
                "label_name": row['label_name'],
                "split": split,
                "actor_id": actor_id,
                "feature_dimension": 512,
                "video_feature_norm": float(torch.norm(video_feat).item()),
                "governance_type": "DERIVED_VIDEO_FEATURE"
            })
            print(f"  Extracted {len(raw_frames)} frames | Video Embedding L2 Norm: {torch.norm(video_feat):.4f}")
            
    # Save feature tables
    df_vid_out = pd.DataFrame(video_records)
    df_frm_out = pd.DataFrame(frame_records)
    
    vid_parquet = os.path.join(out_dir, "dfd_video_features.parquet")
    frm_parquet = os.path.join(out_dir, "dfd_frame_features.parquet")
    tensors_pt = os.path.join(out_dir, "video_tensors.pt")
    
    df_vid_out.to_parquet(vid_parquet, index=False)
    df_frm_out.to_parquet(frm_parquet, index=False)
    torch.save(video_tensors, tensors_pt)
    
    print("\n============================================================")
    print("VIDEO PREPROCESSING COMPLETE")
    print("============================================================")
    print(f"Video Features Parquet: {vid_parquet} ({len(df_vid_out)} records)")
    print(f"Frame Features Parquet: {frm_parquet} ({len(df_frm_out)} records)")
    print(f"Serialized Tensors:     {tensors_pt}")
    print("Status: PASS")
    print("============================================================")

if __name__ == "__main__":
    main()
