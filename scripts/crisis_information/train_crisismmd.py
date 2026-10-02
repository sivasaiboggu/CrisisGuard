#!/usr/bin/env python3
"""
CrisisGuard — Phase 7: CrisisMMD Modeling Engine (Baseline & Transformer)
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Trains and evaluates:
1. Classical TF-IDF + Logistic Regression / SVM Baseline for Humanitarian & Informative tasks.
2. Fine-tuned DistilBERT Sequence Classifier on CrisisMMD text.
3. Generates comprehensive test metrics and feature outputs.
4. Strictly marks modality: image_available_locally = False.
"""

import os
import sys
import json
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

class TextDataset(Dataset):
    def __init__(self, encodings, labels=None):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.encodings["input_ids"])

def train_crisismmd():
    print("=" * 65)
    print("CRISISGUARD PHASE 7: CRISISMMD MODELING ENGINE")
    print("=" * 65)
    
    root = Path(__file__).resolve().parent.parent.parent
    data_path = root / "data" / "processed" / "crisismmd" / "crisismmd_records.parquet"
    model_dir = root / "models" / "crisis_information" / "crisismmd"
    out_feat_dir = root / "data" / "features" / "crisis_information"
    
    model_dir.mkdir(parents=True, exist_ok=True)
    out_feat_dir.mkdir(parents=True, exist_ok=True)
    
    if not data_path.exists():
        raise FileNotFoundError(f"CrisisMMD data not found at {data_path}")
        
    df = pd.read_parquet(data_path)
    print(f"Loaded CrisisMMD: {df.shape[0]} records, {df.shape[1]} columns")
    
    # Check official splits
    train_df = df[df["split"] == "train"].copy()
    dev_df = df[df["split"] == "dev"].copy()
    test_df = df[df["split"] == "test"].copy()
    
    print(f"Official Splits: Train={len(train_df)}, Dev={len(dev_df)}, Test={len(test_df)}")
    
    # -------------------------------------------------------------
    # 1. PRIMARY TASK: Humanitarian Classification (5 classes)
    # -------------------------------------------------------------
    target_col = "humanitarian_label"
    categories = sorted(df[target_col].unique())
    label2id = {label: i for i, label in enumerate(categories)}
    id2label = {i: label for i, label in enumerate(categories)}
    
    print(f"\nTask 1: Humanitarian Classification ({len(categories)} classes)")
    for cat in categories:
        cnt = (train_df[target_col] == cat).sum()
        pct = (cnt / len(train_df)) * 100
        print(f"  - {cat:40s}: {cnt} train ({pct:.2f}%)")
        
    y_train = np.array([label2id[l] for l in train_df[target_col]])
    y_dev = np.array([label2id[l] for l in dev_df[target_col]])
    y_test = np.array([label2id[l] for l in test_df[target_col]])
    
    X_train_text = train_df["clean_text"].tolist()
    X_dev_text = dev_df["clean_text"].tolist()
    X_test_text = test_df["clean_text"].tolist()
    
    # -------------------------------------------------------------
    # 2. CLASSICAL BASELINE: TF-IDF + Logistic Regression
    # -------------------------------------------------------------
    print("\n--- Training TF-IDF + Logistic Regression Baseline ---")
    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    X_tr_tfidf = tfidf.fit_transform(X_train_text)
    X_te_tfidf = tfidf.transform(X_test_text)
    
    lr_clf = LogisticRegression(C=1.0, max_iter=1000, class_weight="balanced", random_state=42)
    lr_clf.fit(X_tr_tfidf, y_train)
    
    y_pred_base = lr_clf.predict(X_te_tfidf)
    y_prob_base = lr_clf.predict_proba(X_te_tfidf)
    
    acc_base = accuracy_score(y_test, y_pred_base)
    macro_p_base = precision_score(y_test, y_pred_base, average="macro", zero_division=0)
    macro_r_base = recall_score(y_test, y_pred_base, average="macro", zero_division=0)
    macro_f1_base = f1_score(y_test, y_pred_base, average="macro", zero_division=0)
    weighted_f1_base = f1_score(y_test, y_pred_base, average="weighted", zero_division=0)
    cm_base = confusion_matrix(y_test, y_pred_base).tolist()
    
    print(f"Baseline Test Performance:")
    print(f"  Accuracy:         {acc_base:.4f}")
    print(f"  Macro Precision:  {macro_p_base:.4f}")
    print(f"  Macro Recall:     {macro_r_base:.4f}")
    print(f"  Macro F1:         {macro_f1_base:.4f}")
    print(f"  Weighted F1:      {weighted_f1_base:.4f}")
    
    # Save baseline artifacts
    joblib.dump(lr_clf, model_dir / "crisismmd_baseline_logistic.joblib")
    joblib.dump(tfidf, model_dir / "crisismmd_tfidf_vectorizer.joblib")
    
    # -------------------------------------------------------------
    # 3. SECONDARY TASK: Binary Informativeness Baseline
    # -------------------------------------------------------------
    print("\n--- Training Secondary Task: Informativeness Baseline ---")
    inf_label2id = {"not_informative": 0, "informative": 1}
    y_train_inf = np.array([inf_label2id.get(l, 0) for l in train_df["informative_label"]])
    y_test_inf = np.array([inf_label2id.get(l, 0) for l in test_df["informative_label"]])
    
    inf_clf = LogisticRegression(C=1.0, max_iter=1000, class_weight="balanced", random_state=42)
    inf_clf.fit(X_tr_tfidf, y_train_inf)
    y_pred_inf = inf_clf.predict(X_te_tfidf)
    acc_inf = accuracy_score(y_test_inf, y_pred_inf)
    f1_inf = f1_score(y_test_inf, y_pred_inf, average="macro", zero_division=0)
    print(f"Informativeness Baseline Accuracy: {acc_inf:.4f}, Macro F1: {f1_inf:.4f}")
    joblib.dump(inf_clf, model_dir / "crisismmd_informative_baseline.joblib")
    
    # -------------------------------------------------------------
    # 4. ADVANCED MODEL: DistilBERT Sequence Classifier
    # -------------------------------------------------------------
    print("\n--- Training DistilBERT Transformer Classifier ---")
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(categories),
        id2label=id2label,
        label2id=label2id
    )
    
    # Tokenize datasets
    max_len = 128
    train_enc = tokenizer(X_train_text, truncation=True, padding="max_length", max_length=max_len)
    dev_enc = tokenizer(X_dev_text, truncation=True, padding="max_length", max_length=max_len)
    test_enc = tokenizer(X_test_text, truncation=True, padding="max_length", max_length=max_len)
    
    train_ds = TextDataset(train_enc, y_train)
    dev_ds = TextDataset(dev_enc, y_dev)
    test_ds = TextDataset(test_enc, y_test)
    
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    dev_loader = DataLoader(dev_ds, batch_size=64, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=64, shuffle=False)
    
    device = torch.device("cpu")
    model.to(device)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=2.0e-5, weight_decay=0.01)
    epochs = 2  # 2 epochs on CPU for convergence and speed
    
    print(f"Beginning fine-tuning ({epochs} epochs, {len(train_loader)} batches/epoch)...")
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for b_idx, batch in enumerate(train_loader):
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
            if (b_idx + 1) % 50 == 0:
                print(f"  Epoch {epoch}/{epochs} | Step {b_idx + 1}/{len(train_loader)} | Batch Loss: {loss.item():.4f}")
                
        avg_loss = total_loss / len(train_loader)
        
        # Dev evaluation
        model.eval()
        dev_preds, dev_targets = [], []
        with torch.no_grad():
            for batch in dev_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
                dev_preds.extend(preds)
                dev_targets.extend(batch["labels"].numpy())
        dev_f1 = f1_score(dev_targets, dev_preds, average="macro", zero_division=0)
        print(f"Epoch {epoch} Complete | Train Loss: {avg_loss:.4f} | Dev Macro F1: {dev_f1:.4f}")
        
    # Evaluate Transformer on Test set
    model.eval()
    test_preds, test_probs = [], []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=1).cpu().numpy()
            preds = np.argmax(probs, axis=1)
            test_preds.extend(preds)
            test_probs.extend(probs)
            
    test_preds = np.array(test_preds)
    test_probs = np.array(test_probs)
    
    acc_tf = accuracy_score(y_test, test_preds)
    macro_p_tf = precision_score(y_test, test_preds, average="macro", zero_division=0)
    macro_r_tf = recall_score(y_test, test_preds, average="macro", zero_division=0)
    macro_f1_tf = f1_score(y_test, test_preds, average="macro", zero_division=0)
    weighted_f1_tf = f1_score(y_test, test_preds, average="weighted", zero_division=0)
    cm_tf = confusion_matrix(y_test, test_preds).tolist()
    
    print("\n--- Transformer Test Performance ---")
    print(f"  Accuracy:         {acc_tf:.4f}")
    print(f"  Macro Precision:  {macro_p_tf:.4f}")
    print(f"  Macro Recall:     {macro_r_tf:.4f}")
    print(f"  Macro F1:         {macro_f1_tf:.4f}")
    print(f"  Weighted F1:      {weighted_f1_tf:.4f}")
    
    # Save transformer model & tokenizer
    tf_save_path = model_dir / "transformer_humanitarian"
    tf_save_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(tf_save_path)
    tokenizer.save_pretrained(tf_save_path)
    print(f"Saved Transformer model to: {tf_save_path}")
    
    # Save comprehensive metrics JSON
    metrics_summary = {
        "dataset": "CrisisMMD",
        "primary_task": "humanitarian_classification",
        "classes": categories,
        "splits": {"train": len(train_df), "dev": len(dev_df), "test": len(test_df)},
        "baseline_tfidf_logistic": {
            "accuracy": float(acc_base),
            "macro_precision": float(macro_p_base),
            "macro_recall": float(macro_r_base),
            "macro_f1": float(macro_f1_base),
            "weighted_f1": float(weighted_f1_base),
            "confusion_matrix": cm_base
        },
        "transformer_distilbert": {
            "model_name": model_name,
            "accuracy": float(acc_tf),
            "macro_precision": float(macro_p_tf),
            "macro_recall": float(macro_r_tf),
            "macro_f1": float(macro_f1_tf),
            "weighted_f1": float(weighted_f1_tf),
            "confusion_matrix": cm_tf
        },
        "informative_baseline": {
            "accuracy": float(acc_inf),
            "macro_f1": float(f1_inf)
        }
    }
    
    metrics_path = model_dir / "crisismmd_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"Saved metrics summary to: {metrics_path}")
    
    # -------------------------------------------------------------
    # 5. GENERATE PREDICTIONS FEATURE PARQUET (Test Set)
    # -------------------------------------------------------------
    pred_scores = np.max(test_probs, axis=1)
    predicted_labels = [id2label[p] for p in test_preds]
    
    pred_df = test_df.copy()
    pred_df["predicted_category"] = predicted_labels
    pred_df["model_score"] = [float(s) for s in pred_scores]
    pred_df["confidence"] = [float(s) for s in pred_scores]
    pred_df["calibration_status"] = "UNCALIBRATED"
    pred_df["task_name"] = "humanitarian_classification_5class"
    pred_df["model_version"] = "crisismmd_distilbert_v1"
    pred_df["text_available"] = True
    pred_df["image_available"] = False  # Strictly honest
    pred_df["provenance"] = "crisismmd_official_test_split"
    pred_df["quality_status"] = "VALID"
    
    out_parquet = out_feat_dir / "crisismmd_predictions.parquet"
    pred_df.to_parquet(out_parquet, index=False)
    print(f"Generated CrisisMMD test features: {out_parquet} ({len(pred_df)} records)")
    
    return True

if __name__ == "__main__":
    success = train_crisismmd()
    sys.exit(0 if success else 1)
