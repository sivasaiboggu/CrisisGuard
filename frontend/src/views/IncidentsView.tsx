import React, { useState } from 'react';
import {
  Search,
  Filter,
  Eye,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  X,
  FileText,
  MapPin,
  ExternalLink
} from 'lucide-react';
import { IncidentSummary, ClaimAssessment, AllocationRecord, api } from '../api/client';

interface IncidentsViewProps {
  incidents: IncidentSummary[];
  loading: boolean;
  onNavigateToEvidence?: (incidentId: string) => void;
  onNavigateToAllocation?: (incidentId: string) => void;
}

export const IncidentsView: React.FC<IncidentsViewProps> = ({
  incidents,
  loading,
  onNavigateToEvidence,
  onNavigateToAllocation
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOutcome, setFilterOutcome] = useState('ALL');
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [incidentDetail, setIncidentDetail] = useState<{
    assessment: ClaimAssessment;
    allocation: AllocationRecord | null;
  } | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const filtered = incidents.filter((inc) => {
    const matchesSearch =
      inc.incident_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.crisis_category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesOutcome =
      filterOutcome === 'ALL' || inc.verification_status === filterOutcome;
    return matchesSearch && matchesOutcome;
  });

  const handleOpenDetail = async (incidentId: string) => {
    setSelectedIncidentId(incidentId);
    setDetailLoading(true);
    try {
      const detail = await api.getIncidentDetail(incidentId);
      setIncidentDetail(detail);
    } catch (err) {
      console.error('Failed to load incident detail', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCloseDetail = () => {
    setSelectedIncidentId(null);
    setIncidentDetail(null);
  };

  return (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Controls Bar */}
      <div
        className="card"
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
          padding: '1rem 1.25rem'
        }}
      >
        {/* Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: '1 1 300px' }}>
          <div style={{ position: 'relative', width: '100%' }}>
            <Search
              size={16}
              style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }}
            />
            <input
              type="text"
              placeholder="Search by Incident ID, report text, or category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-control"
              style={{ paddingLeft: '34px' }}
            />
          </div>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Filter size={16} color="var(--text-muted)" />
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>Verification:</span>
          <select
            value={filterOutcome}
            onChange={(e) => setFilterOutcome(e.target.value)}
            className="input-control"
            style={{ width: 'auto' }}
          >
            <option value="ALL">All Outcomes</option>
            <option value="EVIDENCE_SUPPORTED">EVIDENCE_SUPPORTED</option>
            <option value="CONTRADICTED_BY_EVIDENCE">CONTRADICTED_BY_EVIDENCE</option>
            <option value="REQUIRES_HUMAN_REVIEW">REQUIRES_HUMAN_REVIEW</option>
            <option value="UNVERIFIED">UNVERIFIED</option>
          </select>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Ingested Crisis Reports ({filtered.length})</div>
            <div className="card-subtitle">
              Multi-modal claims ingested via Kafka stream, NLP categorized, and evidence assessed
            </div>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: '2rem' }}>
            <div className="skeleton" style={{ height: '40px', marginBottom: '8px' }} />
            <div className="skeleton" style={{ height: '40px', marginBottom: '8px' }} />
            <div className="skeleton" style={{ height: '40px' }} />
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <AlertTriangle className="empty-state-icon" />
            <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>No matching incidents found</div>
            <div style={{ fontSize: '0.8125rem', marginTop: '4px' }}>
              Try adjusting your search criteria or outcome filter.
            </div>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Incident ID</th>
                  <th>Submitted Report</th>
                  <th>Crisis Category</th>
                  <th>Verification Outcome</th>
                  <th>Uncertainty</th>
                  <th>Media Risk</th>
                  <th>Evidence</th>
                  <th>Human Review</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((inc) => {
                  let badgeClass = 'badge-neutral';
                  if (inc.verification_status === 'EVIDENCE_SUPPORTED') badgeClass = 'badge-success';
                  if (inc.verification_status === 'CONTRADICTED_BY_EVIDENCE') badgeClass = 'badge-danger';
                  if (inc.verification_status === 'REQUIRES_HUMAN_REVIEW') badgeClass = 'badge-warning';

                  return (
                    <tr key={inc.incident_id}>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 600 }}>
                        {inc.incident_id}
                      </td>
                      <td style={{ maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {inc.text}
                      </td>
                      <td>
                        <span className="badge badge-neutral">{inc.crisis_category}</span>
                      </td>
                      <td>
                        <span className={`badge ${badgeClass}`}>{inc.verification_status}</span>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                        {inc.uncertainty_score?.toFixed(3) ?? '0.000'}
                      </td>
                      <td>
                        {inc.synthetic_media_risk !== null ? (
                          <span
                            className="badge badge-warning"
                            title={`Forensic score: ${inc.synthetic_media_risk} (${inc.calibration_status})`}
                          >
                            {(inc.synthetic_media_risk * 100).toFixed(1)}%
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>None</span>
                        )}
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.8125rem' }}>
                          {inc.evidence_count} sources
                        </span>
                      </td>
                      <td>
                        {inc.human_review_required ? (
                          <span className="badge badge-warning">Required</span>
                        ) : (
                          <span className="badge badge-neutral">Auto-Gated</span>
                        )}
                      </td>
                      <td>
                        <button
                          onClick={() => handleOpenDetail(inc.incident_id)}
                          className="btn btn-outline btn-sm"
                          style={{ padding: '4px 8px' }}
                        >
                          <Eye size={12} /> Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Incident Detail Modal */}
      {selectedIncidentId && (
        <div className="modal-overlay" onClick={handleCloseDetail}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText size={18} color="var(--accent-primary)" />
                <span style={{ fontWeight: 600, fontSize: '0.9375rem', color: 'var(--text-primary)' }}>
                  Incident Dossier: {selectedIncidentId}
                </span>
              </div>
              <button
                onClick={handleCloseDetail}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              {detailLoading || !incidentDetail ? (
                <div style={{ padding: '2rem' }}>
                  <div className="skeleton" style={{ height: '80px', marginBottom: '1rem' }} />
                  <div className="skeleton" style={{ height: '120px' }} />
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  {/* Original Report */}
                  <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Original Submitted Report
                    </label>
                    <div
                      style={{
                        padding: '0.75rem',
                        backgroundColor: 'var(--bg-elevated)',
                        borderRadius: 'var(--radius-md)',
                        marginTop: '4px',
                        fontSize: '0.875rem',
                        color: 'var(--text-primary)'
                      }}
                    >
                      {incidentDetail.assessment.report_text}
                    </div>
                  </div>

                  {/* Extracted Claim & Category */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        Extracted Core Claim
                      </label>
                      <div
                        style={{
                          padding: '0.625rem',
                          backgroundColor: 'var(--bg-elevated)',
                          borderRadius: 'var(--radius-md)',
                          marginTop: '4px',
                          fontSize: '0.8125rem',
                          color: 'var(--text-secondary)'
                        }}
                      >
                        {incidentDetail.assessment.extracted_claim}
                      </div>
                    </div>
                    <div>
                      <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        Category & Uncertainty
                      </label>
                      <div
                        style={{
                          padding: '0.625rem',
                          backgroundColor: 'var(--bg-elevated)',
                          borderRadius: 'var(--radius-md)',
                          marginTop: '4px',
                          fontSize: '0.8125rem'
                        }}
                      >
                        <div>
                          <strong>{incidentDetail.assessment.crisis_category}</strong> (Conf:{' '}
                          {(incidentDetail.assessment.category_confidence * 100).toFixed(0)}%)
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          Uncertainty score: {incidentDetail.assessment.uncertainty_score?.toFixed(3)}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Verification Outcome */}
                  <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Verification Outcome & Citations
                    </label>
                    <div
                      style={{
                        padding: '0.75rem',
                        backgroundColor: 'var(--bg-elevated)',
                        borderRadius: 'var(--radius-md)',
                        marginTop: '4px'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <span
                          className={`badge ${
                            incidentDetail.assessment.assessment_outcome === 'EVIDENCE_SUPPORTED'
                              ? 'badge-success'
                              : incidentDetail.assessment.assessment_outcome === 'CONTRADICTED_BY_EVIDENCE'
                              ? 'badge-danger'
                              : 'badge-warning'
                          }`}
                        >
                          {incidentDetail.assessment.assessment_outcome}
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {incidentDetail.assessment.evidence_references?.length || 0} reference sources evaluated
                        </span>
                      </div>

                      {incidentDetail.assessment.evidence_references?.map((ref, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: '0.35rem 0.5rem',
                            borderLeft: '2px solid var(--border-default)',
                            marginBottom: '4px',
                            fontSize: '0.75rem'
                          }}
                        >
                          <strong>{ref.source}</strong>: {ref.evidence_id} (Relevance:{' '}
                          {(ref.relevance_score * 100).toFixed(0)}%)
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Forensic Media Assessment */}
                  {incidentDetail.assessment.synthetic_media_risk !== null && (
                    <div>
                      <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        Forensic Synthetic-Media Evaluation
                      </label>
                      <div
                        style={{
                          padding: '0.75rem',
                          backgroundColor: 'var(--bg-elevated)',
                          borderRadius: 'var(--radius-md)',
                          marginTop: '4px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                      >
                        <div>
                          <div style={{ fontWeight: 600, color: 'var(--status-warning)', fontSize: '0.875rem' }}>
                            Synthetic Probability: {(incidentDetail.assessment.synthetic_media_risk * 100).toFixed(1)}%
                          </div>
                          <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                            Model: ResNet-18 Forensics &bull; Calibration: {incidentDetail.assessment.calibration_status}
                          </div>
                        </div>
                        <span className="badge badge-warning">ARTIFACTS DETECTED</span>
                      </div>
                    </div>
                  )}

                  {/* Associated Allocation */}
                  <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Associated MILP Allocation Decision
                    </label>
                    <div
                      style={{
                        padding: '0.75rem',
                        backgroundColor: 'var(--bg-elevated)',
                        borderRadius: 'var(--radius-md)',
                        marginTop: '4px'
                      }}
                    >
                      {incidentDetail.allocation ? (
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontWeight: 600, fontSize: '0.8125rem' }}>
                              Status: {incidentDetail.allocation.allocation_status}
                            </span>
                            <span className="badge badge-info">
                              {incidentDetail.allocation.assigned_quantity} / {incidentDetail.allocation.demanded_quantity}{' '}
                              {incidentDetail.allocation.required_resource_type}
                            </span>
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                            Depot: {incidentDetail.allocation.assigned_depot_id || 'None'} &bull; Road Distance:{' '}
                            {incidentDetail.allocation.road_distance_km ? `${incidentDetail.allocation.road_distance_km.toFixed(2)} km` : 'N/A'}
                          </div>
                          <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                            Rationale: {incidentDetail.allocation.priority_rationale}
                          </div>
                        </div>
                      ) : (
                        <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                          No solver allocation has been run for this incident yet.
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button onClick={handleCloseDetail} className="btn btn-secondary btn-sm">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
