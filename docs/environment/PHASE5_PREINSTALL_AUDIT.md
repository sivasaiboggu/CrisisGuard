# CrisisGuard: Phase 5 Pre-Installation Environment Audit

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  
**Timestamp:** 2026-09-27T16:15:30+05:30  
**Phase Status:** Phase 5 Pre-Installation Audit Complete  

---

## 1. Host & Virtualization Architecture

| Parameter | Observed Value | Evaluation / Status |
| :--- | :--- | :--- |
| **Host Operating System** | Microsoft Windows 11 Home Single Language (Build 10.0.26200) | Valid host environment |
| **Architecture** | x86_64 / AMD64 | 64-bit architecture compatible with Big Data binaries |
| **CPU Model** | AMD Ryzen 7 7445HS w/ Radeon 740M Graphics | 6 Physical Cores / 12 Logical Processors |
| **Host Physical RAM** | 16 GB (15,973,788 KB visible) | Sufficient for containerized / WSL2 micro-cluster |
| **WSL Version** | WSL2 (Virtualization platform) | Native Linux syscall translation |
| **Active WSL Distribution** | `Ubuntu-24.04` (State: Running, Version 2) | Dedicated execution substrate |
| **WSL Kernel** | Linux 6.6.87.2-microsoft-standard-WSL2 | Modern LTS Linux kernel |
| **WSL OS Version** | Ubuntu 24.04.4 LTS (Noble Numbat) | Verified stable Linux distribution |

---

## 2. Resource & Storage Audit

| Resource | Total Allocated | Currently Used | Available | Utilization % | Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **WSL Memory (RAM)** | 7.4 GiB | 606 MiB | 6.8 GiB | 8% used | Abundant headroom for local Hadoop/Spark/Kafka nodes |
| **WSL Swap** | 2.0 GiB | 0 B | 2.0 GiB | 0% used | Clean swap baseline |
| **WSL Root Filesystem (`/`)** | 1007 GiB (`/dev/sdd`) | 13 GiB | 943 GiB | 2% used | **943 GiB free** — optimal for HDFS and Kafka data logs |
| **Windows Host Mount (`/mnt/c`)** | 476 GiB | 240 GiB | 237 GiB | 51% used | 237 GiB free on Windows C: |

> [!IMPORTANT]
> To eliminate Windows filesystem translation latency (`/mnt/c/`), all Big Data runtime storage (HDFS data blocks, Kafka logs, Spark local scratch dirs) will be provisioned directly within the native Linux ext4 filesystem (`/var/crisisguard/` or `/opt/crisisguard/`). Project code and processed Parquet tables remain linked to `/mnt/c/Users/HP/OneDrive/Desktop/CrisisGuard/`.

---

## 3. Runtimes & Dependency Audit

| Component | Target Version | Observed Version | Current Path | Status / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **Python** | 3.12.x | Python 3.12.3 | `/usr/bin/python3` | **PASS** — Ready for PySpark and validation |
| **Java 11** | OpenJDK 11 LTS | Installed: `java-11-openjdk-amd64` | `/usr/lib/jvm/java-11-openjdk-amd64` | **PASS** — Present; configure `JAVA_HOME` explicitly |
| **JAVA_HOME** | Path to Java 11 | Not set in default shell | None | Action: Export `/usr/lib/jvm/java-11-openjdk-amd64` |
| **Git** | >= 2.x | git version 2.43.0 | `/usr/bin/git` | **PASS** — Operational |
| **Network Connectivity**| External Internet | ping archive.ubuntu.com: 0% loss; curl dlcdn.apache.org: HTTP 200 | Operating | **PASS** — Direct access to Apache repositories |

---

## 4. Big Data Stack Audit (Pre-Installation Baseline)

| Big Data Tool | Target Version | Currently Installed? | Path | Status |
| :--- | :--- | :---: | :--- | :--- |
| **Scala** | 2.12.18 | **No** | None | Pending Step 4 installation |
| **Apache Hadoop** | 3.3.6 | **No** | None | Pending Step 5 installation |
| **Apache Spark** | 3.5.1 | **No** | None | Pending Step 6 installation |
| **Apache Kafka** | 3.7.0 | **No** | None | Pending Step 8 installation |
| **Apache Hive** | Compatible (3.1.3 / Metastore) | **No** | None | Pending Step 10 installation |

---

## 5. Audit Conclusion

The execution environment meets all prerequisites:
1. Native WSL2 Linux kernel with 12 logical vCPUs and 6.8 GiB available memory.
2. 943 GiB available on Linux native ext4 storage.
3. OpenJDK 11 is already installed; setting `JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64` satisfies the Java requirement.
4. Python 3.12.3 and Git 2.43.0 are verified.
5. All target Big Data components are currently absent, ensuring a completely clean installation and validation trajectory.
