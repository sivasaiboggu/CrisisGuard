# CrisisGuard — Phase 7: Model Cards
**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 7 — Crisis Information Intelligence Engine  
**Date:** September 2026  
**Status:** VALIDATED RESEARCH MODEL CARDS  

---

## Model Card 1: HumAID Stratified Prior Classifier (`humaid_stratified_baseline_v1`)

### 1. Model Details
- **Developer:** CrisisGuard Research Team (Author: B.SIVASAI)
- **Model Type:** Empirical Multi-Class Prior Baseline
- **Version:** `v1.0`
- **Trained on:** HumAID Benchmark Training Set ($N=53,531$)
- **License:** CC BY 4.0

### 2. Intended Use
- **Primary Intended Use:** Establishing empirical class prior distributions, baseline lower bounds, and class imbalance expectations for 10 humanitarian disaster response categories.
- **Out-of-Scope Use:** MUST NOT be used for real-time dispatch decision-making, individual casualty assessment, or high-stakes evacuation prioritization.

### 3. Training & Validation Data
- **Dataset:** HumAID (Imran et al., ICWSM 2021)
- **Target:** 10 consensus categories (`rescue_volunteering_or_donation_effort`, `other_relevant_information`, `sympathy_and_support`, `infrastructure_and_utility_damage`, `injured_or_dead_people`, `not_humanitarian`, `caution_and_advice`, `displaced_people_and_evacuations`, `requests_or_urgent_needs`, `missing_or_found_people`).
- **Splits:** Official QCRI partition (Train: 53,531, Dev: 7,793, Test: 15,160). Verified zero ID leakage across partitions.

### 4. Quantitative Factors & Metrics
- **Accuracy:** 0.1497
- **Macro Precision:** 0.0984
- **Macro Recall:** 0.0985
- **Macro F1:** 0.0984
- **Weighted F1:** 0.1492

### 5. Ethical Considerations & Limitations
- **Data Reality:** Operates on categorical metadata without text due to Twitter Terms of Service data restrictions in the official QCRI `all_combined` archive.
- **Probabilities:** Output scores reflect historical category base rates and are explicitly labeled `calibration_status: "UNCALIBRATED"`.

---

## Model Card 2: CrisisMMD DistilBERT Humanitarian Classifier (`crisismmd_distilbert_v1`)

### 1. Model Details
- **Architecture:** Pretrained `distilbert-base-uncased` (66M parameters) fine-tuned for multi-class sequence classification.
- **Tokenizer:** WordPiece (vocabulary size 30,522, max sequence length 128).
- **Optimizer:** AdamW ($lr=2.0 \times 10^{-5}$, weight decay=0.01).
- **Target:** 5 humanitarian response categories.

### 2. Intended Use
- **Intended Applications:** Automated categorization of incoming disaster tweets into operational buckets (`infrastructure_and_utility_damage`, `rescue_volunteering_or_donation_effort`, `affected_individuals`, `other_relevant_information`, `not_humanitarian`).
- **Prohibited Applications:** Autonomous dispatch decisions; replacement of official emergency dispatchers.

### 3. Quantitative Performance
- **Test Partition ($N=955$):**
  - **Accuracy:** 0.8199
  - **Macro Precision:** 0.8519
  - **Macro Recall:** 0.6678
  - **Macro F1:** 0.7078
  - **Weighted F1:** 0.8167

### 4. Modality Limitations & Honesty Mandate
- **Modality Scope:** Strictly **Text-Only**. Although CrisisMMD has image references in metadata, zero local image binaries are present in the raw repository (`image_available_locally = False`).
- **Event Generalization:** In-distribution evaluation shares events with training data. True unseen-event holdout testing shows a performance delta of approximately **-11.2% in Accuracy** and **-5.0% in Macro F1**.
- **Calibration Status:** Softmax probability outputs are strictly labeled `calibration_status: "UNCALIBRATED"`.

---

## Model Card 3: CrisisMMD TF-IDF Logistic Regression Baseline

### 1. Model Details
- **Architecture:** Term Frequency-Inverse Document Frequency (1-2 n-grams, 5000 max features) + Multinomial Logistic Regression with L2 regularization and balanced class weights.
- **Test Performance ($N=955$):**
  - Accuracy: 0.7445
  - Macro Precision: 0.5915
  - Macro Recall: 0.6584
  - Macro F1: 0.6171
  - Weighted F1: 0.7501
