# CrisisGuard: WSL2 Subsystem Baseline Verification & Toolchain Architecture

**Document Version:** 1.0.0  
**Verification Date:** 2026-09-27  
**Subsystem Runtime:** Ubuntu 24.04.4 LTS (Noble Numbat) on WSL2  
**Kernel:** Linux 6.6.87.2-microsoft-standard-WSL2 (x86_64)  

---

## 1. WSL Subsystem Status & Host Integration

* **WSL Default Version:** 2 (`wsl --status`)
* **Default Distribution:** `Ubuntu-24.04` (State: Stopped/Active on demand)
* **Secondary Distribution:** `docker-desktop` (State: Stopped)
* **Cross-Filesystem Access Point:**
  - Windows project path: `C:\Users\HP\OneDrive\Desktop\CrisisGuard\`
  - WSL mounted path: `/mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard/`

---

## 2. Package Manager Verification
* Executed `apt-get update` against official Ubuntu Noble repositories (`noble-security`, `noble-updates`, `noble-backports`).
* Successfully fetched and indexed 11.6 MB in 9 seconds.
* Package management is 100% operational and healthy.

---

## 3. Java Runtime Inspection

Audit of `/usr/lib/jvm/` revealed two pre-installed OpenJDK LTS environments:
1. `java-8-openjdk-amd64` (JRE: `1.8.0_502`, Priority: 1081)
2. `java-11-openjdk-amd64` (JDK: `11.0.x`, Priority: 1111)

**Decision:**
* Standardize on **OpenJDK 11** (`/usr/lib/jvm/java-11-openjdk-amd64`) for the Big Data stack.
* OpenJDK 11 satisfies the universal compatibility overlap between Apache Spark 3.5.x, Apache Kafka 3.7.x, and Apache Hadoop 3.3.6 without requiring any external repository installations.

---

## 4. Python Environment Architecture

* **System Python:** Python 3.12.3 (`/usr/bin/python3`)
* **Python Runtime Strategy:**
  - Create a dedicated virtual environment: `CrisisGuard/.venv` via `python3 -m venv .venv`.
  - Install project-specific packages: `pyspark==3.5.1`, `kafka-python-ng`, `pyyaml`, `pandas`, `numpy`.
  - Strictly isolate the pipeline from the Windows host Python 3.14 installation to eliminate PySpark serialization errors.

---

## 5. Storage Capacity Breakdown

* **WSL Native Ext4 Filesystem (`/dev/sdd` mounted on `/`):**
  - Total Size: **1,007 GB**
  - Used: **13 GB**
  - Available: **943 GB** (98% free)
* **Windows Host Drive (`/mnt/c`):**
  - Total Size: **476 GB**
  - Used: **240 GB**
  - Available: **237 GB** (50% free)

**Storage Policy:**
* Maintain project source files and processed Parquet tables on `/mnt/c/.../CrisisGuard/` so both Windows tools/IDE and WSL processes interact seamlessly.
* Leverage WSL native disk (`/tmp/` or ext4 symlinks) if high-throughput scratch I/O is required for Spark shuffle spills.

---

## 6. Docker Desktop Evaluation

* **Audit Result:** Docker CLI 29.5.3 is installed, but Docker Desktop is stopped.
* **Architecture Decision:** **Docker is NOT required.**
  - WSL2 runs a genuine Linux kernel with complete POSIX compatibility and system isolation.
  - Running Kafka, Spark, and Hive natively inside WSL2 avoids Docker Desktop memory overhead (which typically claims 2–4 GB host RAM just for container engine daemons).
  - A WSL-native deployment provides cleaner execution traces, faster filesystem throughput, and direct terminal debugging.
