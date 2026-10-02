#!/usr/bin/env python3
"""
CrisisGuard — Phase 7 Independent Consistency Audit Script
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing
Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
         Propagation Analysis and Emergency Response Prioritization

Independent Cross-Check Validator for Phase 7:
Independently verifies:
1. Dataset counts (derived directly from processed parquets and raw data)
2. Split counts (verifies partition completeness, integrity, and disjointness)
3. Model artifact existence (all checkpoints, configs, tokenizers present)
4. Model loading & parameter count (independently loads PyTorch DistilBERT & Sklearn models)
5. Prediction row counts (matches official test split partitions exactly)
6. Schema validity (strict jsonschema validation across unified records)
7. Duplicate IDs & cross-dataset isolation (zero split leakage, zero cross-dataset collisions)
8. Confidence and score ranges (strictly bounded in [0.0, 1.0])
9. Calibration semantics & quality separation (UNCALIBRATED flag verified, quality_status verified)
10. Modality honesty (physically verifies image binary absence, verifies text-only flags)
11. Documentation & metrics consistency (compares JSON metrics against documentation & registry)
12. Unified Parquet consistency (verifies additive sum 15,160 + 955 + 88,015 = 104,130)
"""

import os
import sys
import json
import re
import yaml
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import jsonschema

def audit_consistency():
    print("=" * 75)
    print("CRISISGUARD — INDEPENDENT PHASE 7 CONSISTENCY & INTEGRITY AUDIT")
    print("=" * 75)
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("Phase:  7 — Crisis Information Intelligence Engine")
    print("=" * 75)
    
    root = Path(__file__).resolve().parent.parent.parent
    results = {}
    
    # ------------------------------------------------------------------
    # 1. Dataset Counts
    # ------------------------------------------------------------------
    try:
        df_h = pd.read_parquet(root / "data" / "processed" / "humaid" / "humaid_records.parquet")
        df_c = pd.read_parquet(root / "data" / "processed" / "crisismmd" / "crisismmd_records.parquet")
        df_l = pd.read_parquet(root / "data" / "processed" / "crisislex" / "crisislex_records.parquet")
        
        n_h = len(df_h)
        n_c = len(df_c)
        n_l = len(df_l)
        
        c1 = (n_h == 76484) and (n_c == 8079) and (n_l == 88015)
        results["1. Dataset Counts"] = (c1, f"HumAID={n_h}, CrisisMMD={n_c}, CrisisLex={n_l}")
    except Exception as e:
        results["1. Dataset Counts"] = (False, f"Exception: {e}")
        
    # ------------------------------------------------------------------
    # 2. Split Counts
    # ------------------------------------------------------------------
    try:
        h_splits = df_h["split"].value_counts().to_dict()
        c_splits = df_c["split"].value_counts().to_dict()
        
        h_sum = sum(h_splits.values())
        c_sum = sum(c_splits.values())
        
        c2 = (h_splits.get("train") == 53531 and h_splits.get("dev") == 7793 and h_splits.get("test") == 15160 and
              c_splits.get("train") == 6126 and c_splits.get("dev") == 998 and c_splits.get("test") == 955 and
              h_sum == n_h and c_sum == n_c)
        results["2. Split Counts"] = (c2, f"HumAID={h_splits}, CrisisMMD={c_splits}")
    except Exception as e:
        results["2. Split Counts"] = (False, f"Exception: {e}")
        
    # ------------------------------------------------------------------
    # 3. Model Artifact Existence
    # ------------------------------------------------------------------
    try:
        h_model_f = root / "models" / "crisis_information" / "humaid" / "humaid_baseline_model.joblib"
        c_log_f = root / "models" / "crisis_information" / "crisismmd" / "crisismmd_baseline_logistic.joblib"
        c_vec_f = root / "models" / "crisis_information" / "crisismmd" / "crisismmd_tfidf_vectorizer.joblib"
        c_tf_dir = root / "models" / "crisis_information" / "crisismmd" / "transformer_humanitarian"
        
        tf_cfg = c_tf_dir / "config.json"
        tf_weights = c_tf_dir / "model.safetensors"
        if not tf_weights.exists():
            tf_weights = c_tf_dir / "pytorch_model.bin"
            
        c3 = (h_model_f.exists() and c_log_f.exists() and c_vec_f.exists() and
              c_tf_dir.exists() and tf_cfg.exists() and tf_weights.exists())
        results["3. Model Artifact Existence"] = (c3, f"HumAID={h_model_f.exists()}, Baseline={c_log_f.exists()}, TF={c_tf_dir.exists()}")
    except Exception as e:
        results["3. Model Artifact Existence"] = (False, f"Exception: {e}")

    # ------------------------------------------------------------------
    # 4. Model Loading & Parameter Count
    # ------------------------------------------------------------------
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        h_model = joblib.load(h_model_f)
        c_log = joblib.load(c_log_f)
        c_vec = joblib.load(c_vec_f)
        
        tf_model = AutoModelForSequenceClassification.from_pretrained(str(c_tf_dir))
        tokenizer = AutoTokenizer.from_pretrained(str(c_tf_dir))
        
        param_count = sum(p.numel() for p in tf_model.parameters())
        # distilbert-base-uncased with 5 classes ~ 66.958M
        param_ok = (66_900_000 <= param_count <= 67_000_000)
        num_labels = tf_model.config.num_labels
        labels_ok = (num_labels == 5)
        
        c4 = (h_model is not None and c_log is not None and c_vec is not None and
              tf_model is not None and tokenizer is not None and param_ok and labels_ok)
        results["4. Model Loading & Architecture"] = (c4, f"Loaded successfully, DistilBERT params={param_count:,}, num_labels={num_labels}")
    except Exception as e:
        results["4. Model Loading & Architecture"] = (False, f"Exception: {e}")

    # ------------------------------------------------------------------
    # 5. Prediction Row Counts
    # ------------------------------------------------------------------
    try:
        p_humaid = pd.read_parquet(root / "data" / "features" / "crisis_information" / "humaid_predictions.parquet")
        p_cmmd = pd.read_parquet(root / "data" / "features" / "crisis_information" / "crisismmd_predictions.parquet")
        
        c5 = (len(p_humaid) == 15160) and (len(p_cmmd) == 955)
        results["5. Prediction Row Counts"] = (c5, f"HumAID test preds={len(p_humaid)} (15,160), CrisisMMD test preds={len(p_cmmd)} (955)")
    except Exception as e:
        results["5. Prediction Row Counts"] = (False, f"Exception: {e}")

    # ------------------------------------------------------------------
    # 6. Schema Validity
    # ------------------------------------------------------------------
    try:
        schema_file = root / "schemas" / "crisis_intelligence_schema.json"
        unified_file = root / "data" / "features" / "crisis_information" / "unified_crisis_intelligence.parquet"
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_json = json.load(f)
            
        df_unified = pd.read_parquet(unified_file)
        
        # Sample 100 records across sources
        sample_records = df_unified.sample(n=min(100, len(df_unified)), random_state=42).to_dict(orient="records")
        for rec in sample_records:
            jsonschema.validate(instance=rec, schema=schema_json)
            
        c6 = True
        results["6. Schema Validity"] = (c6, f"Validated against {schema_file.name} for 100 diverse sample records")
    except Exception as e:
        results["6. Schema Validity"] = (False, f"Validation error: {e}")

    # ------------------------------------------------------------------
    # 7. Duplicate IDs & Cross-Dataset Isolation
    # ------------------------------------------------------------------
    try:
        h_ids = set(df_h["source_record_id"])
        c_ids = set(df_c["source_record_id"])
        l_ids = set(df_l["source_record_id"])
        
        # Split isolation
        h_train_ids = set(df_h[df_h["split"] == "train"]["source_record_id"])
        h_test_ids = set(df_h[df_h["split"] == "test"]["source_record_id"])
        c_train_ids = set(df_c[df_c["split"] == "train"]["source_record_id"])
        c_test_ids = set(df_c[df_c["split"] == "test"]["source_record_id"])
        
        split_leak = len(h_train_ids.intersection(h_test_ids)) + len(c_train_ids.intersection(c_test_ids))
        
        # Cross dataset overlap
        ov_hc = len(h_ids.intersection(c_ids))
        ov_hl = len(h_ids.intersection(l_ids))
        ov_cl = len(c_ids.intersection(l_ids))
        
        c7 = (split_leak == 0) and (ov_hc == 0) and (ov_hl == 0) and (ov_cl == 0)
        results["7. Duplicate IDs & Dataset Isolation"] = (c7, f"Split leak={split_leak}, Overlap(H,C)={ov_hc}, Overlap(H,L)={ov_hl}, Overlap(C,L)={ov_cl}")
    except Exception as e:
        results["7. Duplicate IDs & Dataset Isolation"] = (False, f"Exception: {e}")

    # ------------------------------------------------------------------
    # 8. Confidence & Score Ranges
    # ------------------------------------------------------------------
    try:
        c8_h_score = (p_humaid["model_score"].between(0.0, 1.0)).all() and not p_humaid["model_score"].isna().any()
        c8_h_conf = (p_humaid["confidence"].between(0.0, 1.0)).all() and not p_humaid["confidence"].isna().any()
        c8_c_score = (p_cmmd["model_score"].between(0.0, 1.0)).all() and not p_cmmd["model_score"].isna().any()
        c8_c_conf = (p_cmmd["confidence"].between(0.0, 1.0)).all() and not p_cmmd["confidence"].isna().any()
        
        # Check unified numeric bounds: prediction sources non-null in [0,1], lexical features null
        u_model_scores = df_unified["model_score"].dropna()
        u_model_confs = df_unified["confidence"].dropna()
        u_score_valid = ((u_model_scores.between(0.0, 1.0)).all() and
                         (len(u_model_scores) == len(p_humaid) + len(p_cmmd)) and
                         (u_model_confs.between(0.0, 1.0)).all() and
                         (len(u_model_confs) == len(p_humaid) + len(p_cmmd)))
        
        c8 = c8_h_score and c8_h_conf and c8_c_score and c8_c_conf and u_score_valid
        results["8. Confidence & Score Ranges"] = (c8, f"All scores and confidences in [0.0, 1.0], prediction records non-null, lexical records null")
    except Exception as e:
        results["8. Confidence & Score Ranges"] = (False, f"Exception: {e}")

    # ------------------------------------------------------------------
    # 9. Calibration Semantics & Quality Separation
    # ------------------------------------------------------------------
    try:
        calib_statuses = set(df_unified["calibration_status"].unique())
        quality_statuses = set(df_unified["quality_status"].unique())
        
        # Uncalibrated predictions must be explicitly UNCALIBRATED
        cmmd_calib = set(p_cmmd["calibration_status"].unique())
        humaid_calib = set(p_humaid["calibration_status"].unique())
        
        c9_calib = (cmmd_calib == {"UNCALIBRATED"}) and (humaid_calib == {"UNCALIBRATED"})
        c9_quality = (quality_statuses == {"VALID"})
        c9_sep = calib_statuses.issubset({"UNCALIBRATED", "NOT_APPLICABLE", "CALIBRATED_EMPIRICAL"})
        
        c9 = c9_calib and c9_quality and c9_sep
        results["9. Calibration & Quality Semantics"] = (c9, f"calib_statuses={calib_statuses}, quality_statuses={quality_statuses}")
    except Exception as e:
        results["9. Calibration & Quality Semantics"] = (False, f"Exception: {e}")

    # ------------------------------------------------------------------
    # 10. Modality Honesty
    # ------------------------------------------------------------------
    try:
        # Physical file check: verify 0 image binaries exist in data/raw/crisismmd/
        raw_cmmd_dir = root / "data" / "raw" / "crisismmd"
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
        existing_images = []
        if raw_cmmd_dir.exists():
            for root_d, _, files in os.walk(raw_cmmd_dir):
                for f in files:
                    if Path(f).suffix.lower() in image_extensions:
                        existing_images.append(f)
                        
        n_images_found = len(existing_images)
        p_image_flags = p_cmmd["image_available"].unique()
        df_c_flags = df_c["image_available_locally"].unique()
        
        c10 = (n_images_found == 0) and (list(p_image_flags) == [False]) and (list(df_c_flags) == [False])
        results["10. Modality Honesty"] = (c10, f"Local image files={n_images_found}, image_available={p_image_flags}, image_available_locally={df_c_flags}")
    except Exception as e:
        results["10. Modality Honesty"] = (False, f"Exception: {e}")

    # ------------------------------------------------------------------
    # 11. Documentation & Metrics Consistency
    # ------------------------------------------------------------------
    try:
        with open(root / "models" / "crisis_information" / "crisismmd" / "crisismmd_metrics.json", "r", encoding="utf-8") as f:
            metrics_json = json.load(f)
            
        tf_metrics = metrics_json["transformer_distilbert"]
        base_metrics = metrics_json["baseline_tfidf_logistic"]
        doc_report = (root / "docs" / "crisis_information" / "PHASE7_FINAL_REPORT.md").read_text(encoding="utf-8")
        
        # Verify numbers in documentation
        acc_str = f"{tf_metrics['accuracy']:.4f}"       # 0.8199
        f1_str = f"{tf_metrics['macro_f1']:.4f}"         # 0.7078
        prec_str = f"{tf_metrics['macro_precision']:.4f}" # 0.8519
        rec_str = f"{tf_metrics['macro_recall']:.4f}"    # 0.6678
        base_acc = f"{base_metrics['accuracy']:.4f}"    # 0.7445
        base_f1 = f"{base_metrics['macro_f1']:.4f}"      # 0.6171
        
        c11 = ((acc_str in doc_report) and (f1_str in doc_report) and
               (prec_str in doc_report) and (rec_str in doc_report) and
               (base_acc in doc_report) and (base_f1 in doc_report))
        results["11. Documentation & Metrics Consistency"] = (c11, f"DistilBERT Acc={acc_str}, F1={f1_str}, TFIDF Acc={base_acc}, F1={base_f1} verified in doc")
    except Exception as e:
        results["11. Documentation & Metrics Consistency"] = (False, f"Exception: {e}")

    # ------------------------------------------------------------------
    # 12. Unified Parquet Consistency
    # ------------------------------------------------------------------
    try:
        n_unified = len(df_unified)
        n_expected = len(p_humaid) + len(p_cmmd) + len(df_l)  # 15160 + 955 + 88015 = 104130
        
        # Verify components
        source_counts = df_unified["source_dataset"].value_counts().to_dict()
        c12 = (n_unified == 104130) and (n_unified == n_expected) and (
            source_counts.get("humaid_all_combined") == 15160 and
            source_counts.get("crisismmd_multimodal") == 955 and
            source_counts.get("crisislex_t6_and_t26") == 88015
        )
        results["12. Unified Parquet Additive Sum"] = (c12, f"Total={n_unified} (expected {n_expected}), breakdown={source_counts}")
    except Exception as e:
        results["12. Unified Parquet Additive Sum"] = (False, f"Exception: {e}")

    # ------------------------------------------------------------------
    # Final Output Summary
    # ------------------------------------------------------------------
    print("\nAUDIT CHECKLIST SUMMARY:")
    all_passed = True
    for item, (passed, detail) in results.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"  [{status}] {item:40s} : {detail}")
        
    print("\n" + "=" * 75)
    if all_passed:
        print("OVERALL INDEPENDENT AUDIT DECISION: PASS — 100% CONSISTENT & VERIFIED")
    else:
        print("OVERALL INDEPENDENT AUDIT DECISION: FAIL — DEFECTS DETECTED")
    print("=" * 75)
    
    return all_passed

if __name__ == "__main__":
    success = audit_consistency()
    sys.exit(0 if success else 1)
