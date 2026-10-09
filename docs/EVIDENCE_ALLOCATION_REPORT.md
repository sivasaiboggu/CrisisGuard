# CrisisGuard — Scientific Implementation & Validation Report
## Real-Time Detection of Synthetic Misinformation and Intelligent Emergency Resource Allocation

**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Branch:** `feat/misinformation-resource-allocation`  
**Repository Baseline Commit:** `cbb3942`  
**Status:** VALIDATED & DEMONSTRATION-READY (10/10 PASS)

---

## 1. Executive Summary & Objective

This report details the implementation, mathematical formulation, architectural integration, and scientific validation of two production-grade Big Data decision-support capabilities in **CrisisGuard**:

1. **Feature A — Evidence-Aware Misinformation Assessment:**
   An epistemic assessment pipeline that accepts multimodal crisis reports (text, image, video, metadata), performs crisis category classification (CrisisMMD TF-IDF + Logistic Regression), executes forensic synthetic-media risk inference (ResNet-18 with Platt calibration for images; temporal classifiers for video), retrieves traceable reference facts from an authoritative evidence store (NDMA situation reports, CWC water gauge telemetry, municipal infrastructure logs, fire dispatch logs), and outputs differentiated assessment outcomes (`EVIDENCE_SUPPORTED`, `CONTRADICTED_BY_EVIDENCE`, `UNVERIFIED`, `INSUFFICIENT_EVIDENCE`, `REQUIRES_HUMAN_REVIEW`) with explicit uncertainty bounds.
   - **Critical Principle:** Strictly prevents conflating synthetic-media risk with claim falsehood. A high synthetic media score indicates potential AI manipulation of the media asset, *not* proof that the real-world incident is false.

2. **Feature B — Intelligent Emergency Resource Allocation:**
   A constrained Mixed-Integer Linear Programming (MILP) optimization module that ingests verified and dispatcher-reviewed crisis incidents, matches incident and depot locations to an OpenStreetMap (OSM) regional road network (63,660 nodes, 146,156 edges), computes exact shortest road distances (km) and travel times (minutes) via Dijkstra's algorithm, and assigns compatible emergency resources (Ambulances, Rescue Boats, Fire Tenders, Infrastructure Crews, Relief Trucks) from a transparent demonstration inventory while respecting capacity limits, urgency weights, and reachability.
   - **Critical Policy Gate:** Unverified claims cannot trigger autonomous dispatch (held in an `AWAITING_APPROVAL` queue), and claims contradicted by authoritative telemetry are marked `INFEASIBLE` under `UNVERIFIED_GATE`.

---

## 2. System Architecture & End-to-End Big Data Flow

The extended CrisisGuard architecture preserves genuine tool-to-tool data flow across the Big Data pipeline:

```
[Raw Multimodal Crisis Stream]
             │
             ▼
[Apache Hadoop HDFS (Port 9000)]  <── Processed Event Logs (5,004 records)
             │
             ▼
[Apache Spark Batch (Local / Cluster)] ── Node ID Indexing & Edge List Extraction
             │
             ▼
[Spark GraphX Analytics] ── PageRank (20 iters) & Connected Components (7,494 vertices)
             │
             ▼
[Apache Kafka Message Broker] ── High-Throughput Topics (crisisguard-demo-events)
             │
             ▼
[Spark Structured Streaming] ── 1-Hour Watermark + 1-Hour Tumbling Windows (32 Windows)
             │
             ▼
[Apache Hive Warehouse] ── Analytical Forensic Tables (default.propagation_events)
             │
             ▼
========================================================================================
NEW CAPABILITY EXTENSIONS
========================================================================================
             │
             ▼
[Feature A: Evidence-Aware Misinformation Assessment]
  ├── Phase 6 Forensics: ResNet-18 (Platt-Calibrated Images, Uncalibrated Video)
  ├── Phase 7 NLP: CrisisMMD Humanitarian Text Classifier
  ├── Phase 8 Context: GraphX PageRank & Streaming Burst Ratios
  └── Traceable Evidence Store: NDMA Sitreps, CWC Water Gauges, Municipal Logs
             │
      Outcome Differentiation:
      EVIDENCE_SUPPORTED | CONTRADICTED_BY_EVIDENCE | UNVERIFIED | INSUFFICIENT_EVIDENCE
             │
             ▼
[Safety & Policy Dispatch Gatekeeper]
  ├── Contradicted Claims  ──> INFEASIBLE (UNVERIFIED_GATE) [Dispatch Prohibited]
  ├── Unverified Claims    ──> AWAITING_APPROVAL (Dispatcher Triage Queue)
  └── Supported / Approved ──> ELIGIBLE INCIDENT CANDIDATES
             │
             ▼
[Feature B: Intelligent Emergency Resource Allocation]
  ├── Regional Road Topology: OpenStreetMap (63,660 nodes, 146,156 edges)
  ├── Spatial Pathfinding: Scipy Sparse Dijkstra (Shortest Path Distance & Travel Time)
  ├── Demonstration Inventory: Depots mapped to OSM Nodes (Boats, Ambulances, Trucks)
  └── Constrained MILP Optimizer: HiGHS Solver (Urgency Weights, Capacity Constraints)
             │
             ▼
[Decision-Support Outputs & Audit Ledger]
  ├── Structured JSON & Parquet Recommendations (schemas/allocation/allocation_schema.json)
  ├── Human Dispatcher Approval & Action History
  └── Hive / Spark Queryable Parquet Storage in results/
```

