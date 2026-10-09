/**
 * CrisisGuard Centralized Typed API Client
 * Fully aligned with src/api/server.py FastAPI backend
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export interface ServiceDetail {
  status: 'ONLINE' | 'OFFLINE' | 'AVAILABLE' | 'MISSING' | 'CONFIGURED';
  endpoint?: string;
  details?: string;
  path?: string;
  version?: string;
  metastore?: string;
  calibration_status?: string;
  framework?: string;
  nodes?: number;
  edges?: number;
  vertices?: number;
  windows?: number;
}

export interface ServicesHealthResponse {
  big_data_cluster: {
    hdfs: ServiceDetail;
    kafka: ServiceDetail;
    spark: ServiceDetail;
    hive: ServiceDetail;
  };
  models_and_forensics: {
    resnet18_image: ServiceDetail;
    platt_calibrator: ServiceDetail;
    crisismmd_classifier: ServiceDetail;
  };
  spatial_and_graph: {
    osm_road_network: ServiceDetail;
    graphx_metrics: ServiceDetail;
    streaming_window_metrics: ServiceDetail;
  };
  timestamp: string;
}

export interface OverviewMetrics {
  total_ingested_events: number;
  evidence_supported_count: number;
  contradicted_count: number;
  unverified_count: number;
  human_review_required_count: number;
  total_depot_resources: number;
  total_resource_capacity: number;
  available_resource_capacity: number;
  allocated_units: number;
  unmet_units: number;
  recommended_allocations: number;
  pending_approval_allocations: number;
}

export interface OverviewResponse {
  metrics: OverviewMetrics;
  outcome_breakdown: Record<string, number>;
  allocation_breakdown: Record<string, number>;
  recent_assessments: ClaimAssessment[];
  recent_allocations: AllocationRecord[];
  streaming_status: {
    window_size: string;
    watermark: string;
    total_windows: number;
    latest_propagation_rate: string;
  };
  last_refreshed: string;
}

export interface IncidentSummary {
  incident_id: string;
  text: string;
  crisis_category: string;
  category_confidence: number;
  verification_status: string;
  uncertainty_score: number;
  synthetic_media_risk: number | null;
  calibration_status: string;
  evidence_count: number;
  human_review_required: boolean;
  timestamp: string;
}

export interface ClaimAssessment {
  assessment_id: string;
  claim_id: string;
  report_text: string;
  extracted_claim: string;
  crisis_category: string;
  category_confidence: number;
  urgency_level: string;
  verification_status: string;
  assessment_outcome: string;
  uncertainty_score: number;
  synthetic_media_risk: number | null;
  calibration_status: string;
  evidence_references: Array<{
    evidence_id: string;
    source: string;
    relevance_score: number;
    title?: string;
  }>;
  propagation_context?: {
    cascade_risk?: string;
    burst_detected?: boolean;
    structural_note?: string;
  };
  human_review_required: boolean;
  review_reasons: string[];
  demanded_resources: {
    resource_type: string;
    demanded_quantity: number;
  };
  timestamp: string;
}

export interface MediaAnalysisResult {
  filename: string;
  media_type: string;
  synthetic_media_risk: number | null;
  calibration_status: string;
  inference_latency_ms: number;
  explanation: string;
  timestamp: string;
}

export interface AuthorityNode {
  vertex_id: number;
  pagerank: number;
  in_degree: number;
  out_degree: number;
  label?: string;
}

export interface StreamingWindow {
  window_index: number;
  window_start: string;
  window_end: string;
  events_in_window: number;
  propagation_rate_per_min: number;
  burst_indicator: boolean;
}

export interface PropagationSummary {
  graph_metrics: {
    total_vertices: number;
    total_edges: number;
    connected_components: number;
    giant_component_size: number;
    top_pagerank_value: number;
  };
  top_authority_nodes: AuthorityNode[];
  streaming_windows: StreamingWindow[];
}

export interface GraphNode {
  id: string;
  label: string;
  pagerank: number;
  in_degree: number;
  out_degree: number;
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface PropagationGraphSample {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface DepotResource {
  resource_id: string;
  depot_id: string;
  resource_type: string;
  total_capacity: number;
  allocated_quantity: number;
  latitude: number;
  longitude: number;
}

export interface ResourcesResponse {
  resources: DepotResource[];
  is_synthetic_demonstration: boolean;
  disclaimer: string;
}

export interface AllocationRecord {
  allocation_id: string;
  incident_id: string;
  incident_category: string;
  urgency_level: string;
  verification_status: string;
  required_resource_type: string;
  demanded_quantity: number;
  assigned_quantity: number;
  unmet_quantity: number;
  assigned_depot_id: string | null;
  road_distance_km: number | null;
  travel_time_minutes: number | null;
  allocation_status: 'RECOMMENDED' | 'AWAITING_APPROVAL' | 'UNALLOCATED' | 'INFEASIBLE';
  feasibility_status: string;
  priority_rationale: string;
  safety_note: string;
  solver_name: string;
  timestamp: string;
}

export interface AuditEntry {
  audit_id: string;
  action: string;
  target_id: string;
  actor: string;
  timestamp: string;
  details: Record<string, any>;
}

class ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Accept': 'application/json',
          ...(options?.headers || {})
        }
      });

      if (!response.ok) {
        let errorMessage = `API Error ${response.status}: ${response.statusText}`;
        try {
          const errorJson = await response.json();
          if (errorJson.detail) {
            errorMessage = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
          }
        } catch {
          // ignore parsing error
        }
        throw new Error(errorMessage);
      }

      return response.json();
    } catch (err: any) {
      console.error(`Request failed for ${endpoint}:`, err);
      throw err;
    }
  }

  // Health
  getHealth() {
    return this.request<{ status: string; service: string; version: string; timestamp: string }>('/health');
  }

  getServicesHealth() {
    return this.request<ServicesHealthResponse>('/health/services');
  }

  // Executive Overview
  getOverview() {
    return this.request<OverviewResponse>('/overview');
  }

  // Crisis Incidents
  getIncidents() {
    return this.request<IncidentSummary[]>('/incidents');
  }

  getIncidentDetail(incidentId: string) {
    return this.request<{ assessment: ClaimAssessment; allocation: AllocationRecord | null }>(`/incidents/${incidentId}`);
  }

  // Forensics / Media Analysis
  analyzeMedia(file: File, mediaType: 'IMAGE' | 'VIDEO' = 'IMAGE') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('media_type', mediaType);
    return this.request<MediaAnalysisResult>('/media/analyze', {
      method: 'POST',
      body: formData
    });
  }

  // Evidence Verification
  assessClaim(data: {
    text: string;
    location?: string;
    latitude?: number;
    longitude?: number;
    source_type?: string;
    media_path?: string;
    media_type?: string;
  }) {
    return this.request<ClaimAssessment>('/assessment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  }

  getAssessmentHistory() {
    return this.request<ClaimAssessment[]>('/assessment/history');
  }

  // Propagation Intelligence
  getPropagationSummary() {
    return this.request<PropagationSummary>('/propagation/summary');
  }

  getPropagationGraph() {
    return this.request<PropagationGraphSample>('/propagation/graph');
  }

  // Resource Inventory & Allocation
  getResources() {
    return this.request<ResourcesResponse>('/resources');
  }

  getAllocations() {
    return this.request<AllocationRecord[]>('/allocations');
  }

  optimizeAllocations(incidents: any[], updateInventory = true) {
    return this.request<AllocationRecord[]>('/allocations/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        incidents,
        update_inventory: updateInventory
      })
    });
  }

  approveAllocation(allocationId: string, reviewer = 'Chief Dispatcher') {
    return this.request<{ updated_allocation: AllocationRecord; audit_entry: AuditEntry }>(
      `/allocations/${encodeURIComponent(allocationId)}/approve?reviewer=${encodeURIComponent(reviewer)}`,
      { method: 'POST' }
    );
  }

  rejectAllocation(allocationId: string, reviewer = 'Chief Dispatcher', reason = 'Dispatched manually or cancelled') {
    return this.request<{ updated_allocation: AllocationRecord; audit_entry: AuditEntry }>(
      `/allocations/${encodeURIComponent(allocationId)}/reject?reviewer=${encodeURIComponent(reviewer)}&reason=${encodeURIComponent(reason)}`,
      { method: 'POST' }
    );
  }

  // Persistent Audit Log
  getAuditLog() {
    return this.request<AuditEntry[]>('/audit');
  }
}

export const api = new ApiClient();
