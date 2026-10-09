import React from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
}

interface ToastProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '1.5rem',
        right: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
        zIndex: 1000,
        maxWidth: '420px',
        width: '100%'
      }}
    >
      {toasts.map((toast) => {
        let borderColor = 'var(--accent-primary)';
        let Icon = Info;
        let iconColor = 'var(--accent-primary)';

        if (toast.type === 'success') {
          borderColor = 'var(--status-success)';
          Icon = CheckCircle2;
          iconColor = 'var(--status-success)';
        } else if (toast.type === 'warning') {
          borderColor = 'var(--status-warning)';
          Icon = AlertTriangle;
          iconColor = 'var(--status-warning)';
        } else if (toast.type === 'error') {
          borderColor = 'var(--status-danger)';
          Icon = AlertCircle;
          iconColor = 'var(--status-danger)';
        }

        return (
          <div
            key={toast.id}
            style={{
              backgroundColor: 'var(--bg-card)',
              borderLeft: `4px solid ${borderColor}`,
              borderTop: '1px solid var(--border-default)',
              borderRight: '1px solid var(--border-default)',
              borderBottom: '1px solid var(--border-default)',
              borderRadius: 'var(--radius-md)',
              padding: '0.875rem 1rem',
              boxShadow: 'var(--shadow-lg)',
              display: 'flex',
              gap: '0.75rem',
              alignItems: 'flex-start'
            }}
          >
            <Icon size={18} color={iconColor} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                {toast.title}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                {toast.message}
              </div>
            </div>
            <button
              onClick={() => onDismiss(toast.id)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '2px'
              }}
            >
              <X size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
};
