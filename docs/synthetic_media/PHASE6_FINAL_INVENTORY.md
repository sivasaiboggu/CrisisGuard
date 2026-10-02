# CrisisGuard — Phase 6 Complete Final Inventory

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 6 Final Hardening & Freeze  
**Date:** September 2026  

---

## 1. Inventory Summary

This catalog documents all verified artifacts, scripts, models, schemas, configurations, prediction datasets, and documentation comprising CrisisGuard Phase 6.

---

## 2. Scripts Inventory

### 2.1 Forensics & Preprocessing Scripts (`scripts/synthetic_media/`)
| Script Name | Purpose | Modality | Output Artifacts |
|---|---|---|---|
| `validate_phase6_inputs.py` | Validates raw datasets, file integrity, keyframes, and SHA256 hashes prior to model training | Multimodal | Terminal validation report |
| `preprocess_video.py` | Extracts uniform temporal keyframes from DFD videos, generates 512-dim ResNet-18 representations, and temporal mean pooling | Video | `dfd_video_features.parquet`, `dfd_frame_features.parquet`, `video_tensors.pt` |
| `preprocess_images.py` | Loads CIFAKE images, applies normalized tensor transforms ($64 \times 64 \times 3$), partitions 70/15/15 | Image | `cifake_partitions.parquet`, `cifake_tensors.pt` |
| `train_image_model.py` | Trains fine-tuned `ResNet18BinaryClassifier` on 350 train images with AdamW and cosine annealing; early stops on val loss | Image | `image_model_best.pt`, `image_training_history.json`, `image_predictions.parquet` |
| `train_video_model.py` | Trains `VideoTemporalClassifier` on pooled video representations; evaluates at strict video level | Video | `video_model_best.pt`, `video_training_history.json`, `video_predictions.parquet` |
| `inspect_errors.py` | Forensic failure analysis inspecting false positives and false negatives | Multimodal | Diagnostic inspection logs |
| `generate_explainability.py` | Generates Grad-CAM attention heatmaps for model behavior analysis | Multimodal | Heatmaps in `outputs/synthetic_media/explainability/` |
| `infer_media.py` | Unified inference engine with automated MIME/extension routing, schema validation, and unified dataset assembly | Multimodal | `unified_media_risk.parquet` |

### 2.2 Validation Scripts (`scripts/validation/`)
| Script Name | Scope | Key Validations |
|---|---|---|
| `validate_phase6_models.py` | Phase 6 Comprehensive Check | Datasets, non-leakage, checkpoints, predictions, schema contract, provenance, raw data immutability |
| `validate_phase6_final.py` | Master Hardening & Freeze Audit | 21-point verification covering provenance, benchmark scope, uncalibrated status, quality separation, immutability |

---

## 3. Configuration & Schema Contracts

| File Path | Format | Description |
|---|---|---|
| `config/synthetic_media.yaml` | YAML | Deterministic seed (42), architectures, batch sizes, learning rates, epochs, paths, risk thresholds |
| `schemas/media_risk_schema.json` | JSON Schema (Draft 2020-12) | Standardized media-risk contract defining `model_score`, `synthetic_probability`, `synthetic_risk`, `calibration_status`, `quality_status`, `provenance` |

---

## 4. Models & Checkpoints (`models/synthetic_media/`)

| File Name | Size | Architecture | Checkpoint Contents |
|---|---|---|---|
| `image_model_best.pt` | 44.8 MB | ResNet-18 (`IMAGENET1K_V1` + Dropout(0.3) + Linear(512, 1)) | Model state dict |
| `image_training_history.json` | 1.9 KB | Metrics Record | Loss history, test metrics (Acc: 93.33%, AUC: 0.9815, Brier: 0.0569) |
| `video_model_best.pt` | 134 KB | `VideoTemporalClassifier` (Linear(512, 128) + ReLU + Dropout(0.2) + Linear(128, 1)) | Model state dict |
| `video_training_history.json` | 348 B | Metrics Record | Video-level test accuracy, evaluation unit, sample size |
| `model_registry.yaml` | 4.8 KB | Governance Catalog | Versions, seeds, splits, metrics, limitations, calibration status |

