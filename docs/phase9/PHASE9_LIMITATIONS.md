# CrisisGuard — Phase 9 Limitations & Epistemic Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** 9 — End-to-End Intelligence Integration & Analytical Validation  
**Date:** September 2026  
**Status:** PASS — FULL TRANSPARENCY ENFORCED  

---

## 1. Introduction & Epistemic Stance

In accordance with rigorous scientific practice and the explicit engineering principles of CSE412, this document provides an exhaustive enumeration of all technical, empirical, methodological, and infrastructural limitations inherent to the CrisisGuard pipeline.

The goal of CrisisGuard is to build a mathematically rigorous, provenance-preserving big data pipeline. Recognizing what the system *cannot* do is just as important as demonstrating what it *can* do. Under no circumstances should CrisisGuard be represented as an autonomous, deployment-ready emergency dispatch system.

---

## 2. Comprehensive Limitation Audit

### 2.1 Synthetic Nature of Propagation Data (Phase 8)
- **Description:** Social media cascade events and graph interactions were generated using simulated diffusion processes based on three parameterized crisis dissemination profiles (`ORGANIC_DIFFUSION`, `HIGH_VELOCITY_VIRAL`, and `COORDINATED_BOT_BURST`).
- **Impact:** While the data flows through genuine distributed enterprise infrastructure (Apache Kafka, Apache Spark 3.5.1, Spark GraphX, and Spark Structured Streaming), the user accounts and sharing events do not reflect real-time live Twitter/X firehose traffic.
- **Epistemic Classification:** The cascade topology exhibits scale-free and branching features, but must be treated as a controlled experimental benchmark rather than observed sociopolitical reality.

### 2.2 Constrained Forensic Evaluation Sample (Phase 6)
- **CIFAKE Image Subset:** Evaluated on 72 curated images (36 synthetic diffusion samples, 36 real photographs) rather than the complete 120,000-image dataset, due to local GPU memory and computational throughput constraints.
- **Deepfake Detection (DFD) Video Sample:** Constrained to 5 representative video sequences (1,714 extracted facial frames).
- **Impact:** Statistical distributions of synthetic risk provide proof-of-concept validation of the ResNet-18 feature extraction and temporal classification pipelines, but do not capture the long-tail variance of adversarial in-the-wild synthetic media.

### 2.3 Uncalibrated Deep Learning Probabilities (Phase 6)
- **Audit Finding:** Both `resnet18_cifake_v1.0` and `temporal_dfd_resnet18_v1.0` possess `calibration_status = UNCALIBRATED`.
- **Epistemic Rule:** Network output scores represent raw uncalibrated sigmoid activations. They CANNOT be interpreted as true Bayesian posterior probabilities of synthetic tampering.
- **Mitigation:** The Phase 9 schema explicitly distinguishes `model_score` from `synthetic_probability` and annotates all records with `calibration_status = UNCALIBRATED`.

### 2.4 Text-Only Modeling for CrisisMMD (Phase 7)
- **Limitation:** Although the raw CrisisMMD benchmark is designed as a multimodal image-text dataset, CrisisGuard modeled the 955 available records strictly using natural language processing (text-only TF-IDF and classification pipelines).
- **Prohibited Claim:** The CrisisMMD model must NEVER be described as multimodal or vision-language in this project. No image embeddings were fused into Phase 7 crisis intelligence.

### 2.5 Unavailable Tweet Text in HumAID (Phase 7)
- **Limitation:** In accordance with Twitter/X Developer Terms of Service, HumAID distributes dehydrated tweet IDs and humanitarian category labels. Raw tweet body text was unavailable for 15,160 records.
- **Impact:** Classification features for HumAID represent curated ground-truth annotations and label metadata rather than live end-to-end NLP inference outputs over raw text strings.

