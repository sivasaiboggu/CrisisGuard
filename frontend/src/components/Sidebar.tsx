import React from 'react';
import {
  ShieldAlert,
  LayoutDashboard,
  AlertTriangle,
  ScanEye,
  FileCheck2,
  Share2,
  Truck,
  UserCheck2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

export type NavTab = 
  | 'overview'
  | 'incidents'
  | 'synthetic_media'
  | 'evidence'
  | 'propagation'
  | 'allocation'
  | 'review';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  pendingReviewCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  collapsed,
  onToggleCollapse,
  pendingReviewCount = 0
}) => {
  const navItems = [
    { id: 'overview' as NavTab, label: 'Executive Overview', icon: LayoutDashboard },
    { id: 'incidents' as NavTab, label: 'Crisis Incidents', icon: AlertTriangle },
    { id: 'synthetic_media' as NavTab, label: 'Synthetic-Media Lab', icon: ScanEye },
    { id: 'evidence' as NavTab, label: 'Evidence Verification', icon: FileCheck2 },
    { id: 'propagation' as NavTab, label: 'Propagation Analytics', icon: Share2 },
    { id: 'allocation' as NavTab, label: 'Resource Allocation', icon: Truck },
    {
      id: 'review' as NavTab,
      label: 'Human Review & Audit',
      icon: UserCheck2,
      badge: pendingReviewCount > 0 ? pendingReviewCount : undefined
    }
  ];

  return (
    <aside
      style={{
        width: collapsed ? '68px' : '260px',
        backgroundColor: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.2s ease',
        flexShrink: 0,
        zIndex: 50
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          padding: '1.25rem 1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          borderBottom: '1px solid var(--border-subtle)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', overflow: 'hidden' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              backgroundColor: 'rgba(59, 130, 246, 0.15)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-primary)',
              flexShrink: 0
            }}
          >
            <ShieldAlert size={20} />
          </div>
          {!collapsed && (
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#FFFFFF', letterSpacing: '-0.01em' }}>
                CrisisGuard
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                Decision Support Platform
              </div>
            </div>
          )}
        </div>

        <button
          onClick={onToggleCollapse}
          className="btn-outline"
          style={{
            padding: '4px',
            borderRadius: '4px',
            border: 'none',
            display: collapsed ? 'none' : 'flex'
          }}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <ChevronLeft size={16} />
        </button>
      </div>

      {/* Navigation Links */}
      <nav style={{ padding: '0.75rem 0.5rem', flex: 1, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                width: '100%',
                padding: collapsed ? '0.75rem 0' : '0.625rem 0.875rem',
                justifyContent: collapsed ? 'center' : 'flex-start',
                borderRadius: 'var(--radius-md)',
                backgroundColor: isActive ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                color: isActive ? '#FFFFFF' : 'var(--text-secondary)',
                border: isActive ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid transparent',
                cursor: 'pointer',
                fontSize: '0.8125rem',
                fontWeight: isActive ? 600 : 500,
                textAlign: 'left',
                transition: 'all 0.15s ease'
              }}
              title={collapsed ? item.label : undefined}
            >
              <Icon size={18} color={isActive ? '#3B82F6' : '#94A3B8'} style={{ flexShrink: 0 }} />
              {!collapsed && (
                <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {item.label}
                </span>
              )}
              {!collapsed && item.badge && (
                <span
                  style={{
                    backgroundColor: 'var(--status-warning)',
                    color: '#000000',
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    padding: '2px 6px',
                    borderRadius: '999px',
                    lineHeight: 1
                  }}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom Collapsed Toggle Button */}
      {collapsed && (
        <div style={{ padding: '0.75rem', display: 'flex', justifyContent: 'center', borderTop: '1px solid var(--border-subtle)' }}>
          <button
            onClick={onToggleCollapse}
            className="btn-outline"
            style={{ padding: '6px', borderRadius: '4px', border: 'none' }}
            title="Expand sidebar"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      )}

      {/* Footer info */}
      {!collapsed && (
        <div
          style={{
            padding: '1rem',
            borderTop: '1px solid var(--border-subtle)',
            fontSize: '0.6875rem',
            color: 'var(--text-muted)'
          }}
        >
          <div style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>CSE412 — Big Data Project</div>
          <div>B.SIVASAI (2023BCS0228)</div>
          <div style={{ marginTop: '4px', color: '#10B981', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#10B981' }} />
            Decision-Support Active
          </div>
        </div>
      )}
    </aside>
  );
};
