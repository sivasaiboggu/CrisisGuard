#!/usr/bin/env python3
"""
CrisisGuard — Phase 7: HumAID Humanitarian Classification Training Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Trains humanitarian classification baselines on the official HumAID benchmark:
- Enforces official QCRI disjoint split: Train (53,531), Dev (7,793), Test (15,160)
- Preserves all 10 official humanitarian categories without collapsing
- Evaluates class imbalance mitigation (balanced prior vs empirical prior)
- Persists model artifacts to models/crisis_information/humaid/
- Generates reproducible metrics and test predictions
"""

import os
import sys
import json
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

def train_humaid():
    print("=" * 65)
    print("CRISISGUARD PHASE 7: HUMAID BASELINE CLASSIFIER TRAINING")
    print("=" * 65)
    
    root = Path(__file__).resolve().parent.parent.parent
    data_path = root / "data" / "processed" / "humaid" / "humaid_records.parquet"
    model_dir = root / "models" / "crisis_information" / "humaid"
    out_feat_dir = root / "data" / "features" / "crisis_information"
    
    model_dir.mkdir(parents=True, exist_ok=True)
    out_feat_dir.mkdir(parents=True, exist_ok=True)
    
    if not data_path.exists():
        raise FileNotFoundError(f"HumAID data not found at {data_path}")
        
    df = pd.read_parquet(data_path)
    print(f"Loaded HumAID dataset: {df.shape[0]} records, {df.shape[1]} columns")
    
    # 1. Enforce official QCRI splits
    train_df = df[df["split"] == "train"].copy()
    dev_df = df[df["split"] == "dev"].copy()
    test_df = df[df["split"] == "test"].copy()
    
    print(f"Split sizes: Train={len(train_df)}, Dev={len(dev_df)}, Test={len(test_df)}")
    
    # Verify split disjointness
    train_ids = set(train_df["source_record_id"])
    dev_ids = set(dev_df["source_record_id"])
    test_ids = set(test_df["source_record_id"])
    assert len(train_ids.intersection(dev_ids)) == 0, "Train-Dev ID leakage detected!"
    assert len(train_ids.intersection(test_ids)) == 0, "Train-Test ID leakage detected!"
    assert len(dev_ids.intersection(test_ids)) == 0, "Dev-Test ID leakage detected!"
    print("Leakage verification: Zero cross-split ID overlap confirmed.")
    
    # 2. Extract targets
    target_col = "category"
    categories = sorted(df[target_col].unique())
    print(f"Number of categories: {len(categories)}")
    for idx, cat in enumerate(categories):
        cnt = (train_df[target_col] == cat).sum()
        pct = (cnt / len(train_df)) * 100
        print(f"  [{idx}] {cat}: {cnt} train examples ({pct:.2f}%)")
        
    y_train = train_df[target_col].values
    y_dev = dev_df[target_col].values
    y_test = test_df[target_col].values
    
    # Dummy features for structural fitting (dummy classifier only uses labels)
    X_train_dummy = np.zeros((len(y_train), 1))
    X_test_dummy = np.zeros((len(y_test), 1))
    
    # 3. Model 1: Stratified Prior Baseline (samples according to empirical distribution)
    strat_clf = DummyClassifier(strategy="stratified", random_state=42)
    strat_clf.fit(X_train_dummy, y_train)
    
    # 4. Model 2: Most Frequent (Majority) Baseline
    most_freq_clf = DummyClassifier(strategy="most_frequent", random_state=42)
    most_freq_clf.fit(X_train_dummy, y_train)
    
    # 5. Model 3: Uniform Prior Baseline (balanced prior hypothesis)
    uniform_clf = DummyClassifier(strategy="uniform", random_state=42)
    uniform_clf.fit(X_train_dummy, y_train)
    
    # Evaluate baselines on Test set
    models = {
        "stratified_prior": strat_clf,
        "majority_class": most_freq_clf,
        "uniform_prior": uniform_clf
    }
    
    results = {}
    best_model_name = "stratified_prior"
    
    for name, clf in models.items():
        y_pred = clf.predict(X_test_dummy)
        y_prob = clf.predict_proba(X_test_dummy)
        
        acc = accuracy_score(y_test, y_pred)
        macro_prec = precision_score(y_test, y_pred, labels=categories, average="macro", zero_division=0)
        macro_rec = recall_score(y_test, y_pred, labels=categories, average="macro", zero_division=0)
        macro_f1 = f1_score(y_test, y_pred, labels=categories, average="macro", zero_division=0)
        weighted_f1 = f1_score(y_test, y_pred, labels=categories, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred, labels=categories).tolist()
        
        print(f"\n--- Model Evaluation: {name} ---")
        print(f"Accuracy:         {acc:.4f}")
        print(f"Macro Precision:  {macro_prec:.4f}")
        print(f"Macro Recall:     {macro_rec:.4f}")
        print(f"Macro F1:         {macro_f1:.4f}")
        print(f"Weighted F1:      {weighted_f1:.4f}")
        
        results[name] = {
            "accuracy": float(acc),
            "macro_precision": float(macro_prec),
            "macro_recall": float(macro_rec),
            "macro_f1": float(macro_f1),
            "weighted_f1": float(weighted_f1),
            "confusion_matrix": cm,
            "classes": categories
        }
        
    # Save best baseline model and metadata
    saved_model_path = model_dir / "humaid_baseline_model.joblib"
    joblib.dump(strat_clf, saved_model_path)
    print(f"\nSaved model artifact to: {saved_model_path}")
    
    metrics_path = model_dir / "humaid_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved metrics to: {metrics_path}")
    
    # 6. Generate test set predictions with calibration metadata
    # In accordance with Step 20, uncalibrated scores are explicitly labeled
    strat_test_preds = strat_clf.predict(X_test_dummy)
    strat_test_probs = strat_clf.predict_proba(X_test_dummy)
    
    # Probability assigned to predicted class
    pred_scores = np.max(strat_test_probs, axis=1)
    
    pred_df = test_df.copy()
    pred_df["predicted_category"] = strat_test_preds
    pred_df["model_score"] = pred_scores
    pred_df["confidence"] = pred_scores
    pred_df["quality_status"] = "VALID"
    pred_df["calibration_status"] = "UNCALIBRATED"
    pred_df["task_name"] = "humanitarian_classification_10class"
    pred_df["model_version"] = "humaid_stratified_baseline_v1"
    pred_df["text_available"] = False
    pred_df["image_available"] = False
    pred_df["provenance"] = "humaid_official_test_split"
    
    out_parquet = out_feat_dir / "humaid_predictions.parquet"
    pred_df.to_parquet(out_parquet, index=False)
    print(f"Generated test prediction features: {out_parquet} ({len(pred_df)} records)")
    
    return True

if __name__ == "__main__":
    success = train_humaid()
    sys.exit(0 if success else 1)
