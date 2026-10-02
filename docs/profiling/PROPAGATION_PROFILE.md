# CrisisGuard: Semi-Synthetic Propagation Network Profile

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Methodology:** Pure Python NetworkX Topological Analysis (Pre-GraphX Profiling)  

---

## 1. Network Topology Metrics

| Metric | Computed Value | Description |
| :--- | :--- | :--- |
| **Total Diffusion Events** | **5,004** | Timestamped dissemination actions in `events.jsonl` |
| **Total Directed Edges** | **4,999** | Parent-to-child propagation links in `edges.csv` |
| **Unique Graph Nodes** | **4,986** | Distinct user accounts participating in diffusion |
| **Graph Density** | **0.000201** | Sparse tree-structured cascade distribution |
| **Max In-Degree** | **13** | Maximum viral amplification received by a single spreader node |
| **Max Out-Degree** | **2** | Outgoing retweets per individual event node |
| **Average Degree** | **1.002** | Characteristic branching factor of crisis propagation |
| **Governance Tag Compliance** | **100% (5,004 / 5,004)** | All records retain `governance_tag: "SEMI_SYNTHETIC"` |

---

## 2. Scenario Distribution & Cascades

| Scenario Identifier | Event Count | Percentage | Propagation Characteristics |
| :--- | :---: | :---: | :--- |
| **`ORGANIC_DIFFUSION`** | 3,047 | 60.89% | Natural citizen retweets, power-law inter-arrival times, moderate depth |
| **`COORDINATED_BOT_BURST`** | 1,002 | 20.02% | High concurrency, synchronized timestamps (< 30s latency), ring topology |
| **`HIGH_VELOCITY_VIRAL`** | 955 | 19.08% | Rapid exponential branching, celebrity / influencer amplification |
