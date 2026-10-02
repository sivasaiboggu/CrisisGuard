# CrisisGuard — Google DFD Controlled Sample Leakage & Split Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Audit Phase:** Phase 6 Final Hardening Audit  
**Date:** September 2026  

---

## 1. Scientific Status Designation

The Google DFD local data cohort is officially designated as a:

> **CONTROLLED VIDEO-FORENSICS PROOF-OF-CONCEPT / PIPELINE-VALIDATION EXPERIMENT**

It is **NOT** a statistically representative benchmark of general video deepfake detection. It is designed to validate the end-to-end architectural capability of ingesting video, sampling keyframes deterministically, extracting temporal representations, performing video-level aggregation, and emitting schema-compliant risk records into the big data pipeline.

---

## 2. Dataset Cohort Inventory

The local controlled sample consists of exactly 4 multimedia assets and 12 extracted keyframes:

| Content ID | File Path | Media Type | Total Keyframes | Ground Truth Label | Actor / Source Identity | Assigned Split |
|---|---|---|---|---|---|---|
| `dfd_dfd_video_sample_02` | `data/raw/deepfake_dfd/dfd_video_sample_02.gif` | Video / GIF | 5 | 1 (Synthetic) | `actor_02` | **TRAIN** |
| `dfd_dfd_frame_actor_orig` | `data/raw/deepfake_dfd/dfd_frame_actor_real.png` | Image Reference | 1 | 0 (Real) | `actor_real_01` | **TRAIN** |
| `dfd_dfd_video_sample_01` | `data/raw/deepfake_dfd/dfd_video_sample_01.gif` | Video / GIF | 5 | 1 (Synthetic) | `actor_01` | **TEST** |
| `dfd_dfd_frame_actor_fake` | `data/raw/deepfake_dfd/dfd_frame_actor_fake.png` | Image Reference | 1 | 1 (Synthetic) | `actor_fake_01` | **TEST** |

- **Total Video Assets:** 4
- **Training Assets:** 2 (1 Real, 1 Synthetic) — 6 Keyframes total
- **Validation Assets:** 0 (Sample size cannot support a distinct validation partition without training starvation)
- **Holdout Test Assets:** 2 (2 Synthetic) — 6 Keyframes total
- **Evaluation Unit:** Strict **VIDEO LEVEL** (aggregated temporal representation per asset)

---

## 3. Leakage Control Verification

### 3.1 Video-Level Atomicity (Zero Cross-Split Asset Leakage)
- $\text{Assets}_{\text{Train}} = \{\text{dfd\_video\_sample\_02}, \text{dfd\_frame\_actor\_real}\}$
- $\text{Assets}_{\text{Test}} = \{\text{dfd\_video\_sample\_01}, \text{dfd\_frame\_actor\_fake}\}$
- $\text{Assets}_{\text{Train}} \cap \text{Assets}_{\text{Test}} = \emptyset$
- **Result:** **PASS** (Zero asset overlap across splits).

### 3.2 Frame-Level Leakage Prevention (Zero Intra-Video Frame Splitting)
- All 5 frames from `dfd_video_sample_02` belong strictly to **TRAIN**.
- The 1 frame from `dfd_frame_actor_real` belongs strictly to **TRAIN**.
- All 5 frames from `dfd_video_sample_01` belong strictly to **TEST**.
- The 1 frame from `dfd_frame_actor_fake` belongs strictly to **TEST**.
- Zero frames from any training asset were evaluated in testing.
- **Result:** **PASS** (Zero frame leakage).

### 3.3 Actor / Source Biometric Disjointness
- $\text{Actors}_{\text{Train}} = \{\text{actor\_02}, \text{actor\_real\_01}\}$
- $\text{Actors}_{\text{Test}} = \{\text{actor\_01}, \text{actor\_fake\_01}\}$
- $\text{Actors}_{\text{Train}} \cap \text{Actors}_{\text{Test}} = \emptyset$
- **Result:** **PASS** (Complete actor biometric disjointness).

---

## 4. Calibration & Statistical Status

- **Holdout Test Size:** $N=2$ video assets.
- **Statistical Calibration Validity:** Statistical probability calibration (e.g. Platt scaling, isotonic regression, Expected Calibration Error, Brier score decomposition) requires large sample sizes ($N \gg 50$) to produce statistically meaningful confidence intervals. Computing calibration curves on $N=2$ test instances is mathematically degenerate.
- **Recorded Status:** Formally documented as:
  $$\text{calibration\_status: UNCALIBRATED}$$
  $$\text{quality\_status: VALID}$$
- Zero fabrication of calibration metrics.

---

## 5. Audit Verdict

| Leakage Criterion | Target Requirement | Measured Status | Verification |
|---|---|---|---|
| Video Split Independence | Same video never across splits | Fully Disjoint | **PASS** |
| Frame Non-Leakage | Frames from same video in same split | 100% Video-Atomic | **PASS** |
| Actor Identity Disjointness | No actor overlap between splits | 100% Disjoint | **PASS** |
| Evaluation Unit | Strict video-level prediction | Video-Level Aggregation | **PASS** |
| Calibration Transparency | No fabricated calibration claims | Labeled UNCALIBRATED | **PASS** |

**OVERALL DFD AUDIT VERDICT: PASS**
