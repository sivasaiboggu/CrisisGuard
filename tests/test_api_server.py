"""
Test FastAPI server endpoints using TestClient.
Verifies all Phase 4 endpoints with the real server implementation.
"""
import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert "timestamp" in data

def test_health_services():
    res = client.get("/api/health/services")
    assert res.status_code == 200
    data = res.json()
    assert "big_data_cluster" in data
    assert "models_and_forensics" in data
    assert "spatial_and_graph" in data

def test_overview():
    res = client.get("/api/overview")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "outcome_breakdown" in data
    assert "allocation_breakdown" in data

def test_incidents_list():
    res = client.get("/api/incidents")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "incident_id" in data[0]
        assert "verification_status" in data[0]

def test_propagation_summary():
    res = client.get("/api/propagation/summary")
    assert res.status_code == 200
    data = res.json()
    assert "graph_metrics" in data
    assert "top_authority_nodes" in data
    assert "streaming_windows" in data
    assert data["graph_metrics"]["total_vertices"] == 7494

def test_propagation_graph():
    res = client.get("/api/propagation/graph")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0

def test_resources_list():
    res = client.get("/api/resources")
    assert res.status_code == 200
    data = res.json()
    assert "resources" in data
    assert data["is_synthetic_demonstration"] is True
    assert len(data["resources"]) > 0

def test_allocations_list():
    res = client.get("/api/allocations")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_audit_list():
    res = client.get("/api/audit")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_assessment_history():
    res = client.get("/api/assessment/history")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_claim_assessment_execution():
    payload = {
        "text": "Yamuna water level crossed 208.66m at Old Railway Bridge.",
        "location": "Old Railway Bridge, Delhi",
        "latitude": 28.6619,
        "longitude": 77.2492,
        "source_type": "CITIZEN_REPORT"
    }
    res = client.post("/api/assessment", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "assessment_outcome" in data
    assert "uncertainty_score" in data
    assert "evidence_references" in data
