#!/usr/bin/env python3
"""
CrisisGuard — Phase 3 Final Corrections Verification Script
Validates:
1. DFD terminology correction (Google DFD-derived controlled development sample)
2. CIFAKE role correction (AI-generated image detection development/evaluation)
3. Two-branch media architecture (Video Forensics & Image Forensics)
4. Unified media schema (canonical record output)
5. Data lineage update (two branches, unified features, multi-criteria EDPI)
6. No false generalization claim (independent branch evaluation)
7. Emergency-priority separation (synthetic media as feature, balanced priority)
"""

import os
import sys
import yaml
import json
from pathlib import Path

def test_corrections():
    root = Path(__file__).resolve().parent.parent.parent
    
    # 1. DFD terminology correction
    dfd_yaml_path = root / "data" / "manifests" / "deepfake_dfd.yaml"
    dfd_pass = False
    if dfd_yaml_path.exists():
        with open(dfd_yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
            if ("CONTROLLED_DERIVED_SAMPLE" in content and
                "Google DFD-derived controlled development sample" in content and
                "selection_seed: 42" in content and
                "purpose:" in content and
                "original_dataset: \"Google DeepFake Detection Dataset (DFD)\"" in content):
                dfd_pass = True

    # 2. CIFAKE role correction
    cifake_yaml_path = root / "data" / "manifests" / "synthetic_media_eval.yaml"
    cifake_pass = False
    if cifake_yaml_path.exists():
        with open(cifake_yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
            if ("Image Forensics Branch" in content and
                "AI-generated image detection" in content and
                "NOT a video or deepfake benchmark" in content):
                cifake_pass = True

    # 3. Two-branch media architecture
    strategy_doc = root / "docs" / "datasets" / "DEEPFAKE_DATA_STRATEGY.md"
    arch_pass = False
    if strategy_doc.exists():
        with open(strategy_doc, "r", encoding="utf-8") as f:
            content = f.read()
            if ("Two-Branch Synthetic-Media Architecture" in content and
                "VIDEO FORENSICS" in content and
                "IMAGE FORENSICS" in content and
                "Unified Media Risk" in content):
                arch_pass = True

    # 4. Unified media schema
    schema_pass = False
    required_fields = ["content_id", "media_type", "synthetic_probability", "synthetic_risk", "model_version", "prediction_timestamp"]
    if strategy_doc.exists():
        with open(strategy_doc, "r", encoding="utf-8") as f:
            content = f.read()
            if all(field in content for field in required_fields):
                schema_pass = True

    # 5. Data lineage update
    lineage_doc = root / "docs" / "datasets" / "DATA_LINEAGE.md"
    lineage_pass = False
    if lineage_doc.exists():
        with open(lineage_doc, "r", encoding="utf-8") as f:
            content = f.read()
            if ("Video Forensics Branch" in content and
                "Image Forensics Branch" in content and
                "UNIFIED MEDIA RISK" in content and
                "Emergency Dispatch Priority (EDPI)" in content):
                lineage_pass = True

    # 6. No false generalization claim
    gen_pass = False
    if strategy_doc.exists():
        with open(strategy_doc, "r", encoding="utf-8") as f:
            content = f.read()
            if ("evaluated independently" in content and
                "not a direct cross-dataset generalization test" in content):
                gen_pass = True

    # 7. Emergency-priority separation
    priority_pass = False
    if strategy_doc.exists() and lineage_doc.exists():
        with open(strategy_doc, "r", encoding="utf-8") as f:
            s_content = f.read()
        with open(lineage_doc, "r", encoding="utf-8") as f:
            l_content = f.read()
        if ("does not directly determine whether an emergency crisis report is true or false" in s_content and
            "Synthetic media risk is a FEATURE" in l_content and
            "Emergency Dispatch Priority (EDPI)" in l_content):
            priority_pass = True

    print("=" * 60)
    print("FINAL VALIDATION")
    print("=" * 60)
    print(f"DFD terminology correction: {'PASS' if dfd_pass else 'FAIL'}")
    print(f"CIFAKE role correction: {'PASS' if cifake_pass else 'FAIL'}")
    print(f"Two-branch media architecture: {'PASS' if arch_pass else 'FAIL'}")
    print(f"Unified media schema: {'PASS' if schema_pass else 'FAIL'}")
    print(f"Data lineage update: {'PASS' if lineage_pass else 'FAIL'}")
    print(f"No false generalization claim: {'PASS' if gen_pass else 'FAIL'}")
    print(f"Emergency-priority separation: {'PASS' if priority_pass else 'FAIL'}")
    print("=" * 60)

    all_passed = all([dfd_pass, cifake_pass, arch_pass, schema_pass, lineage_pass, gen_pass, priority_pass])
    if all_passed:
        print("PHASE 3 FINAL STATUS: PHASE 3 = FROZEN")
    else:
        print("PHASE 3 FINAL STATUS: CORRECTIONS INCOMPLETE")
    print("=" * 60)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(test_corrections())
