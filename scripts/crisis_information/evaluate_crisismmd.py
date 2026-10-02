#!/usr/bin/env python3
"""
CrisisGuard — Phase 7: CrisisMMD Comprehensive Evaluation Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Evaluates CrisisMMD Baseline and Transformer models, produces detailed
per-class precision/recall/F1 metrics, confusion matrices, and error reports.
"""

import sys
import json
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

def evaluate_crisismmd():
    print("=" * 65)
    print("CRISISGUARD PHASE 7: CRISISMMD DETAILED EVALUATION")
    print("=" * 65)
    
    root = Path(__file__).resolve().parent.parent.parent
    data_path = root / "data" / "processed" / "crisismmd" / "crisismmd_records.parquet"
    pred_path = root / "data" / "features" / "crisis_information" / "crisismmd_predictions.parquet"
    model_dir = root / "models" / "crisis_information" / "crisismmd"
    
    if not pred_path.exists():
        raise FileNotFoundError(f"CrisisMMD predictions not found at {pred_path}. Run train_crisismmd.py first.")
        
    df_preds = pd.read_parquet(pred_path)
    categories = sorted(df_preds["humanitarian_label"].unique())
    
    y_true = df_preds["humanitarian_label"].values
    y_pred = df_preds["predicted_category"].values
    
    report_dict = classification_report(y_true, y_pred, labels=categories, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=categories)
    
    print("\nCrisisMMD Transformer Test Classification Report:")
    for cat in categories:
        m = report_dict[cat]
        print(f"  - {cat:42s}: P={m['precision']:.3f}, R={m['recall']:.3f}, F1={m['f1-score']:.3f}, Support={m['support']}")
        
    print(f"\nOverall Macro F1:    {report_dict['macro avg']['f1-score']:.4f}")
    print(f"Overall Weighted F1: {report_dict['weighted avg']['f1-score']:.4f}")
    print(f"Overall Accuracy:    {report_dict['accuracy']:.4f}")
    
    # Error diagnostics: Confusion patterns
    print("\nConfusion Matrix:")
    print(f"Labels: {categories}")
    print(cm)
    
    eval_report = {
        "dataset": "CrisisMMD",
        "model": "DistilBERT Sequence Classifier",
        "test_records": len(df_preds),
        "accuracy": float(report_dict["accuracy"]),
        "macro_f1": float(report_dict["macro avg"]["f1-score"]),
        "weighted_f1": float(report_dict["weighted avg"]["f1-score"]),
        "per_class": report_dict,
        "confusion_matrix": cm.tolist(),
        "classes": categories
    }
    
    eval_json = model_dir / "crisismmd_eval_report.json"
    with open(eval_json, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=2)
    print(f"\nSaved evaluation report to {eval_json}")
    return True

if __name__ == "__main__":
    success = evaluate_crisismmd()
    sys.exit(0 if success else 1)
