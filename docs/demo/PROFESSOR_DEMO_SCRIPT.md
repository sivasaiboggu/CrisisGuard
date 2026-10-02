# CrisisGuard — Professor Demonstration Script & Verbal Walkthrough

**Author:** B.SIVASAI (Roll Number: 2023BCS0228)  
**Course:** CSE412 — Big Data & Large-Scale Computing  
**Project:** CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization  

---

## Presentation Overview

| Duration | 10–12 Minutes |
|:---|:---|
| **Speaker** | B.Sivasai (2023BCS0228) |
| **Audience** | Professor & Evaluation Panel |
| **Goal** | Demonstrate end-to-end Big Data pipeline functionality, distributed graph analytics, real-time streaming, and rigorous data integrity. |

---

## Stage 1: Introduction & Problem Context (1.5 Minutes)

### Spoken Script:
> *"Respected Professors and Evaluators, good morning.*  
> *My name is B.Sivasai, roll number 2023BCS0228. Today I present CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media Propagation Analysis and Emergency Response Prioritization.*
>
> *During major humanitarian crises—such as flash floods or earthquakes—emergency responders face two massive Big Data challenges simultaneously:*
> 1. *First, an avalanche of high-velocity social media messages, where identifying authentic distress calls requires scalable NLP.*
> 2. *Second, the weaponization of synthetic media—deepfake images and manipulated videos—which propagate across social networks, triggering false panics and misdirecting physical emergency resources.*
>
> *CrisisGuard addresses this by deploying a Big Data pipeline architecture that unifies real-time event streaming via Kafka, distributed stream processing with Apache Spark Structured Streaming, large-scale graph analytics via Spark GraphX, reliable storage via Hadoop HDFS, and analytical querying via Apache Hive."*

---

## Stage 2: Architecture & Infrastructure Walkthrough (2 Minutes)

### Spoken Script:
> *"Let us examine the architecture. The pipeline operates across four tiers:*
>
> 1. **Ingestion Tier:** *Apache Kafka acts as our distributed event buffer, decoupling high-velocity publishers from analytical consumers. Kafka guarantees ordering within partitions and durable replay.*
> 2. **Processing Tier:** *Apache Spark runs in two modes:*
>    - *Spark GraphX runs distributed PageRank and Connected Components on our 7,494-vertex propagation network.*
>    - *Spark Structured Streaming executes continuous micro-batches with a 1-hour event-time watermark and 1-hour tumbling temporal windows.*
> 3. **Storage Tier:** *Apache Hadoop HDFS provides scalable, fault-tolerant persistence with 3x replication.*
> 4. **Analytical & Governance Tier:** *Apache Hive manages our warehouse tables, feeding into our Phase 9 Multi-Stream Decision Ledger of 175,361 rows.*
>
> *Let us first verify that our Big Data infrastructure is live and operational."*

### Action:
```bash
python scripts/demo/check_demo_environment.py
```

### Verbal Commentary on Output:
> *"As you can see on the screen, our health check confirms:*
> - *Hadoop HDFS NameNode is active on port 9000 with over 900 GB of capacity.*
> - *Apache Kafka is reachable on port 9092 with all required topics.*
> - *Apache Spark 3.5.1 and our compiled GraphX assembly JAR of 13,092 bytes are ready.*
> - *The Apache Hive Derby metastore is present.*
> - *All 9 machine learning and Big Data packages are verified.*
> *The entire environment reports PASS."*

---

## Stage 3: Live Multimodal Inferences (2.5 Minutes)

### Spoken Script:
> *"Before streaming events, let us demonstrate our underlying machine learning forensics models.*
>
> *In Phase 6, we deployed dual ResNet-18 architectures for image and video forensics. Notice an important scientific detail: in accordance with strict academic honesty, our outputs are explicitly labeled UNCALIBRATED, as raw Sigmoid probabilities should not be misrepresented as calibrated empirical likelihoods without formal Platt scaling or temperature scaling.*
>
> *Let us run image forensics on an incoming asset:"*

### Action:
```bash
python scripts/demo/run_image_demo.py data/demo/input/sample_image.jpg
```

