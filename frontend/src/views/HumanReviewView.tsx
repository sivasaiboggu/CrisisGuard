import React, { useState } from 'react';
import {
  UserCheck2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  ShieldCheck,
  FileText,
  History,
  X,
  ExternalLink
} from 'lucide-react';
import {
  AllocationRecord,
  AuditEntry,
  api
} from '../api/client';

interface HumanReviewViewProps {
  allocations: AllocationRecord[];
  auditLogs: AuditEntry[];
  loading: boolean;
  onRefresh: () => void;
  onNotify: (type: 'success' | 'warning' | 'error' | 'info', title: string, message: string) => void;
}

export const HumanReviewView: React.FC<HumanReviewViewProps> = ({
  allocations,
  auditLogs,
  loading,
  onRefresh,
  onNotify
}) => {
  const [selectedAction, setSelectedAction] = useState<{
    type: 'APPROVE' | 'REJECT';
    allocation: AllocationRecord;
  } | null>(null);
  const [dispatcherName, setDispatcherName] = useState('CrisisCoordinator_DisasterControl');
  const [rejectReason, setRejectReason] = useState('Infeasible flood access route; diverted to emergency shelter');
  const [processing, setProcessing] = useState(false);

  // Review queue includes allocations awaiting approval or unallocated with review flag
  const reviewQueue = allocations.filter(
    (a) => a.allocation_status === 'AWAITING_APPROVAL' || a.verification_status === 'REQUIRES_HUMAN_REVIEW'
  );

  const handleConfirmAction = async () => {
    if (!selectedAction) return;
    setProcessing(true);
    try {
      if (selectedAction.type === 'APPROVE') {
        const res = await api.approveAllocation(selectedAction.allocation.allocation_id, dispatcherName);
        onNotify(
          'success',
          'Allocation Approved & Persisted',
          `Incident ${selectedAction.allocation.incident_id} approved by ${dispatcherName}. Status updated to RECOMMENDED.`
        );
      } else {
        const res = await api.rejectAllocation(
          selectedAction.allocation.allocation_id,
          dispatcherName,
          rejectReason
        );
        onNotify(
          'warning',
          'Allocation Rejected & Logged',
          `Incident ${selectedAction.allocation.incident_id} rejected by ${dispatcherName}. Recorded in audit history.`
        );
      }
      setSelectedAction(null);
      onRefresh();
    } catch (err: any) {
      onNotify('error', 'Action Failed', err.message || 'Failed to submit review action.');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Governance Banner */}
      <div
        className="card"
        style={{
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          borderLeft: '4px solid var(--status-success)',
          display: 'flex',
          gap: '1rem',
          alignItems: 'flex-start'
        }}
      >
        <ShieldCheck size={20} color="var(--status-success)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
            Dispatcher Sign-Off & Immutable Audit Trail
          </div>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
            Allocations tagged as <code>REQUIRES_HUMAN_REVIEW</code> or held by safety gates require explicit human dispatcher approval.
            Every decision triggers an immutable cryptographic audit record persisted in <code>results/audit/audit_history.json</code>.
          </p>
        </div>
      </div>

      {/* Review Queue Cards */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <UserCheck2 size={16} /> Pending Dispatcher Approval Queue ({reviewQueue.length})
            </div>
            <div className="card-subtitle">
              Incidents requiring human validation before emergency resource recommendation is released
            </div>
          </div>
        </div>

        {reviewQueue.length === 0 ? (
          <div className="empty-state">
            <CheckCircle2 className="empty-state-icon" style={{ color: 'var(--status-success)' }} />
            <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>No Pending Approvals</div>
            <div style={{ fontSize: '0.8125rem', marginTop: '4px' }}>
              All current incidents have either passed automated verification gates or been reviewed.
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {reviewQueue.map((item) => (
              <div
                key={item.allocation_id}
                style={{
                  padding: '1.25rem',
                  backgroundColor: 'var(--bg-elevated)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-default)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '1rem',
                  flexWrap: 'wrap'
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                      {item.incident_id}
                    </span>
                    <span className="badge badge-warning">{item.allocation_status}</span>
                    <span className="badge badge-neutral">{item.required_resource_type}</span>
                    <span className="badge badge-info">{item.urgency_level} URGENCY</span>
                  </div>

                  <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                    Demanded: {item.demanded_quantity} units &bull; Solver Proposed:{' '}
                    <strong>{item.assigned_quantity} units</strong> from {item.assigned_depot_id || 'Depot'}
                  </div>

                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Safety Rationale: {item.priority_rationale}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    onClick={() => setSelectedAction({ type: 'APPROVE', allocation: item })}
                    className="btn btn-primary btn-sm"
                    style={{ backgroundColor: 'var(--status-success)', borderColor: 'var(--status-success)' }}
                  >
                    <CheckCircle2 size={14} /> Approve Recommendation
                  </button>
                  <button
                    onClick={() => setSelectedAction({ type: 'REJECT', allocation: item })}
                    className="btn btn-danger btn-sm"
                  >
                    <XCircle size={14} /> Reject / Block
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Persistent Audit Log Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <History size={16} /> Immutable Dispatcher Audit Log ({auditLogs.length})
            </div>
            <div className="card-subtitle">
              Persisted audit history loaded directly from <code>results/audit/audit_history.json</code>
            </div>
          </div>
        </div>

        <div className="table-container" style={{ maxHeight: '360px' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Audit ID</th>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Target Incident / Resource</th>
                <th>Dispatcher / Actor</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    No audit records logged yet. Run assessments or approve allocations to generate audit entries.
                  </td>
                </tr>
              ) : (
                auditLogs.map((log) => {
                  let badgeClass = 'badge-neutral';
                  if (log.action.includes('APPROVED')) badgeClass = 'badge-success';
                  if (log.action.includes('REJECTED')) badgeClass = 'badge-danger';
                  if (log.action.includes('OPTIMIZATION')) badgeClass = 'badge-info';

                  return (
                    <tr key={log.audit_id}>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                        {log.audit_id}
                      </td>
                      <td style={{ fontSize: '0.75rem' }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td>
                        <span className={`badge ${badgeClass}`}>{log.action}</span>
                      </td>
                      <td style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                        {log.target_id}
                      </td>
                      <td style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                        {log.actor}
                      </td>
                      <td style={{ fontSize: '0.75rem', maxWidth: '300px', color: 'var(--text-muted)' }}>
                        {typeof log.details === 'object' ? JSON.stringify(log.details) : String(log.details)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Confirmation Modal */}
      {selectedAction && (
        <div className="modal-overlay" onClick={() => setSelectedAction(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {selectedAction.type === 'APPROVE' ? (
                  <CheckCircle2 size={18} color="var(--status-success)" />
                ) : (
                  <XCircle size={18} color="var(--status-danger)" />
                )}
                <span style={{ fontWeight: 600, fontSize: '0.9375rem', color: 'var(--text-primary)' }}>
                  {selectedAction.type === 'APPROVE' ? 'Confirm Allocation Approval' : 'Confirm Allocation Rejection'}
                </span>
              </div>
              <button
                onClick={() => setSelectedAction(null)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              <div style={{ marginBottom: '1rem', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                Target Incident: <strong>{selectedAction.allocation.incident_id}</strong> &bull; Resource:{' '}
                {selectedAction.allocation.demanded_quantity} {selectedAction.allocation.required_resource_type}
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Dispatcher Identification
                  </label>
                  <input
                    type="text"
                    value={dispatcherName}
                    onChange={(e) => setDispatcherName(e.target.value)}
                    className="input-control"
                    style={{ marginTop: '4px' }}
                  />
                </div>

                {selectedAction.type === 'REJECT' && (
                  <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Rejection Justification (Logged to Audit Trail)
                    </label>
                    <textarea
                      rows={2}
                      value={rejectReason}
                      onChange={(e) => setRejectReason(e.target.value)}
                      className="input-control"
                      style={{ marginTop: '4px' }}
                    />
                  </div>
                )}
              </div>
            </div>

            <div className="modal-footer">
              <button onClick={() => setSelectedAction(null)} className="btn btn-secondary btn-sm">
                Cancel
              </button>
              <button
                onClick={handleConfirmAction}
                disabled={processing}
                className={`btn btn-sm ${selectedAction.type === 'APPROVE' ? 'btn-primary' : 'btn-danger'}`}
              >
                {processing ? 'Persisting Decision...' : 'Commit to Audit Log'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
