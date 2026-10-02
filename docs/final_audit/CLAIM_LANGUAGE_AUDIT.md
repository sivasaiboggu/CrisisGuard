# CrisisGuard — Claim Integrity & Scientific Language Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Target:** Repository-Wide Epistemic Language Integrity  
**Audit Date:** September 2026  

---

## 1. Executive Summary

This audit performs a systematic search across all documentation, comments, and schemas for claims or statements that exceed empirical evidence, assert causal relationships without experimental control, imply autonomous life-safety dispatch capabilities, or mischaracterize uncalibrated model outputs as true probabilities.

In strict compliance with audit rules:
> **"For every issue give: File, Current statement, Why problematic, Recommended correction. Do NOT perform large automatic rewrites."**

every flagged statement is documented below with its exact location and recommended correction for the final submission pass.

---

## 2. Identified Claim & Language Inconsistencies

### Issue 1: Planned Emergency Dispatch Index (EDPI) in Inception Documents
- **File:** [`README.md`](file:///c:/Users/HP/OneDrive/Desktop/CrisisGuard/README.md#L29) (Line 29)
  - **Current Statement:** `"4. Distributed Emergency Prioritization (MLlib): Train scalable predictive models with Spark MLlib to compute the Emergency Dispatch Priority Index (EDPI), jointly evaluating authenticity scores, cascade virality, urgency indicators, and transit feasibility."`
  - **Why Problematic:** Inception-phase text. Computing an arbitrary linear EDPI formula without empirical ground truth was explicitly rejected in Phases 7, 8, and 9 as unscientific.
  - **Recommended Correction:** Replace with: `"4. Decision-Support Feature Stream: Assemble verified, multi-attribute feature representations for qualified emergency analysts without ungrounded heuristic priority scoring."`

### Issue 2: EDPI Formula in Inception Data Lineage Document
- **File:** [`docs/datasets/DATA_LINEAGE.md`](file:///c:/Users/HP/OneDrive/Desktop/CrisisGuard/docs/datasets/DATA_LINEAGE.md#L149) (Line 149)
  - **Current Statement:** `"The Emergency Dispatch Priority Index (EDPI) balances: EDPI = f(Severity, Urgency, Velocity, PageRank, SyntheticRisk, RoadAccessibility, Proximity)"`
  - **Why Problematic:** Suggests an automated priority scoring function exists in the pipeline, whereas Phase 9 strictly preserved separate feature streams to prevent arbitrary weighting.
  - **Recommended Correction:** Add an explicit epistemic note: `"Note: The theoretical composite function f() was evaluated and formally prohibited during Phase 9 to avoid arbitrary weighting without ground truth; feature dimensions are maintained in parallel."`

### Issue 3: Primary Benchmark Claims for Video Deepfakes
- **File:** [`README.md`](file:///c:/Users/HP/OneDrive/Desktop/CrisisGuard/README.md#L95-L97) (Lines 95–97)
  - **Current Statement:** Listing `DFDC`, `Celeb-DF (v2)`, and `FaceForensics++` as the primary benchmark datasets.
  - **Why Problematic:** Due to local resource boundaries, Phase 6 used a controlled development sample of Google DFD (5 video sequences) and CIFAKE (72 test images). Claiming evaluation across DFDC/FF++ without local execution misrepresents benchmark coverage.
  - **Recommended Correction:** Clarify that DFDC and Celeb-DF represent external evaluation references, while physical pipeline execution was conducted on the Google DFD controlled sample and CIFAKE subset.

### Issue 4: Historical Vertex Count in Phase 8 Spark Preprocessing Report
- **File:** [`docs/phase8/PHASE8_SPARK_REPORT.md`](file:///c:/Users/HP/OneDrive/Desktop/CrisisGuard/docs/phase8/PHASE8_SPARK_REPORT.md#L30) (Line 30)
  - **Current Statement:** `"Total Unique Graph Vertices | 7,495 | Distinct vertices across all sources and targets"`
  - **Why Problematic:** `7,495` represents the pre-reconciliation count where `target_node = NULL` was mapped as a vertex before `isNotNull()` filtering. The final reconciled graph size is `7,494`.
  - **Recommended Correction:** Update to: `"Total Unique Graph Vertices | 7,494 | Distinct non-null vertices (reconciled after filtering 5 root broadcast NULL targets)."`

### Issue 5: Historical Vertex Count in Phase 8 Streaming Report
- **File:** [`docs/phase8/PHASE8_STREAMING_REPORT.md`](file:///c:/Users/HP/OneDrive/Desktop/CrisisGuard/docs/phase8/PHASE8_STREAMING_REPORT.md#L56) (Line 56)
  - **Current Statement:** `"Total Unique Graph Nodes | 7,495 | 7,495 | PASS"`
  - **Why Problematic:** Reflects legacy pre-reconciliation node count before NULL-target isolation.
  - **Recommended Correction:** Update to `7,494` in accordance with `PHASE8_GRAPHX_REPORT.md` and `validate_phase8.py`.

### Issue 6: Phase Status Badge in README.md
- **File:** [`README.md`](file:///c:/Users/HP/OneDrive/Desktop/CrisisGuard/README.md#L4) (Line 4)
  - **Current Statement:** `"[![Phase](https://img.shields.io/badge/Phase-0%3A%20Initialization%20%26%20Architecture%20Freeze-green.svg)](#)"`
  - **Why Problematic:** Inaccurately portrays the repository as still in Phase 0.
  - **Recommended Correction:** Update badge to reflect `Phase 9: Final Decision-Support Layer — Frozen`.

---

## 3. Verified Prohibitions (No Violations Found)

The following high-risk claims were searched across the entire repository and verified as **COMPLETELY FREE OF VIOLATIONS**:

| Claim Category | Verification Search | Repository Finding | Status |
| :--- | :--- | :--- | :--- |
| **Multimodal CrisisMMD Classification** | Grep `multimodal classification` | Zero claims found. All Phase 7/9 docs declare text-only modeling. | **PASS** |
| **Calibrated Model Probabilities** | Grep `calibrated probabilit` | Zero claims of calibrated probabilities. Explicitly declared `UNCALIBRATED`. | **PASS** |
| **Malicious Intent / Deception Proof** | Grep `malicious intent`, `proof of fake` | Zero claims found. Synthetic risk is strictly an analytical feature. | **PASS** |
| **Causal Attribution in Graph Analytics** | Grep `causal source`, `caused panic` | Zero claims found. Centrality is strictly topological. | **PASS** |
| **Real Emergency Dispatch Capability** | Grep `autonomous dispatch`, `certified 911` | Zero claims found. Disclaimed across all limitations documents. | **PASS** |

---

*Claim integrity audit verdict: 6 documentation corrections identified for pre-submission update; zero scientific fraud or prohibited claims found in core engine.*
