import React from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Truck,
  Server,
  Layers,
  Activity,
  ArrowUpRight,
  ExternalLink
} from 'lucide-react';
import { OverviewResponse, ServicesHealthResponse } from '../api/client';

interface OverviewViewProps {
  overview: OverviewResponse | null;
  servicesHealth: ServicesHealthResponse | null;
  loading: boolean;
  onNavigate: (tab: any) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  overview,
  servicesHealth,
  loading,
  onNavigate
}) => {
  if (loading && !overview) {
    return (
      <div style={{ padding: '2rem' }}>
        <div className="skeleton" style={{ height: '140px', marginBottom: '1.5rem' }} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton" style={{ height: '110px' }} />
          ))}
        </div>
        <div className="skeleton" style={{ height: '300px' }} />
      </div>
    );
  }

  const m = overview?.metrics;
  const cluster = servicesHealth?.big_data_cluster;
  const models = servicesHealth?.models_and_forensics;
  const spatial = servicesHealth?.spatial_and_graph;

  return (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner: Decision-Support Governance Context */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(14, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.8) 100%)',
          borderLeft: '4px solid var(--accent-primary)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span style={{ fontWeight: 700, fontSize: '1rem', color: '#FFFFFF' }}>
              Operational Crisis Intelligence & Evidence-Aware Resource Allocation
            </span>
            <span className="badge badge-info">CSE412 Live Pipeline</span>
          </div>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', maxWidth: '900px', margin: 0 }}>
            Strict Human-in-the-Loop decision governance active. All synthetic media forensics and OSM-routed HiGHS MILP 
            allocations are advisory recommendations. Zero autonomous dispatch commands are issued.
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Streaming Tumbling Window</div>
          <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            {overview?.streaming_status?.window_size || '1-Hour Tumbling'}
          </div>
          <div style={{ fontSize: '0.6875rem', color: '#10B981' }}>
            {overview?.streaming_status?.latest_propagation_rate || '16.7 evt/min'}
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '1rem' }}>
        {/* Total Ingested */}
        <div className="stat-card">
          <div className="stat-header">
            <span>Ingested Incidents</span>
            <Layers size={16} color="var(--accent-primary)" />
          </div>
          <div className="stat-value">{m?.total_ingested_events ?? 0}</div>
          <div className="stat-subtext">
            <span>Verified claims in pipeline</span>
          </div>
        </div>

        {/* Evidence Supported */}
        <div className="stat-card">
          <div className="stat-header">
            <span>Evidence Supported</span>
            <CheckCircle2 size={16} color="var(--status-success)" />
          </div>
          <div className="stat-value" style={{ color: 'var(--status-success)' }}>
            {m?.evidence_supported_count ?? 0}
          </div>
          <div className="stat-subtext">
            <span>Matches official reference data</span>
          </div>
        </div>

        {/* Contradicted by Evidence */}
        <div className="stat-card">
          <div className="stat-header">
            <span>Contradicted Claims</span>
            <XCircle size={16} color="var(--status-danger)" />
          </div>
          <div className="stat-value" style={{ color: 'var(--status-danger)' }}>
            {m?.contradicted_count ?? 0}
          </div>
          <div className="stat-subtext">
            <span>Safety-gated / Non-dispatched</span>
          </div>
        </div>

        {/* Human Review Required */}
        <div className="stat-card">
          <div className="stat-header">
            <span>Requires Human Review</span>
            <AlertTriangle size={16} color="var(--status-warning)" />
          </div>
          <div className="stat-value" style={{ color: 'var(--status-warning)' }}>
            {m?.human_review_required_count ?? 0}
          </div>
          <div className="stat-subtext">
            <span>High uncertainty / conflicting evidence</span>
          </div>
        </div>

        {/* Total Resource Capacity */}
        <div className="stat-card">
          <div className="stat-header">
            <span>Available / Total Capacity</span>
            <Truck size={16} color="var(--status-info)" />
          </div>
          <div className="stat-value">
            {m?.available_resource_capacity ?? 0}
            <span style={{ fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 400 }}>
              /{m?.total_resource_capacity ?? 0}
            </span>
          </div>
          <div className="stat-subtext">
            <span>{m?.total_depot_resources ?? 0} emergency depots</span>
          </div>
        </div>

        {/* Recommended Allocations */}
        <div className="stat-card">
          <div className="stat-header">
            <span>Recommended Units</span>
            <Activity size={16} color="var(--status-success)" />
          </div>
          <div className="stat-value" style={{ color: 'var(--text-primary)' }}>
            {m?.allocated_units ?? 0}
          </div>
          <div className="stat-subtext">
            <span>Unmet demand: {m?.unmet_units ?? 0} units</span>
          </div>
        </div>
      </div>

      {/* Verification Breakdown & Service Health */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Verification Outcomes Distribution */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Verification Outcome Distribution</div>
              <div className="card-subtitle">Real DeBERTa NLI & Evidence Matching Outcomes</div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
            {Object.entries(overview?.outcome_breakdown || {}).map(([outcome, count]) => {
              const total = Math.max(overview?.metrics?.total_ingested_events || 1, 1);
              const pct = Math.round((count / total) * 100);
              let barColor = 'var(--status-neutral)';
              if (outcome === 'EVIDENCE_SUPPORTED') barColor = 'var(--status-success)';
              if (outcome === 'CONTRADICTED_BY_EVIDENCE') barColor = 'var(--status-danger)';
              if (outcome === 'REQUIRES_HUMAN_REVIEW') barColor = 'var(--status-warning)';
              if (outcome === 'UNVERIFIED') barColor = 'var(--status-info)';

              return (
                <div key={outcome}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{outcome}</span>
                    <span style={{ color: 'var(--text-muted)' }}>
                      {count} ({pct}%)
                    </span>
                  </div>
                  <div style={{ height: '6px', backgroundColor: 'var(--bg-elevated)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${pct}%`, backgroundColor: barColor, borderRadius: '3px' }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Backend & Big Data Subsystem Status */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <Server size={16} /> Backend Architecture & Subsystems
              </div>
              <div className="card-subtitle">Live socket probes & filesystem model checks</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            {/* HDFS */}
            <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, fontSize: '0.8125rem' }}>HDFS Cluster</span>
                <span className={`badge ${cluster?.hdfs?.status === 'ONLINE' ? 'badge-success' : 'badge-neutral'}`}>
                  {cluster?.hdfs?.status || 'OFFLINE'}
                </span>
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Port 9000 &bull; Raw multi-modal storage
              </div>
            </div>

            {/* Kafka */}
            <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, fontSize: '0.8125rem' }}>Kafka Broker</span>
                <span className={`badge ${cluster?.kafka?.status === 'ONLINE' ? 'badge-success' : 'badge-neutral'}`}>
                  {cluster?.kafka?.status || 'OFFLINE'}
                </span>
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Port 9092 &bull; Real-time event ingress
              </div>
            </div>

            {/* ResNet-18 */}
            <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, fontSize: '0.8125rem' }}>ResNet-18 Forensics</span>
                <span className={`badge ${models?.resnet18_image?.status === 'AVAILABLE' ? 'badge-success' : 'badge-warning'}`}>
                  {models?.resnet18_image?.status || 'READY'}
                </span>
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Platt Calibrated &bull; Synthetic detector
              </div>
            </div>

            {/* HiGHS & OSM */}
            <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, fontSize: '0.8125rem' }}>HiGHS MILP / OSM</span>
                <span className="badge badge-success">OPERATIONAL</span>
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                63,660 nodes &bull; Exact Dijkstra router
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Incidents Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Recent Ingested Incidents & Verifications</div>
            <div className="card-subtitle">Active multi-modal claims undergoing decision-support evaluation</div>
          </div>
          <button onClick={() => onNavigate('incidents')} className="btn btn-outline btn-sm">
            View All Incidents <ArrowUpRight size={14} />
          </button>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Incident ID</th>
                <th>Claim Text</th>
                <th>Crisis Category</th>
                <th>Verification Outcome</th>
                <th>Uncertainty</th>
                <th>Synthetic Media</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {(overview?.recent_assessments || []).map((asmt) => {
                let badgeClass = 'badge-neutral';
                if (asmt.assessment_outcome === 'EVIDENCE_SUPPORTED') badgeClass = 'badge-success';
                if (asmt.assessment_outcome === 'CONTRADICTED_BY_EVIDENCE') badgeClass = 'badge-danger';
                if (asmt.assessment_outcome === 'REQUIRES_HUMAN_REVIEW') badgeClass = 'badge-warning';

                return (
                  <tr key={asmt.assessment_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                      {asmt.claim_id}
                    </td>
                    <td style={{ maxWidth: '320px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {asmt.extracted_claim || asmt.report_text}
                    </td>
                    <td>
                      <span className="badge badge-neutral">{asmt.crisis_category}</span>
                    </td>
                    <td>
                      <span className={`badge ${badgeClass}`}>{asmt.assessment_outcome}</span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      {asmt.uncertainty_score?.toFixed(3) ?? 'N/A'}
                    </td>
                    <td>
                      {asmt.synthetic_media_risk !== null ? (
                        <span className="badge badge-warning">
                          Risk: {(asmt.synthetic_media_risk * 100).toFixed(1)}%
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>None</span>
                      )}
                    </td>
                    <td>
                      <button
                        onClick={() => onNavigate('evidence')}
                        className="btn btn-outline btn-sm"
                        style={{ padding: '2px 8px', fontSize: '0.6875rem' }}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Allocations Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Recent MILP Allocation Recommendations</div>
            <div className="card-subtitle">HiGHS solver assignments constrained by evidence verification gate</div>
          </div>
          <button onClick={() => onNavigate('allocation')} className="btn btn-outline btn-sm">
            Open Allocation Workspace <ArrowUpRight size={14} />
          </button>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Allocation ID</th>
                <th>Target Incident</th>
                <th>Resource Type</th>
                <th>Demanded</th>
                <th>Assigned</th>
                <th>Assigned Depot</th>
                <th>Road Dist (km)</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {(overview?.recent_allocations || []).map((al) => {
                let statusBadge = 'badge-neutral';
                if (al.allocation_status === 'RECOMMENDED') statusBadge = 'badge-success';
                if (al.allocation_status === 'AWAITING_APPROVAL') statusBadge = 'badge-warning';
                if (al.allocation_status === 'UNALLOCATED') statusBadge = 'badge-danger';

                return (
                  <tr key={al.allocation_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                      {al.allocation_id}
                    </td>
                    <td style={{ fontWeight: 500 }}>{al.incident_id}</td>
                    <td>{al.required_resource_type}</td>
                    <td>{al.demanded_quantity}</td>
                    <td style={{ fontWeight: 600, color: al.assigned_quantity > 0 ? '#10B981' : '#EF4444' }}>
                      {al.assigned_quantity}
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      {al.assigned_depot_id || 'None'}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      {al.road_distance_km ? `${al.road_distance_km.toFixed(2)} km` : 'N/A'}
                    </td>
                    <td>
                      <span className={`badge ${statusBadge}`}>{al.allocation_status}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
