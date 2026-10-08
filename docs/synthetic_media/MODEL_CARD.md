# CrisisGuard — Synthetic Media Detection Model Card

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Version:** 1.0.0 (Phase 6 Frozen)  
**Date:** September 2026  

---

## 1. Model Details

### 1.1 Model Overview
CrisisGuard incorporates a dual-branch synthetic media intelligence engine:
1. **Image Forensics Branch (`resnet18_cifake_forensics`):** A fine-tuned convolutional neural network (ResNet-18) trained to detect AI-generated synthetic imagery from diffusion and GAN architectures against real photographic content.
2. **Video Forensics Branch (`temporal_dfd_video_forensics`):** A temporal aggregation pipeline combining frame-level deep representation extraction with temporal mean pooling and classification to predict deepfake manipulation at the **video level**.

### 1.2 Model Dates & Status
- **Training Date:** September 27, 2026
- **Model Checkpoints:**
  - Image: `models/synthetic_media/image_model_best.pt`
  - Video: `models/synthetic_media/video_model_best.pt`
- **Model Registry:** `models/synthetic_media/model_registry.yaml`
- **Output Schema:** `schemas/media_risk_schema.json`

---

## 2. Intended Use

- **Primary Intended Use:** Automated estimation of synthetic manipulation risk ($P(\text{synthetic}) \in [0, 1]$) for multimedia assets associated with crisis incident reports in a big data pipeline.
- **Pipeline Role:** Generates upstream intermediate features (`synthetic_probability`, `synthetic_risk`) to be ingested downstream by Spark GraphX and MLlib ranking stages in subsequent phases.
- **Modality-Specific Routing:** Automatically routes image formats (`.jpg`, `.jpeg`, `.png`, `.webp`) to the image forensics branch and video formats (`.mp4`, `.avi`, `.mov`, `.mkv`) to the video forensics branch.

---

## 3. Out-of-Scope and Prohibited Uses

> [!CAUTION]
> **CRITICAL SCIENTIFIC & ETHICAL BOUNDARIES**
> 1. **IMAGE BRANCH SCOPE:**
>    - Developed on a controlled 500-image CIFAKE subset.
>    - All 500 local images originate from the upstream `DATASET/test` partition.
>    - The local split is a controlled closed-world experiment, NOT the standard official CIFAKE benchmark.
>    - Results are limited strictly to this controlled experiment.
>    - No claim of universal synthetic-image detection capability across arbitrary generators.
> 2. **VIDEO BRANCH SCOPE:**
>    - Developed on a Google DFD-derived controlled development sample.
>    - Very small cohort ($N=4$ video assets, 12 keyframes).
>    - Functions strictly as a proof-of-concept / pipeline-validation experiment.
>    - Not a statistically representative broad benchmark of video deepfake detection.
>    - No cross-modal generalization claim (DFD video models do not generalize to images).
> 3. **GENERAL ETHICAL & OPERATIONAL BOUNDARIES:**
>    - Synthetic-media risk does NOT establish the truth or falsity of an emergency incident.
>    - Synthetic-media risk does NOT establish misinformation intent.
>    - Synthetic-media risk does NOT establish malicious intent.
>    - Synthetic-media risk does NOT identify the creator or manipulator.
>    - Decision-support feature only: MUST NEVER be used autonomously to deprioritize emergency dispatch.

---

## 4. Training and Evaluation Data

### 4.1 Image Forensics Branch (CIFAKE Controlled Subset)
- **Dataset Source:** CIFAKE (Bird & Lotfi, 2024), sampled from CIFAR-10 photographic images and Stable Diffusion v1.4 synthetic images.
- **Upstream Origin:** All 500 images were drawn from the upstream `DATASET/test` partition.
- **Controlled Subset:** Phase 4 verified 500-image balanced partition (250 real, 250 synthetic).
- **Split Protocol (Leakage-Controlled Closed-World):**
  - **Train (70%):** 350 images (175 real, 175 synthetic).
  - **Validation (15%):** 75 images (37 real, 38 synthetic).
  - **Holdout Test (15%):** 75 images (38 real, 37 synthetic).
  - Deterministic random seed: `42`.
  - Zero cross-split leakage ($\text{Train} \cap \text{Val} \cap \text{Test} = \emptyset$).
  - **Benchmark Scope Limitation:** Because local training images originated from upstream `DATASET/test`, this evaluation cannot be compared directly with external models trained on the official 100,000-image training partition.

### 4.2 Video Forensics Branch (Google DFD Controlled Sample)
- **Dataset Source:** Google DeepFake Detection Dataset (DFD) — controlled development sample.
- **Controlled Subset:** Exactly 4 video assets, 12 uniform temporal keyframes.
- **Split Protocol (Video-Atomic & Actor-Disjoint):**
  - **Train:** 2 videos (`dfd_video_sample_02`, `dfd_frame_actor_real`) across actors `actor_02` and `actor_real_01`.
  - **Holdout Test:** 2 videos (`dfd_video_sample_01`, `dfd_frame_actor_fake`) across actors `actor_01` and `actor_fake_01`.
  - Zero frame leakage across splits; video-level atomic isolation.
  - Proof-of-concept / pipeline validation only; not a broad benchmark.

