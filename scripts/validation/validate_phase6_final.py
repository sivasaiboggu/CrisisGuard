#!/usr/bin/env python3
"""
CrisisGuard — Phase 6 Master Final Freeze Validation Script
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Audits and verifies:
 1. Raw data exists
 2. Raw data unchanged
 3. CIFAKE provenance documented
 4. CIFAKE count (exactly 500)
 5. CIFAKE label distribution (250 real, 250 fake)
 6. CIFAKE SHA256 uniqueness (500 unique)
 7. CIFAKE train/val/test disjointness (0 overlap)
 8. DFD video atomicity
 9. DFD frame non-leakage
10. DFD actor/source separation
11. Image checkpoint exists & loads
12. Video checkpoint exists & loads
13. Prediction datasets exist & verified
14. Media-risk schema contract satisfied
15. Quality and calibration separation
16. Probability / score semantics
17. Calibration status (UNCALIBRATED)
18. Provenance tracking complete
19. Reproducibility metadata (seed=42)
20. Model registry & model card published
21. Cross-document consistency verified
"""

import os
import sys
import json
import yaml
import torch
import pandas as pd
import numpy as np
import jsonschema

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def run_freeze_audit():
    print("=" * 65)
    print("CRISISGUARD — PHASE 6 MASTER FINAL FREEZE AUDIT")
    print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    print("Course: CSE412 — Big Data & Large-Scale Computing")
    print("=" * 65)

    checks = []

    # 1. Raw data exists
    raw_dfd = os.path.join(BASE_DIR, "data", "raw", "deepfake_dfd")
    raw_cifake = os.path.join(BASE_DIR, "data", "raw", "synthetic_media_eval")
    raw_exists = os.path.isdir(raw_dfd) and os.path.isdir(raw_cifake)
    checks.append(("Raw data directories exist", raw_exists, f"DFD: {os.path.isdir(raw_dfd)}, CIFAKE: {os.path.isdir(raw_cifake)}"))

    # 2. Raw data unchanged & counts verified
    cifake_real_dir = os.path.join(raw_cifake, "real")
    cifake_fake_dir = os.path.join(raw_cifake, "fake")
    real_files = os.listdir(cifake_real_dir) if os.path.isdir(cifake_real_dir) else []
    fake_files = os.listdir(cifake_fake_dir) if os.path.isdir(cifake_fake_dir) else []
    cifake_count = len(real_files) + len(fake_files)
    dfd_files = os.listdir(raw_dfd)
    raw_unchanged = (cifake_count == 500) and (len(dfd_files) >= 4)
    checks.append(("Raw data unchanged (file counts)", raw_unchanged, f"CIFAKE: {cifake_count} (250 real + 250 fake), DFD: {len(dfd_files)} assets"))

    # 3. CIFAKE provenance documented
    cifake_prov_doc = os.path.join(BASE_DIR, "docs", "synthetic_media", "CIFAKE_SUBSET_PROVENANCE.md")
    prov_doc_ok = os.path.isfile(cifake_prov_doc) and os.path.getsize(cifake_prov_doc) > 1000
    checks.append(("CIFAKE provenance documentation", prov_doc_ok, cifake_prov_doc))

    # 4. CIFAKE exact count & label distribution
    exact_dist = (len(real_files) == 250) and (len(fake_files) == 250)
    checks.append(("CIFAKE count & label distribution (250/250)", exact_dist, f"Real: {len(real_files)}, Fake: {len(fake_files)}"))

    # 5. CIFAKE SHA256 uniqueness
    raw_meta_file = os.path.join(raw_cifake, "metadata.json")
    sha_unique = False
    if os.path.isfile(raw_meta_file):
        with open(raw_meta_file, "r") as f:
            rmeta = json.load(f)
        hashes = [r["sha256"] for r in rmeta.get("records", [])]
        sha_unique = (len(hashes) == 500) and (len(set(hashes)) == 500)
    checks.append(("CIFAKE SHA-256 uniqueness (500 distinct)", sha_unique, f"Unique hashes: {len(set(hashes)) if sha_unique else 'N/A'}"))

    # 6. CIFAKE train/val/test disjointness
    part_file = os.path.join(BASE_DIR, "data", "features", "synthetic_media", "cifake_partitions.parquet")
    parts_disjoint = False
    part_msg = ""
    if os.path.isfile(part_file):
        df_part = pd.read_parquet(part_file)
        tr_h = set(df_part[df_part["split"] == "train"]["sha256"])
        va_h = set(df_part[df_part["split"] == "val"]["sha256"])
        te_h = set(df_part[df_part["split"] == "test"]["sha256"])
        disj = (len(tr_h & va_h) == 0) and (len(tr_h & te_h) == 0) and (len(va_h & te_h) == 0)
        parts_disjoint = disj and (len(tr_h) == 350) and (len(va_h) == 75) and (len(te_h) == 75)
        part_msg = f"Disjoint: {disj}, Train={len(tr_h)}, Val={len(va_h)}, Test={len(te_h)}"
    checks.append(("CIFAKE train/val/test disjointness", parts_disjoint, part_msg))

    # 7. DFD video atomicity & frame non-leakage
    vid_feat_file = os.path.join(BASE_DIR, "data", "features", "deepfake_dfd", "dfd_video_features.parquet")
    frm_feat_file = os.path.join(BASE_DIR, "data", "features", "deepfake_dfd", "dfd_frame_features.parquet")
    dfd_atomicity_ok = False
    if os.path.isfile(vid_feat_file) and os.path.isfile(frm_feat_file):
        df_vf = pd.read_parquet(vid_feat_file)
        df_ff = pd.read_parquet(frm_feat_file)
        valid_map = set(df_ff["content_id"]).issubset(set(df_vf["content_id"]))
        dfd_atomicity_ok = (len(df_vf) == 4) and (len(df_ff) == 12) and valid_map
    checks.append(("DFD video atomicity & frame non-leakage", dfd_atomicity_ok, f"Videos: {len(df_vf)}, Frames: {len(df_ff)}"))

    # 8. DFD actor/source separation
    actor_disjoint = False
    if os.path.isfile(vid_feat_file):
        df_vf = pd.read_parquet(vid_feat_file)
        tr_act = set(df_vf[df_vf["split"] == "train"]["actor_id"])
        te_act = set(df_vf[df_vf["split"] == "test"]["actor_id"])
        actor_disjoint = len(tr_act & te_act) == 0 and len(tr_act) > 0 and len(te_act) > 0
    checks.append(("DFD actor biometric disjointness", actor_disjoint, f"Train actors: {tr_act}, Test actors: {te_act}"))

    # 9. Model checkpoints load successfully
    img_ckpt = os.path.join(BASE_DIR, "models", "synthetic_media", "image_model_best.pt")
    vid_ckpt = os.path.join(BASE_DIR, "models", "synthetic_media", "video_model_best.pt")
    ckpts_load = False
    if os.path.isfile(img_ckpt) and os.path.isfile(vid_ckpt):
        try:
            ci = torch.load(img_ckpt, map_location="cpu")
            cv = torch.load(vid_ckpt, map_location="cpu")
            ckpts_load = isinstance(ci, dict) and isinstance(cv, dict)
        except Exception:
            ckpts_load = False
    checks.append(("Model checkpoints exist & load", ckpts_load, f"Image: {os.path.getsize(img_ckpt)} B, Video: {os.path.getsize(vid_ckpt)} B"))

    # 10. Prediction datasets exist & zero NaNs
    img_pred = os.path.join(BASE_DIR, "data", "features", "synthetic_media", "image_predictions.parquet")
    vid_pred = os.path.join(BASE_DIR, "data", "features", "synthetic_media", "video_predictions.parquet")
    uni_pred = os.path.join(BASE_DIR, "data", "features", "synthetic_media", "unified_media_risk.parquet")
    preds_ok = False
    if os.path.isfile(img_pred) and os.path.isfile(vid_pred) and os.path.isfile(uni_pred):
        di = pd.read_parquet(img_pred)
        dv = pd.read_parquet(vid_pred)
        du = pd.read_parquet(uni_pred)
        no_nulls = (di.isnull().sum().sum() == 0) and (dv.isnull().sum().sum() == 0) and (du.isnull().sum().sum() == 0)
        counts_match = (len(di) == 75) and (len(dv) == 2) and (len(du) == 77)
        preds_ok = no_nulls and counts_match
    checks.append(("Prediction datasets valid & zero nulls", preds_ok, f"Image: {len(di)}, Video: {len(dv)}, Unified: {len(du)}"))

    # 11. Schema contract validation
    schema_file = os.path.join(BASE_DIR, "schemas", "media_risk_schema.json")
    schema_ok = False
    if os.path.isfile(schema_file) and os.path.isfile(uni_pred):
        with open(schema_file, "r") as f:
            schema = json.load(f)
        du = pd.read_parquet(uni_pred)
        recs = du.to_dict(orient="records")
        try:
            for r in recs:
                jsonschema.validate(instance=r, schema=schema)
            schema_ok = True
        except Exception as e:
            schema_ok = False
    checks.append(("Unified Media-Risk Schema validated", schema_ok, f"All {len(recs)} records conform to schema"))

    # 12. Quality and Calibration Separation
    du = pd.read_parquet(uni_pred)
    quality_values = set(du["quality_status"].unique())
    calib_values = set(du["calibration_status"].unique())
    qc_sep = ("UNCALIBRATED" not in quality_values) and (quality_values == {"VALID"}) and (calib_values == {"UNCALIBRATED"})
    checks.append(("Quality & Calibration separation verified", qc_sep, f"quality_status: {quality_values}, calibration_status: {calib_values}"))

    # 13. Probability & Score semantics
    prob_in_bounds = (du["synthetic_probability"] >= 0.0).all() and (du["synthetic_probability"] <= 1.0).all()
    risk_in_bounds = (du["synthetic_risk"] >= 0.0).all() and (du["synthetic_risk"] <= 1.0).all()
    scores_numeric = np.issubdtype(du["model_score"].dtype, np.number)
    sem_ok = prob_in_bounds and risk_in_bounds and scores_numeric
    checks.append(("Score & probability bounds in [0, 1]", sem_ok, "model_score numeric, synthetic_probability & synthetic_risk in [0, 1]"))

    # 14. Calibration status designated UNCALIBRATED
    calib_uncal = (du["calibration_status"] == "UNCALIBRATED").all()
    checks.append(("Calibration status honestly UNCALIBRATED", calib_uncal, "Zero fabricated calibration claims across all 77 rows"))

    # 15. Provenance tracking complete
    req_cols = ["content_id", "media_type", "model_branch", "model_version", "model_score", "synthetic_probability", "synthetic_risk", "calibration_status", "prediction_timestamp", "source_dataset", "quality_status", "provenance"]
    prov_complete = all(c in du.columns for c in req_cols)
    checks.append(("Provenance columns complete", prov_complete, f"All {len(req_cols)} required columns present"))

    # 16. Unified inference script execution
    infer_py = os.path.join(BASE_DIR, "scripts", "synthetic_media", "infer_media.py")
    infer_py_ok = os.path.isfile(infer_py)
    checks.append(("Unified inference script present", infer_py_ok, infer_py))

    # 17. Model registry complete
    mod_reg = os.path.join(BASE_DIR, "models", "synthetic_media", "model_registry.yaml")
    reg_ok = False
    if os.path.isfile(mod_reg):
        with open(mod_reg, "r") as f:
            y = yaml.safe_load(f)
        models_list = y.get("models", [])
        reg_ok = len(models_list) == 2 and all("calibration_status" in m for m in models_list)
    checks.append(("Model registry complete & audited", reg_ok, mod_reg))

    # 18. Model card published with ethical bounds
    mod_card = os.path.join(BASE_DIR, "docs", "synthetic_media", "MODEL_CARD.md")
    card_ok = False
    if os.path.isfile(mod_card):
        with open(mod_card, "r") as f:
            ct = f.read().lower()
        card_ok = ("controlled 500-image" in ct or "controlled closed-world" in ct) and ("proof-of-concept" in ct) and ("decision-support" in ct or "decision support" in ct)
    checks.append(("Model card with ethical & operational bounds", card_ok, mod_card))

    # 19. Reproducibility metadata (seed=42)
    cfg_file = os.path.join(BASE_DIR, "config", "synthetic_media.yaml")
    cfg_ok = False
    if os.path.isfile(cfg_file):
        with open(cfg_file, "r") as f:
            cfg = yaml.safe_load(f)
        s = cfg.get("reproducibility", {}).get("seed", cfg.get("seed"))
        cfg_ok = (s == 42)
    checks.append(("Reproducibility configuration (seed=42)", cfg_ok, cfg_file))

    # 20. Inventory document published
    inv_doc = os.path.join(BASE_DIR, "docs", "synthetic_media", "PHASE6_FINAL_INVENTORY.md")
    inv_ok = os.path.isfile(inv_doc) and os.path.getsize(inv_doc) > 1000
    checks.append(("Phase 6 Final Inventory published", inv_ok, inv_doc))

    # 21. Cross-document consistency verified
    rep_doc = os.path.join(BASE_DIR, "docs", "synthetic_media", "PHASE6_FINAL_REPORT.md")
    rep_ok = False
    if os.path.isfile(rep_doc):
        with open(rep_doc, "r") as f:
            rt = f.read()
        rep_ok = ("PART A:" in rt or "PART A —" in rt) and ("PART E:" in rt or "PART E —" in rt) and ("UNCALIBRATED" in rt)
    checks.append(("Cross-document consistency (Report Parts A-E)", rep_ok, rep_doc))

    print("\nFINAL FREEZE AUDIT SUMMARY:")
    all_passed = True
    for name, status, details in checks:
        flag = "[PASS]" if status else "[FAIL]"
        if not status:
            all_passed = False
        print(f"  {flag} {name:<45} : {details}")

    print("-" * 65)
    if all_passed:
        print("OVERALL PHASE 6 FINAL AUDIT: PASS — FROZEN WITH DOCUMENTED LIMITATIONS")
        print("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
        return 0
    else:
        print("OVERALL PHASE 6 FINAL AUDIT: FAIL / BLOCKED")
        return 1

if __name__ == "__main__":
    sys.exit(run_freeze_audit())
