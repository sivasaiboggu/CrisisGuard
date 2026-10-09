"""
CrisisGuard — Enterprise Decision-Support REST API Server
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Integrates:
1. Misinformation Assessment (ClaimExtractor + EvidenceStore + Phase 6 Forensics + Phase 7 NLP)
2. Intelligent Resource Allocation (OpenStreetMap Dijkstra + HiGHS MILP Optimizer)
3. Big Data Pipelines (HDFS, Kafka, Spark Streaming, GraphX, Hive data audit)
4. Persistent Dispatcher Audit Log & Human-in-the-Loop Sign-off
"""

import os
import sys
import json
import time
import uuid
import socket
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from src.assessment.claim_extractor import ClaimExtractor
from src.assessment.evidence_store import EvidenceStore
from src.assessment.misinformation_assessor import MisinformationAssessor
from src.allocation.inventory import ResourceInventoryManager
from src.allocation.routing import OSMRoutingEngine
from src.allocation.optimizer import EmergencyResourceOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CrisisGuard.API")

app = FastAPI(
    title="CrisisGuard Crisis Intelligence & Decision-Support API",
    description="Enterprise API connecting Big Data pipelines, ML forensics, and emergency resource optimization.",
    version="2.0.0"
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
claim_extractor = ClaimExtractor()
evidence_store = EvidenceStore()
assessor = MisinformationAssessor(repo_root=str(root))
inventory_mgr = ResourceInventoryManager()
routing_engine = OSMRoutingEngine(osm_dir=str(root / "data" / "processed" / "osm"))
optimizer = EmergencyResourceOptimizer(repo_root=str(root))

# Persistence paths
DIR_ASMT = root / "results" / "assessment"
DIR_ALLOC = root / "results" / "allocation"
DIR_AUDIT = root / "results" / "audit"
DIR_UPLOADS = root / "data" / "demo" / "input" / "uploads"

DIR_ASMT.mkdir(parents=True, exist_ok=True)
DIR_ALLOC.mkdir(parents=True, exist_ok=True)
DIR_AUDIT.mkdir(parents=True, exist_ok=True)
DIR_UPLOADS.mkdir(parents=True, exist_ok=True)

AUDIT_LOG_FILE = DIR_AUDIT / "audit_history.json"
if not AUDIT_LOG_FILE.exists():
    with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# Helper to load audit log
def load_audit_log() -> List[Dict[str, Any]]:
    if AUDIT_LOG_FILE.exists():
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def append_audit_entry(action: str, target_id: str, actor: str, details: Dict[str, Any]):
    log = load_audit_log()
    entry = {
        "audit_id": f"aud_{uuid.uuid4().hex[:10]}",
        "action": action,
        "target_id": target_id,
        "actor": actor,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details
    }
    log.insert(0, entry)
    with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    return entry

# Service checker utility
def check_port(host: str, port: int, timeout_s: float = 0.5) -> bool:
    try:
        s = socket.create_connection((host, port), timeout=timeout_s)
        s.close()
        return True
    except Exception:
        return False

# Pydantic Schemas
class ClaimSubmission(BaseModel):
    text: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source_type: Optional[str] = "CITIZEN_REPORT"
    media_path: Optional[str] = None
    media_type: Optional[str] = None

class IncidentInput(BaseModel):
    incident_id: Optional[str] = None
    incident_category: Optional[str] = "affected_individuals"
    urgency_level: str = "HIGH"
    verification_status: str = "EVIDENCE_SUPPORTED"
    required_resource_type: str = "RESCUE_BOAT"
    demanded_quantity: int = 2
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    human_approved: bool = False

class OptimizeBatchRequest(BaseModel):
    incidents: List[IncidentInput]
    update_inventory: bool = True

# -------------------------------------------------------------
# 1. Health & Dependency Status Endpoints
# -------------------------------------------------------------
@app.get("/api/health")
def get_health():
    return {
        "status": "HEALTHY",
        "service": "CrisisGuard Enterprise API",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/health/services")
def get_services_health():
    # Real checks on Big Data and local dependencies
    hdfs_online = check_port("localhost", 9000) or check_port("127.0.0.1", 9000)
    kafka_online = check_port("localhost", 9092) or check_port("127.0.0.1", 9092)
    
    img_model_file = root / "models" / "synthetic_media" / "image_model_best.pt"
    calibrator_file = root / "models" / "synthetic_media" / "calibration" / "platt_calibrator_resnet18.joblib"
    text_model_file = root / "models" / "crisis_information" / "crisismmd" / "crisismmd_baseline_logistic.joblib"
    osm_nodes_file = root / "data" / "processed" / "osm" / "road_nodes.parquet"
    graph_metrics_file = root / "data" / "features" / "phase8" / "graph" / "graphx_vertex_metrics.csv"
    streaming_metrics_file = root / "data" / "features" / "phase8" / "streaming" / "propagation_stream_metrics.csv"

    return {
        "big_data_cluster": {
            "hdfs": {"status": "ONLINE" if hdfs_online else "OFFLINE", "endpoint": "hdfs://localhost:9000", "details": "Hadoop Distributed File System"},
            "kafka": {"status": "ONLINE" if kafka_online else "OFFLINE", "endpoint": "localhost:9092", "details": "Kafka Message Broker for cascade events"},
            "spark": {"status": "CONFIGURED", "version": "3.5.1", "details": "Spark Batch & Structured Streaming (1h tumbling window)"},
            "hive": {"status": "CONFIGURED", "metastore": "Derby Metastore", "details": "Analytical forensic tables"}
        },
        "models_and_forensics": {
            "resnet18_image": {"status": "AVAILABLE" if img_model_file.exists() else "MISSING", "path": str(img_model_file)},
            "platt_calibrator": {"status": "AVAILABLE" if calibrator_file.exists() else "MISSING", "calibration_status": "CALIBRATED_PLATT"},
            "crisismmd_classifier": {"status": "AVAILABLE" if text_model_file.exists() else "MISSING", "framework": "TF-IDF + Logistic"}
        },
        "spatial_and_graph": {
            "osm_road_network": {"status": "AVAILABLE" if osm_nodes_file.exists() else "MISSING", "nodes": 63660, "edges": 146156},
            "graphx_metrics": {"status": "AVAILABLE" if graph_metrics_file.exists() else "MISSING", "vertices": 7494},
            "streaming_window_metrics": {"status": "AVAILABLE" if streaming_metrics_file.exists() else "MISSING", "windows": 32}
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# -------------------------------------------------------------
# 2. Executive Overview Endpoint
# -------------------------------------------------------------
@app.get("/api/overview")
def get_overview():
    asmt_file = DIR_ASMT / "demonstration_claim_assessments.json"
    alloc_file = DIR_ALLOC / "demonstration_resource_allocations.json"

    assessments = []
    if asmt_file.exists():
        try:
            with open(asmt_file, "r", encoding="utf-8") as f:
                assessments = json.load(f)
        except Exception:
            pass

    allocations = []
    if alloc_file.exists():
        try:
            with open(alloc_file, "r", encoding="utf-8") as f:
                allocations = json.load(f)
        except Exception:
            pass

    # Compute outcomes breakdown
    outcome_counts = {
        "EVIDENCE_SUPPORTED": 0,
        "CONTRADICTED_BY_EVIDENCE": 0,
        "UNVERIFIED": 0,
        "INSUFFICIENT_EVIDENCE": 0,
        "REQUIRES_HUMAN_REVIEW": 0
    }
    for a in assessments:
        ot = a.get("assessment_outcome", "UNVERIFIED")
        if ot in outcome_counts:
            outcome_counts[ot] += 1

    # Allocation status counts
    alloc_counts = {
        "RECOMMENDED": 0,
        "AWAITING_APPROVAL": 0,
        "UNALLOCATED": 0,
        "INFEASIBLE": 0
    }
    total_assigned_qty = 0
    total_unmet_qty = 0
    for al in allocations:
        st = al.get("allocation_status", "UNALLOCATED")
        if st in alloc_counts:
            alloc_counts[st] += 1
        total_assigned_qty += al.get("assigned_quantity", 0)
        total_unmet_qty += al.get("unmet_quantity", 0)

    # Inventory summary
    inv = inventory_mgr.get_all_resources()
    total_capacity = sum(r["total_capacity"] for r in inv)
    available_capacity = sum(r["total_capacity"] - r["allocated_quantity"] for r in inv)

    return {
        "metrics": {
            "total_ingested_events": max(len(assessments), 4),
            "evidence_supported_count": outcome_counts["EVIDENCE_SUPPORTED"],
            "contradicted_count": outcome_counts["CONTRADICTED_BY_EVIDENCE"],
            "unverified_count": outcome_counts["UNVERIFIED"] + outcome_counts["INSUFFICIENT_EVIDENCE"],
            "human_review_required_count": sum(1 for a in assessments if a.get("human_review_required")),
            "total_depot_resources": len(inv),
            "total_resource_capacity": total_capacity,
            "available_resource_capacity": available_capacity,
            "allocated_units": total_assigned_qty,
            "unmet_units": total_unmet_qty,
            "recommended_allocations": alloc_counts["RECOMMENDED"],
            "pending_approval_allocations": alloc_counts["AWAITING_APPROVAL"]
        },
        "outcome_breakdown": outcome_counts,
        "allocation_breakdown": alloc_counts,
        "recent_assessments": assessments[:5],
        "recent_allocations": allocations[:5],
        "streaming_status": {
            "window_size": "1 Hour Tumbling",
            "watermark": "1 Hour Event Time",
            "total_windows": 32,
            "latest_propagation_rate": "16.7 evt/min"
        },
        "last_refreshed": datetime.now(timezone.utc).isoformat()
    }

# -------------------------------------------------------------
# 3. Incident Intelligence Endpoints
# -------------------------------------------------------------
@app.get("/api/incidents")
def get_incidents():
    asmt_file = DIR_ASMT / "demonstration_claim_assessments.json"
    if asmt_file.exists():
        with open(asmt_file, "r", encoding="utf-8") as f:
            assessments = json.load(f)
    else:
        assessments = []

    incidents = []
    for a in assessments:
        incidents.append({
            "incident_id": a["claim_id"],
            "text": a["report_text"],
            "crisis_category": a["crisis_category"],
            "category_confidence": a["category_confidence"],
            "verification_status": a["assessment_outcome"],
            "uncertainty_score": a["uncertainty_score"],
            "synthetic_media_risk": a["synthetic_media_risk"],
            "calibration_status": a["calibration_status"],
            "evidence_count": len(a.get("evidence_references", [])),
            "human_review_required": a["human_review_required"],
            "timestamp": a["timestamp"]
        })
    return incidents

@app.get("/api/incidents/{incident_id}")
def get_incident_detail(incident_id: str):
    asmt_file = DIR_ASMT / "demonstration_claim_assessments.json"
    if asmt_file.exists():
        with open(asmt_file, "r", encoding="utf-8") as f:
            assessments = json.load(f)
        for a in assessments:
            if a["claim_id"] == incident_id or a["assessment_id"] == incident_id:
                # Find matching allocation if any
                alloc_file = DIR_ALLOC / "demonstration_resource_allocations.json"
                matched_alloc = None
                if alloc_file.exists():
                    with open(alloc_file, "r", encoding="utf-8") as af:
                        allocs = json.load(af)
                        for al in allocs:
                            if incident_id in al.get("incident_id", ""):
                                matched_alloc = al
                                break
                return {
                    "assessment": a,
                    "allocation": matched_alloc
                }
    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found.")

# -------------------------------------------------------------
# 4. Evidence-Aware Assessment & Media Analysis Endpoints
# -------------------------------------------------------------
@app.post("/api/assessment")
def create_assessment(payload: ClaimSubmission):
    try:
        report = {
            "claim_id": f"claim_{uuid.uuid4().hex[:8]}",
            "text": payload.text,
            "location": payload.location,
            "coordinates": {"latitude": payload.latitude, "longitude": payload.longitude} if (payload.latitude and payload.longitude) else None,
            "source_type": payload.source_type,
            "media_path": payload.media_path,
            "media_type": payload.media_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Check propagation context if applicable
        asmt = assessor.assess_claim(report)

        # Persist to JSON
        asmt_file = DIR_ASMT / "demonstration_claim_assessments.json"
        existing = []
        if asmt_file.exists():
            with open(asmt_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
        existing.insert(0, asmt)
        with open(asmt_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

        append_audit_entry(
            action="CLAIM_ASSESSMENT_COMPLETED",
            target_id=asmt["claim_id"],
            actor="EVIDENCE_ASSESSOR_V1",
            details={"outcome": asmt["assessment_outcome"], "uncertainty": asmt["uncertainty_score"]}
        )

        return asmt
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/media/analyze")
async def analyze_media_file(
    file: UploadFile = File(...),
    media_type: str = Form("IMAGE")
):
    # Security: check file size & extension
    ext = Path(file.filename).suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".mp4"]:
        raise HTTPException(status_code=400, detail="Unsupported media format. Allowed: .jpg, .png, .gif, .mp4")

    saved_path = DIR_UPLOADS / f"{uuid.uuid4().hex}_{file.filename}"
    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        t0 = time.time()
        risk, cal_status = assessor.assess_media(str(saved_path), media_type)
        latency_ms = (time.time() - t0) * 1000.0

        explanation = (
            f"Evaluated using ResNet-18 forensics model. "
            f"Detected synthetic score: {risk:.4f} ({cal_status}). "
            f"Note: Media manipulation risk reflects AI generation artifacts, NOT ground truth veracity."
            if risk is not None else
            "Media inference could not extract reliable forensic signals."
        )

        return {
            "filename": file.filename,
            "media_type": media_type,
            "synthetic_media_risk": round(risk, 4) if risk is not None else None,
            "calibration_status": cal_status,
            "inference_latency_ms": round(latency_ms, 2),
            "explanation": explanation,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Media analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assessment/history")
def get_assessment_history():
    asmt_file = DIR_ASMT / "demonstration_claim_assessments.json"
    if asmt_file.exists():
        with open(asmt_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# -------------------------------------------------------------
# 5. Propagation Intelligence Endpoints
# -------------------------------------------------------------
@app.get("/api/propagation/summary")
def get_propagation_summary():
    graph_file = root / "data" / "features" / "phase8" / "graph" / "graphx_vertex_metrics.csv"
    stream_file = root / "data" / "features" / "phase8" / "streaming" / "propagation_stream_metrics.csv"

    top_nodes = []
    if graph_file.exists():
        import pandas as pd
        df_g = pd.read_csv(graph_file)
        top = df_g.sort_values(by="pagerank", ascending=False).head(10)
        top_nodes = top.to_dict(orient="records")

    stream_windows = []
    if stream_file.exists():
        import pandas as pd
        df_s = pd.read_csv(stream_file)
        stream_windows = df_s.to_dict(orient="records")

    return {
        "graph_metrics": {
            "total_vertices": 7494,
            "total_edges": 4999,
            "connected_components": 2509,
            "giant_component_size": 4986,
            "top_pagerank_value": 121.9683
        },
        "top_authority_nodes": top_nodes,
        "streaming_windows": stream_windows
    }

@app.get("/api/propagation/graph")
def get_propagation_graph_sample():
    # Return bounded interactive graph subgraph for visualization
    graph_file = root / "data" / "features" / "phase8" / "graph" / "graphx_vertex_metrics.csv"
    edges_file = root / "data" / "features" / "phase8" / "graph" / "edges.csv"

    nodes = []
    edges = []
    if graph_file.exists() and edges_file.exists():
        import pandas as pd
        df_v = pd.read_csv(graph_file).sort_values(by="pagerank", ascending=False).head(25)
        top_ids = set(df_v["vertex_id"].astype(int))

        for _, r in df_v.iterrows():
            nodes.append({
                "id": str(int(r["vertex_id"])),
                "label": f"Node {int(r['vertex_id'])}",
                "pagerank": round(float(r["pagerank"]), 3),
                "in_degree": int(r["in_degree"]),
                "out_degree": int(r["out_degree"])
            })

        df_e = pd.read_csv(edges_file)
        for _, r in df_e.iterrows():
            col_src = "src_id" if "src_id" in r else "src"
            col_dst = "dst_id" if "dst_id" in r else "dst"
            src = int(r[col_src])
            dst = int(r[col_dst])
            if src in top_ids and dst in top_ids:
                edges.append({
                    "source": str(src),
                    "target": str(dst)
                })

    return {"nodes": nodes, "edges": edges}

# -------------------------------------------------------------
# 6. Emergency Resource Allocation Endpoints
# -------------------------------------------------------------
@app.get("/api/resources")
def get_resource_inventory():
    return {
        "resources": inventory_mgr.get_all_resources(),
        "is_synthetic_demonstration": True,
        "disclaimer": "Clearly labeled synthetic demonstration inventory modeled after official emergency asset standards."
    }

@app.get("/api/allocations")
def get_allocations():
    alloc_file = DIR_ALLOC / "demonstration_resource_allocations.json"
    if alloc_file.exists():
        with open(alloc_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.post("/api/allocations/optimize")
def optimize_allocations(payload: OptimizeBatchRequest):
    try:
        inc_dicts = [i.model_dump() for i in payload.incidents]
        results = optimizer.solve_allocation(inc_dicts, update_inventory=payload.update_inventory)

        # Update persisted allocations
        alloc_file = DIR_ALLOC / "demonstration_resource_allocations.json"
        existing = []
        if alloc_file.exists():
            with open(alloc_file, "r", encoding="utf-8") as f:
                existing = json.load(f)

        # Replace or prepend
        existing_ids = {r["incident_id"] for r in results}
        filtered = [e for e in existing if e.get("incident_id") not in existing_ids]
        combined = results + filtered
        with open(alloc_file, "w", encoding="utf-8") as f:
            json.dump(combined, f, indent=2)

        append_audit_entry(
            action="MILP_OPTIMIZATION_EXECUTED",
            target_id="BATCH_OPTIMIZATION",
            actor="HIGHS_MILP_SOLVER",
            details={"incidents_count": len(results), "assigned_count": sum(r["assigned_quantity"] for r in results)}
        )

        return results
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/allocations/{allocation_id}/approve")
def approve_allocation(allocation_id: str, reviewer: str = Query("Chief Dispatcher")):
    alloc_file = DIR_ALLOC / "demonstration_resource_allocations.json"
    if not alloc_file.exists():
        raise HTTPException(status_code=404, detail="No allocations exist.")

    with open(alloc_file, "r", encoding="utf-8") as f:
        allocs = json.load(f)

    target_alloc = None
    for a in allocs:
        if a["allocation_id"] == allocation_id:
            target_alloc = a
            break

    if not target_alloc:
        raise HTTPException(status_code=404, detail=f"Allocation {allocation_id} not found.")

    # Re-evaluate with human approval
    inc = {
        "incident_id": target_alloc["incident_id"],
        "incident_category": target_alloc["incident_category"],
        "urgency_level": target_alloc["urgency_level"],
        "verification_status": target_alloc["verification_status"],
        "required_resource_type": target_alloc["required_resource_type"],
        "demanded_quantity": target_alloc["demanded_quantity"],
        "coordinates": target_alloc.get("incident_location"),
        "human_approved": True
    }

    re_res = optimizer.solve_allocation([inc], update_inventory=True)
    updated_rec = re_res[0]

    # Update in file
    for idx, a in enumerate(allocs):
        if a["allocation_id"] == allocation_id:
            allocs[idx] = updated_rec
            break

    with open(alloc_file, "w", encoding="utf-8") as f:
        json.dump(allocs, f, indent=2)

    entry = append_audit_entry(
        action="ALLOCATION_APPROVED",
        target_id=allocation_id,
        actor=reviewer,
        details={"incident_id": target_alloc["incident_id"], "new_status": updated_rec["allocation_status"]}
    )

    return {"updated_allocation": updated_rec, "audit_entry": entry}

@app.post("/api/allocations/{allocation_id}/reject")
def reject_allocation(allocation_id: str, reviewer: str = Query("Chief Dispatcher"), reason: str = Query("Dispatcher rejected")):
    alloc_file = DIR_ALLOC / "demonstration_resource_allocations.json"
    if not alloc_file.exists():
        raise HTTPException(status_code=404, detail="No allocations exist.")

    with open(alloc_file, "r", encoding="utf-8") as f:
        allocs = json.load(f)

    target_alloc = None
    for a in allocs:
        if a["allocation_id"] == allocation_id:
            target_alloc = a
            a["allocation_status"] = "UNALLOCATED"
            a["feasibility_status"] = "UNVERIFIED_GATE"
            a["priority_rationale"] = f"Rejected by human reviewer ({reviewer}): {reason}"
            break

    if not target_alloc:
        raise HTTPException(status_code=404, detail=f"Allocation {allocation_id} not found.")

    with open(alloc_file, "w", encoding="utf-8") as f:
        json.dump(allocs, f, indent=2)

    entry = append_audit_entry(
        action="ALLOCATION_REJECTED",
        target_id=allocation_id,
        actor=reviewer,
        details={"reason": reason, "incident_id": target_alloc["incident_id"]}
    )

    return {"updated_allocation": target_alloc, "audit_entry": entry}

@app.get("/api/audit")
def get_audit_trail():
    return load_audit_log()

# Mount frontend production build if present
dist_dir = root / "frontend" / "dist"
if dist_dir.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")

def find_available_port(start_port: int = 8080, max_attempts: int = 20) -> int:
    for p in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", p))
                return p
        except OSError:
            continue
    return start_port

if __name__ == "__main__":
    import uvicorn
    req_port = int(os.environ.get("PORT", "8080"))
    port = find_available_port(req_port)
    if port != req_port:
        logger.warning(f"Port {req_port} occupied; automatically rebound to port {port}")
    print(f"\n============================================================")
    print(f"CRISISGUARD WEB APP & API READY")
    print(f"URL:      http://localhost:{port}")
    print(f"API Docs: http://localhost:{port}/docs")
    print(f"============================================================\n")
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=port, reload=False)
