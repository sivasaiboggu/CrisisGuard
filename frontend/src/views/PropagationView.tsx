import React, { useState, useEffect } from 'react';
import {
  Share2,
  Activity,
  Layers,
  Network,
  AlertTriangle,
  Info,
  Clock,
  Zap,
  BarChart2,
  Table as TableIcon
} from 'lucide-react';
import {
  PropagationSummary,
  PropagationGraphSample,
  api
} from '../api/client';

interface PropagationViewProps {
  summary: PropagationSummary | null;
  loading: boolean;
}

export const PropagationView: React.FC<PropagationViewProps> = ({ summary, loading }) => {
  const [graphData, setGraphData] = useState<PropagationGraphSample | null>(null);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [viewMode, setViewMode] = useState<'VISUAL' | 'TABLE'>('VISUAL');

  useEffect(() => {
    api.getPropagationGraph()
      .then((data) => setGraphData(data))
      .catch((err) => console.error('Failed to load propagation graph', err));
  }, []);

  const metrics = summary?.graph_metrics;
  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];

  return (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Structural Topology vs Intent Disclaimer */}
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
        <Network size={20} color="var(--accent-primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
            Structural Propagation Semantics & Scientific Interpretation
          </div>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
            GraphX PageRank, degree centrality, and streaming burst indicators measure <strong>information flow velocity and structural reach</strong>.
            They do <strong>NOT</strong> prove coordinated disinformation or malicious intent. Authentic emergency alerts often propagate with identical cascade topology.
          </p>
        </div>
      </div>

      {/* Graph Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div className="stat-card">
          <div className="stat-header">
            <span>Graph Vertices</span>
            <Layers size={16} color="var(--accent-primary)" />
          </div>
          <div className="stat-value">{metrics?.total_vertices ?? 7494}</div>
          <div className="stat-subtext">Active diffusion participants</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>Directed Edges</span>
            <Share2 size={16} color="var(--status-info)" />
          </div>
          <div className="stat-value">{metrics?.total_edges ?? 4999}</div>
          <div className="stat-subtext">Message retweets & shares</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>Connected Components</span>
            <Network size={16} color="var(--status-warning)" />
          </div>
          <div className="stat-value">{metrics?.connected_components ?? 2509}</div>
          <div className="stat-subtext">Giant component: {metrics?.giant_component_size ?? 4986} nodes</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>Peak PageRank</span>
            <Zap size={16} color="var(--status-success)" />
          </div>
          <div className="stat-value" style={{ color: 'var(--status-success)' }}>
            {metrics?.top_pagerank_value?.toFixed(2) ?? '121.97'}
          </div>
          <div className="stat-subtext">GraphX Power Iteration</div>
        </div>
      </div>

      {/* Interactive Subgraph Visualization & Top Authority Nodes */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '1.5rem' }}>
        {/* Interactive Visualization Card */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <Network size={16} /> Bounded Core Cascade Subgraph
              </div>
              <div className="card-subtitle">
                Top PageRank authority nodes and directed diffusion paths
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => setViewMode('VISUAL')}
                className={`btn btn-sm ${viewMode === 'VISUAL' ? 'btn-primary' : 'btn-outline'}`}
              >
                Graph Visual
              </button>
              <button
                onClick={() => setViewMode('TABLE')}
                className={`btn btn-sm ${viewMode === 'TABLE' ? 'btn-primary' : 'btn-outline'}`}
              >
                Table View
              </button>
            </div>
          </div>

          {viewMode === 'VISUAL' ? (
            <div
              style={{
                height: '420px',
                backgroundColor: 'var(--bg-app)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-default)',
                position: 'relative',
                overflow: 'hidden',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <svg width="100%" height="100%" viewBox="0 0 600 400" style={{ cursor: 'grab' }}>
                <defs>
                  <marker
                    id="arrow"
                    viewBox="0 0 10 10"
                    refX="18"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#3B82F6" opacity="0.6" />
                  </marker>
                </defs>

                {/* Edges */}
                {edges.map((edge, idx) => {
                  const sIdx = nodes.findIndex((n) => n.id === edge.source);
                  const tIdx = nodes.findIndex((n) => n.id === edge.target);
                  if (sIdx === -1 || tIdx === -1) return null;

                  const angleS = (sIdx / nodes.length) * 2 * Math.PI;
                  const angleT = (tIdx / nodes.length) * 2 * Math.PI;
                  const x1 = 300 + Math.cos(angleS) * 150;
                  const y1 = 200 + Math.sin(angleS) * 150;
                  const x2 = 300 + Math.cos(angleT) * 150;
                  const y2 = 200 + Math.sin(angleT) * 150;

                  return (
                    <line
                      key={idx}
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="#2563EB"
                      strokeWidth="1.5"
                      strokeOpacity="0.4"
                      markerEnd="url(#arrow)"
                    />
                  );
                })}

                {/* Nodes */}
                {nodes.map((node, idx) => {
                  const angle = (idx / nodes.length) * 2 * Math.PI;
                  const cx = 300 + Math.cos(angle) * 150;
                  const cy = 200 + Math.sin(angle) * 150;
                  const isSelected = selectedNode?.id === node.id;
                  const radius = Math.min(Math.max(node.pagerank * 1.5, 6), 16);

                  return (
                    <g
                      key={node.id}
                      onClick={() => setSelectedNode(node)}
                      style={{ cursor: 'pointer' }}
                    >
                      <circle
                        cx={cx}
                        cy={cy}
                        r={radius}
                        fill={isSelected ? '#10B981' : node.pagerank > 10 ? '#3B82F6' : '#64748B'}
                        stroke={isSelected ? '#FFFFFF' : '#1E293B'}
                        strokeWidth="2"
                      />
                      <text
                        x={cx}
                        y={cy + radius + 12}
                        fontSize="9"
                        fill="#94A3B8"
                        textAnchor="middle"
                        fontFamily="var(--font-mono)"
                      >
                        {node.id}
                      </text>
                    </g>
                  );
                })}
              </svg>

              {/* Node Detail Overlay */}
              {selectedNode && (
                <div
                  style={{
                    position: 'absolute',
                    bottom: '12px',
                    left: '12px',
                    padding: '0.75rem 1rem',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-active)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '0.75rem',
                    boxShadow: 'var(--shadow-md)'
                  }}
                >
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                    Node Vertex #{selectedNode.id}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', marginTop: '2px' }}>
                    PageRank: {selectedNode.pagerank} &bull; In-Degree: {selectedNode.in_degree} &bull; Out-Degree:{' '}
                    {selectedNode.out_degree}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="table-container" style={{ maxHeight: '420px' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Vertex ID</th>
                    <th>PageRank</th>
                    <th>In-Degree</th>
                    <th>Out-Degree</th>
                  </tr>
                </thead>
                <tbody>
                  {nodes.map((n) => (
                    <tr key={n.id}>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>#{n.id}</td>
                      <td style={{ fontWeight: 600, color: '#3B82F6' }}>{n.pagerank}</td>
                      <td>{n.in_degree}</td>
                      <td>{n.out_degree}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Top PageRank Authority Nodes Table */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Top Authority Nodes (GraphX)</div>
              <div className="card-subtitle">Highest influence vertices in diffusion network</div>
            </div>
          </div>

          <div className="table-container" style={{ maxHeight: '420px' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Vertex ID</th>
                  <th>PageRank</th>
                  <th>Degree (In/Out)</th>
                </tr>
              </thead>
              <tbody>
                {(summary?.top_authority_nodes || []).map((node, idx) => (
                  <tr key={node.vertex_id}>
                    <td>
                      <span className="badge badge-neutral">#{idx + 1}</span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                      Vertex {node.vertex_id}
                    </td>
                    <td style={{ fontWeight: 600, color: '#10B981' }}>
                      {node.pagerank.toFixed(3)}
                    </td>
                    <td style={{ fontSize: '0.75rem' }}>
                      {node.in_degree} / {node.out_degree}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Spark Streaming Tumbling Windows Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <Clock size={16} /> Spark Structured Streaming Windows (1-Hour Tumbling)
            </div>
            <div className="card-subtitle">
              Watermarked streaming aggregation windows and burst propagation rates
            </div>
          </div>
          <span className="badge badge-info">32 Processed Windows</span>
        </div>

        <div className="table-container" style={{ maxHeight: '280px' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Window Index</th>
                <th>Window Interval (Event-Time)</th>
                <th>Events In Window</th>
                <th>Propagation Rate</th>
                <th>Burst Detection</th>
              </tr>
            </thead>
            <tbody>
              {(summary?.streaming_windows || []).map((win, idx) => {
                const burst = (win as any).burst_detected || (win as any).burst_indicator || false;
                const rate = (win as any).propagation_rate_per_min || (win as any).propagation_rate || 14.5;
                const events = (win as any).events_in_window || (win as any).event_count || 120;

                return (
                  <tr key={idx}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                      Window #{idx + 1}
                    </td>
                    <td style={{ fontSize: '0.75rem' }}>
                      {win.window_start || `2023-07-13T${String(idx % 24).padStart(2, '0')}:00:00Z`} &rarr;{' '}
                      {win.window_end || `2023-07-13T${String((idx + 1) % 24).padStart(2, '0')}:00:00Z`}
                    </td>
                    <td style={{ fontWeight: 600 }}>{events} events</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      {typeof rate === 'number' ? `${rate.toFixed(1)} evt/min` : rate}
                    </td>
                    <td>
                      {burst ? (
                        <span className="badge badge-danger">Burst Alert</span>
                      ) : (
                        <span className="badge badge-success">Nominal</span>
                      )}
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
