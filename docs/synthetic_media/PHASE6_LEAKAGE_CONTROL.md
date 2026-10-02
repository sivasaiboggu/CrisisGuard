# CrisisGuard: Phase 6 Machine Learning Leakage Control Policy

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 6 — Synthetic Media Detection & Unified Media-Risk Engine  

---

## 1. Scientific Imperative & Threat Model

In machine learning pipelines applied to multimedia crisis intelligence, **data leakage** corrupts empirical validation, resulting in over-optimistic performance estimates that fail catastrophically during live deployment.

Data leakage occurs through multiple subtle vectors:
1. **Temporal/Frame Leakage:** Correlated adjacent video frames from the same video sequence placed simultaneously into train and test sets.
2. **Identity/Actor Leakage:** Facial biometric features of the same actor present in training and evaluation partitions, causing the model to memorize facial geometry rather than manipulation artifacts.
3. **Pre-processing / Normalization Leakage:** Fitting scalers, feature encoders, or image normalization statistics ($z$-score $\mu, \sigma$) across the entire dataset before partitioning.
4. **Cross-Modality Conflation:** Mixing video frames and still photographic images into an unprincipled hybrid pool, falsely claiming cross-modal transferability.

CrisisGuard enforces strict algorithmic barriers against all four leakage vectors.

---

## 2. Branch A: Google DFD Video Leakage Control

### 2.1 Video-Atomic Split Enforcement
Individual frames are **never** treated as independent sampling units during dataset partitioning. The atomic unit of splitting is the **video file / media asset**:

$$\text{Video } V_i = \{f_{i,1}, f_{i,2}, \dots, f_{i,T}\} \implies \forall f \in V_i, \quad \text{Split}(f) \equiv \text{Split}(V_i)$$

Under no circumstances is $f_{i,j}$ assigned to Train while $f_{i,k}$ is assigned to Validation or Test.

### 2.2 Actor & Media Asset Allocation

In the Google DFD-derived controlled sample, the media assets are partitioned strictly by media asset and actor identifier:

| Media ID | Content Identifier | Modality | Ground Truth | Assigned Split | Actor ID / Pair |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `dfd_frame_actor_orig` | `dfd_dfd_frame_actor_orig` | Image/PNG | 0 (Pristine) | **TRAIN** | `actor_dfd_071` |
| `dfd_video_sample_02` | `dfd_dfd_video_sample_02` | Video/GIF (50 frames) | 1 (Manipulated) | **VALIDATION** | `actor_dfd_pair_02` |
| `dfd_video_sample_01` | `dfd_dfd_video_sample_01` | Video/GIF (100 frames)| 1 (Manipulated) | **TEST** | `actor_dfd_pair_01` |
| `dfd_frame_actor_fake` | `dfd_dfd_frame_actor_fake` | Image/PNG | 1 (Manipulated) | **TEST** | `actor_dfd_054` |

*Actor Disjointness:* The actors in the test set (`actor_dfd_pair_01`, `actor_dfd_054`) share zero overlap with the actor in the validation set (`actor_dfd_pair_02`) or the training set (`actor_dfd_071`).

### 2.3 Video-Level Inference & Evaluation Protocol
The primary evaluation unit is the **complete video sequence**. Frame-level prediction probabilities $p(f_{i,j})$ are aggregated temporally via mean/max pooling to produce a single video prediction:

$$P_{\text{video}}(V_i) = \frac{1}{T} \sum_{j=1}^T P_{\text{frame}}(f_{i,j})$$

Metrics (Accuracy, Precision, Recall, F1, ROC-AUC) are computed strictly across video instances $V_i$, preventing artificial inflation from correlated frames.

---

## 3. Branch B: CIFAKE Image Leakage Control

### 3.1 Deterministic Stratified Partitioning
The CIFAKE benchmark dataset (500 images: 250 pristine photographic from CIFAR-10, 250 AI-generated from Stable Diffusion v1.4) is partitioned into mutually exclusive subsets:
- **Train Split (70%):** 350 images (175 Real, 175 Synthetic)
- **Validation Split (15%):** 75 images (38 Real, 37 Synthetic)
- **Test Split (15%):** 75 images (37 Real, 38 Synthetic)

Partitioning is conducted deterministically using `StratifiedShuffleSplit` with fixed random seed `42` applied to SHA256 hashes.

### 3.2 Deduplication Verification
All 500 images were evaluated via cryptographically secure SHA256 checksums (`validate_phase6_inputs.py`). Exactly 500 unique hashes were verified:

$$\text{Count}(\text{Unique Hashes}) = 500 = \text{Count}(\text{Records})$$

Zero perceptual duplicates or duplicate hashes cross split boundaries:

$$\text{Hashes}(\text{Train}) \cap \text{Hashes}(\text{Val}) = \emptyset, \quad \text{Hashes}(\text{Train}) \cap \text{Hashes}(\text{Test}) = \emptyset, \quad \text{Hashes}(\text{Val}) \cap \text{Hashes}(\text{Test}) = \emptyset$$

### 3.3 Normalization Isolation
All image transformations (resizing to $32 \times 32 \times 3$, tensor scaling to $[0, 1]$, and standardization via ImageNet parameters $\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$) utilize fixed external baseline statistics or are fitted exclusively on the training partition. No test set statistics inform training transformations.

---

## 4. Cross-Modality Boundary Enforcement

To respect scientific rigor:
- **Zero Cross-Training:** The image classifier is never trained on DFD video frames, and the video temporal classifier is never evaluated on CIFAKE images.
- **Model Decoupling:** Branch A and Branch B maintain dedicated model architectures, dedicated checkpoints, and independent metric registries.
- **Post-Inference Unification:** Integration between video forensics and image forensics occurs solely at the downstream data schema boundary (`schemas/media_risk_schema.json`).
