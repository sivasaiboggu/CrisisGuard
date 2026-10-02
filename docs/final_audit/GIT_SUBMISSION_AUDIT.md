# CRISISGUARD — GIT & SUBMISSION CLEANLINESS AUDIT

**Author:** B.SIVASAI  
**Roll Number:** 2023BCS0228  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Audit Target:** Git Hygiene, Submission Packaging, Ignored Patterns, and Secrets Verification  
**Policy:** No destructive Git operations (`git reset`, `git clean`, force push) permitted.

---

## 1. Secrets & Credentials Scan Results

A full-repository automated regex and pattern audit was executed targeting:
- API keys, Auth Tokens, Bearer Tokens, Passwords, Private Keys
- Connection strings, AWS/GCP/Azure credentials

### Findings:
- **Real Secrets Detected:** **0**
- **Findings Summary:** Only harmless configuration templates and environment placeholders exist in `.env.example`.
- **Verdict:** **100% SECURE FOR ACADEMIC SUBMISSION**.

---

## 2. Machine-Specific Paths Audit

A comprehensive search for hard-coded absolute paths (`C:\Users\...`, `/home/sivasai/...`, `/mnt/c/Users/...`) identified 12 files:
- Documentation audit logs (`ENVIRONMENT_AUDIT.md`, `WSL_BASELINE.md`, `PHASE5_PREINSTALL_AUDIT.md`, `RESOURCE_PLAN.md`) which record the historical WSL2 host environment.
- Local metastore configuration (`metastore_db/service.properties`).
- Integration test smoke scripts (`test_hive_smoke.py`, etc.).

### Recommendation for Portable Submission:
- Core production scripts already utilize relative path resolution (`Path(__file__).resolve().parents[...]`) or environment variables (`SPARK_HOME`, `HADOOP_HOME`, `HDFS_BASE`).
- Retain documentation logs as historical audit evidence of the exact hardware/OS environment on which the pipeline was executed.

---

## 3. Git Ignore & Tracked Artifact Audit

### 3.1 Recommended `.gitignore` Rules:
Ensure the following patterns are enforced prior to final submission archive:
```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# OS / Tooling metadata
.DS_Store
._*
.Rhistory
*.tmp
*.bak

# Spark / Hive Runtime Artifacts
derby.log
metastore_db/*.lck

# Build directories
target/
project/project/
project/target/
```

### 3.2 Submission Package Size Profile:
- **Total Workspace Size:** 774.35 MB
- **Core Code & Docs:** ~1.5 MB
- **Frozen Models:** 299.39 MB (required for inference reproducibility)
- **Frozen Datasets & Manifests:** 233.90 MB (required for data provenance)
- **Validation Suite:** 176.09 MB (NIST/DARPA test suite)
- **Frozen Features & Ledger:** 63.11 MB (GraphX & Phase 9 outputs)
