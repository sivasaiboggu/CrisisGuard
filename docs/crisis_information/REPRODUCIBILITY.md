# CrisisGuard — Phase 7: Reproducibility & Environment Audit
**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 7 — Crisis Information Intelligence Engine  
**Date:** September 2026  
**Status:** REPRODUCIBILITY CERTIFIED  

---

## 1. Environment & Software Stack Specification

| Component | Specified Version | Runtime Environment | Provenance / Verification |
| :--- | :--- | :--- | :--- |
| **Operating System** | Ubuntu 24.04.1 LTS | WSL2 on Windows 11 Host | Linux 6.6.x Kernel |
| **Python Interpreter**| 3.12.3 (64-bit) | System CPython | GCC 13.3.0 |
| **PyTorch** | 2.14.0+cpu | CPU-only | PyTorch Foundation Distribution |
| **Transformers** | 5.17.0 | HuggingFace Hub | Tokenizers 0.23.2, Safetensors 0.8.0 |
| **Scikit-Learn** | 1.5.2 | ThreadpoolCTL 3.7.0 | Verified L-BFGS & DummyClassifiers |
| **Pandas** | 2.1.4 | Debian package | Fast Parquet engine via PyArrow 25.0.1 |
| **NumPy** | 1.26.4 | C-accelerated BLAS | Deterministic matrix operations |

---

## 2. Global Determinism & Random Seed Policy

All stochastic procedures throughout Phase 7 strictly set:
```python
RANDOM_SEED = 42
np.random.seed(42)
torch.manual_seed(42)
```
- **TF-IDF Vectorization:** Sublinear TF scaling with deterministic vocabulary sorting.
- **Logistic Regression:** Scikit-Learn `random_state=42`, solver `lbfgs`.
- **DistilBERT Fine-Tuning:** PyTorch random seed initialized to 42, deterministic DataLoader batch iteration.
- **Baseline Prior Sampling:** Scikit-Learn `DummyClassifier(strategy='stratified', random_state=42)`.

---

## 3. Dataset Integrity & Partition Lineage

| Dataset | Local Processed Parquet | Record Count | Official Splits | Partition Disjointness |
| :--- | :--- | :---: | :---: | :---: |
| **HumAID** | `data/processed/humaid/humaid_records.parquet` | 76,484 | Train (53,531), Dev (7,793), Test (15,160) | Verified: 0 ID overlap across splits |
| **CrisisMMD** | `data/processed/crisismmd/crisismmd_records.parquet`| 8,079 | Train (6,126), Dev (998), Test (955) | Verified: 0 ID overlap across splits |
| **CrisisLex** | `data/processed/crisislex/crisislex_records.parquet`| 88,015 | T26 (27,933), T6 (60,082) across 32 events | Verified: 0 ID overlap across events |

---

## 4. Model Artifact Checkpoints & Output Schema

All generated artifacts are persisted in designated versioned directories outside the data folders:
- **HumAID Baseline:** `models/crisis_information/humaid/humaid_baseline_model.joblib`
- **CrisisMMD Baseline:** `models/crisis_information/crisismmd/crisismmd_baseline_logistic.joblib`
- **CrisisMMD Vectorizer:** `models/crisis_information/crisismmd/crisismmd_tfidf_vectorizer.joblib`
- **CrisisMMD Transformer:** `models/crisis_information/crisismmd/transformer_humanitarian/`
- **Model Registry:** `models/crisis_information/model_registry.yaml`
- **Contract Schema:** `schemas/crisis_intelligence_schema.json`

### Feature Output Layer:
- `data/features/crisis_information/humaid_predictions.parquet`
- `data/features/crisis_information/crisismmd_predictions.parquet`
- `data/features/crisis_information/crisislex_features.parquet`
- `data/features/crisis_information/unified_crisis_intelligence.parquet`
