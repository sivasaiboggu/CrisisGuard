# CrisisGuard: Comprehensive Data Quality & Cleaning Profile

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Document Standard:** Rule-Governed Quality Assessment & Cleaning Directives  

---

## 1. Global Quality Assessment Matrix

| Dataset | Total Records | Missing Values | Missing % | Duplicates | Dup % | Invalid Records | Quality Decision | Primary Cleaning Action |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Google DFD Sample** | 4 media | 0 | 0.00% | 0 | 0.00% | 0 | **KEEP** | Frame extraction & feature assembly |
| **CIFAKE** | 500 images | 0 | 0.00% | 0 | 0.00% | 0 | **KEEP** | Verified SHA256 & spatial/frequency features |
| **HumAID** | 76484 | 76,484 (text) | 100.0% (text) | 0 | 0.00% | 0 | **CLEAN** | Category preserved, null text recorded |
| **CrisisMMD** | 8079 | 0 (text) | 0.00% | 0 | 0.00% | 0 | **CLEAN** | Unicode NFKC, URL/mention normalization |
| **CrisisLex** | 88015 | 0 (text) | 0.00% | 4 | 0.005% | 0 | **CLEAN** | Deduplicated tweet IDs, Unicode cleaning |
| **OpenStreetMap** | 146156 edges | 141,788 (speed)| 97.01% (speed)| 0 | 0.00% | 0 | **CLEAN** | Haversine distance computed, speed NULL preserved |
| **Propagation** | 5004 events | 0 | 0.00% | 0 | 0.00% | 0 | **KEEP** | Enforced SEMI_SYNTHETIC tag validation |

---

## 2. Quality Decisions Rationale (KEEP / CLEAN / EXCLUDE)

1. **Google DFD-Derived Sample (`KEEP`):** All 4 canonical media assets and 12 sampled frames have verified dimensions, valid TUM partition splits, and complete metadata.
2. **CIFAKE (`KEEP`):** 500 images strictly verified for JPEG header validity, 32x32x3 geometry, and balanced labels (250 real / 250 synthetic). Zero corrupted or unreadable files.
3. **HumAID (`CLEAN`):** 76,484 records across 10 humanitarian classes preserved. Missing text in the `all_combined` split is documented explicitly without fabricating synthetic text.
4. **CrisisMMD (`CLEAN`):** 8,079 multimodal records. Cleaned URLs and mentions while retaining `raw_text`. Image references retained with honest `image_available_locally: False` flag.
5. **CrisisLex (`CLEAN`):** 88,015 records across 32 crises. Removed 4 redundant duplicate ID rows. Normalized whitespace and HTML escape codes into `clean_text`.
6. **OpenStreetMap (`CLEAN`):** 63,660 nodes and 146,156 edges. Geodesic distance computed. Missing speed tags left as NULL to preserve data authenticity.
7. **Semi-Synthetic Propagation (`KEEP`):** 5,004 events and 4,999 edges verified with valid tree structures and zero governance tag corruption.

---

## 3. Duplicate Detection Policy & Results

* **Structured Records:** Evaluated via composite primary keys `(source_dataset, source_record_id)`.
* **Images:** Verified via cryptographic SHA256 hashes of raw byte contents. Zero duplicate hashes in CIFAKE.
* **Videos / Frames:** Verified via file hashes and frame index identifiers.
* **Policy on Natural Repetition:** Multiple tweets referencing identical disaster events across different days are recognized as natural observations and preserved.