### 2.6 Absence of Universal Cross-Dataset Identifiers
- **Audit Finding:** Thorough cross-phase forensic audit confirmed that Phase 6 (forensic assets), Phase 7 (disaster tweets), Phase 8 (cascade graph nodes), and Phase 4 (OSM road intersections) share zero common keys or semantic entities.
- **Scientific Resolution:** Rather than manufacturing spurious entity links or arbitrary fuzzy joins, CrisisGuard implements a **Parallel Feature Stream Architecture** (`STREAM_A` through `STREAM_D`). Any unified presentation is maintained as a multi-stream ledger preserving complete source provenance and explicit NULLs.

### 2.7 Strict Prohibition of Arbitrary Emergency Priority Scores
- **Prohibited Constructs:** EDPI (Emergency Dispatch Priority Index), Danger Score, or composite formulas of the form:
  $$\text{Priority} = \alpha \cdot \text{MediaRisk} + \beta \cdot \text{CrisisScore} + \gamma \cdot \text{PageRank}$$
- **Rationale:** Assigning subjective linear weights ($\alpha, \beta, \gamma$) to unrelated, uncalibrated domain metrics lacks scientific validity and could lead to catastrophic resource misallocation in real crises.
- **Resolution:** CrisisGuard provides transparent, unweighted multi-attribute feature representations for human analyst decision-support.

### 2.8 Absence of Causal Source Attribution in Graph Analytics
- **Limitation:** GraphX PageRank and degree metrics measure structural prominence within directed forwarding trees.
- **Prohibition:** Structural centrality does NOT imply causal authorship, bad-faith intent, or coordination. A high-in-degree node may simply be a public official or news outlet debunking false media. PageRank is a topological summary, not an indicator of malice.

### 2.9 Unlinked Spatial Infrastructure (OpenStreetMap)
- **Limitation:** The 63,660 road nodes and 146,156 road edges extracted from OpenStreetMap represent validated physical routing topology, but cannot be joined to social media messages due to the absence of verified GPS geotags in the crisis corpora.
- **Classification:** OSM data is maintained as an independent spatial infrastructure stream (`STREAM_D`) ready for future GPS-tagged feeds.

### 2.10 Localized / Single-Node Deployment Footprint
- **Hardware Footprint:** All distributed components (HDFS, Apache Spark, Spark GraphX, Apache Kafka, Spark Structured Streaming) were deployed and executed on a single developer workstation (Windows 11 + Ubuntu 24.04 WSL2, 16 GB RAM).
- **Impact:** While distributed APIs and batch/streaming semantics were strictly verified, throughput, latency, and fault tolerance benchmarks reflect single-node execution and cannot be extrapolated to multi-rack cloud clusters.

### 2.11 No Autonomous Emergency Dispatch Readiness
- **Critical Safety Notice:** CrisisGuard is an academic research demonstration developed for CSE412. It is NOT certified for life-safety operations, 911/112 dispatch automation, or unverified civilian alerting.

---

## 3. Summary Table of Limitations

| Domain | Limitation | Scientific Risk | Mitigation in Phase 9 |
| :--- | :--- | :--- | :--- |
| **Forensics** | Uncalibrated models; 77 samples | Overconfidence in synthetic label | Flagged as `UNCALIBRATED`; raw logits recorded |
| **Crisis NLP** | Text-only CrisisMMD; dehydrated HumAID | Mischaracterizing multimodal capability | Labeled `TEXT_ONLY`; documented data provenance |
| **Graph Dynamics** | Synthetic cascade generation | Mistaking simulation for live reality | Classified as `SIMULATED_CASCADE` |
| **Relational Model**| Zero cross-dataset entity overlap | Data corruption via false joins | Parallel Feature Stream design; zero forced joins |
| **Decision Logic** | No validated joint weighting formula | Arbitrary dispatch decisions | Zero composite priority index; raw multi-attribute ledger |
| **Infrastructure** | Single-node WSL2 cluster | False claims of petabyte scalability | Benchmarked strictly on local hardware footprint |

---

*Phase 9 limitation audit confirmed complete, uncompromised, and fully aligned with project frozen state.*
