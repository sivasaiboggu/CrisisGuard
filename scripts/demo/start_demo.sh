#!/usr/bin/env bash
# CrisisGuard — One-Command Live Demo Launcher (WSL2/Linux)
# Author: B.SIVASAI (Roll Number: 2023BCS0228)
# Course: CSE412 — Big Data & Large-Scale Computing
#
# USAGE (from WSL2 terminal or wsl -d Ubuntu-24.04):
#   bash scripts/demo/start_demo.sh
#
# All components execute inside WSL2 Ubuntu-24.04 using the
# isolated .venv (Python 3.12.3) which correctly includes:
#   - torch 2.14.0+cpu
#   - torchvision 0.29.0+cpu
#   - scikit-learn 1.5.2
#   - kafka-python 2.2.3
#
# DO NOT run demo scripts from Windows Python 3.14 directly.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "ERROR: .venv not found at $PROJECT_ROOT/.venv"
    echo "Run: cd $PROJECT_ROOT && python3 -m venv .venv --system-site-packages"
    exit 1
fi

cd "$PROJECT_ROOT"

echo "============================================================"
echo "CRISISGUARD — LIVE DEMO LAUNCHER (WSL2 Ubuntu-24.04)"
echo "Author: B.SIVASAI (Roll Number: 2023BCS0228)"
echo "Python: $($VENV_PYTHON --version)"
echo "Project Root: $PROJECT_ROOT"
echo "============================================================"

echo ""
echo "[1/3] Environment Health Check..."
"$VENV_PYTHON" scripts/demo/check_demo_environment.py
echo ""

echo "[2/3] Running Live Demo (Modes A + B)..."
"$VENV_PYTHON" scripts/demo/run_live_demo.py
echo ""

echo "[3/4] Verifying Frozen Computational Integrity..."
"$VENV_PYTHON" scripts/validation/validate_final_project.py
"$VENV_PYTHON" scripts/validation/run_functional_acceptance_tests.py
echo ""

echo "[4/4] Evidence-Aware Misinformation Assessment & Intelligent Resource Allocation..."
"$VENV_PYTHON" scripts/validation/validate_evidence_allocation.py
"$VENV_PYTHON" scripts/demo/run_demo_evidence_allocation.py
"$VENV_PYTHON" scripts/demo/view_decision_support_dashboard.py

echo ""
echo "============================================================"
echo "CRISISGUARD DEMO: COMPLETE"
echo "============================================================"
