# CrisisGuard: Data Partitioning & Leakage Control Policy

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Policy Status:** Enforced & Validated Baseline  

---

## 1. Core Partitioning Directives

Data leakage between training, validation, and evaluation partitions invalidates machine learning claims. CrisisGuard enforces three strict leakage control rules:

1. **Identity & Actor Stratification (Video Forensics):** Frames originating from the same source actor pair or video sequence are never split across train and test. Google DFD partition splits (`train.json`, `val.json`, `test.json`) are preserved strictly.
2. **Benchmark Test Isolation (CIFAKE Image Forensics):** The acquired 500 CIFAKE images originate from the official test benchmark partition. They are preserved exclusively for out-of-domain image evaluation and are never mixed into training folds.
3. **Disaster Event Isolation (Crisis Text):** Crisis datasets (HumAID, CrisisMMD, CrisisLex) preserve original disaster event boundaries. Models are validated on held-out disaster events to ensure generalization across novel disaster types.

## 2. Partition Summary Table

| Dataset | Split Strategy | Train Records | Dev / Val Records | Test Records | Leakage Prevention Mechanism |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Google DFD Sample** | Actor-Pair Stratified | 1 sequence (ex_actors) | 1 sequence (DDD_samples) | 2 sequences (deepfake_vid, ex_fake) | Disjoint actor pairs |
| **CIFAKE** | Benchmark Test Set | 0 (Held-out eval) | 0 | 500 images (250 real / 250 syn) | Zero training contamination |
| **HumAID** | Official QCRI Splits | 53,531 (70.0%) | 7,793 (10.2%) | 15,160 (19.8%) | Official event-stratified splits |
| **CrisisMMD** | Consensus Splits | 6,126 (75.8%) | 998 (12.4%) | 955 (11.8%) | Agreed-label event splits |
| **CrisisLex** | Event-Holdout Split | 61,610 (70.0%) | 8,802 (10.0%) | 17,603 (20.0%) | Stratified by disaster event |
