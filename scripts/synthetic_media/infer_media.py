#!/usr/bin/env python3
"""
CrisisGuard — Phase 6 Unified Media Inference Engine
Author: B.SIVASAI (2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Ingests arbitrary media assets (image or video), automatically inspects
modality, routes to the corresponding forensics model branch (Branch A: Video,
Branch B: Image), and emits a standardized record matching schemas/media_risk_schema.json.
"""

import os
import sys
import json
import yaml
import mimetypes
from datetime import datetime, timezone
import torch
import numpy as np
import pandas as pd
from PIL import Image
import torchvision.transforms as transforms
import jsonschema

# Import branch models
sys.path.append("scripts/synthetic_media")
from train_image_model import ResNet18BinaryClassifier
from train_video_model import VideoTemporalClassifier
import torchvision.models as models

class UnifiedMediaInferenceEngine:
    def __init__(self, config_path="config/synthetic_media.yaml"):
        with open(config_path, "r") as f:
            self.cfg = yaml.safe_load(f)
            
        with open(self.cfg['paths']['schema_path'], "r") as f:
            self.schema = json.load(f)
            
        self.device = torch.device("cpu")
        
        # Load Image Model
        img_ckpt = os.path.join(self.cfg['paths']['checkpoint_dir'], "image_model_best.pt")
        assert os.path.exists(img_ckpt), f"Image model checkpoint missing: {img_ckpt}"
        self.image_model = ResNet18BinaryClassifier()
        self.image_model.load_state_dict(torch.load(img_ckpt, map_location=self.device, weights_only=False))
        self.image_model.eval()
        
        # Load Video Temporal Model
        vid_ckpt = os.path.join(self.cfg['paths']['checkpoint_dir'], "video_model_best.pt")
        assert os.path.exists(vid_ckpt), f"Video model checkpoint missing: {vid_ckpt}"
        self.video_temporal_model = VideoTemporalClassifier(in_features=512)
        self.video_temporal_model.load_state_dict(torch.load(vid_ckpt, map_location=self.device, weights_only=False))
        self.video_temporal_model.eval()

        # Load Platt Calibrator for Image Forensics if available
        platt_ckpt = os.path.join(self.cfg['paths']['checkpoint_dir'], "calibration", "platt_calibrator_resnet18.joblib")
        if os.path.exists(platt_ckpt):
            import joblib
            self.platt_calibrator = joblib.load(platt_ckpt)
        else:
            self.platt_calibrator = None
        
        # Video frame feature extractor backbone
        weights = models.ResNet18_Weights.DEFAULT
        self.video_feature_extractor = models.resnet18(weights=weights)
        self.video_feature_extractor.fc = torch.nn.Identity()
        self.video_feature_extractor.eval()
        
        # Standard transformations
        self.image_transform = transforms.Compose([
            transforms.Resize((self.cfg['image_branch']['image_size'], self.cfg['image_branch']['image_size'])),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        self.video_frame_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
    def detect_modality(self, media_path):
        mime, _ = mimetypes.guess_type(media_path)
        ext = os.path.splitext(media_path)[1].lower()
        if mime:
            if "video" in mime or ext in ['.mp4', '.avi', '.mov', '.mkv', '.gif']:
                return "video"
            if "image" in mime or ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                return "image"
        # Fallback inspection via PIL
        try:
            with Image.open(media_path) as img:
                if getattr(img, 'n_frames', 1) > 1:
                    return "video"
                return "image"
        except Exception:
            return "unknown"
            
    def infer_image(self, image_path, content_id, source_dataset="Unknown"):
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')
            tensor = self.image_transform(rgb_img).unsqueeze(0).to(self.device)
            
        with torch.no_grad():
            logits = self.image_model(tensor)
            raw_score = float(logits.item())
            uncal_prob = float(torch.sigmoid(logits).item())
            
        if self.platt_calibrator is not None:
            cal_prob = float(self.platt_calibrator.predict_proba(np.array([[raw_score]]))[:, 1][0])
            cal_status = "CALIBRATED_PLATT"
            final_prob = cal_prob
        else:
            cal_status = "UNCALIBRATED"
            final_prob = uncal_prob

        record = {
            "content_id": content_id,
            "media_type": "image",
            "model_branch": "image_forensics",
            "model_version": "resnet18_cifake_v1.0",
            "model_score": round(raw_score, 6),
            "synthetic_probability": round(final_prob, 6),
            "synthetic_risk": round(final_prob, 6),
            "calibration_status": cal_status,
            "prediction_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_dataset": source_dataset,
            "quality_status": "VALID",
            "provenance": "CrisisGuard_Phase6_B.SIVASAI_2023BCS0228"
        }
        jsonschema.validate(instance=record, schema=self.schema)
        return record
        
    def infer_video(self, video_path, content_id, source_dataset="Unknown", num_frames=5):
        # Extract uniform frames
        frames = []
        with Image.open(video_path) as img:
            total_frames = getattr(img, 'n_frames', 1)
            step = max(1, total_frames / num_frames)
            indices = [int(i * step) for i in range(num_frames)] if total_frames > num_frames else list(range(total_frames))
            for idx in indices:
                img.seek(idx)
                frames.append(img.convert('RGB'))
                
        frame_tensors = [self.video_frame_transform(f) for f in frames]
        stacked = torch.stack(frame_tensors).to(self.device)  # (T, 3, 224, 224)
        
        with torch.no_grad():
            feats = self.video_feature_extractor(stacked)  # (T, 512)
            logits = self.video_temporal_model(feats)
            prob = float(torch.sigmoid(logits).item())
            raw_score = float(logits.item())
            
        record = {
            "content_id": content_id,
            "media_type": "video",
            "model_branch": "video_forensics",
            "model_version": "temporal_dfd_resnet18_v1.0",
            "model_score": round(raw_score, 6),
            "synthetic_probability": round(prob, 6),
            "synthetic_risk": round(prob, 6),
            "calibration_status": "UNCALIBRATED",
            "prediction_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_dataset": source_dataset,
            "quality_status": "VALID",
            "provenance": "CrisisGuard_Phase6_B.SIVASAI_2023BCS0228"
        }
        jsonschema.validate(instance=record, schema=self.schema)
        return record
        
    def predict(self, media_path, content_id=None, source_dataset="InferenceStream"):
        assert os.path.exists(media_path), f"File not found: {media_path}"
        if not content_id:
            content_id = os.path.splitext(os.path.basename(media_path))[0]
            
        modality = self.detect_modality(media_path)
        if modality == "image":
            return self.infer_image(media_path, content_id, source_dataset)
        elif modality == "video":
            return self.infer_video(media_path, content_id, source_dataset)
        else:
            raise ValueError(f"Unsupported media modality for: {media_path}")

def build_unified_dataset():
    """Merges verified image and video test predictions into unified_media_risk.parquet."""
    print("\n--- Assembling Unified Media Risk Dataset ---")
    img_parquet = "data/features/synthetic_media/image_predictions.parquet"
    vid_parquet = "data/features/synthetic_media/video_predictions.parquet"
    out_parquet = "data/features/synthetic_media/unified_media_risk.parquet"
    
    assert os.path.exists(img_parquet), f"Missing image predictions: {img_parquet}"
    assert os.path.exists(vid_parquet), f"Missing video predictions: {vid_parquet}"
    
    df_img = pd.read_parquet(img_parquet)
    df_vid = pd.read_parquet(vid_parquet)
    
    df_unified = pd.concat([df_img, df_vid], ignore_index=True)
    df_unified.to_parquet(out_parquet, index=False)
    
    print(f"Image Predictions:   {len(df_img)} records")
    print(f"Video Predictions:   {len(df_vid)} records")
    print(f"Unified Media Risk:  {len(df_unified)} records saved to: {out_parquet}")
    return df_unified

def main():
    print("============================================================")
    print("CRISISGUARD — UNIFIED MEDIA INFERENCE ENGINE")
    print("Author: B.SIVASAI (2023BCS0228) | Roll: 2023BCS0228")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("============================================================")
    
    engine = UnifiedMediaInferenceEngine()
    print("Inference Engine initialized and models loaded.")
    
    # Smoke test on a real image
    sample_img = "data/raw/synthetic_media_eval/fake/0 (10).jpg"
    rec_img = engine.predict(sample_img, content_id="infer_test_sample_img", source_dataset="CIFAKE")
    print("\n[Branch B - Image Inference Smoke Test]:")
    print(json.dumps(rec_img, indent=2))
    assert rec_img["media_type"] == "image"
    assert rec_img["model_branch"] == "image_forensics"
    assert 0.0 <= rec_img["synthetic_probability"] <= 1.0
    
    # Smoke test on a video
    sample_vid = "data/raw/deepfake_dfd/videos/deepfakedetection.gif"
    rec_vid = engine.predict(sample_vid, content_id="infer_test_sample_vid", source_dataset="Google_DFD")
    print("\n[Branch A - Video Inference Smoke Test]:")
    print(json.dumps(rec_vid, indent=2))
    assert rec_vid["media_type"] == "video"
    assert rec_vid["model_branch"] == "video_forensics"
    assert 0.0 <= rec_vid["synthetic_probability"] <= 1.0
    
    # Build and validate unified output dataset
    df_unified = build_unified_dataset()
    print("\nUnified Inference Engine Verification: ALL PASS")

if __name__ == "__main__":
    main()
