# CrisisGuard: Phase 6 Machine Learning & Forensics Environment Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 6 — Synthetic Media Detection & Unified Media-Risk Engine  
**Audit Timestamp:** 2026-09-27T12:56:00Z  

---

## 1. Executive Summary

Phase 6 introduces the first automated intelligence components of CrisisGuard: the dual-branch synthetic media detection engine (Branch A: Google DFD-derived Video Forensics; Branch B: CIFAKE Image Forensics) and the downstream Unified Media-Risk schema.

To guarantee scientific reproducibility and satisfy the strict CSE412 computational boundaries, this audit benchmarks the active ML library stack, host hardware capabilities, and execution substrate.

---

## 2. Verified Software & Machine Learning Runtimes

| Component / Package | Verified Version | Installation Path / Environment | Status | Verification Command |
| :--- | :---: | :--- | :---: | :--- |
| **Operating System** | Ubuntu 24.04 LTS | WSL2 (`Linux 5.15.167.4-microsoft-standard-WSL2 x86_64`) | **OPERATIONAL** | `cat /etc/os-release` |
| **Python Runtime** | `3.12.3` | `/usr/bin/python3` (GCC 13.3.0) | **OPERATIONAL** | `python3 --version` |
| **PyTorch** | `2.14.0+cpu` | `/home/sivasai/.local/lib/python3.12/site-packages/torch` | **OPERATIONAL** | `python3 -c "import torch"` |
| **Torchvision** | `0.29.0+cpu` | `/home/sivasai/.local/lib/python3.12/site-packages/torchvision` | **OPERATIONAL** | `python3 -c "import torchvision"` |
| **NumPy** | `1.26.4` | `/home/sivasai/.local/lib/python3.12/site-packages/numpy` | **OPERATIONAL** | `python3 -c "import numpy"` |
| **Pandas** | `2.1.4` | `/usr/lib/python3/dist-packages/pandas` | **OPERATIONAL** | `python3 -c "import pandas"` |
| **OpenCV** | `4.10.0` (Headless) | `/home/sivasai/.local/lib/python3.12/site-packages/cv2` | **OPERATIONAL** | `python3 -c "import cv2"` |
| **PIL / Pillow** | `10.2.0` | `/usr/lib/python3/dist-packages/PIL` | **OPERATIONAL** | `python3 -c "import PIL"` |
| **Scikit-Learn** | `1.5.2` | `/home/sivasai/.local/lib/python3.12/site-packages/sklearn` | **OPERATIONAL** | `python3 -c "import sklearn"` |
| **PyArrow** | `14.0.2` | `/usr/local/lib/python3.12/dist-packages/pyarrow` | **OPERATIONAL** | `python3 -c "import pyarrow"` |

---

## 3. Hardware & Compute Substrate

| Hardware Resource | Specification / Measured Allocation | Operational Status & Policy |
| :--- | :--- | :--- |
| **Host CPU** | AMD Ryzen 7 7445HS (6 Physical Cores / 12 Logical Threads) | CPU-accelerated multithreaded tensor operations active |
| **Host Physical RAM**| 16 GB DDR5 | Windows 11 host retains $\ge 8\text{ GB}$ headroom |
| **WSL2 Allocated RAM**| 7.4 GiB Total ($5.8\text{ GiB}$ free / available) | Memory ceiling enforced: training jobs capped $\le 2.5\text{ GiB}$ |
| **Swap Storage** | 2.0 GiB | Swap buffer operational |
| **Host GPU** | NVIDIA GeForce RTX 2050 (4096 MiB VRAM, Driver 592.82) | Detected on host; CPU training explicitly selected for reproducibility |
| **CUDA Execution** | `torch.cuda.is_available() == False` | **CPU-Compatible Training Active** (Zero CUDA fabrication) |
| **WSL2 ext4 Storage**| `/dev/sdd` (1007 GB total, **939 GB Available**) | Primary storage for temporary tensors and feature extracts |
| **Windows Workspace**| `C:\Users\HP\OneDrive\Desktop\CrisisGuard` (**226 GB Available**) | Houses immutable code, models, and Parquet outputs |

---

## 4. Execution Policy & Reproducibility Constraints

1. **Deterministic Random Seeds:** Global seed `42` enforced across Python `random`, `numpy`, and `torch.manual_seed`.
2. **Deterministic CPU Computation:** All convolutional backbones execute with `torch.use_deterministic_algorithms(False)` and deterministic seed initialization, avoiding non-deterministic CUDA kernel divergence across diverse evaluator environments.
3. **Memory Safeguards:** Batch size capped at 32 for images and 8 for video frame sequences to prevent out-of-memory kernel panics on the 7.4 GiB WSL allocation.
4. **Data Isolation:** Raw input datasets in `data/raw/` remain 100% immutable and read-only.
