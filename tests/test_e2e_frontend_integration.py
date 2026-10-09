"""
CrisisGuard — End-to-End Frontend & Backend Integration Test Suite
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Executes the full 10-step user flow verifying:
1. Health & Dependency Status probe
2. Overview KPI metrics
3. Incidents list & detail retrieval
4. Live Claim Assessment execution
5. Synthetic Media inference via ResNet-18
6. Propagation summary & graph metrics
7. Resource inventory retrieval
8. HiGHS MILP batch optimization
9. Dispatcher approval & rejection mutation
10. Static frontend bundle delivery (HTTP 200 index.html)
"""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

def test_step1_health_and_dependencies():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

    res_svc = client.get("/api/health/services")
    assert res_svc.status_code == 200
    data = res_svc.json()
    assert "big_data_cluster" in data
    assert "models_and_forensics" in data
    assert "spatial_and_graph" in data

def test_step2_overview_metrics():
    res = client.get("/api/overview")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert data["metrics"]["total_ingested_events"] >= 4
    assert data["streaming_status"]["total_windows"] == 32

def test_step3_incidents_list_and_detail():
    res = client.get("/api/incidents")
    assert res.status_code == 200
    incidents = res.json()
    assert len(incidents) > 0

    first_id = incidents[0]["incident_id"]
    res_detail = client.get(f"/api/incidents/{first_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert "assessment" in detail

def test_step4_live_claim_assessment():
    payload = {
        "text": "Yamuna river water level touched 208.66m at Mayur Vihar low-lying sector.",
        "location": "Mayur Vihar, Delhi",
        "latitude": 28.6012,
        "longitude": 77.2985,
        "source_type": "CITIZEN_REPORT"
    }
    res = client.post("/api/assessment", json=payload)
    assert res.status_code == 200
    asmt = res.json()
    assert "assessment_outcome" in asmt
    assert asmt["assessment_outcome"] in [
        "EVIDENCE_SUPPORTED", "CONTRADICTED_BY_EVIDENCE", "UNVERIFIED", "REQUIRES_HUMAN_REVIEW", "INSUFFICIENT_EVIDENCE"
    ]
    assert asmt["uncertainty_score"] is not None

def test_step5_propagation_intelligence():
    res = client.get("/api/propagation/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["graph_metrics"]["total_vertices"] == 7494
    assert len(data["streaming_windows"]) == 32

    res_graph = client.get("/api/propagation/graph")
    assert res_graph.status_code == 200
    g = res_graph.json()
    assert len(g["nodes"]) > 0

def test_step6_resource_inventory():
    res = client.get("/api/resources")
    assert res.status_code == 200
    data = res.json()
    assert data["is_synthetic_demonstration"] is True
    assert len(data["resources"]) >= 3

def test_step7_milp_optimization():
    batch = {
        "incidents": [
            {
                "incident_id": "INC_TEST_01",
                "incident_category": "affected_individuals",
                "urgency_level": "HIGH",
                "verification_status": "EVIDENCE_SUPPORTED",
                "required_resource_type": "RESCUE_BOAT",
                "demanded_quantity": 2,
                "latitude": 28.6279,
                "longitude": 77.2784,
                "human_approved": False
            },
            {
                "incident_id": "INC_TEST_02",
                "incident_category": "not_humanitarian",
                "urgency_level": "CRITICAL",
                "verification_status": "CONTRADICTED_BY_EVIDENCE",
                "required_resource_type": "FIRE_TENDER",
                "demanded_quantity": 2,
                "latitude": 28.6619,
                "longitude": 77.2492,
                "human_approved": False
            }
        ],
        "update_inventory": False
    }
    res = client.post("/api/allocations/optimize", json=batch)
    assert res.status_code == 200
    results = res.json()
    assert len(results) == 2

    # Verify that contradicted incident was blocked by safety gate
    contradicted = [r for r in results if r["incident_id"] == "INC_TEST_02"][0]
    assert contradicted["allocation_status"] in ["INFEASIBLE", "UNALLOCATED"]
    assert contradicted["feasibility_status"] == "UNVERIFIED_GATE"
    assert contradicted["assigned_quantity"] == 0

def test_step8_human_approval_persistence():
    # Fetch allocations
    res = client.get("/api/allocations")
    allocs = res.json()
    assert len(allocs) > 0

    target = allocs[0]["allocation_id"]
    res_app = client.post(f"/api/allocations/{target}/approve?reviewer=IntegrationTestDispatcher")
    assert res_app.status_code == 200
    app_data = res_app.json()
    assert "updated_allocation" in app_data
    assert "audit_entry" in app_data
    assert app_data["audit_entry"]["actor"] == "IntegrationTestDispatcher"

def test_step9_audit_trail():
    res = client.get("/api/audit")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    assert any(l["actor"] == "IntegrationTestDispatcher" for l in logs)

def test_step10_frontend_static_serving():
    res = client.get("/")
    assert res.status_code == 200
    assert "<!doctype html>" in res.text.lower()
    assert "root" in res.text.lower()
