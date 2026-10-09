import React, { useState } from 'react';
import {
  Truck,
  MapPin,
  Play,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  ShieldAlert,
  Info,
  Layers,
  ArrowRight
} from 'lucide-react';
import {
  AllocationRecord,
  DepotResource,
  api
} from '../api/client';

interface ResourceAllocationViewProps {
  allocations: AllocationRecord[];
  resources: DepotResource[];
  loading: boolean;
  onRefresh: () => void;
  onNotify: (type: 'success' | 'warning' | 'error' | 'info', title: string, message: string) => void;
  onNavigateToReview: () => void;
}

export const ResourceAllocationView: React.FC<ResourceAllocationViewProps> = ({
  allocations,
  resources,
  loading,
  onRefresh,
  onNotify,
  onNavigateToReview
}) => {
  const [optimizing, setOptimizing] = useState(false);
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredAllocations = allocations.filter((a) => {
    return statusFilter === 'ALL' || a.allocation_status === statusFilter;
  });

  const handleRunOptimizer = async () => {
    setOptimizing(true);
    try {
      // Run batch optimization over test crisis incidents
      const demoIncidents = [
        {
          incident_id: 'INC_01_YAMUNA_BREACH',
          incident_category: 'affected_individuals',
          urgency_level: 'HIGH',
          verification_status: 'EVIDENCE_SUPPORTED',
          required_resource_type: 'RESCUE_BOAT',
          demanded_quantity: 4,
          latitude: 28.6279,
          longitude: 77.2784,
          human_approved: false
        },
        {
          incident_id: 'INC_02_BRIDGE_COLLAPSE',
          incident_category: 'infrastructure_and_utility_damage',
          urgency_level: 'HIGH',
          verification_status: 'CONTRADICTED_BY_EVIDENCE',
          required_resource_type: 'AMBULANCE',
          demanded_quantity: 3,
          latitude: 28.6619,
          longitude: 77.2492,
          human_approved: false
        },
        {
          incident_id: 'INC_03_FLOOD_RELIEF_ROHINI',
          incident_category: 'affected_individuals',
          urgency_level: 'MEDIUM',
          verification_status: 'EVIDENCE_SUPPORTED',
          required_resource_type: 'SUPPLY_TRUCK',
          demanded_quantity: 2,
          latitude: 28.7159,
          longitude: 77.1102,
          human_approved: false
        },
        {
          incident_id: 'INC_04_METRO_TRAUMA_STANDBY',
          incident_category: 'infrastructure_and_utility_damage',
          urgency_level: 'MEDIUM',
          verification_status: 'REQUIRES_HUMAN_REVIEW',
          required_resource_type: 'AMBULANCE',
          demanded_quantity: 2,
          latitude: 28.6304,
          longitude: 77.2177,
          human_approved: false
        }
      ];

      const res = await api.optimizeAllocations(demoIncidents, true);
      onNotify(
        'success',
        'HiGHS MILP Optimization Solved',
        `Successfully optimized ${res.length} incidents using OSM road network Dijkstra.`
      );
      onRefresh();
    } catch (err: any) {
      onNotify('error', 'Optimization Failed', err.message || 'Error running MILP solver.');
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Human-in-the-Loop Dispatch Warning & Disclaimer */}
      <div
        className="card"
        style={{
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          borderLeft: '4px solid var(--status-warning)',
          display: 'flex',
          gap: '1rem',
          alignItems: 'flex-start'
        }}
      >
        <ShieldAlert size={20} color="var(--status-warning)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
            Strict Human-in-the-Loop Governance: Advisory Decision Support Only
          </div>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
            Allocations generated below are mathematical solver recommendations derived via <strong>HiGHS MILP optimization</strong> and <strong>OpenStreetMap Dijkstra routing</strong>.
            They do <strong>NOT</strong> dispatch real vehicles, boats, or personnel. Unverified claims and contradicted hoaxes are automatically held or blocked at the verification gate.
          </p>
        </div>
      </div>

      {/* Depot Inventory Overview Cards with Synthetic Badge */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <Truck size={16} /> Regional Emergency Depots & Available Inventory
            </div>
            <div className="card-subtitle">
              Current demonstration asset capacities across Delhi metropolitan emergency depots
            </div>
          </div>
          <span className="badge badge-synthetic">Synthetic Demo Assets</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
          {resources.map((res) => {
            const avail = res.total_capacity - res.allocated_quantity;
            return (
              <div
                key={res.resource_id}
                style={{
                  padding: '1rem',
                  backgroundColor: 'var(--bg-elevated)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-default)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.8125rem', color: 'var(--text-primary)' }}>
                      {res.resource_type.replace('_', ' ')}
                    </div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                      {res.depot_id}
                    </div>
                  </div>
                  <span
                    className={`badge ${avail > 0 ? 'badge-success' : 'badge-danger'}`}
                  >
                    {avail} Avail
                  </span>
                </div>

                <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  <div>Total Capacity: {res.total_capacity} units</div>
                  <div>Allocated: {res.allocated_quantity} units</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Solver Action Bar */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={handleRunOptimizer}
            disabled={optimizing}
            className="btn btn-primary"
          >
            <Play size={14} className={optimizing ? 'animate-spin' : ''} />
            {optimizing ? 'Solving HiGHS MILP...' : 'Execute Multi-Incident MILP Optimization'}
          </button>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Routing: OSM Dijkstra (63.6k nodes) &bull; Safety Gate: Active
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>Filter Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-control"
            style={{ width: 'auto' }}
          >
            <option value="ALL">All Statuses</option>
            <option value="RECOMMENDED">RECOMMENDED</option>
            <option value="AWAITING_APPROVAL">AWAITING_APPROVAL</option>
            <option value="UNALLOCATED">UNALLOCATED</option>
          </select>
        </div>
      </div>

      {/* Allocations Results Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Solver Allocation Recommendations ({filteredAllocations.length})</div>
            <div className="card-subtitle">
              Exact solver outputs based on urgency, road distance, and verification outcomes
            </div>
          </div>
          <button onClick={onNavigateToReview} className="btn btn-outline btn-sm">
            Open Dispatcher Review Queue <ArrowRight size={14} />
          </button>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Allocation ID</th>
                <th>Incident ID</th>
                <th>Verification</th>
                <th>Resource Type</th>
                <th>Demand</th>
                <th>Assigned</th>
                <th>Assigned Depot</th>
                <th>OSM Distance</th>
                <th>Status</th>
                <th>Rationale / Safety Gate</th>
              </tr>
            </thead>
            <tbody>
              {filteredAllocations.map((al) => {
                let badgeClass = 'badge-neutral';
                if (al.allocation_status === 'RECOMMENDED') badgeClass = 'badge-success';
                if (al.allocation_status === 'AWAITING_APPROVAL') badgeClass = 'badge-warning';
                if (al.allocation_status === 'UNALLOCATED') badgeClass = 'badge-danger';

                return (
                  <tr key={al.allocation_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                      {al.allocation_id}
                    </td>
                    <td style={{ fontWeight: 600 }}>{al.incident_id}</td>
                    <td>
                      <span
                        className={`badge ${
                          al.verification_status === 'EVIDENCE_SUPPORTED'
                            ? 'badge-success'
                            : al.verification_status === 'CONTRADICTED_BY_EVIDENCE'
                            ? 'badge-danger'
                            : 'badge-warning'
                        }`}
                      >
                        {al.verification_status}
                      </span>
                    </td>
                    <td>{al.required_resource_type}</td>
                    <td>{al.demanded_quantity}</td>
                    <td style={{ fontWeight: 700, color: al.assigned_quantity > 0 ? '#10B981' : '#EF4444' }}>
                      {al.assigned_quantity}
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      {al.assigned_depot_id || 'None'}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      {al.road_distance_km ? `${al.road_distance_km.toFixed(2)} km` : 'N/A'}
                    </td>
                    <td>
                      <span className={`badge ${badgeClass}`}>{al.allocation_status}</span>
                    </td>
                    <td style={{ fontSize: '0.75rem', maxWidth: '280px', color: 'var(--text-secondary)' }}>
                      {al.priority_rationale}
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
