# CrisisGuard: Master Dataset Statistics Report

**Author:** B.SIVASAI (Roll No: 2023BCS0228)  
**Status:** Phase 4 Audited Baseline  

---

## Comparative Dataset Statistics Table

| Dataset | Raw Records / Files | Valid Records | Excluded | Duplicates | Missing Values | Classes | Dominant Class (%) | Temporal Range | Location Coverage | Processed Size |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: |
| **Google DFD Sample** | 9 files | 4 media / 12 frames | 0 | 0 | 0 | 2 (real/fake) | Manipulated (75%) | N/A (Video clips) | Lab actors | 0.02 MB |
| **CIFAKE** | 500 images | 500 images | 0 | 0 | 0 | 2 (real/syn) | Balanced (50% / 50%) | N/A (Image set) | Web / Diffusion | 0.16 MB |
| **HumAID** | 76,484 rows | 76,484 rows | 0 | 0 | 76,484 (text) | 10 categories | Rescue effort (27.8%) | 2016 – 2019 | 19 global disasters | 12.47 MB |
| **CrisisMMD** | 8,079 rows | 8,079 rows | 0 | 0 | 0 (text) | 5 categories | Not humanitarian (52.9%)| 2017 – 2018 | 7 disaster zones | 5.51 MB |
| **CrisisLex** | 88,019 rows | 88,015 rows | 4 (dups) | 4 | 0 (text) | Multi-class | Informative (~65%) | 2012 – 2013 | 32 disaster zones | 43.34 MB |
| **OpenStreetMap** | 468,038 nodes | 63,660 nodes | 0 | 0 | 141,788 (speed)| 20+ road types | Residential (46.0%) | 2026 OSM extract | Southern India | 3.85 MB |
| **Propagation** | 5,004 events | 5,004 events | 0 | 0 | 0 | 3 scenarios | Organic (60.9%) | 2026-09-27 stream | Synthetic network | 2.24 MB |
