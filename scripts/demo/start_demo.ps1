# CrisisGuard — One-Command Live Demo Launcher (Windows PowerShell)
# Author: B.SIVASAI (Roll Number: 2023BCS0228)
# Course: CSE412 — Big Data & Large-Scale Computing
#
# USAGE (from Windows PowerShell):
#   .\scripts\demo\start_demo.ps1
#
# This script delegates execution to WSL2 Ubuntu-24.04 where all
# Big Data services (Hadoop, Kafka, Spark, Hive) operate and where
# the correct Python environment (.venv, Python 3.12.3) exists.
#
# DO NOT run demo scripts using the Windows Python 3.14 directly.
# It lacks kafka-python and torchvision compatibility.

$ProjectRoot = (Resolve-Path "$PSScriptRoot\..\..")
$WslProjectRoot = "/mnt/c" + ($ProjectRoot.ToString().Substring(2).Replace('\', '/'))

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CRISISGUARD — LIVE DEMO LAUNCHER (via WSL2 Ubuntu-24.04)" -ForegroundColor Cyan
Write-Host "Author: B.SIVASAI (Roll Number: 2023BCS0228)" -ForegroundColor Cyan
Write-Host "Project Root (Win): $ProjectRoot" -ForegroundColor Cyan
Write-Host "Project Root (WSL): $WslProjectRoot" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n[Step 1] Environment Health Check..." -ForegroundColor Yellow
wsl -d Ubuntu-24.04 -e bash -c "cd '$WslProjectRoot' && .venv/bin/python scripts/demo/check_demo_environment.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Health check reported issues. Review output above." -ForegroundColor Yellow
}

Write-Host "`n[Step 2] Running Live Demonstration (Mode B)..." -ForegroundColor Yellow
wsl -d Ubuntu-24.04 -e bash -c "cd '$WslProjectRoot' && .venv/bin/python scripts/demo/run_live_demo.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Live demo encountered an error." -ForegroundColor Red
    exit 1
}

Write-Host "`n[Step 3] Verifying Frozen Computational Integrity..." -ForegroundColor Yellow
wsl -d Ubuntu-24.04 -e bash -c "cd '$WslProjectRoot' && .venv/bin/python scripts/validation/validate_final_project.py && .venv/bin/python scripts/validation/run_functional_acceptance_tests.py"

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "CRISISGUARD DEMO: COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