---

## 5. Model Architecture

```
IMAGE BRANCH (CIFAKE):
Input (3 x 64 x 64) 
    → ResNet-18 Backbone (Pretrained ImageNet-1K)
    → AdaptiveAvgPool2d (512-dim)
    → Dropout(p=0.3)
    → Linear(512 → 1)
    → Sigmoid → synthetic_probability

VIDEO BRANCH (DFD):
Input Video (K Uniform Temporal Keyframes, 3 x 112 x 112)
    → ResNet-18 Feature Extractor (Per-frame 512-dim representations)
    → Temporal Mean Pooling (Aggregate across K keyframes)
    → L2 Feature Normalization
    → Linear(512 → 128) → ReLU → Dropout(p=0.2)
    → Linear(128 → 1)
    → Sigmoid → synthetic_probability (VIDEO-LEVEL)
```

---

## 6. Evaluation Metrics

### 6.1 Image Forensics Performance (Test Set $N=75$)
- **Accuracy:** 93.33% (70 / 75 correct)
- **Precision:** 0.9444 (34 / 36 positive calls true synthetic)
- **Recall:** 0.9189 (34 / 37 true synthetic identified)
- **F1-Score:** 0.9315
- **ROC-AUC:** 0.9815
- **PR-AUC:** 0.9823
- **Brier Score:** 0.0569 (Strong probability sharpness)
- **Expected Calibration Error (ECE):** 0.4686 (Baseline uncalibrated sigmoid)
- **Confusion Matrix:** $\text{TN}=36, \text{FP}=2, \text{FN}=3, \text{TP}=34$

> **Phase 10 Probability Calibration (Platt Scaling):**
> - **Method:** Logistic calibration fitted on disjoint validation split ($N=75$, seed 42) with parameters $a=0.6062, b=0.4443$.
> - **Holdout Test ECE (5-bin):** Reduced from **0.4686** to **0.4061** (-13.3% relative improvement).
> - **Holdout Test ECE (10-bin):** Reduced from **0.4827** to **0.4411** (-8.6% relative improvement).
> - **Holdout Test ROC-AUC:** 0.9815 (Preserved).
> - **Holdout Test PR-AUC:** 0.9823 (Preserved).
> - **Artifact:** `models/synthetic_media/calibration/platt_calibrator_resnet18.joblib`

### 6.2 Video Forensics Performance (Test Set $N=2$ Videos)
- **Evaluation Unit:** Strict **VIDEO-LEVEL** prediction (not independent frame scoring).
- **Test Results:**
  - `dfd_video_sample_01` (Label: 1/Fake) $\rightarrow \hat{p} = 0.4176$
  - `dfd_frame_actor_fake` (Label: 1/Fake) $\rightarrow \hat{p} = 0.4162$
- **Calibration Status:** Marked `UNCALIBRATED` in metadata due to statistical invalidity of computing calibration curves on $N=2$ test samples.

---

## 7. Explainability & Interpretability

- **Method:** Gradient-weighted Class Activation Mapping (Grad-CAM) targeting the final residual block (`layer4`).
- **Observations:**
  - **True Synthetic:** Model activates strongly on high-frequency boundary discrepancies, background blending gradients, and anomalous planar textures typical of latent diffusion upsampling.
  - **True Real:** Model diffuses attention naturally across structural biological features, organic lighting transitions, and coherent edges.
  - **False Positives:** Ringing artifacts from aggressive JPEG quantization trigger false localized activations.
  - **False Negatives:** Ultra-smooth, high-entropy diffusion patches mimic genuine low-detail camera captures.
- **Visual Artifacts Location:** `outputs/synthetic_media/explainability/`

---

## 8. Limitations & Known Failure Modes

1. **Resolution Bounds:** The image model was trained on $32 \times 32$ upscaled to $64 \times 64$. Direct application to high-megapixel DSLR emergency imagery without patch-based tiling may experience domain degradation.
2. **Compression Sensitivity:** Heavy lossy compression (JPEG quality $< 30$, low-bitrate H.264 video compression) induces artifact patterns that can cause false synthetic predictions.
3. **Small Video Cohort:** The DFD cohort is a controlled development sample ($N=4$). Model weights are conservative and uncalibrated for production deployment outside controlled benchmarking.
4. **Adversarial Perturbations:** Neither branch incorporates explicit adversarial training against adversarial noise attacks or anti-forensic post-processing filters.

---

## 9. Provenance & Reproducibility

- **Random Seed:** `42` (fixed across Python `random`, NumPy `np.random`, and PyTorch `torch.manual_seed`).
- **Deterministic Execution:** PyTorch deterministic algorithms enabled (`torch.use_deterministic_algorithms(True, warn_only=True)`).
- **Execution Platform:** Ubuntu 24.04 LTS (WSL2), Python 3.12.3, PyTorch 2.14.0+cpu, NumPy 1.26.4.
- **Raw Data Immutability:** All input files in `data/raw/` remained strictly read-only and unaltered throughout execution.
