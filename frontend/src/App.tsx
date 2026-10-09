import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar, NavTab } from './components/Sidebar';
import { Header } from './components/Header';
import { ToastContainer, ToastMessage } from './components/Toast';

import { OverviewView } from './views/OverviewView';
import { IncidentsView } from './views/IncidentsView';
import { SyntheticMediaView } from './views/SyntheticMediaView';
import { EvidenceVerificationView } from './views/EvidenceVerificationView';
import { PropagationView } from './views/PropagationView';
import { ResourceAllocationView } from './views/ResourceAllocationView';
import { HumanReviewView } from './views/HumanReviewView';

import {
  api,
  OverviewResponse,
  ServicesHealthResponse,
  IncidentSummary,
  ClaimAssessment,
  PropagationSummary,
  DepotResource,
  AllocationRecord,
  AuditEntry
} from './api/client';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Global Backend Data State
  const [backendOnline, setBackendOnline] = useState(false);
  const [servicesHealth, setServicesHealth] = useState<ServicesHealthResponse | null>(null);
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [assessments, setAssessments] = useState<ClaimAssessment[]>([]);
  const [propagationSummary, setPropagationSummary] = useState<PropagationSummary | null>(null);
  const [resources, setResources] = useState<DepotResource[]>([]);
  const [allocations, setAllocations] = useState<AllocationRecord[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditEntry[]>([]);

  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState<string>('');

  // Toast notifications
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (
    type: 'success' | 'warning' | 'error' | 'info',
    title: string,
    message: string
  ) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  };

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Central Data Fetcher
  const fetchData = useCallback(async (isSilent = false) => {
    if (!isSilent) setIsRefreshing(true);
    try {
      // 1. Health check
      try {
        await api.getHealth();
        setBackendOnline(true);
      } catch {
        setBackendOnline(false);
      }

      // 2. Fetch parallel endpoints
      const [
        svcHealth,
        ovView,
        incList,
        asmtList,
        propSumm,
        resList,
        allocList,
        audList
      ] = await Promise.allSettled([
        api.getServicesHealth(),
        api.getOverview(),
        api.getIncidents(),
        api.getAssessmentHistory(),
        api.getPropagationSummary(),
        api.getResources(),
        api.getAllocations(),
        api.getAuditLog()
      ]);

      if (svcHealth.status === 'fulfilled') setServicesHealth(svcHealth.value);
      if (ovView.status === 'fulfilled') setOverview(ovView.value);
      if (incList.status === 'fulfilled') setIncidents(incList.value);
      if (asmtList.status === 'fulfilled') setAssessments(asmtList.value);
      if (propSumm.status === 'fulfilled') setPropagationSummary(propSumm.value);
      if (resList.status === 'fulfilled') setResources(resList.value.resources || []);
      if (allocList.status === 'fulfilled') setAllocations(allocList.value);
      if (audList.status === 'fulfilled') setAuditLogs(audList.value);

      setLastRefreshed(new Date().toISOString());
    } catch (err: any) {
      console.error('Data refresh error:', err);
      if (!isSilent) {
        addToast('error', 'Connection Error', 'Failed to reach CrisisGuard FastAPI backend.');
      }
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchData();
    // Poll every 30 seconds
    const interval = setInterval(() => {
      fetchData(true);
    }, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Tab Titles
  const tabTitles: Record<NavTab, { title: string; subtitle: string }> = {
    overview: {
      title: 'Executive Intelligence Overview',
      subtitle: 'Real-time multi-modal crisis intelligence and humanitarian resource allocation'
    },
    incidents: {
      title: 'Crisis Incident Intelligence',
      subtitle: 'In-depth multi-modal claims, NLP categorization, and evidence verification'
    },
    synthetic_media: {
      title: 'Synthetic-Media Forensics Lab',
      subtitle: 'PyTorch ResNet-18 DeepFake detection and Platt logistic calibration'
    },
    evidence: {
      title: 'Evidence & Claim Verification',
      subtitle: 'DeBERTa NLI cross-referencing against NDMA and official emergency records'
    },
    propagation: {
      title: 'Propagation & Diffusion Analytics',
      subtitle: 'Spark Structured Streaming tumbling windows and GraphX PageRank analysis'
    },
    allocation: {
      title: 'Emergency Resource Allocation',
      subtitle: 'OpenStreetMap Dijkstra road routing and HiGHS MILP optimization workspace'
    },
    review: {
      title: 'Dispatcher Review & Immutable Audit',
      subtitle: 'Human-in-the-loop decision-support sign-off and persistent audit logs'
    }
  };

  const pendingReviewCount = allocations.filter(
    (a) => a.allocation_status === 'AWAITING_APPROVAL' || a.verification_status === 'REQUIRES_HUMAN_REVIEW'
  ).length;

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        pendingReviewCount={pendingReviewCount}
      />

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>
        {/* Header */}
        <Header
          title={tabTitles[currentTab].title}
          subtitle={tabTitles[currentTab].subtitle}
          lastRefreshed={lastRefreshed}
          onRefresh={() => fetchData(false)}
          isRefreshing={isRefreshing}
          servicesHealth={servicesHealth}
          backendOnline={backendOnline}
        />

        {/* Scrollable Page Body */}
        <main style={{ flex: 1, overflowY: 'auto', backgroundColor: 'var(--bg-app)' }}>
          {currentTab === 'overview' && (
            <OverviewView
              overview={overview}
              servicesHealth={servicesHealth}
              loading={loading}
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'incidents' && (
            <IncidentsView
              incidents={incidents}
              loading={loading}
              onNavigateToEvidence={() => setCurrentTab('evidence')}
              onNavigateToAllocation={() => setCurrentTab('allocation')}
            />
          )}

          {currentTab === 'synthetic_media' && (
            <SyntheticMediaView onNotify={addToast} />
          )}

          {currentTab === 'evidence' && (
            <EvidenceVerificationView
              assessments={assessments}
              loading={loading}
              onRefresh={() => fetchData(true)}
              onNotify={addToast}
            />
          )}

          {currentTab === 'propagation' && (
            <PropagationView summary={propagationSummary} loading={loading} />
          )}

          {currentTab === 'allocation' && (
            <ResourceAllocationView
              allocations={allocations}
              resources={resources}
              loading={loading}
              onRefresh={() => fetchData(true)}
              onNotify={addToast}
              onNavigateToReview={() => setCurrentTab('review')}
            />
          )}

          {currentTab === 'review' && (
            <HumanReviewView
              allocations={allocations}
              auditLogs={auditLogs}
              loading={loading}
              onRefresh={() => fetchData(true)}
              onNotify={addToast}
            />
          )}
        </main>
      </div>

      {/* Global Notifications */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
};

export default App;
