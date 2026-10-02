# CrisisGuard: End-to-End Preprocessing Lineage & Transformations

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Document Standard:** Provenance Traceability & Deterministic Transformation Flow  

---

## 1. Transformation Flow Architecture

```
RAW DATA (data/raw/) [IMMUTABLE]
       │
       ▼
VALIDATION & INVENTORY (Integrity, Hashing, Schema Check)
       │
       ▼
CLEANING & NORMALIZATION (Unicode NFKC, Whitespace, HTML unescape, Haversine)
       │
       ▼
CANONICAL INTERIM PARTITION (data/interim/) [CSV/JSONL]
       │
       ▼
FEATURE EXTRACTION & PREPARED STRUCTURES (data/features/ & data/processed/) [Parquet]
```

---

## 2. Dataset-Specific Preprocessing Lineage

| Dataset | Input Path | Processing Script | Transformation Parameters | Output Location | Seed | Raw Records | Processed Records |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **Google DFD-Derived Sample** | `data/raw/deepfake_dfd/` | `scripts/preprocessing/preprocess_deepfake_dfd.py` | Keyframe stride sampling, Laplacian variance, RGB mean/std | `data/interim/deepfake_dfd/ & data/processed/deepfake_dfd/` | 42 | 4 | 12 |
| **CIFAKE Benchmark** | `data/raw/synthetic_media_eval/` | `scripts/preprocessing/preprocess_cifake.py` | SHA256 verification, 32x32 RGB minmax normalization, FFT 2D energy, Laplacian | `data/interim/cifake/ & data/processed/cifake/` | 42 | 500 | 500 |
| **HumAID Corpus** | `data/raw/humaid/all_combined/` | `scripts/preprocessing/preprocess_humaid.py` | Multi-split consolidation (train/dev/test), 10-class preservation, null text logging | `data/interim/humaid/ & data/processed/humaid/` | 42 | 76484 | 76484 |
| **CrisisMMD Multimodal** | `data/raw/crisismmd/crisismmd_datasplit_agreed_label/` | `scripts/preprocessing/preprocess_crisismmd.py` | Unicode NFKC, URL tokenization, honest image reference tagging | `data/interim/crisismmd/ & data/processed/crisismmd/` | 42 | 8079 | 8079 |
| **CrisisLex Collections** | `data/raw/crisislex/data/` | `scripts/preprocessing/preprocess_crisislex.py` | T26 + T6 consolidation across 32 events, deduplication of 4 IDs, Unicode cleaning | `data/interim/crisislex/ & data/processed/crisislex/` | 42 | 88019 | 88015 |
| **OpenStreetMap** | `data/raw/osm/regional_extract.osm.pbf` | `scripts/preprocessing/preprocess_osm.py` | Osmium two-pass highway parsing, Geodesic Haversine edge distance, NULL speed retention | `data/interim/osm/ & data/processed/osm/` | 42 | 468038 | 63660 |
| **Propagation Cascades** | `data/generated/propagation/` | `scripts/preprocessing/preprocess_propagation.py` | NetworkX topology metrics, parent-child link validation, SEMI_SYNTHETIC tag verification | `data/interim/propagation/ & data/processed/propagation/` | 42 | 5004 | 5004 |
