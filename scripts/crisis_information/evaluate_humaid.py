#!/usr/bin/env python3
"""
CrisisGuard — Phase 7: HumAID Evaluation Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Evaluates HumAID models, generates full confusion matrix reports,
class-wise breakdown, and per-category error diagnostics.
"""

import sys
import json
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

def evaluate_humaid():
    print("=" * 65)
    print("CRISISGUARD PHASE 7: HUMAID COMPREHENSIVE EVALUATION")
    print("=" * 65)
    
    root = Path(__file__).resolve().parent.parent.parent
    data_path = root / "data" / "processed" / "humaid" / "humaid_records.parquet"
    model_path = root / "models" / "crisis_information" / "humaid" / "humaid_baseline_model.joblib"
    out_dir = root / "models" / "crisis_information" / "humaid"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}. Run train_humaid.py first.")
        
    clf = joblib.load(model_path)
    df = pd.read_parquet(data_path)
    test_df = df[df["split"] == "test"].copy()
    
    categories = sorted(df["category"].unique())
    y_test = test_df["category"].values
    X_test_dummy = np.zeros((len(y_test), 1))
    
    y_pred = clf.predict(X_test_dummy)
    
    acc = accuracy_score(y_test, y_pred)
    macro_prec = precision_score(y_test, y_pred, labels=categories, average="macro", zero_division=0)
    macro_rec = recall_score(y_test, y_pred, labels=categories, average="macro", zero_division=0)
    macro_f1 = f1_score(y_test, y_pred, labels=categories, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_test, y_pred, labels=categories, average="weighted", zero_division=0)
    report_dict = classification_report(y_test, y_pred, labels=categories, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=categories)
    
    print(f"\nHumAID Test Performance:")
    print(f"  Accuracy:         {acc:.4f}")
    print(f"  Macro Precision:  {macro_prec:.4f}")
    print(f"  Macro Recall:     {macro_rec:.4f}")
    print(f"  Macro F1:         {macro_f1:.4f}")
    print(f"  Weighted F1:      {weighted_f1:.4f}")
    
    print("\nPer-Category Performance Breakdown:")
    for cat in categories:
        metrics = report_dict[cat]
        print(f"  - {cat:42s}: P={metrics['precision']:.3f}, R={metrics['recall']:.3f}, F1={metrics['f1-score']:.3f}, Support={metrics['support']}")
        
    eval_summary = {
        "dataset": "HumAID",
        "split": "test",
        "total_test_records": len(y_test),
        "accuracy": float(acc),
        "macro_precision": float(macro_prec),
        "macro_recall": float(macro_rec),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "confusion_matrix": cm.tolist(),
        "categories": categories,
        "per_category_report": report_dict
    }
    
    eval_json = out_dir / "humaid_eval_report.json"
    with open(eval_json, "w", encoding="utf-8") as f:
        json.dump(eval_summary, f, indent=2)
    print(f"\nSaved evaluation report to {eval_json}")
    return True

if __name__ == "__main__":
    success = evaluate_humaid()
    sys.exit(0 if success else 1)
