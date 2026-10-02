# CrisisGuard: Phase 6 Model Selection & Architecture Justification

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 6 — Synthetic Media Detection & Unified Media-Risk Engine  

---

## 1. Architectural Philosophy & Constraints

Phase 6 implements a dual-branch forensics architecture:
1. **Branch A (Video Forensics):** Designed for temporal video sequences (Google DFD-derived sample).
2. **Branch B (Image Forensics):** Designed for individual still photographs (CIFAKE benchmark).

Because the operational context of CrisisGuard involves emergency prioritization on a resource-constrained workstation (16 GB RAM, 7.4 GiB WSL allocation, CPU execution), model selection must balance representational capacity against computational efficiency, over-fitting risks on small cohorts, and strict non-leakage constraints.

---

## 2. Branch B: Image Forensics Candidate Evaluation

| Architecture Family | Candidate Backbone | Parameter Count | Computational Footprint (FLOPs) | Strengths for Synthetic Media | Limitations for CIFAKE | Selected? |
| :--- | :--- | :---: | :---: | :--- | :--- | :---: |
| **ResNet** | **ResNet-18** | **11.2M** | **1.8 GFLOPs** | Residual skips preserve high-frequency artifacts (checkerboard patterns, boundary smearing) introduced by latent diffusion decoders. Well-conditioned gradients on small datasets ($N=500$). | Fixed receptive field receptive to local artifact cues. | **SELECTED (Primary Backbone)** |
| **EfficientNet** | EfficientNet-B0 | 5.3M | 0.39 GFLOPs | Highly compact compound scaling; low parameter count reduces overfitting. | Depthwise separable convolutions can smooth subtle pixel-level high-frequency Fourier artifacts. | Candidate / Baseline |
| **ConvNeXt** | ConvNeXt-Tiny | 28.6M | 4.5 GFLOPs | Modern 7x7 depthwise convolutions; transformer-like performance in pure CNN. | Overparameterized for $N=500$ sample; high risk of empirical overfitting without massive pretraining. | Rejected (Overfitting Risk) |
| **Vision Transformer (ViT)** | ViT-B/16 | 86.6M | 17.6 GFLOPs | Global self-attention across image patches. | Severe data hunger; requires hundreds of thousands of images; quadratic attention computational cost. | Rejected (Incompatible with $N=500$) |

### Justification for ResNet-18 (Image Branch):
- **Diffusion Artifact Sensitivity:** Generative models like Stable Diffusion v1.4 introduce micro-structural frequency artifacts in the spatial domain during VAE latent decoding. Standard convolutional kernels in ResNet-18 directly capture these spatial discontinuities without patch-averaging.
- **Sample Size Regularization:** With 500 images (350 train, 75 val, 75 test), ResNet-18 with transfer learning (ImageNet pretrained weights, frozen initial residual stages, fine-tuned high-level stages, and dropout $p=0.3$) provides optimal capacity without catastrophic overfitting.
- **CPU Inference Efficiency:** ResNet-18 processes a batch of 32 images in $< 20\text{ ms}$ on the AMD Ryzen 7 7445HS CPU, satisfying stream readiness requirements.

---

## 3. Branch A: Video Forensics Candidate Evaluation

Because the local DFD cohort is a controlled development sample (2 video sequences + keyframe pairs), training a monolithic 3D Convolutional Network (e.g. I3D, SlowFast, VideoMAE) with tens of millions of spatio-temporal parameters would violate scientific integrity, as such models would immediately memorize the single video instances.

| Architecture Paradigm | Description | Parameters | Feasibility on Controlled Sample | Selected? |
| :--- | :--- | :---: | :---: | :---: |
| **Monolithic 3D CNN (I3D / SlowFast)** | Spatio-temporal 3D kernels over raw video volumes | 25M–50M | **Statistically Unsound:** Immediate memorization of 2 video instances. Severe overfitting. | **REJECTED** |
| **End-to-End CNN-LSTM / GRU** | 2D CNN feature extractor followed by recurrent sequence model | 15M–20M | **Excessive Parameters:** Overfits temporal sequence on tiny video sample. | **REJECTED** |
| **Decoupled Frame Extractor + Temporal Pooling** | Frame-level feature extractor $\rightarrow$ Frame representations $\rightarrow$ Temporal aggregation (Mean/Max) $\rightarrow$ Video classifier | **11.2M (Transfer Learning)** | **Scientifically Principled:** Employs frozen spatial feature extractor; aggregates frame representations temporally; evaluates at video level. | **SELECTED (Primary Backbone)** |

### Justification for Decoupled Temporal Pooling (Video Branch):
- **Video-Atomic Design:** Frame representations $z_{i,t} = f_\theta(\text{frame}_{i,t}) \in \mathbb{R}^{512}$ are extracted for each uniformly sampled frame $t \in \{1, \dots, T\}$.
- **Temporal Invariance:** Video representation is formed via temporal average pooling:
  $$\mathbf{z}_i = \frac{1}{T} \sum_{t=1}^T z_{i,t}$$
- **Video-Level Classification:** A linear classification head maps $\mathbf{z}_i \mapsto \hat{y}_i \in [0, 1]$, producing a single probability for the entire video instance.
- **Anti-Overfitting:** Feature extraction utilizes the pretrained backbone; only the classification head and temporal aggregation operate during training, preventing spurious correlation memorization while maintaining temporal integrity.

---

## 4. Hyperparameter & Optimization Rationale

- **Optimizer:** AdamW ($\beta_1=0.9, \beta_2=0.999$, weight decay $\lambda = 1\times 10^{-4}$) to prevent weight explosion.
- **Learning Rate:** $\eta = 1\times 10^{-3}$ for classification heads; $\eta = 1\times 10^{-4}$ for fine-tuned backbone stages.
- **Batch Size:** 32 (Image), 4 (Video sequences) to conform to memory safety boundaries.
- **Loss Function:** Binary Cross-Entropy with Logits (`BCEWithLogitsLoss`), numerically stable against saturation.
- **Early Stopping:** Patience of 5 epochs monitoring validation loss to capture the optimal checkpoint.
