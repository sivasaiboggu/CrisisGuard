# CrisisGuard — Enterprise Web Application & API Launcher (PowerShell)
# Author: B.SIVASAI (Roll Number: 2023BCS0228)
# Course: CSE412 — Big Data & Large-Scale Computing
#
# USAGE in PowerShell (already in repo directory):
#   .\scripts\demo\start_web.ps1

$Port = if ($env:PORT) { $env:PORT } else { "8080" }

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CRISISGUARD — DECISION SUPPORT WEB APP & API" -ForegroundColor Cyan
Write-Host "Author: B.SIVASAI (Roll Number: 2023BCS0228)" -ForegroundColor Cyan
Write-Host "Course: CSE412 — Big Data & Large-Scale Computing" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Launching server in WSL2 Ubuntu-24.04..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

wsl -d Ubuntu-24.04 --cd /mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard python3 -m src.api.server
