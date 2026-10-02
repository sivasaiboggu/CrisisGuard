# CrisisGuard: Resource Allocation & Storage Governance Plan

**Host Hardware Baseline:** 16 GB Physical RAM (AMD Ryzen 7 7445HS, 6C/12T), 237 GB Free on Host C:, 943 GB Free on WSL2 ext4.  
**WSL2 Assigned Memory:** 7.4 GB RAM, 2.0 GB Swap.  

---

## 1. Memory Allocation Matrix

| Resource | Available | Recommended Allocation | Reason |
| :--- | :--- | :--- | :--- |
| **Total Host RAM** | 16.0 GB (Physical) | 16.0 GB total | Preserves host OS stability while allocating controlled quota to WSL2 |
| **WSL2 Subsystem RAM** | 7.4 GB visible (6.3 GB free) | 7.4 GB Max | Default Microsoft WSL2 ceiling (50% of physical host memory) |
| **Spark Driver** | Within WSL2 RAM | **2.0 GB** (`-Xmx2g` / `--driver-memory 2g`) | Sufficient for driver-side schema resolution, vector assemblers, and Spark SQL query execution |
| **Spark Executor / Local Mode** | Within WSL2 RAM | **2.0 GB** (`--executor-memory 2g` / `local[4]`) | Restricts concurrency to 4 cores to prevent thrashing; handles sliding-window stream micro-batches smoothly |
| **Apache Kafka (KRaft Broker)** | Within WSL2 RAM | **512 MB** (`KAFKA_HEAP_OPTS="-Xms256m -Xmx512m"`) | Single-broker KRaft runs with minimal heap while servicing event topics |
| **Hive Metastore / Spark SQL Catalog** | Within WSL2 RAM | **512 MB** | Embedded Derby or standalone Metastore catalog requires minimal JVM memory |
| **Hadoop / HDFS Client / Local IO** | Within WSL2 RAM | **512 MB** | Lightweight buffer for checkpoint writes and local filesystem/HDFS operations |
| **OS, Buffer Cache & WSL Kernel** | Within WSL2 RAM | **~1.88 GB** | Reserved for Linux page cache, active I/O buffering, and Python runtime |
| **TOTAL ACTIVE JVM ALLOCATION** | 7.4 GB Available | **~5.52 GB Max Concurrent** | Leaves a safe ~1.88 GB headroom buffer; prevents OOM killer invocation |

---

## 2. Storage Allocation Strategy

| Directory / Artifact | Recommended Storage Target | Filesystem Type | Size Quota / Budget | Storage Policy & Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Source Code & Configs** | `/mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard/` | NTFS via 9P / drvfs | $< 100\text{ MB}$ | Facilitates simultaneous Windows IDE editing and Git version control |
| **Raw Datasets (`data/raw/`)** | `/mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard/data/raw/` | NTFS | $\le 5.0\text{ GB}$ (Hard Limit) | **STRICT POLICY:** Ingest only tabular metadata, facial feature matrices, and small sample extracts ($\le 5\text{ GB}$). Full multi-hundred-GB raw video archives are strictly prohibited. |
| **Streaming Checkpoints (`data/interim/`)**| `/mnt/c/.../data/interim/` or `/tmp/crisisguard/` | ext4 / NTFS | $\approx 2.0\text{ GB}$ | High-frequency offset and state-store writes for Spark Structured Streaming |
| **Processed Tables (`data/processed/`)** | `/mnt/c/.../data/processed/` | NTFS / Parquet | $\approx 5.0\text{ GB}$ | Partitioned Parquet and ORC warehouse tables for Hive querying |
| **ML Models (`models/`)** | `/mnt/c/.../models/` | NTFS | $\approx 1.0\text{ GB}$ | Serialized MLlib PipelineModels, vector metadata, and evaluation logs |
| **Logs (`logs/`)** | `/mnt/c/.../logs/` | NTFS | $\approx 500\text{ MB}$ | Rotating application and daemon execution logs with 50 MB rollover |

---

## 3. Storage Analysis: Deepfake Video vs. Feature Matrices

1. **The Raw Deepfake Data Problem:**
   - DFDC raw video: ~470 GB compressed, $> 1$ TB uncompressed.
   - FaceForensics++ raw video: ~500 GB uncompressed.
   - Total Host C: available: **237 GB**. Attempting to download full raw video corpora would guarantee a disk exhaustion crash.
2. **The CrisisGuard Solution:**
   - Use authentic pre-extracted facial feature tables (frame-level face crops, bounding box metadata, pre-computed Inception/EfficientNet feature embeddings, and genuine ground-truth authenticity labels) from verified research sources.
   - Maintain a small sample evaluation set ($\le 50$ video clips, $\approx 500$ MB) for end-to-end video pipeline demonstration.
   - This conforms 100% to course data transparency rules while preserving disk integrity.
