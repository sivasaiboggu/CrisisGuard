# CrisisGuard — Stale Artifact & Legacy Metric Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Target:** Stale and Legacy Metric Detection  
**Audit Date:** September 2026  

---

## 1. Executive Summary

During multi-phase development, pipelines evolve as forensic discrepancies are resolved. When an earlier iteration's metrics are updated (e.g. reconciling graph vertex counts after identifying NULL-target root broadcasts), historical text in early draft documentation may retain legacy numbers.

In strict compliance with audit rules:
> **"Do NOT silently delete stale artifacts. Report them."**

this document catalogs every legacy, stale, or superseded number discovered across the repository.

---

## 2. Stale Value Search & Audit Results

### 2.1 The "7,495" vs "7,494" Vertex Count
- **Root Cause:** In the initial Phase 8 run, Spark batch preprocessing (`spark_prepare_propagation.py`) unioned source and target nodes without filtering `NULL`, producing 7,495 distinct entries (7,494 unique users + 1 `NULL` entity) and assigning `vertex_id = 1` (`1,` in CSV). GraphX dropped this empty string line upon loading, computing metrics on 7,494 vertices.
- **Resolution:** Reconciled by adding explicit `isNotNull()` filtering across all preprocessing and validation scripts, fixing the true graph size at **7,494**.
- **Found Stale Occurrences:**
  1. `docs/phase8/PHASE8_SPARK_REPORT.md`: Line 30 (`7,495` vertices in table), Line 57 (`vertex_id <= 7,495`), Line 78 (`vertices.csv (N=7,495)`).
  2. `docs/phase8/PHASE8_STREAMING_REPORT.md`: Line 56 (`Total Unique Graph Nodes | 7,495`).
  3. `docs/phase8/PHASE8_ARCHITECTURE.md`: Line 45 (`GX_VERT["vertices.csv / parquet<br/>(7,495 vertices)"]`).
  4. `docs/phase8/PHASE8_REPRODUCIBILITY.md`: Line 89 (`spark_batch_summary.json ... 7,495 vertices`).
- **Audit Decision:** Retained for provenance; documented here and flagged for final documentation polish.

### 2.2 The "2,509" vs "2,508" Target Node Count
- **Root Cause:** If `NULL` targets in root broadcast events are included in target sets, the count is 2,509 ($2,508 \text{ real user targets} + 1 \text{ NULL target}$). The true count of non-null target accounts is **2,508**.
- **Found Stale Occurrences:** None in active code. Properly explained in `docs/phase8/BATCH_STREAMING_VALIDATION.md` and `docs/phase8/PHASE8_FINAL_REPORT.md`.

### 2.3 Early HumAID Target Counts
- **Description:** Raw HumAID contains 76,484 multi-split records. Some early planning documents referenced the entire corpus size before the test partition evaluation ($N=15,160$) was finalized in Phase 7.
- **Audit Finding:** All Phase 7 and Phase 9 feature tables consistently evaluate the **15,160** test partition records.

### 2.4 Early Planned Phase 0 Tools (Spark MLlib EDPI)
- **Description:** Early Phase 0 planning proposed using Spark MLlib to compute a composite Emergency Dispatch Priority Index (EDPI).
- **Audit Finding:** In Phases 7 through 9, this was formally abandoned and prohibited. `README.md` and `PROJECT_STATUS.md` contain legacy references to this abandoned objective.

---

## 3. Summary of Files Containing Stale Metrics

| File Path | Legacy / Stale Metric Found | Current Verified Truth | Action Required |
| :--- | :--- | :--- | :--- |
| `docs/phase8/PHASE8_SPARK_REPORT.md` | `7,495` vertices | `7,494` vertices | Update text to 7,494 during final doc polish |
| `docs/phase8/PHASE8_STREAMING_REPORT.md` | `7,495` nodes | `7,494` nodes | Update text to 7,494 during final doc polish |
| `docs/phase8/PHASE8_ARCHITECTURE.md` | `(7,495 vertices)` | `(7,494 vertices)` | Update diagram label to 7,494 |
| `docs/phase8/PHASE8_REPRODUCIBILITY.md` | `7,495 vertices` | `7,494 vertices` | Update text to 7,494 |
| `README.md` | Phase 0 badge, MLlib EDPI | Phase 9 Frozen, Parallel streams | Overhaul README.md |
| `PROJECT_STATUS.md` | Phase 0/4 status entries | Phases 4–9 Frozen | Update master tracking table |

---

*Stale artifact audit completed: All legacy references cataloged without unapproved file deletions.*
