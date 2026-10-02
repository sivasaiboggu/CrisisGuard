# CrisisGuard — CIFAKE Subset Provenance & Benchmark Scope Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 6 Final Hardening & Freeze  
**Audit Status:** FINAL VERIFIED TRUTH  
**Date:** September 2026  

---

## 1. Scientific Experiment Classification

> [!IMPORTANT]
> **FORMAL SCIENTIFIC DESIGNATION**
> The experiment conducted in CrisisGuard Phase 6 is a:
>
> **CONTROLLED CLOSED-WORLD CIFAKE SUBSET EXPERIMENT**
>
> It is **NOT** the standard official CIFAKE benchmark.

All local training, validation, and testing images originate from the upstream CIFAKE `DATASET/test` partition. Therefore, the local holdout test set is **NOT** an untouched copy of the official CIFAKE test benchmark, and this model was **NOT** trained on the official CIFAKE training partition.

---

## 2. Upstream Dataset Provenance & Attribution

- **Dataset Title:** CIFAKE: Real and AI-Generated Synthetic Images
- **Authors:** Jordan J. Bird and Ahmad Lotfi (2024), Nottingham Trent University
- **Reference Publication:** Bird, J.J. and Lotfi, A., 2024. "CIFAKE: Image Classification and Explainable Identification of AI-Generated Synthetic Images." *IEEE Access*.
- **Official Repository:** `https://github.com/jordan-bird/CIFAKE-Real-and-AI-Generated-Synthetic-Images`
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Official Upstream Structure:**
  - `DATASET/train/REAL` (50,000 CIFAR-10 photographic images)
  - `DATASET/train/FAKE` (50,000 Stable Diffusion v1.4 synthetic images)
  - `DATASET/test/REAL` (10,000 CIFAR-10 photographic images)
  - `DATASET/test/FAKE` (10,000 Stable Diffusion v1.4 synthetic images)
- **Local Acquisition Source:** Directly sampled from `DATASET/test/REAL` and `DATASET/test/FAKE` via `scripts/acquisition/acquire_cifake_eval.py`.

---

## 3. Verified Local File Facts (Zero Fabrication)

The local cohort was audited by direct file inspection:

| Measurement Dimension | Exact Verified Count | Audit Evidence | Status |
|---|---|---|---|
| Total Local Images | **500 images** | `len(os.listdir(real)) + len(os.listdir(fake))` | **VERIFIED** |
| Real / Pristine Images | **250 images** | Stored in `data/raw/synthetic_media_eval/real/` | **VERIFIED** |
| Synthetic Images | **250 images** | Stored in `data/raw/synthetic_media_eval/fake/` | **VERIFIED** |
| Image Dimensions | **$32 \times 32 \times 3$** | Verified via PIL header inspection (100% RGB) | **VERIFIED** |
| File Format | **JPEG** | 100% valid JPEG encoding, 0 corruptions | **VERIFIED** |
| Unique SHA-256 Hashes | **500 unique hashes** | Exactly 500 distinct hashes; 0 duplicates | **VERIFIED** |
| Upstream Origin | **`DATASET/test` (100%)** | 0 images from upstream `DATASET/train` | **VERIFIED** |

---

## 4. Local Split Analysis & Leakage Verification

The 500 local images were partitioned into a closed-world 70/15/15 split using deterministic seed `42` (`data/features/synthetic_media/cifake_partitions.parquet`):

| Partition | Total Images | Real Images (Label=0) | Synthetic Images (Label=1) | Ratio |
|---|---|---|---|---|
| **TRAIN** | 350 | 175 | 175 | 70.0% |
| **VALIDATION** | 75 | 37 | 38 | 15.0% |
| **TEST** | 75 | 38 | 37 | 15.0% |
| **TOTAL** | **500** | **250** | **250** | **100.0%** |

### Leakage Verification by SHA-256 Checksums
- $\text{Hashes}_{\text{Train}} \cap \text{Hashes}_{\text{Val}} = \emptyset$ (0 overlapping hashes)
- $\text{Hashes}_{\text{Train}} \cap \text{Hashes}_{\text{Test}} = \emptyset$ (0 overlapping hashes)
- $\text{Hashes}_{\text{Val}} \cap \text{Hashes}_{\text{Test}} = \emptyset$ (0 overlapping hashes)
- **Result:** **ZERO DATA LEAKAGE** across local partitions.

---

## 5. Answers to Mandatory Provenance Questions

1. **Were the 500 images selected from the official dataset?**  
   **YES.** All 500 images were downloaded from the official Jordan Bird CIFAKE repository on GitHub.
2. **Which were selected from the official training partition?**  
   **ZERO (0 images).** None of the 500 images were drawn from the upstream `DATASET/train` partition.
3. **Which were selected from the official test partition?**  
   **ALL 500 IMAGES (100%).** Exactly 250 real and 250 synthetic images were sampled from upstream `DATASET/test`.
4. **Were validation images derived from the training partition?**  
   **NO.** The 75 validation images were sampled from the local 500-image cohort (originating from upstream `DATASET/test`).
5. **Were any official test images used for training?**  
   **YES.** All 350 images in the local training set were drawn from the 500-image cohort that originated in upstream `DATASET/test`.
6. **Are local train/validation/test sets disjoint?**  
   **YES.** The local subsets are 100% mutually disjoint with zero shared files or hashes.
7. **Are hashes unique?**  
   **YES.** Exactly 500 unique SHA-256 hashes exist across all 500 images.
8. **Is the current 350/75/75 split scientifically valid?**  
   **YES, AS A CONTROLLED CLOSED-WORLD SUBSET EXPERIMENT.** It is internally valid and leakage-free for evaluating feature representations and pipeline integration. However, it cannot be claimed as an official CIFAKE benchmark result, because upstream test-partition images were used in local training.

---

## 6. Audit Verdict

- **CIFAKE Provenance:** **PASS** (100% traceable, verified, zero unidentified files).
- **CIFAKE Split Integrity:** **PASS** (100% mutually disjoint, zero internal leakage).
- **CIFAKE Benchmark Scope:** **PASS — DOCUMENTED AS CONTROLLED CLOSED-WORLD SUBSET EXPERIMENT** (Zero overclaiming of standard benchmark comparability).
