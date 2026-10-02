# CrisisGuard — Live User Input CLI Guide (Mode A)

**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  

---

## 1. Overview

The `scripts/demo/crisisguard_input.py` CLI provides a unified interface for ingesting real-time user data into CrisisGuard across all four input streams:
1. **Propagation Cascade Events** (`--type propagation`)
2. **Crisis Information Text** (`--type text`)
3. **Synthetic Media Image Forensics** (`--type image`)
4. **Synthetic Media Video Forensics** (`--type video`)

Every input is validated against schema contracts before transmission to Apache Kafka, ensuring strict structural integrity and zero downstream consumer crashes.

---

## 2. Propagation Events (`--type propagation`)

### 2.1 Interactive Prompt Mode
When invoked without required arguments, the tool prompts interactively:
```bash
.venv/bin/python scripts/demo/crisisguard_input.py --type propagation
```
**Prompts:**
- Source Node ID: `osm_node_1001`
- Target Node ID: `osm_node_1002`
- Scenario ID: `delhi_monsoon_flood_2026`
- Synthetic Media Risk: `0.88`
- Priority: `CRITICAL`
- Propagation Type: `retweet_cascade`

### 2.2 Direct Command-Line Arguments
```bash
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type propagation \
  --source-node osm_node_552190 \
  --target-node osm_node_884102 \
  --scenario yamuna_crest_surge \
  --risk 0.92 \
  --priority CRITICAL \
  --topic crisisguard-demo-events
```

### 2.3 JSON File Ingestion
```bash
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type propagation \
  --file data/demo/input/sample_propagation_event.json \
  --topic crisisguard-demo-events
```

### 2.4 Dry-Run Validation Mode
Validate schema conformity without sending to Kafka:
```bash
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type propagation \
  --source-node osm_node_100 \
  --target-node osm_node_200 \
  --risk 0.75 \
  --dry-run
```

---

## 3. Crisis Text Intelligence (`--type text`)

Analyzes emergency messages and tweets using Phase 7's trained CrisisMMD TF-IDF + Logistic Regression classifier.

### 3.1 Direct Text String
```bash
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type text \
  --text "CRITICAL: Embankment collapsed at Sector 5, 200 residents marooned on rooftops!"
```
**Outputs:**
- Predicted Humanitarian Category (e.g. `rescue_volunteering_or_donation_effort`)
- Model Confidence Score (%)
- Full 5-class Probability Distribution with ASCII bar chart
- Latency (ms)

### 3.2 Convenient Wrapper CLI
```bash
.venv/bin/python scripts/demo/run_text_demo.py "Need medical team and potable water at shelter 3 immediately"
```

---

## 4. Synthetic Media Forensics (`--type image` & `--type video`)

### 4.1 Image Forensics (ResNet-18)
Ingests an arbitrary image and evaluates synthetic media risk:
```bash
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type image \
  --path data/demo/input/sample_image.jpg
```
Or via wrapper:
```bash
.venv/bin/python scripts/demo/run_image_demo.py data/demo/input/sample_image.jpg
```

**Output Semantics:**
- Raw Logits (`model_score`)
- Uncalibrated Sigmoid Probability (`synthetic_media_risk`)
- Classification: `SYNTHETIC / MANIPULATED` ($\ge 0.5$) vs `AUTHENTIC / REAL` ($< 0.5$)
- Calibration Notice: `UNCALIBRATED` (Standard Sigmoid on frozen ResNet-18 checkpoint)

### 4.2 Video Temporal Forensics (ResNet-18 Temporal Extractor)
Ingests a video or animated GIF and evaluates temporal manipulation risk:
```bash
.venv/bin/python scripts/demo/crisisguard_input.py \
  --type video \
  --path data/demo/input/sample_video.gif
```
Or via wrapper:
```bash
.venv/bin/python scripts/demo/run_video_demo.py data/demo/input/sample_video.gif
```

---

## 5. Kafka Destination Isolation

| Parameter | Default | Description |
|:---|:---|:---|
| `--topic` | `crisisguard-demo-events` | Dedicated isolated topic preventing pollution of frozen Phase 8 production streams |
| `--bootstrap-servers` | `localhost:9092` | Kafka broker endpoint |
| `--publish` | `False` | For text/image/video, packages output into an intelligence record and transmits to Kafka |

---

## 6. Safety & Governance Notes

1. **Isolation Guarantee:** All user inputs target `crisisguard-demo-events` unless explicitly overridden.
2. **Schema Protection:** Input schemas strictly match Phase 8 event contracts.
3. **No Frozen Modifications:** CLI never writes to `data/features/` or `data/processed/`.
