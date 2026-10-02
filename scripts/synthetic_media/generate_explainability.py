#!/usr/bin/env python3
"""
CrisisGuard — Phase 6 Feature & Explainability Analysis (Grad-CAM)
Author: B.SIVASAI (2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Generates Gradient-weighted Class Activation Mapping (Grad-CAM) heatmaps
for representative predictions across image and video forensics models,
visualizing salient spatial regions that drive synthetic media classification.
"""

import os
import sys
import json
import torch
import torch.nn.functional as F
import numpy as np
try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False
from PIL import Image
import pandas as pd
import torchvision.models as models
import torchvision.transforms as transforms

class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks — use register_full_backward_hook (register_backward_hook deprecated since PyTorch 1.8)
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)
        
    def save_activation(self, module, input, output):
        self.activations = output.detach()
        
    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()
        
    def generate_heatmap(self, input_tensor):
        self.model.zero_grad()
        logits = self.model(input_tensor)
        # Target synthetic score
        score = logits.squeeze()
        score.backward()
        
        # Pooled gradients across channels
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        activations = self.activations[0]
        
        for i in range(len(pooled_gradients)):
            activations[i, :, :] *= pooled_gradients[i]
            
        heatmap = torch.mean(activations, dim=0).cpu().numpy()
        heatmap = np.maximum(heatmap, 0)
        max_v = np.max(heatmap)
        if max_v > 0:
            heatmap /= max_v
        return heatmap

def overlay_heatmap(image_path, heatmap, out_path, target_size=(256, 256)):
    if not _CV2_AVAILABLE:
        raise RuntimeError("cv2 (opencv-python) is required for heatmap overlay. Install with: pip install opencv-python-headless")
    raw_img = cv2.imread(image_path)
    raw_img = cv2.resize(raw_img, target_size)
    heatmap_resized = cv2.resize(heatmap, target_size)
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    superimposed = np.uint8(0.6 * raw_img + 0.4 * heatmap_colored)
    cv2.imwrite(out_path, superimposed)

def main():
    print("============================================================")
    print("CRISISGUARD — GRAD-CAM EXPLAINABILITY ANALYSIS")
    print("Author: B.SIVASAI (2023BCS0228) | Roll: 2023BCS0228")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("============================================================")
    
    out_dir = "outputs/synthetic_media/explainability"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Load Image Model
    from train_image_model import ResNet18BinaryClassifier
    img_model = ResNet18BinaryClassifier()
    ckpt_path = "models/synthetic_media/image_model_best.pt"
    assert os.path.exists(ckpt_path), f"Checkpoint missing: {ckpt_path}"
    img_model.load_state_dict(torch.load(ckpt_path, map_location="cpu", weights_only=False))
    img_model.eval()
    
    target_layer = img_model.model.layer4[1].conv2
    grad_cam = GradCAM(img_model, target_layer)
    
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Read test predictions
    df_pred = pd.read_parquet("data/features/synthetic_media/image_predictions.parquet")
    df_part = pd.read_parquet("data/features/synthetic_media/cifake_partitions.parquet")
    test_df = df_part[df_part['split'] == 'test'].reset_index(drop=True)
    merged = pd.merge(test_df, df_pred, on='content_id')
    merged['pred_label'] = (merged['synthetic_probability'] >= 0.5).astype(int)
    
    # Select representatives:
    tp = merged[(merged['label'] == 1) & (merged['pred_label'] == 1)].sort_values('synthetic_probability', ascending=False).iloc[0]
    tn = merged[(merged['label'] == 0) & (merged['pred_label'] == 0)].sort_values('synthetic_probability', ascending=True).iloc[0]
    fp = merged[(merged['label'] == 0) & (merged['pred_label'] == 1)].iloc[0]
    fn = merged[(merged['label'] == 1) & (merged['pred_label'] == 0)].iloc[0]
    
    cases = [
        ("true_positive_synthetic", tp),
        ("true_negative_real", tn),
        ("false_positive", fp),
        ("false_negative", fn)
    ]
    
    results = {}
    print("\n--- Generating Image Forensics Grad-CAM Heatmaps ---")
    for name, row in cases:
        img_p = row['source_path']
        with Image.open(img_p) as pil_img:
            t = transform(pil_img.convert('RGB')).unsqueeze(0)
            
        t.requires_grad = True
        heatmap = grad_cam.generate_heatmap(t)
        
        save_p = os.path.join(out_dir, f"gradcam_{name}.png")
        overlay_heatmap(img_p, heatmap, save_p)
        print(f"Case: {name:<25} | ID: {row['content_id']:<20} | Prob: {row['synthetic_probability']:.4f} | Saved: {save_p}")
        
        results[name] = {
            "content_id": row["content_id"],
            "source_path": row["source_path"],
            "ground_truth": int(row["label"]),
            "predicted_probability": float(row["synthetic_probability"]),
            "heatmap_path": save_p
        }
        
    # 2. DFD Video Frame Representative Explainability
    print("\n--- Generating Video Keyframe Explainability Visualization ---")
    dfd_frame_p = "data/processed/deepfake_dfd/frames/dfd_video_sample_01_frame_020.png"
    if os.path.exists(dfd_frame_p):
        with Image.open(dfd_frame_p) as pil_img:
            t_vid = transform(pil_img.convert('RGB')).unsqueeze(0)
        t_vid.requires_grad = True
        heatmap_vid = grad_cam.generate_heatmap(t_vid)
        vid_save_p = os.path.join(out_dir, "gradcam_dfd_video_frame.png")
        overlay_heatmap(dfd_frame_p, heatmap_vid, vid_save_p)
        print(f"Video Keyframe Grad-CAM saved to: {vid_save_p}")
        results["dfd_video_sample_01_frame_020"] = {
            "content_id": "dfd_dfd_video_sample_01_f020",
            "source_path": dfd_frame_p,
            "heatmap_path": vid_save_p
        }
        
    summary_path = os.path.join(out_dir, "explainability_summary.json")
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\nExplainability summary saved to: {summary_path}")
    print("Grad-CAM Explainability Analysis: PASS")

if __name__ == "__main__":
    main()
