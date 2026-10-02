#!/usr/bin/env python3
"""
CrisisGuard — Phase 6 Image Forensics Model Training & Evaluation
Author: B.SIVASAI (2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Trains a ResNet-18 image classifier on CIFAKE benchmark partitions:
- Monitors training and validation loss with early stopping.
- Evaluates holdout test partition on Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, Confusion Matrix.
- Evaluates probability calibration (Brier score, ECE).
- Saves model checkpoint, training history, and prediction records.
"""

import os
import sys
import json
import yaml
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, brier_score_loss
)
import torchvision.models as models

def load_config():
    with open("config/synthetic_media.yaml", "r") as f:
        return yaml.safe_load(f)

def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_ece(probs, labels, n_bins=5):
    """Computes Expected Calibration Error."""
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (probs > bin_lower) & (probs <= bin_upper) if i > 0 else (probs >= bin_lower) & (probs <= bin_upper)
        prop_in_bin = np.mean(in_bin)
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(labels[in_bin] == (probs[in_bin] >= 0.5))
            avg_confidence_in_bin = np.mean(probs[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
    return float(ece)

class ResNet18BinaryClassifier(nn.Module):
    def __init__(self, dropout_rate=0.3):
        super().__init__()
        weights = models.ResNet18_Weights.DEFAULT
        backbone = models.resnet18(weights=weights)
        # Freeze stage 1 and stage 2 for sample regularization
        for name, param in backbone.named_parameters():
            if "layer3" not in name and "layer4" not in name and "fc" not in name:
                param.requires_grad = False
                
        num_ftrs = backbone.fc.in_features
        backbone.fc = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(num_ftrs, 1)
        )
        self.model = backbone
        
    def forward(self, x):
        return self.model(x).squeeze(1)

def main():
    print("============================================================")
    print("CRISISGUARD — IMAGE FORENSICS MODEL TRAINING")
    print("Author: B.SIVASAI (2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("============================================================")
    
    cfg = load_config()
    seed = cfg['reproducibility']['global_seed']
    set_seed(seed)
    
    ckpt_dir = cfg['paths']['checkpoint_dir']
    out_dir = cfg['paths']['features_output_dir']
    os.makedirs(ckpt_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    
    tensors_pt = os.path.join(out_dir, "cifake_tensors.pt")
    partitions_parquet = os.path.join(out_dir, "cifake_partitions.parquet")
    
    data = torch.load(tensors_pt, weights_only=False)
    df_part = pd.read_parquet(partitions_parquet)
    
    tensors = data['tensors']
    labels = data['labels']
    splits = data['splits']
    content_ids = data['content_ids']
    
    train_mask = [s == 'train' for s in splits]
    val_mask = [s == 'val' for s in splits]
    test_mask = [s == 'test' for s in splits]
    
    train_loader = DataLoader(
        TensorDataset(tensors[train_mask], labels[train_mask].float()),
        batch_size=cfg['image_branch']['batch_size'],
        shuffle=True
    )
    val_loader = DataLoader(
        TensorDataset(tensors[val_mask], labels[val_mask].float()),
        batch_size=cfg['image_branch']['batch_size'],
        shuffle=False
    )
    test_loader = DataLoader(
        TensorDataset(tensors[test_mask], labels[test_mask].float()),
        batch_size=cfg['image_branch']['batch_size'],
        shuffle=False
    )
    
    print(f"Data Partitions: Train={len(train_loader.dataset)}, Val={len(val_loader.dataset)}, Test={len(test_loader.dataset)}")
    
    # Model instantiation
    model = ResNet18BinaryClassifier(dropout_rate=cfg['image_branch']['dropout_rate'])
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=cfg['image_branch']['learning_rate'],
        weight_decay=cfg['image_branch']['weight_decay']
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg['image_branch']['epochs'])
    
    epochs = cfg['image_branch']['epochs']
    patience = cfg['image_branch']['early_stopping_patience']
    
    best_val_loss = float('inf')
    best_epoch = 0
    patience_counter = 0
    best_weights_path = os.path.join(ckpt_dir, "image_model_best.pt")
    
    history = {"train_loss": [], "val_loss": [], "val_acc": [], "val_f1": []}
    
    print("\n--- Beginning Model Training Loop ---")
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        for x_b, y_b in train_loader:
            optimizer.zero_grad()
            logits = model(x_b)
            loss = criterion(logits, y_b)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * len(y_b)
            
        train_loss = running_loss / len(train_loader.dataset)
        scheduler.step()
        
        # Validation pass
        model.eval()
        v_loss = 0.0
        v_preds, v_targets = [], []
        with torch.no_grad():
            for x_b, y_b in val_loader:
                logits = model(x_b)
                loss = criterion(logits, y_b)
                v_loss += loss.item() * len(y_b)
                probs = torch.sigmoid(logits).cpu().numpy()
                v_preds.extend(probs)
                v_targets.extend(y_b.cpu().numpy())
                
        val_loss = v_loss / len(val_loader.dataset)
        v_preds = np.array(v_preds)
        v_targets = np.array(v_targets)
        val_acc = accuracy_score(v_targets, (v_preds >= 0.5).astype(int))
        val_f1 = f1_score(v_targets, (v_preds >= 0.5).astype(int), zero_division=0)
        
        history["train_loss"].append(float(train_loss))
        history["val_loss"].append(float(val_loss))
        history["val_acc"].append(float(val_acc))
        history["val_f1"].append(float(val_f1))
        
        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f} | Val F1: {val_f1:.4f}")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch
            patience_counter = 0
            torch.save(model.state_dict(), best_weights_path)
            print(f"  --> Checkpoint saved (val_loss improved to {best_val_loss:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered at epoch {epoch} (patience={patience})")
                break
                
    print(f"\nTraining Complete. Best Validation Loss: {best_val_loss:.4f} at Epoch {best_epoch}")
    
    # Load best checkpoint for holdout testing
    model.load_state_dict(torch.load(best_weights_path, weights_only=False))
    model.eval()
    
    # 4. Independent Holdout Test Evaluation
    print("\n--- Evaluating Independent Holdout Test Partition (N=75) ---")
    test_probs = []
    test_targets = []
    test_logits = []
    
    with torch.no_grad():
        for x_b, y_b in test_loader:
            logits = model(x_b)
            probs = torch.sigmoid(logits)
            test_probs.extend(probs.cpu().numpy())
            test_targets.extend(y_b.cpu().numpy())
            test_logits.extend(logits.cpu().numpy())
            
    test_probs = np.array(test_probs)
    test_targets = np.array(test_targets).astype(int)
    test_preds = (test_probs >= 0.5).astype(int)
    
    acc = float(accuracy_score(test_targets, test_preds))
    prec = float(precision_score(test_targets, test_preds, zero_division=0))
    rec = float(recall_score(test_targets, test_preds, zero_division=0))
    f1 = float(f1_score(test_targets, test_preds, zero_division=0))
    roc_auc = float(roc_auc_score(test_targets, test_probs))
    pr_auc = float(average_precision_score(test_targets, test_probs))
    cm = confusion_matrix(test_targets, test_preds)
    tn, fp, fn, tp = [int(v) for v in cm.ravel()]
    brier = float(brier_score_loss(test_targets, test_probs))
    ece = compute_ece(test_probs, test_targets)
    
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"PR-AUC:    {pr_auc:.4f}")
    print(f"Brier Score Loss: {brier:.4f}")
    print(f"Expected Calibration Error (ECE): {ece:.4f}")
    print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    
    # 5. Output Prediction Records (Common Schema)
    test_df_subset = df_part[df_part['split'] == 'test'].copy().reset_index(drop=True)
    prediction_records = []
    now_iso = datetime.now(timezone.utc).isoformat()
    
    for idx, row in test_df_subset.iterrows():
        p_val = float(test_probs[idx])
        # Direct probability mapping without arbitrary weighting
        risk_val = p_val
        rec_data = {
            "content_id": row["content_id"],
            "media_type": "image",
            "synthetic_probability": round(p_val, 6),
            "synthetic_risk": round(risk_val, 6),
            "model_version": "resnet18_cifake_v1.0",
            "model_branch": "image_forensics",
            "prediction_timestamp": now_iso,
            "source_dataset": "CIFAKE",
            "quality_status": "VALID",
            "provenance": f"CrisisGuard_Phase6_B.SIVASAI_2023BCS0228_GroundTruth_{int(row['label'])}"
        }
        prediction_records.append(rec_data)
        
    df_pred_out = pd.DataFrame(prediction_records)
    pred_parquet = os.path.join(out_dir, "image_predictions.parquet")
    df_pred_out.to_parquet(pred_parquet, index=False)
    print(f"\nSerialized {len(df_pred_out)} image test predictions to: {pred_parquet}")
    
    # Save training metrics summary
    metrics_summary = {
        "model_name": cfg['image_branch']['model_name'],
        "backbone": cfg['image_branch']['backbone'],
        "best_epoch": best_epoch,
        "best_val_loss": float(best_val_loss),
        "test_metrics": {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "roc_auc": roc_auc,
            "pr_auc": pr_auc,
            "brier_score": brier,
            "ece": ece,
            "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp}
        },
        "training_history": history,
        "author": "B.SIVASAI",
        "roll_number": "2023BCS0228",
        "timestamp": now_iso
    }
    history_json = os.path.join(ckpt_dir, "image_training_history.json")
    with open(history_json, "w") as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"Metrics & History saved to: {history_json}")
    
    print("\n============================================================")
    print("IMAGE MODEL TRAINING & EVALUATION: PASS")
    print("============================================================")

if __name__ == "__main__":
    main()
