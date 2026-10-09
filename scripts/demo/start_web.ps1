# CrisisGuard — Enterprise Web Application & API Launcher (PowerShell)
# Author: B.SIVASAI (Roll Number: 2023BCS0228)
# Course: CSE412 — Big Data & Large-Scale Computing
#
# Launches the FastAPI REST API and serves the production-built React frontend.
# Access URL: http://localhost:8080

$Port = if ($env:PORT) { $env:PORT } else { "8080" }

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CRISISGUARD — DECISION SUPPORT WEB APP & API" -ForegroundColor Cyan
Write-Host "Author: B.SIVASAI (Roll Number: 2023BCS0228)" -ForegroundColor Cyan
Write-Host "Course: CSE412 — Big Data & Large-Scale Computing" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Uvicorn Server in WSL2 Ubuntu-24.04 on Port $Port..." -ForegroundColor Yellow
Write-Host "Web Application URL: http://localhost:$Port" -ForegroundColor Green
Write-Host "Interactive Swagger API Docs: http://localhost:$Port/docs" -ForegroundColor Green
Write-Host "Press Ctrl+C to terminate the server." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

wsl -d Ubuntu-24.04 --cd /mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard python3 -m uvicorn src.api.server:app --host 0.0.0.0 --port $Port
