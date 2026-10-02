-- CrisisGuard — Phase 8: Hive Analytical Queries
-- Author: B.SIVASAI (Roll Number: 2023BCS0228)
-- Course: CSE412 — Big Data & Large-Scale Computing
-- Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
--          Propagation Analysis and Emergency Response Prioritization

USE crisisguard_phase8;

-- -------------------------------------------------------------
-- Query 1: Top Structurally Central Vertices from GraphX PageRank
-- -------------------------------------------------------------
SELECT 
    vertex_id,
    node_name,
    ROUND(pagerank, 4) AS pagerank_score,
    in_degree,
    out_degree,
    component_id
FROM propagation_graph_metrics
ORDER BY pagerank DESC
LIMIT 10;

-- -------------------------------------------------------------
-- Query 2: Degree Distribution Summary from GraphX Metrics
-- -------------------------------------------------------------
SELECT 
    in_degree,
    COUNT(vertex_id) AS vertex_count,
    ROUND(AVG(pagerank), 4) AS avg_pagerank
FROM propagation_graph_metrics
GROUP BY in_degree
ORDER BY in_degree DESC
LIMIT 10;

-- -------------------------------------------------------------
-- Query 3: Real-Time Stream Progression: Hourly Rate & Synthetic Risk
-- -------------------------------------------------------------
SELECT 
    scenario_id,
    COUNT(window_start) AS active_windows,
    SUM(window_event_count) AS total_events,
    ROUND(AVG(propagation_rate_per_min), 2) AS avg_rate_per_min,
    ROUND(MAX(propagation_rate_per_min), 2) AS peak_rate_per_min,
    ROUND(AVG(mean_synthetic_risk), 4) AS avg_synthetic_risk,
    ROUND(MAX(max_synthetic_risk), 4) AS peak_synthetic_risk
FROM propagation_stream_metrics
GROUP BY scenario_id
ORDER BY total_events DESC;

-- -------------------------------------------------------------
-- Query 4: Synthetic Media Risk Analysis (Phase 6 Outputs)
-- -------------------------------------------------------------
SELECT 
    media_type,
    CASE 
        WHEN synthetic_risk >= 0.7 THEN 'HIGH_RISK'
        WHEN synthetic_risk >= 0.3 THEN 'MEDIUM_RISK'
        ELSE 'LOW_RISK'
    END AS risk_tier,
    COUNT(content_id) AS item_count,
    ROUND(AVG(model_score), 4) AS avg_model_score,
    ROUND(AVG(synthetic_probability), 4) AS avg_synthetic_prob
FROM crisisguard_phase8.media_risk_features
GROUP BY media_type, CASE 
        WHEN synthetic_risk >= 0.7 THEN 'HIGH_RISK'
        WHEN synthetic_risk >= 0.3 THEN 'MEDIUM_RISK'
        ELSE 'LOW_RISK'
    END
ORDER BY media_type, item_count DESC;

-- -------------------------------------------------------------
-- Query 5: Crisis Information Category Distribution (Phase 7 Outputs)
-- -------------------------------------------------------------
SELECT 
    source_dataset,
    crisis_category,
    calibration_status,
    COUNT(content_id) AS total_records,
    ROUND(AVG(model_score), 4) AS avg_confidence
FROM crisis_intelligence_features
GROUP BY source_dataset, crisis_category, calibration_status
ORDER BY total_records DESC
LIMIT 15;

-- -------------------------------------------------------------
-- Query 6: Critical Cross-Stream Join Policy Verification
-- Confirms zero overlap between propagation user nodes and crisis tweet IDs
-- Demonstrates scientific adherence to disjoint feature stream architecture
-- -------------------------------------------------------------
SELECT 
    COUNT(g.vertex_id) AS overlapping_keys_count
FROM propagation_graph_metrics g
JOIN crisis_intelligence_features c
    ON g.node_name = c.source_record_id;