---

## 3. Feature A — Evidence-Aware Misinformation Assessment

### 3.1 Outcome Taxonomy & Verification Conditions

| Outcome | Trigger Condition | Uncertainty Range | Action Required |
| :--- | :--- | :--- | :--- |
| `EVIDENCE_SUPPORTED` | Stated factual claim matches traceable authoritative records (NDMA Sitrep, official advisory) with zero contradiction. | $0.05 - 0.20$ | Candidate for prioritized resource dispatch recommendation. |
| `CONTRADICTED_BY_EVIDENCE` | Stated claim asserts an event (e.g., bridge collapse, chemical cloud) refuted by verified physical sensors (CWC water gauge) or emergency logs. | $0.10 - 0.20$ | Blocked from physical dispatch. Triage flag generated. |
| `REQUIRES_HUMAN_REVIEW` | Supported factual claim accompanied by high-risk synthetic media ($> 0.65$), or conflicting multi-source claims. | $0.30 - 0.50$ | Human analyst inspection required to differentiate synthetic illustrations of real events from disinformation. |
| `UNVERIFIED` | Claim matches general incident keywords, but specific factual assertions cannot be verified from available logs. | $0.50 - 0.70$ | Held in dispatcher triage queue before asset release. |
| `INSUFFICIENT_EVIDENCE` | Zero traceable sitreps, telemetry, or logs exist for the reported location or hazard. | $0.70 - 0.95$ | Queued for field verification or ground scout reconnaissance. |

### 3.2 Epistemic Governance: Synthetic Media vs. Claim Veracity

In disaster informatics, media manipulation and claim veracity are orthogonal dimensions:
- An authentic photograph can accompany a completely fabricated rumor.
- A synthetic/AI-generated or recycled illustration can accompany an accurate, life-threatening disaster report (e.g., a citizen using an AI image generator to depict local flooding).
- **Prohibited:** Combining media risk and crisis category into an arbitrary scalar "misinformation index" or "danger score."
- **Implemented:** CrisisGuard preserves separate fields for `synthetic_media_risk`, `calibration_status`, `crisis_category`, and `evidence_references`, deriving the `assessment_outcome` solely from verifiable evidence corroboration.

---

## 4. Feature B — Intelligent Emergency Resource Allocation

### 4.1 Mathematical Formulation (Mixed-Integer Linear Program)

Let:
- $I = \{1, \dots, M\}$ be the set of eligible, evidence-supported or human-approved incidents.
- $R = \{1, \dots, N\}$ be the set of available emergency resource groups across depots.
- $d_i \in \mathbb{Z}_{\ge 1}$ be the demanded quantity for incident $i$.
- $C_r \in \mathbb{Z}_{\ge 1}$ be the available capacity of resource $r$.
- $w_i \in \{1.0, 2.0, 5.0, 10.0\}$ be the urgency weight of incident $i$ based on reported severity (`LOW`: 1, `MEDIUM`: 2, `HIGH`: 5, `CRITICAL`: 10).
- $t_{i, r} \ge 0$ be the estimated travel time in minutes from depot $r$ to incident $i$, computed via OpenStreetMap Dijkstra shortest paths.
- $P_{\text{unmet}} = 500.0$ be the base penalty for unmet emergency demand.

**Decision Variables:**
- $x_{i, r} \in \mathbb{Z}_{\ge 0}$: Integer quantity of resource $r$ allocated to incident $i$.
- $u_i \in \mathbb{Z}_{\ge 0}$: Unmet demand for incident $i$.

**Objective Function:**
$$\min \sum_{i \in I} \left( w_i \cdot P_{\text{unmet}} \cdot u_i \right) + \sum_{i \in I} \sum_{r \in R} \left( (1.0 + t_{i, r}) \cdot x_{i, r} \right)$$

**Subject to:**
1. **Supply / Capacity Conservation:**
   $$\sum_{i \in I} x_{i, r} \le C_r, \quad \forall r \in R$$
2. **Demand Balance:**
   $$\sum_{r \in \text{Comp}(i)} x_{i, r} + u_i = d_i, \quad \forall i \in I$$
   where $\text{Comp}(i) = \{r \in R \mid \text{Type}(r) = \text{Type}(i) \text{ and } \text{Reachable}(i, r)\}$.
3. **Compatibility & Reachability:**
   $$x_{i, r} = 0, \quad \forall r \notin \text{Comp}(i)$$
4. **Integrality:**
   $$x_{i, r} \in \mathbb{Z}_{\ge 0}, \quad u_i \in \mathbb{Z}_{\ge 0}$$

