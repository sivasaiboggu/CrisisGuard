import React, { useState } from 'react';
import {
  FileCheck2,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Info,
  Clock,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  Send
} from 'lucide-react';
import { ClaimAssessment, api } from '../api/client';

interface EvidenceVerificationViewProps {
  assessments: ClaimAssessment[];
  loading: boolean;
  onRefresh: () => void;
  onNotify: (type: 'success' | 'warning' | 'error' | 'info', title: string, message: string) => void;
}

export const EvidenceVerificationView: React.FC<EvidenceVerificationViewProps> = ({
  assessments,
  loading,
  onRefresh,
  onNotify
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOutcome, setFilterOutcome] = useState('ALL');

  // Live Assessment Form State
  const [claimText, setClaimText] = useState('');
  const [claimLocation, setClaimLocation] = useState('Delhi, NCR');
  const [submitting, setSubmitting] = useState(false);

  const filtered = assessments.filter((asmt) => {
    const matchesSearch =
      asmt.claim_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asmt.report_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asmt.extracted_claim.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asmt.crisis_category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesOutcome =
      filterOutcome === 'ALL' || asmt.assessment_outcome === filterOutcome;
    return matchesSearch && matchesOutcome;
  });

  const handleRunAssessment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!claimText.trim()) return;

    setSubmitting(true);
    try {
      const res = await api.assessClaim({
        text: claimText,
        location: claimLocation,
        latitude: 28.6619,
        longitude: 77.2492
      });
      onNotify('success', 'Claim Assessed Live', `Outcome: ${res.assessment_outcome} (Uncertainty: ${res.uncertainty_score?.toFixed(3)})`);
      setClaimText('');
      onRefresh();
    } catch (err: any) {
      onNotify('error', 'Assessment Error', err.message || 'Failed to execute evidence assessor.');
    } finally {
      setSubmitting(false);
    }
  };

  const loadPresetClaim = (preset: string) => {
    setClaimText(preset);
  };

  return (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Transparency & Reference Notice */}
      <div
        className="card"
        style={{
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          borderLeft: '4px solid var(--accent-primary)',
          display: 'flex',
          gap: '1rem',
          alignItems: 'flex-start'
        }}
      >
        <ShieldCheck size={20} color="var(--accent-primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
            Curated Demonstration Reference Fixtures
          </div>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
            Reference records from NDMA, Central Water Commission (CWC), and Municipal Emergency Logs are 
            curated demonstration baselines modeled after official civil defense formats. They provide ground-truth 
            evidence citations without claiming live, non-public government telemetry feeds.
          </p>
        </div>
      </div>

      {/* Live Claim Submission Console */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <Sparkles size={16} /> Live Evidence Assessor Console
            </div>
            <div className="card-subtitle">
              Extract claims, cross-reference curated evidence store, and apply NLI verification
            </div>
          </div>
        </div>

        <form onSubmit={handleRunAssessment} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Report / Claim Text to Verify
            </label>
            <textarea
              rows={2}
              value={claimText}
              onChange={(e) => setClaimText(e.target.value)}
              placeholder="e.g. Yamuna river breached danger level of 208.66m near Old Railway Bridge..."
              className="input-control"
              style={{ marginTop: '4px', resize: 'vertical' }}
            />
          </div>

          {/* Quick presets */}
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Presets:</span>
            <button
              type="button"
              onClick={() => loadPresetClaim("Yamuna embankment breached at Mayur Vihar, 500 families submerged!")}
              className="btn btn-outline btn-sm"
            >
              Supported: Yamuna Embankment
            </button>
            <button
              type="button"
              onClick={() => loadPresetClaim("Secret chemical explosion spreading green gas cloud over Connaught Place!")}
              className="btn btn-outline btn-sm"
            >
              Contradicted: Toxic Chemical Hoax
            </button>
            <button
              type="button"
              onClick={() => loadPresetClaim("Unconfirmed cracks reported near Metro Pillar 140.")}
              className="btn btn-outline btn-sm"
            >
              Unverified / Human Review
            </button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
            <button type="submit" disabled={!claimText.trim() || submitting} className="btn btn-primary">
              <Send size={14} className={submitting ? 'animate-spin' : ''} />
              {submitting ? 'Evaluating DeBERTa NLI...' : 'Verify Claim with Evidence Store'}
            </button>
          </div>
        </form>
      </div>

      {/* Filter and Search Bar */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: '1 1 300px' }}>
          <div style={{ position: 'relative', width: '100%' }}>
            <Search
              size={16}
              style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }}
            />
            <input
              type="text"
              placeholder="Search assessment claims, keywords, categories..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-control"
              style={{ paddingLeft: '34px' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Filter size={16} color="var(--text-muted)" />
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>Outcome:</span>
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

      {/* Assessment History Cards / Table */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {filtered.map((asmt) => {
          let outcomeBadge = 'badge-neutral';
          if (asmt.assessment_outcome === 'EVIDENCE_SUPPORTED') outcomeBadge = 'badge-success';
          if (asmt.assessment_outcome === 'CONTRADICTED_BY_EVIDENCE') outcomeBadge = 'badge-danger';
          if (asmt.assessment_outcome === 'REQUIRES_HUMAN_REVIEW') outcomeBadge = 'badge-warning';

          return (
            <div key={asmt.assessment_id} className="card" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '4px' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {asmt.claim_id}
                    </span>
                    <span className={`badge ${outcomeBadge}`}>{asmt.assessment_outcome}</span>
                    <span className="badge badge-neutral">{asmt.crisis_category}</span>
                    {asmt.human_review_required && (
                      <span className="badge badge-warning">Review Flagged</span>
                    )}
                  </div>
                  <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                    "{asmt.extracted_claim || asmt.report_text}"
                  </h3>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Uncertainty Score</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
                    {asmt.uncertainty_score?.toFixed(3) ?? '0.000'}
                  </div>
                </div>
              </div>

              {/* Evidence Citations */}
              <div style={{ backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', padding: '0.75rem', marginTop: '0.5rem' }}>
                <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Ground-Truth Evidence References ({asmt.evidence_references?.length || 0}):
                </div>

                {asmt.evidence_references && asmt.evidence_references.length > 0 ? (
                  asmt.evidence_references.map((ref, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: '0.75rem',
                        padding: '4px 0',
                        borderBottom: idx < asmt.evidence_references.length - 1 ? '1px solid var(--border-subtle)' : 'none'
                      }}
                    >
                      <span style={{ color: 'var(--text-primary)' }}>
                        <strong>[{ref.source}]</strong> {ref.evidence_id} {ref.title ? `- ${ref.title}` : ''}
                      </span>
                      <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        Relevance: {(ref.relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))
                ) : (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    No authoritative match found in reference database (Marked UNVERIFIED).
                  </div>
                )}
              </div>

              {/* Forensic & Propagation Footnote */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.75rem', fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                <div>
                  Demanded: {asmt.demanded_resources?.demanded_quantity || 0}{' '}
                  {asmt.demanded_resources?.resource_type || 'N/A'}
                </div>
                <div>
                  Evaluated at: {new Date(asmt.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
