import React from 'react';
import { RefreshCw, Activity, CheckCircle2, AlertOctagon } from 'lucide-react';
import { ServicesHealthResponse } from '../api/client';

interface HeaderProps {
  title: string;
  subtitle: string;
  lastRefreshed: string;
  onRefresh: () => void;
  isRefreshing: boolean;
  servicesHealth: ServicesHealthResponse | null;
  backendOnline: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  lastRefreshed,
  onRefresh,
  isRefreshing,
  servicesHealth,
  backendOnline
}) => {
  const hdfsStatus = servicesHealth?.big_data_cluster?.hdfs?.status || 'UNKNOWN';
  const kafkaStatus = servicesHealth?.big_data_cluster?.kafka?.status || 'UNKNOWN';

  return (
    <header
      style={{
        height: '64px',
        backgroundColor: 'var(--bg-card)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 1.5rem',
        flexShrink: 0
      }}
    >
      {/* Title & Subtitle */}
      <div>
        <h1 style={{ fontSize: '1.125rem', fontWeight: 600, margin: 0, color: 'var(--text-primary)' }}>
          {title}
        </h1>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
          {subtitle}
        </p>
      </div>

      {/* Right Controls: Service Health Indicators & Refresh */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {/* Synthetic Demonstration Badge */}
        <span
          className="badge badge-synthetic"
          title="Incident scenarios, evidence records, and depot inventories are modeled after official emergency management standards for demonstration."
        >
          Curated Demo Environment
        </span>

        {/* Backend & Big Data Health Status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.35rem 0.75rem',
            backgroundColor: 'var(--bg-app)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-default)',
            fontSize: '0.75rem'
          }}
        >
          {backendOnline ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--status-success)' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--status-success)' }} />
              <span style={{ fontWeight: 600 }}>API Connected</span>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--status-danger)' }}>
              <AlertOctagon size={14} />
              <span style={{ fontWeight: 600 }}>API Offline</span>
            </div>
          )}

          <span style={{ color: 'var(--border-default)' }}>|</span>

          {/* Quick cluster indicators */}
          <div style={{ display: 'flex', gap: '0.5rem', color: 'var(--text-secondary)' }}>
            <span
              style={{
                color: hdfsStatus === 'ONLINE' ? 'var(--status-success)' : 'var(--text-muted)',
                fontWeight: 500
              }}
              title={`HDFS 9000: ${hdfsStatus}`}
            >
              HDFS: {hdfsStatus}
            </span>
            <span
              style={{
                color: kafkaStatus === 'ONLINE' ? 'var(--status-success)' : 'var(--text-muted)',
                fontWeight: 500
              }}
              title={`Kafka 9092: ${kafkaStatus}`}
            >
              Kafka: {kafkaStatus}
            </span>
          </div>
        </div>

        {/* Last Refreshed & Refresh Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {lastRefreshed ? `Refreshed ${new Date(lastRefreshed).toLocaleTimeString()}` : ''}
          </span>
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="btn btn-secondary btn-sm"
            title="Refresh live data from backend"
          >
            <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>
    </header>
  );
};
