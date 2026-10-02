# CrisisGuard — Phase 7: CrisisMMD Task Selection & Modeling Strategy
**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Phase:** Phase 7 — Crisis Information Intelligence Engine  
**Date:** September 2026  
**Status:** VALIDATED TASK SPECIFICATION  

---

## 1. Selected Tasks for CrisisGuard Integration

From the available annotations in CrisisMMD, two prediction tasks directly feed into the CrisisGuard information intelligence pipeline:

### Task 1: Primary Task — Humanitarian Information Classification
- **Target Field:** `humanitarian_label`
- **Output Space:** 5 mutually exclusive categorical classes:
  1. `not_humanitarian`
  2. `other_relevant_information`
  3. `rescue_volunteering_or_donation_effort`
  4. `infrastructure_and_utility_damage`
  5. `affected_individuals`
- **Pipeline Contribution:** Direct input into situational awareness and emergency response coordination. Allows automatic routing of relief messages to emergency responders.
- **Evaluation Metric:** **Macro F1** (due to extreme class imbalance: 52.9% `not_humanitarian` vs 1.1% `affected_individuals`), along with Accuracy, Macro Precision, Macro Recall, and Weighted F1.

### Task 2: Secondary Task — Informativeness Filtering
- **Target Field:** `informative_label`
- **Output Space:** Binary classification:
  1. `not_informative` (Negative class, 52.94%)
  2. `informative` (Positive class, 47.06%)
- **Pipeline Contribution:** Upfront triage filter to discard social media noise and chatter before downstream computational processing.
- **Evaluation Metric:** Accuracy, Macro F1, Binary Precision, Recall, and ROC-AUC / PR-AUC.

---

## 2. Modeling Protocol & Leakage Control

1. **Official Benchmark Splits:**
   - Training set: 6,126 records (75.8%)
   - Development set: 998 records (12.4%)
   - Test set: 955 records (11.8%)
2. **Disjointness Audit:** Zero tweet ID overlap between train, dev, and test.
3. **Model Families:**
   - **Baseline:** TF-IDF n-grams (1, 2) + Multinomial Logistic Regression with L2 regularization and balanced class weighting.
   - **Advanced Transformer:** Fine-tuned `distilbert-base-uncased` sequence classifier trained on `clean_text`.
4. **Calibration Protocol:** Uncalibrated model scores and softmax probabilities are preserved with explicit flag `calibration_status: "UNCALIBRATED"`.
