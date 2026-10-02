#!/usr/bin/env python3
"""
CrisisGuard: Phase 0 Validation Script
Validates directory structure, configuration templates, isolation of raw data,
and environment readiness without installing dependencies or external tools.
"""

import os
import sys
from pathlib import Path

# Common dataset file extensions that must NOT be present in data/raw during Phase 0
DATASET_EXTENSIONS = {
    ".csv", ".tsv", ".json", ".jsonl", ".parquet", ".orc", ".avro",
    ".mp4", ".avi", ".mkv", ".mov", ".zip", ".tar", ".gz", ".7z",
    ".h5", ".hdf5", ".npy", ".npz", ".pbf", ".osm"
}

# Source code extensions that must NEVER be in data/raw
SOURCE_CODE_EXTENSIONS = {
    ".py", ".scala", ".java", ".sh", ".ps1", ".sql", ".cpp", ".c", ".h", ".rs", ".go"
}

REQUIRED_DIRECTORIES = [
    "data/raw",
    "data/interim",
    "data/processed",
    "data/features",
    "models",
    "results",
    "logs",
    "docs",
    "docs/datasets",
    "config",
    "tests/smoke",
    "scripts/validation",
    "src"
]

REQUIRED_ROOT_FILES = [
    "PROJECT_STATUS.md",
    "README.md",
    "config/paths.yaml",
    ".gitignore",
    ".env.example",
    "docs/datasets/DATASET_MANIFEST_TEMPLATE.yaml"
]

def run_phase0_validation():
    root = Path(__file__).resolve().parent.parent.parent
    os.chdir(root)
    
    report = []
    has_errors = False

    report.append("=" * 70)
    report.append("CRISISGUARD PHASE 0 VALIDATION REPORT")
    report.append(f"Target Root: {root}")
    report.append(f"Operating System: {sys.platform}")
    report.append("=" * 70)

    # 1. Directory Existence & Separation
    report.append("\n[1] Checking Directory Hierarchy & Data Layer Separation:")
    for directory in REQUIRED_DIRECTORIES:
        dir_path = root / directory
        if dir_path.is_dir():
            report.append(f"  [OK] Directory exists: {directory}")
        else:
            report.append(f"  [FAIL] Missing required directory: {directory}")
            has_errors = True

    # 2. Required Root & Config Files
    report.append("\n[2] Checking Required Root & Configuration Files:")
    for file_rel in REQUIRED_ROOT_FILES:
        file_path = root / file_rel
        if file_path.is_file():
            report.append(f"  [OK] File exists: {file_rel}")
        else:
            report.append(f"  [FAIL] Missing required file: {file_rel}")
            has_errors = True

    # 3. Raw Data Integrity & Zero Contamination Checks
    report.append("\n[3] Validating data/raw Cleanliness & Rule Enforcement:")
    raw_dir = root / "data" / "raw"
    if not raw_dir.exists():
        report.append("  [FAIL] data/raw does not exist.")
        has_errors = True
    else:
        # Scan contents of data/raw recursively
        raw_files = [p for p in raw_dir.rglob("*") if p.is_file()]
        
        # Check for dataset files
        detected_dataset_files = [
            f for f in raw_files if f.suffix.lower() in DATASET_EXTENSIONS
        ]
        if detected_dataset_files:
            report.append(f"  [FAIL] Dataset files detected in data/raw (should be empty in Phase 0):")
            for f in detected_dataset_files:
                report.append(f"         - {f.relative_to(root)}")
            has_errors = True
        else:
            report.append("  [OK] Zero dataset files present in data/raw.")

        # Check for source code accidentally placed in data/raw
        detected_code_files = [
            f for f in raw_files if f.suffix.lower() in SOURCE_CODE_EXTENSIONS
        ]
        if detected_code_files:
            report.append(f"  [FAIL] Source code files detected inside data/raw:")
            for f in detected_code_files:
                report.append(f"         - {f.relative_to(root)}")
            has_errors = True
        else:
            report.append("  [OK] Zero source code files detected in data/raw.")

    # 4. Final Verdict
    report.append("\n" + "=" * 70)
    if has_errors:
        report.append("VERDICT: PHASE 0 VALIDATION FAILED")
        report.append("Resolve the reported issues before proceeding.")
        report.append("=" * 70)
        print("\n".join(report))
        sys.exit(1)
    else:
        report.append("VERDICT: PHASE 0 VALIDATION PASSED (100% COMPLIANT)")
        report.append("Workspace structure, templates, and data policies strictly verified.")
        report.append("Ready for Phase 1 (Environment & Toolchain Audit).")
        report.append("=" * 70)
        print("\n".join(report))
        sys.exit(0)

if __name__ == "__main__":
    run_phase0_validation()
