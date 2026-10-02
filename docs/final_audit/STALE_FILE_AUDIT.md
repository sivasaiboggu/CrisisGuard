# CRISISGUARD — STALE FILE & HISTORICAL ARTIFACT AUDIT

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Audit Target:** Identification of Stale, Abandoned, or Obsolete Artifacts Across All Phases  
**Policy:** Historical audit evidence explaining previous bugs must be retained and clearly labeled. Zero active stale computational artifacts allowed in production.

---

## 1. Audit Scope & Search Methodology

An exhaustive search was conducted across the codebase, configuration, data directories, and documentation for keywords and concepts representing deprecated or superseded prototypes:
- `Phase 0`, `Phase 1`, `Phase 2`, `Phase 3` legacy references
- `7,495` vertex count vs `7,494` GraphX vertex count
- `NULL` target node / graph vertex root broadcast behavior
- `EDPI` (Early Disaster Priority Index) / `Danger Score` / heuristic dispatch score
- Obsolete architecture or abandoned model pipelines
- CrisisMMD and HumAID dataset modeling boundaries

---

## 2. Audit Findings by Category

### 2.1 Phase 0, 1, 2, 3 Artifacts
- **Status:** **CLEAN & PURGED FROM PRODUCTION CODE**
- **Investigation:**
  - No legacy source code or prototype scripts from Phases 0–3 exist in `src/` or `scripts/`.
  - All early experimental code has been replaced by the frozen, standardized pipeline (`scripts/phase8/`, `scripts/phase9/`, `scripts/synthetic_media/`, `scripts/crisis_information/`).
  - `README.md` previously contained Phase 0 mentions; these were completely removed during the final documentation correction.
  - Remaining mentions of Phases 0–3 exist exclusively within historical audit records (`docs/final_audit/PHASE_BY_PHASE_AUDIT.md`) where they document chronological progress.

### 2.2 Phase 8 Vertex Count Audit: 7,495 vs 7,494
- **Status:** **HISTORICALLY RESOLVED & RIGOROUSLY DOCUMENTED**
- **Investigation:**
  - An earlier batch mapping script recorded `7,495` string IDs due to an off-by-one handling of root broadcast events having `target_node = NULL`.
  - The actual GraphX graph contains exactly **7,494 real graph vertices** and **4,999 directed edges** constructed from **5,004 propagation events** (which include exactly 5 root broadcast events with `target_node = NULL`).
  - Documentation files (`PHASE8_SPARK_REPORT.md`, `PHASE8_STREAMING_REPORT.md`, `PHASE8_ARCHITECTURE.md`, `PHASE8_REPRODUCIBILITY.md`) were updated to cite 7,494 vertices as the authoritative physical GraphX vertex count, while explicitly preserving the forensic explanation of the 5 NULL-target root events.
  - The vertex mapping table on disk is `data/features/phase8/graph/vertices.parquet` (7,494 rows).
  - **Verdict:** No stale files exist. Retained historical audit documents are labeled and mathematically sound.

### 2.3 EDPI (Emergency Dispatch Priority Index) & Danger Score
- **Status:** **PERMANENTLY PURGED FROM PRODUCTION CODE**
- **Investigation:**
  - An early project proposal envisioned a synthetic "EDPI" or "Danger Score" composite heuristic.
  - During Phase 7 and Phase 8 forensic audits, this heuristic was identified as scientifically ungrounded and rejected in favor of empirical feature preservation: separate, unadulterated columns for `synthetic_media_risk` (Phase 6), `crisis_priority` (Phase 7), and GraphX graph metrics (`pagerank`, `in_degree`, `out_degree`, `component_id`).
  - Live production scripts (`scripts/phase9/build_phase9_intelligence.py`) contain ZERO instances of EDPI or danger score calculations.
  - Existing occurrences are solely negative assertions in audit logs confirming that EDPI is NOT used.

### 2.4 CrisisMMD and HumAID Dataset Semantics
- **Status:** **EXPLICITLY RECONCILED & DOCUMENTED**
- **CrisisMMD:** Text-based CrisisMMD classification with multimodal metadata and provenance retained; local image binaries = 0 and `image_available_locally = False`.
- **HumAID:** HumAID benchmark dataset containing 76,484 records (53,531 train, 7,793 dev, 15,160 test) with tweet IDs and humanitarian category labels, without local tweet text; modeled via empirical stratified distribution baselines on the official partitions.

### 2.5 Obsolete Datasets & Resource Forks
- **Status:** **IDENTIFIED FOR SAFE AUTHORIZED CLEANUP**
- **Investigation:**
  - 8 macOS resource fork files (`._Readme.txt`, etc.) in `data/raw/crisismmd/__MACOSX/` and `data/raw/humaid/all_combined/`.
  - 25 OS session tracking files (`.DS_Store`, `.Rhistory`) in raw data and external evaluation test suites.
  - These files have 0 computational references and can be safely removed upon authorization.

---

## 3. Phase 9 Multi-Stream Ledger vs Event-Level Tables Reconciliation

- **Analytical Tables:**
  - `data/features/phase9/phase9_media_intelligence.parquet`: 77 records (Stream A).
  - `data/features/phase9/phase9_crisis_intelligence.parquet`: 104,130 records (Stream B).
  - `data/features/phase9/phase9_propagation_intelligence.parquet`: 7,494 records (Stream C).
  - `data/features/phase9/phase9_spatial_intelligence.parquet`: 63,660 records (Stream D).
- **Multi-Stream Union Ledger:**
  - `data/features/phase9/phase9_multi_stream_intelligence.parquet`: **175,361 records** ($77 + 104,130 + 7,494 + 63,660 = 175,361$).
- **5,004 Records:**
  - The 5,004 records in `data/processed/propagation/propagation_events.parquet` and `streaming_parsed_events.parquet` represent **Phase 8 social network cascade diffusion events** (including 5 root broadcast events with `target_node = NULL`). They are NOT a "unified cross-domain join" of media, crisis, and graph data.
  - As proven in `docs/phase9/JOIN_FEASIBILITY_AUDIT.md`, cross-domain foreign keys across Phase 6, 7, 8, and OSM do not exist (0.00% key overlap); therefore, **`NO_VALID_JOIN` decisions were enforced to prevent scientific misconduct.**
