# CrisisGuard: Phase 6 Media Forensics Data Profiling Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 6 — Synthetic Media Detection & Unified Media-Risk Engine  

---

## 1. Overview & Dataset Scope

This report documents the empirical profile, distribution characteristics, and technical parameters of the multimedia datasets ingested into the CrisisGuard Phase 6 Forensics Engine:
1. **Branch A:** Google DFD-Derived Controlled Development Sample (Video & Keyframe Forensics)
2. **Branch B:** CIFAKE AI-Generated vs. Photographic Image Benchmark (Image Forensics)

All statistics are derived directly from physical inspection and programmatic audit (`validate_phase6_inputs.py`).

---

## 2. Branch A: Google DFD-Derived Controlled Development Sample

### 2.1 Media Asset Inventory

| Media ID | Content Identifier | Format / Codec | Dimensions ($W \times H$) | Duration | Total Raw Frames | Sampled Keyframes | Ground Truth Label | Split | Actor Identifier |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `dfd_video_sample_01` | `dfd_dfd_video_sample_01` | Video / GIF | $600 \times 338$ | 3.5 sec | 100 | 5 | 1 (Manipulated) | Test | `actor_dfd_pair_01` |
| `dfd_video_sample_02` | `dfd_dfd_video_sample_02` | Video / GIF | $614 \times 460$ | 3.8 sec | 50 | 5 | 1 (Manipulated) | Validation | `actor_dfd_pair_02` |
| `dfd_frame_actor_orig` | `dfd_dfd_frame_actor_orig` | Image / PNG | $1920 \times 1080$ | N/A | 1 | 1 | 0 (Pristine) | Train | `actor_dfd_071` |
| `dfd_frame_actor_fake` | `dfd_dfd_frame_actor_fake` | Image / PNG | $1920 \times 1080$ | N/A | 1 | 1 | 1 (Manipulated) | Test | `actor_dfd_054` |

### 2.2 Controlled Frame Sampling Summary
- **Total Physical Media Assets:** 4
- **Manipulated Media Count:** 3 (75.0%)
- **Pristine Media Count:** 1 (25.0%)
- **Total Raw Available Frames:** 152 frames across videos and keyframes.
- **Uniform Temporal Sampling Rate:**
  - `dfd_video_sample_01`: Sampled at indices `[0, 20, 40, 60, 80]` (interval $\Delta t = 0.8\text{ s}$).
  - `dfd_video_sample_02`: Sampled at indices `[0, 10, 20, 30, 40]` (interval $\Delta t = 0.4\text{ s}$).
- **Total Extracted Keyframes:** 12 frames stored as lossless PNGs in `data/processed/deepfake_dfd/frames/`.

---

## 3. Branch B: CIFAKE Image Forensics Dataset

### 3.1 Distribution & Class Balance

| Category | Raw Source | Image Count | Proportion | Native Format | Native Resolution | Color Space | Generator Engine |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Pristine Photographic (Real)** | CIFAR-10 Benchmark | 250 | 50.00% | JPEG (`.jpg`) | $32 \times 32$ | 3-Channel RGB | Organic camera sensor |
| **Synthetic Manipulated (Fake)** | Stable Diffusion v1.4 | 250 | 50.00% | JPEG (`.jpg`) | $32 \times 32$ | 3-Channel RGB | Latent Diffusion Model |
| **Total Cohort** | — | **500** | **100.00%** | — | — | — | — |

### 3.2 Integrity, Uniqueness & Quality Metrics

| Audit Property | Measured Value | Threshold / Tolerance | Quality Status |
| :--- | :---: | :---: | :---: |
| **Corrupted Files** | 0 | 0 | **PASS** |
| **Truncated Bitstreams**| 0 | 0 | **PASS** |
| **Unique SHA256 Hashes**| 500 / 500 | 100% Unique | **PASS** |
| **Duplicate Images** | 0 | 0 | **PASS** |
| **Dimension Outliers** | 0 ($32 \times 32$ uniform) | 0 | **PASS** |
| **Channel Consistency** | 3 (RGB uniform) | 3 | **PASS** |
| **Total Disk Footprint**| 164.1 KB | $\le 5\text{ MB}$ | **OPTIMAL** |

### 3.3 Partitioning Plan (Seed 42)

| Dataset Partition | Total Images | Real Images (Class 0) | Synthetic Images (Class 1) | Target Use |
| :--- | :---: | :---: | :---: | :--- |
| **Train Set** | 350 (70.0%) | 175 (50.0%) | 175 (50.0%) | Model parameter optimization |
| **Validation Set** | 75 (15.0%) | 38 (50.7%) | 37 (49.3%) | Early stopping & hyperparameter tuning |
| **Test Set** | 75 (15.0%) | 37 (49.3%) | 38 (50.7%) | Unbiased hold-out generalization evaluation |

---

## 4. Key Engineering Insights

1. **Modality Separation:** The high resolution ($1920 \times 1080$, $600 \times 338$) of DFD video frames contrasts sharply with the low resolution ($32 \times 32$) of CIFAKE diffusion images. Training a single feature extractor on both would cause severe spatial distortion or catastrophic domain shift. Independent branches are scientifically required.
2. **Video-Level Aggregation:** The DFD controlled sample requires video-level evaluation rather than frame-level over-counting to ensure honest reporting.
3. **Class Parity in CIFAKE:** The perfect 50/50 class balance in CIFAKE allows direct use of standard cross-entropy loss without synthetic oversampling or artificial class weighting.
