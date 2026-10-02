# CrisisGuard — README.md Audit & Required Corrections Report

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Target Document:** `README.md` (Top-Level Repository Document)  
**Audit Date:** September 2026  

---

## 1. Executive Summary

This audit rigorously evaluates the top-level `README.md` file against the actual, fully implemented, and frozen codebase (Phases 4 through 9). 

The audit reveals that `README.md` remains in an early **Phase 0 template state** from project inception and contains multiple obsolete architectural claims, ungrounded metrics (such as the unscientific Emergency Dispatch Priority Index, EDPI), and outdated dataset roles.

In strict compliance with the instruction:
> **"Do NOT rewrite the README yet. Only report required corrections."**

this document cataloguers every required correction to ensure complete fidelity with the frozen pipeline before final submission.

---

## 2. Item-by-Item Discrepancy & Required Corrections Matrix

| Section in `README.md` | Current Text / Claim | Actual Implementation Reality (Phases 4–9) | Required Correction | Severity |
| :--- | :--- | :--- | :--- | :--- |
| **Header Badges (L4)** | `[![Phase](https://img.shields.io/badge/Phase-0%3A...` | All phases through Phase 9 are complete and frozen. | Update badge to `Phase 9: Final Decision-Support Layer — Frozen`. | Moderate |
| **Objectives: Item 4 (L29)** | "Train scalable predictive models with Spark MLlib to compute the Emergency Dispatch Priority Index (EDPI)..." | EDPI was explicitly rejected and prohibited across Phases 7, 8, and 9 to avoid arbitrary ungrounded dispatch weighting. | Replace with: "Construct a provenance-preserving multi-attribute decision support layer without arbitrary linear priority scoring." | **BLOCKING (Epistemic)** |
| **Architecture Diagram: Box 5 (L67–71)** | `DISTRIBUTED MACHINE LEARNING (MLLIB)... Output: Emergency Dispatch Priority Index (EDPI Score)` | Spark MLlib EDPI scoring was replaced by Phase 6 Deep Learning (PyTorch ResNet-18) and Phase 7 NLP (DistilBERT/TF-IDF) feature streams. | Replace MLlib EDPI box with Phase 6 & Phase 7 AI Intelligence engines and Phase 9 Multi-Stream Ledger. | **BLOCKING (Epistemic)** |
| **Dataset Roles Table (L95–97)** | DFDC, Celeb-DF, and FaceForensics++ listed as active primary benchmarks. | Phase 6 explicitly utilized a controlled Google DFD development sample (5 videos) and a controlled CIFAKE evaluation subset (72 images). | Update dataset roles table to accurately reflect Google DFD controlled sample and CIFAKE subset. | **High** |
| **Phase 8 Graph Counts** | Not documented in README.md. | Phase 8 produced 5,004 events, 4,999 edges, 7,494 GraphX vertices, and 32 streaming windows. | Add Phase 8 distributed pipeline metrics section. | Moderate |
| **Phase 9 Integration** | Not documented in README.md. | Phase 9 constructed 175,361-record unified ledger across 4 parallel feature streams. | Add Phase 9 multi-stream integration section. | High |
| **Calibration Status** | Not mentioned. | All deep learning models are strictly `UNCALIBRATED`. | Add explicit warning that scores represent uncalibrated sigmoid outputs. | High |
| **Limitations Section** | Missing from README.md. | Exhaustive limitations documented in `docs/phase9/PHASE9_LIMITATIONS.md`. | Add comprehensive limitations section covering simulated cascades, sample sizes, and non-dispatch readiness. | High |

---

## 3. Required README Restructuring Plan

When authorized by the user/instructor to update `README.md`, the document must be overhauled to:
1. **Reflect Project Completion:** Update badges to indicate Phases 4–9 FROZEN.
2. **Remove Prohibited Constructs:** Purge all mentions of EDPI, Danger Score, or arbitrary linear dispatch weighting.
3. **Accurately Represent Datasets:** Document CIFAKE (72 test images), DFD (5 videos), HumAID (15,160 test records, dehydrated), CrisisMMD (8,079 records, text-only), CrisisLex (88,015 records), and OSM (63,660 road nodes).
4. **Display Verified Pipeline Results:**
   - Big Data Pipeline: HDFS $\to$ Spark $\to$ GraphX (7,494 vertices) $\to$ Kafka (5,004 msgs) $\to$ Streaming (32 windows) $\to$ Hive.
   - Decision-Support Layer: 175,361 rows in Parallel Feature Ledger (`data/features/phase9/`).
5. **Provide Exact Execution Commands:** Reference the verified reproduction sequence from `docs/final_audit/REPRODUCIBILITY_AUDIT.md`.
6. **Include Prominent Epistemic Warnings:** Disclaim life-safety dispatch readiness and autonomous decision-making.

---

*README audit completed: README.md requires revision before final submission.*
