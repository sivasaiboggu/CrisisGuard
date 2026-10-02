# CrisisGuard: Phase 1 — Development Environment Audit Report

**Date:** 2026-09-26  
**Auditor:** Senior Big Data & ML Engineering Mentor  
**Host Platform:** Microsoft Windows 11 Home Single Language (64-bit)  
**WSL2 Subsystem:** Ubuntu 24.04 LTS (Kernel: Linux 6.6.x)  

---

## 1. System Hardware & Host Resources

| Hardware Metric | Host Specification | Status / Evaluation |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 Home Single Language (Version 10.0.26200) | Validated Host OS |
| **Architecture** | 64-bit (`x86_64` / AMD64) | Standard distributed computing architecture |
| **CPU Model** | AMD Ryzen 7 7445HS w/ Radeon 740M Graphics | High performance (6 physical cores, 12 logical threads) |
| **Total Memory (RAM)** | 15.23 GB Visible (16 GB Physical) | Sufficient for local distributed pipeline (Kafka + Spark + MLlib) |
| **Free Memory** | ~1.98 GB available currently | Host background processes need headroom; allocations must be budgeted |
| **Host Disk Space (C:)** | **236.45 GB Free** (out of 475.8 GB total) | **CRITICAL CONSTRAINT:** Cannot store full raw video corpora |
| **WSL2 Virtual Disk** | **943 GB Available** (ext4 filesystem) | Substantial capacity for interim features and Parquet warehouse |

---

## 2. Component Inventory & Audit Matrix

| Component | Installed | Version | Path | Working | Notes |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **Operating System** | Yes | 10.0.26200 | `C:\Windows` | Yes | Windows 11 64-bit |
| **Architecture** | Yes | x86_64 | N/A | Yes | Native AMD64 |
| **Python (Host)** | Yes | 3.14.3 | `C:\Users\HP\AppData\Local\Microsoft\WindowsApps\python.exe` | Yes | Cutting-edge version; PySpark official wheels currently target Python $\le$ 3.12 |
| **Python (WSL2)** | Yes | 3.12.3 | `/usr/bin/python3` (WSL Ubuntu-24.04) | Yes | **Optimal for PySpark 3.5.x** |
| **Java (Host)** | Yes | 17.0.19 LTS | `C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot\bin\java.exe` | Yes | OpenJDK 17 Microsoft build; `JAVA_HOME` set |
| **Java (WSL2)** | Yes | 1.8.0_502 | `/usr/bin/java` (WSL Ubuntu-24.04) | Yes | OpenJDK 8 LTS; compatible with legacy Hadoop/Hive |
| **Scala** | **No** | None | Not found | N/A | Missing on both Host and WSL2 |
| **Git** | Yes | 2.53.0.windows.2 | `C:\Program Files\Git\cmd\git.exe` | Yes | Fully functional |
| **Docker** | Partial | 29.5.3 | `C:\Program Files\Docker\Docker\resources\bin\docker.exe` | **No** | CLI installed; Docker Desktop daemon is stopped |
| **WSL2** | Yes | WSL 2 | `C:\Windows\System32\wsl.exe` | Yes | Distro `Ubuntu-24.04` (Default, stopped) and `docker-desktop` |
| **Hadoop / HDFS** | **No** | None | Not found | N/A | `HADOOP_HOME` not set; `hadoop` binary missing |
| **Apache Spark** | **No** | None | Not found | N/A | `SPARK_HOME` not set; `spark-submit` missing; `pyspark` uninstalled |
| **Apache Kafka** | **No** | None | Not found | N/A | `KAFKA_HOME` not set; Kafka broker binary missing |
| **Apache Hive** | **No** | None | Not found | N/A | `HIVE_HOME` not set; Hive CLI / Metastore binary missing |

---

## 3. Workload Suitability & Capacity Analysis

### 3.1 Deepfake Dataset Processing (DFDC, Celeb-DF, FaceForensics++)
* **Constraint:** Raw DFDC is ~470 GB compressed (> 1 TB uncompressed). FaceForensics++ is ~500 GB.
* **Storage Reality:** Host C: has **236.45 GB free**. Attempting to download full uncompressed raw video archives will immediately exhaust disk space and crash the system.
* **Suitability Verdict:** **SUITABLE VIA FEATURE EXTRACTION / SUBSETS ONLY.**
  - Strictly adhere to downloading metadata manifests, precomputed face-crop embeddings, frame-level classification scores, and small verified evaluation samples ($\le$ 5 GB).
  - Raw multi-hundred-gigabyte video dumps must remain prohibited.