---

## 5. Feature & Prediction Datasets

### 5.1 Image & Unified Features (`data/features/synthetic_media/`)
| File Name | Rows | Format | Description |
|---|---|---|---|
| `cifake_partitions.parquet` | 500 | Parquet | Partition metadata: 350 Train, 75 Val, 75 Test with SHA256 hashes |
| `cifake_tensors.pt` | — | PyTorch Tensor | Preprocessed $64 \times 64 \times 3$ image tensors |
| `image_predictions.parquet` | 75 | Parquet | Holdout test predictions conforming to media-risk schema |
| `video_predictions.parquet` | 2 | Parquet | Video-level test predictions conforming to media-risk schema |
| `unified_media_risk.parquet` | 77 | Parquet | Unified dataset merging image (75) and video (2) predictions with full lineage |

### 5.2 Video Features (`data/features/deepfake_dfd/`)
| File Name | Rows | Format | Description |
|---|---|---|---|
| `dfd_video_features.parquet` | 4 | Parquet | Aggregated 512-dim video-level feature representations |
| `dfd_frame_features.parquet` | 12 | Parquet | Frame-level 512-dim ResNet-18 representations across 12 keyframes |
| `video_tensors.pt` | — | PyTorch Tensor | Preprocessed $224 \times 224 \times 3$ keyframe tensors |

---

## 6. Documentation Catalog (`docs/synthetic_media/`)

| Document Name | Focus Area | Key Findings / Design |
|---|---|---|
| `PHASE6_ENVIRONMENT.md` | Hardware & Dependencies | Ubuntu 24.04, Python 3.12.3, PyTorch 2.14.0+cpu, NumPy 1.26.4, deterministic CPU execution |
| `PHASE6_DATA_PROFILE.md` | Data Demographics | DFD video and keyframe counts; CIFAKE 500-image resolution, channel, and format analysis |
| `PHASE6_LEAKAGE_CONTROL.md` | Splitting Protocols | Video-atomic frame partitioning; actor identity disjointness; stratified image splits |
| `MODEL_SELECTION.md` | Architecture Justification | ResNet-18 transfer learning vs ConvNeXt/EfficientNet; temporal pooling vs 3D-CNN |
| `CIFAKE_SUBSET_PROVENANCE.md` | Provenance Truth | Rigorous analysis proving all 500 images originate from upstream `DATASET/test` |
| `DFD_LEAKAGE_AUDIT.md` | Video Leakage Audit | Verification of zero video, frame, or actor overlap across DFD train and test partitions |
| `ERROR_ANALYSIS.md` | Error Decomposition | Observation-based failure analysis of false positives and false negatives |
| `MODEL_CARD.md` | Operational & Ethical Scope | Intended use, out-of-scope boundaries, lack of malicious intent attribution, decision-support role |
| `PHASE6_FINAL_REPORT.md` | Master Academic Report | Comprehensive report structured into Parts A through E |
| `PHASE6_FINAL_INVENTORY.md` | Master Asset Catalog | Complete inventory of all Phase 6 assets (this document) |

---

## 7. Explainability Artifacts (`outputs/synthetic_media/explainability/`)

| File Name | Target Entity | Analysis Role |
|---|---|---|
| `explainability_summary.json` | Catalog | Metadata catalog with `MODEL_BEHAVIOR_ANALYSIS` audit designation |
| `gradcam_true_positive_synthetic.png` | Synthetic Image | Gradient sensitivity on synthetic blending contours |
| `gradcam_true_negative_real.png` | Real Image | Diffuse gradient distribution across natural photographic structures |
| `gradcam_false_positive.png` | Real Image | Localized gradient activation on JPEG compression ringing |
| `gradcam_false_negative.png` | Synthetic Image | Diffuse gradient activation on smooth latent diffusion textures |
| `gradcam_dfd_video_frame.png` | Deepfake Video Keyframe | Facial boundary activation on deepfake video frame |