The optimization problem is solved using the **HiGHS** MILP solver via `scipy.optimize.milp`.

### 4.2 Spatial Road Network Routing (OpenStreetMap Dijkstra)

- **Dataset:** 63,660 road nodes (`road_nodes.parquet`) and 146,156 directed edges (`road_edges.parquet`).
- **Speed Profiles:** Motorway (80 km/h), Trunk (60 km/h), Primary (50 km/h), Secondary (40 km/h), Tertiary (30 km/h), Residential (25 km/h), Default (35 km/h).
- **Edge Travel Time:**
  $$T_{\text{edge}} = \left(\frac{L_{\text{km}}}{V_{\text{km/h}}}\right) \times 60 \text{ minutes}$$
- **Nearest Node Lookup:** Efficient KD-Tree spatial indexing (`scipy.spatial.cKDTree`).
- **Shortest Path Distance:** Sparse adjacency matrix traversal via `scipy.sparse.csgraph.dijkstra`.
- **Handling Disconnections:** If graph components are disconnected, returns `routing_method = UNREACHABLE`. If spatial coordinates are outside graph bounds, returns `routing_method = EUCLIDEAN_FALLBACK` (Haversine $\times 1.35$ detour factor).

---

## 5. Verification & Test Execution Results

All unit, integration, and validation tests pass with 0 failures:

| Test Suite / Validator | File | Result | Notes |
| :--- | :--- | :--- | :--- |
| **Claim Assessment Unit Suite** | `tests/unit/test_claim_assessment.py` | **8/8 PASS** | Validates corroboration, contradiction, epistemic uncertainty, synthetic media separation, duplicate normalization. |
| **Resource Allocation Unit Suite** | `tests/unit/test_resource_allocation.py` | **7/7 PASS** | Validates single incident, competing incidents, type compatibility, zero inventory, conservation laws, verification gating. |
| **End-to-End Integration Suite** | `tests/integration/test_end_to_end_assessment_allocation.py` | **1/1 PASS** | Validates end-to-end pipeline from raw reports to optimization and human dispatcher review. |
| **New Capabilities Validator** | `scripts/validation/validate_evidence_allocation.py` | **10/10 PASS** | Validates schema conformity, evidence records, Dijkstra engine, MILP solver, gating policies, idempotency. |
| **Master Project Validator** | `scripts/validation/validate_final_project.py` | **10/10 PASS** | Validates physical integrity across all frozen phases (Phases 4–9). |
| **Functional Acceptance Test** | `scripts/validation/run_functional_acceptance_tests.py` | **10/10 PASS** | Validates Kafka replay, GraphX metrics, Spark streaming, Hive queries, and Phase 9 multi-stream ledger. |
| **Master Final Demonstration** | `scripts/demo/run_demo_evidence_allocation.py` | **10/10 PASS** | Executes all 10 stages of Section 10 live within 26.44 seconds. |

---

## 6. Demonstration Walkthrough (10-Stage Verification)

```
================================================================================
CRISISGUARD — FINAL MASTER DEMONSTRATION RUN SUMMARY
================================================================================
Stage 1: Environment & Dependency Validation        [PASS] (10/10 checks)
Stage 2: Multi-Incident Crisis Stream Ingestion      [PASS] (4 distinct crisis events)
Stage 3: Forensics & Crisis Intelligence             [PASS] (TF-IDF + ResNet-18)
Stage 4: Propagation Dynamics Integration            [PASS] (Phase 8 GraphX & streaming metrics)
Stage 5: Evidence Corroboration & Contradiction      [PASS] (NDMA, CWC telemetry, municipal logs)
Stage 6: Demonstration Depot Inventory Display       [PASS] (7 asset groups on OSM nodes)
Stage 7: Constrained MILP Optimization (HiGHS)       [PASS] (Solved in 10.03 ms, 0 violations)
Stage 8: Safety Policy Gating & Dispatcher Approval  [PASS] (Blocked fake bridge, held unverified)
Stage 9: Storage & Warehouse Analytical Persistence  [PASS] (Parquet & JSON in results/)
Stage 10: Scientific Evaluation & Limitations Audit  [PASS] (10/10 stages confirmed)
================================================================================
```

---

## 7. Known Limitations & Operating Boundaries

1. **Synthetic Media Detection vs. Ground Truth:** Deepfake classifiers predict manipulation probabilities of media files, *never* factual event occurrence.
2. **Video Calibration:** Video temporal deepfake checkpoint remains `UNCALIBRATED` due to small validation sample size (5 videos).
3. **OpenStreetMap Spatial Boundaries:** Physical network pathfinding is bounded to the regional OpenStreetMap extract; incidents outside bounds transparently trigger `EUCLIDEAN_FALLBACK`.
4. **Synthetic Demonstration Inventory:** Depot inventories and capacities are configured as synthetic demonstration fixtures adhering to Section 4.2.
5. **Human-in-the-Loop Authority:** Allocations are decision-support recommendations; autonomous dispatch is strictly disabled.