### 3.2 Crisis Datasets (HumAID, CrisisMMD, CrisisLex)
* **Storage Footprint:** Combined compressed size is ~2–8 GB (tabular CSV/TSV, JSON, and select crisis imagery).
* **Suitability Verdict:** **FULLY SUITABLE.** The machine has ample storage and memory to hold and process full crisis corpora.

### 3.3 OpenStreetMap Road Network (Geofabrik)
* **Storage Footprint:** Regional PBF extracts (e.g., state or metropolitan area) are 50–500 MB.
* **Suitability Verdict:** **FULLY SUITABLE.**

### 3.4 Apache Kafka
* **Resource Profile:** KRaft mode or local single-broker Kafka requires ~512 MB to 1 GB RAM.
* **Suitability Verdict:** **FULLY SUITABLE.**

### 3.5 Apache Spark & Spark Structured Streaming
* **Resource Profile:** Spark local mode (`local[*]`) will utilize all 12 CPU threads. A driver allocation of 4 GB RAM will execute sliding-window aggregations without memory pressure.
* **Suitability Verdict:** **FULLY SUITABLE.**

### 3.6 Spark GraphX
* **Resource Profile:** Graph algorithms (PageRank, Connected Components, Shortest Path) across social cascades and road networks ($10^4 - 10^6$ edges) require 2–4 GB RAM in Spark.
* **Suitability Verdict:** **FULLY SUITABLE.**

### 3.7 Spark MLlib
* **Resource Profile:** Gradient-Boosted Trees, Random Forest, and Logistic Regression on tabular feature vectors ($\sim 10^5$ rows $\times$ 20 features) execute within seconds to minutes on this CPU.
* **Suitability Verdict:** **FULLY SUITABLE.**

### 3.8 Apache Hive
* **Resource Profile:** Running Hive through Spark SQL with a local metastore (`derby` or lightweight SQLite/PostgreSQL) and Parquet/ORC storage formats avoids the multi-gigabyte memory overhead of standalone Hadoop YARN/Tez daemons.
* **Suitability Verdict:** **FULLY SUITABLE VIA SPARK-HIVE METASTORE WAREHOUSE.**

---

## 4. Triage Categorization: FOUND, MISSING & BROKEN

### A. FOUND Components (Operational)
1. **Host OS:** Windows 11 64-bit (`10.0.26200`)
2. **CPU & RAM:** AMD Ryzen 7 7445HS (12 threads), 16 GB RAM
3. **Storage:** 236.45 GB on Host C:; 943 GB on WSL2 ext4
4. **Git:** Version 2.53.0.windows.2
5. **WSL2 Subsystem:** Operational with `Ubuntu-24.04` (LTS)
6. **Python (WSL2):** Python 3.12.3 (fully compatible with Spark 3.5.x)
7. **Java (Host):** OpenJDK 17.0.19 LTS (Microsoft Build, `JAVA_HOME` configured)
8. **Java (WSL2):** OpenJDK 1.8.0_502 LTS

### B. BROKEN / DEGRADED Components (Requires Remediation Before Use)
1. **Docker Desktop:** Version 29.5.3 CLI installed, but daemon is stopped (`failed to connect to docker API`).
2. **Host Python Compatibility:** Host has Python 3.14.3. Python 3.14 is currently incompatible with standard PySpark worker serialization. (Remediation: Use WSL2 Python 3.12 or a dedicated Python 3.10/3.11 virtual environment).

### C. MISSING Components (Not Yet Installed)
1. **Apache Kafka** (Broker + KRaft / Zookeeper)
2. **Apache Spark** (Spark Core, Structured Streaming, GraphX, MLlib)
3. **PySpark / kafka-python / PyYAML / findspark** libraries
4. **Scala / sbt** (Required if standalone GraphX jar compilation is chosen)
5. **Hadoop / winutils** (or HDFS compatibility layer)
6. **Apache Hive** (Metastore catalog / warehouse layer)

---

## 5. Architectural Recommendation for Phase 2 Toolchain

Given the Windows 11 host constraints (winutils path issues, Python 3.14 incompatibility) and the presence of healthy **WSL2 Ubuntu 24.04 (Python 3.12 + OpenJDK)**:
* **Option A (Highly Recommended):** Standardize the Big Data toolchain (Kafka, Spark 3.5.x, GraphX, Hive Metastore) inside **WSL2 Ubuntu 24.04** or via **Docker Compose** when Docker Desktop is enabled. This ensures 100% Linux POSIX compliance, zero winutils hacks, and seamless Spark/Hive file operations.
* **Option B (Windows Native):** Install Python 3.11 for Windows, download Spark 3.5.x + winutils for Hadoop 3.3.x, and run Kafka for Windows. (Prone to file-locking and fork issues on Windows).