### Verbal Commentary:
> *"The ResNet-18 binary classifier evaluated the image in ~1,000 ms, outputting a synthetic media risk score and raw logits with full provenance metadata.*
>
> *Now, let us examine our Phase 7 Crisis Information Intelligence engine. We trained a TF-IDF and Logistic Regression classifier on the CrisisMMD humanitarian disaster corpus across 5 classes: affected individuals, infrastructure damage, not humanitarian, other relevant information, and rescue volunteering efforts.*
>
> *Let us classify an emergency tweet:"*

### Action:
```bash
python scripts/demo/run_text_demo.py "Urgent: Water levels reached first floor in Sector 4, elderly residents marooned, dispatch rescue boats now!"
```

### Verbal Commentary:
> *"The model immediately classifies this into 'rescue_volunteering_or_donation_effort' with the full probability distribution across all five categories."*

---

## Stage 4: Live Dynamic Kafka & Spark Streaming Execution (3 Minutes)

### Spoken Script:
> *"Now we come to the core Big Data demonstration: Mode B, our Autonomous Live Demonstration Runner.*
>
> *Here is what will happen dynamically:*
> 1. *The script will generate a new propagation cascade event with a dynamic, cryptographically unique UUID event ID.*
> 2. *It will publish this event to our Apache Kafka broker on the topic 'crisisguard-demo-events'.*
> 3. *It will launch Apache Spark Structured Streaming.*
> 4. *Spark will parse the JSON payload, apply a 1-hour event-time watermark, and compute 1-hour tumbling window aggregations.*
> 5. *It will write the output to both local Parquet and to the Hadoop HDFS cluster.*
> 6. *Finally, it will verify that the exact dynamic event ID exists in the output storage, guaranteeing zero data loss and 100% end-to-end traceability.*
>
> *Let us run it live."*

### Action:
```bash
python scripts/demo/run_live_demo.py
```

### Verbal Commentary while Running:
> *"The pipeline is now executing:*
> - *Step 1: Environmental health check passes.*
> - *Step 2: Dual model inferences execute.*
> - *Step 3: A dynamic event with ID `demo_live_...` is generated and confirmed by the Kafka broker at partition 0.*
> - *Step 4: Spark Structured Streaming initializes, loads the Kafka source, applies the watermark, and executes the micro-batch.*
> - *Step 5: Notice the verification output: the exact dynamic event ID is discovered in the local Parquet table and confirmed in HDFS under `/crisisguard/demo/streaming/`.*
> - *Notice the tumbling window summary table: it aggregates window event count, unique source nodes, unique target nodes, mean synthetic risk, and cascade propagation rate per minute.*
> - *Step 6: The demonstration scorecard confirms 10/10 PASS."*

---

## Stage 5: Governance & The "NO_VALID_JOIN" Principle (1.5 Minutes)

### Spoken Script:
> *"Before concluding, I would like to highlight our project's core contribution to Big Data Governance: the NO_VALID_JOIN principle.*
>
> *In many naive multi-stream pipelines, students perform arbitrary joins across heterogeneous datasets—for instance, joining Twitter IDs with OpenStreetMap node IDs using synthetic foreign keys, or computing arbitrary weighted composite scores like 'EDPI'.*
>
> *In CrisisGuard, we conducted a rigorous Key Overlap Audit across our 7 datasets and proved that key overlap is exactly 0.00%. Rather than fabricating false relational joins or arbitrary scoring formulas, CrisisGuard implements an additive multi-stream ledger of 175,361 rows in Phase 9.*
>
> *Each record retains strict source provenance, cross-stream fields are explicitly set to NULL, and decision-makers are provided unadulterated evidence streams.*
>
> *Both our Final Project Master Validator and our Functional Acceptance Test suite verify 10/10 PASS across all 15 frozen research artifacts."*

### Action:
```bash
python scripts/validation/validate_final_project.py
```

---

## Stage 6: Conclusion & Viva Readiness (1 Minute)

### Spoken Script:
> *"In conclusion, CrisisGuard demonstrates that enterprise Big Data pipelines can achieve both high-throughput real-time streaming and uncompromising scientific rigor.*
>
> *All source code, Kafka configs, Spark scripts, GraphX Scala code, HDFS pipelines, Hive tables, and validation suites are fully documented, containerized, and reproducible.*
>
> *I am now ready to answer your questions. Thank you."*
