import React, { useState } from 'react';
import {
  Upload,
  ScanEye,
  FileCheck2,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Sparkles,
  Info,
  ShieldCheck,
  FileWarning
} from 'lucide-react';
import { api, MediaAnalysisResult } from '../api/client';

interface SyntheticMediaViewProps {
  onNotify: (type: 'success' | 'warning' | 'error' | 'info', title: string, message: string) => void;
}

export const SyntheticMediaView: React.FC<SyntheticMediaViewProps> = ({ onNotify }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [mediaType, setMediaType] = useState<'IMAGE' | 'VIDEO'>('IMAGE');
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<MediaAnalysisResult | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (max 25MB)
      if (file.size > 25 * 1024 * 1024) {
        onNotify('error', 'File Too Large', 'File size exceeds 25MB limit.');
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);

      // Auto detect type
      if (file.type.startsWith('video/')) {
        setMediaType('VIDEO');
      } else {
        setMediaType('IMAGE');
      }
    }
  };

  const handleRunInference = async () => {
    if (!selectedFile) return;
    setAnalyzing(true);
    try {
      const res = await api.analyzeMedia(selectedFile, mediaType);
      setResult(res);
      onNotify('success', 'Forensic Analysis Complete', `Inference finished in ${res.inference_latency_ms}ms`);
    } catch (err: any) {
      onNotify('error', 'Inference Failed', err.message || 'Error executing forensics model.');
    } finally {
      setAnalyzing(false);
    }
  };

  // Demo presets
  const handleLoadPreset = (name: string, url: string, type: 'IMAGE' | 'VIDEO') => {
    fetch(url)
      .then((res) => res.blob())
      .then((blob) => {
        const file = new File([blob], name, { type: type === 'IMAGE' ? 'image/jpeg' : 'video/mp4' });
        setSelectedFile(file);
        setPreviewUrl(url);
        setMediaType(type);
        setResult(null);
        onNotify('info', 'Preset Loaded', `Loaded sample fixture: ${name}`);
      })
      .catch(() => {
        onNotify('warning', 'Preset Notice', 'Select an image or video file directly from your local system.');
      });
  };

  return (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Scientific Limitation & Scope Banner */}
      <div
        className="card"
        style={{
          backgroundColor: 'rgba(15, 23, 42, 0.8)',
          borderLeft: '4px solid var(--status-warning)',
          display: 'flex',
          gap: '1rem',
          alignItems: 'flex-start'
        }}
      >
        <AlertTriangle size={20} color="var(--status-warning)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
            Scientific Limitation & Interpretability Protocol
          </div>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
            A synthetic-media score measures <strong>forensic visual artifacts</strong> (e.g. GAN generation, diffusion noise, facial warping).
            It does <strong>NOT</strong> prove that the accompanying humanitarian claim is false. Real crisis incidents frequently contain AI-enhanced or stock images,
            and true crisis events cannot be dismissed purely on media scores.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem' }}>
        {/* Upload & Model Controls */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <ScanEye size={16} /> Multi-Modal Forensic Lab
              </div>
              <div className="card-subtitle">
                PyTorch ResNet-18 DeepFake & Diffusion Forensic Engine
              </div>
            </div>
            <span className="badge badge-info">ResNet-18 PyTorch</span>
          </div>

          {/* Drag & Drop Area */}
          <div
            style={{
              border: '2px dashed var(--border-default)',
              borderRadius: 'var(--radius-lg)',
              padding: '2rem 1.5rem',
              textAlign: 'center',
              backgroundColor: 'var(--bg-elevated)',
              cursor: 'pointer',
              marginBottom: '1rem',
              position: 'relative'
            }}
          >
            <input
              type="file"
              accept="image/*,video/mp4"
              onChange={handleFileChange}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                opacity: 0,
                cursor: 'pointer'
              }}
            />
            <Upload size={36} color="var(--accent-primary)" style={{ margin: '0 auto 0.75rem' }} />
            <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
              {selectedFile ? selectedFile.name : 'Click or drag media here to analyze'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Supports JPEG, PNG, GIF, MP4 (Max 25MB)
            </div>
          </div>

          {/* Preset Buttons for Demo */}
          <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
              Sample Demonstration Fixtures:
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <button
                type="button"
                onClick={() => handleLoadPreset('flood_delhi_bridge.jpg', '/data/demo/input/flood_sample.jpg', 'IMAGE')}
                className="btn btn-outline btn-sm"
              >
                Flood Breach Photo
              </button>
              <button
                type="button"
                onClick={() => handleLoadPreset('synthetic_explosion.jpg', '/data/demo/input/synth_explosion.jpg', 'IMAGE')}
                className="btn btn-outline btn-sm"
              >
                Diffusion Gas Explosion
              </button>
            </div>
          </div>

          {/* Media Type & Action Controls */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <label style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>Modality:</label>
              <select
                value={mediaType}
                onChange={(e) => setMediaType(e.target.value as any)}
                className="input-control"
                style={{ width: 'auto' }}
              >
                <option value="IMAGE">Image (Platt Calibrated)</option>
                <option value="VIDEO">Video (Temporal Forensics - Uncalibrated)</option>
              </select>
            </div>

            <button
              onClick={handleRunInference}
              disabled={!selectedFile || analyzing}
              className="btn btn-primary"
            >
              <Sparkles size={14} className={analyzing ? 'animate-spin' : ''} />
              {analyzing ? 'Running ResNet-18...' : 'Run Forensic Inference'}
            </button>
          </div>
        </div>

        {/* Inference Results Panel */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Forensic Assessment Results</div>
              <div className="card-subtitle">Live output from active PyTorch model weights</div>
            </div>
          </div>

          {analyzing ? (
            <div style={{ padding: '3rem 1.5rem', textAlign: 'center' }}>
              <div className="skeleton" style={{ height: '60px', width: '60px', borderRadius: '50%', margin: '0 auto 1rem' }} />
              <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Executing ResNet-18 Forward Pass...</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Applying Platt Logistic Calibrator & artifact detection
              </div>
            </div>
          ) : result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {/* Score Display */}
              <div
                style={{
                  padding: '1.25rem',
                  backgroundColor: 'var(--bg-elevated)',
                  borderRadius: 'var(--radius-lg)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Synthetic Media Risk
                  </div>
                  <div
                    style={{
                      fontSize: '2rem',
                      fontWeight: 700,
                      color:
                        (result.synthetic_media_risk ?? 0) > 0.6
                          ? 'var(--status-danger)'
                          : (result.synthetic_media_risk ?? 0) > 0.3
                          ? 'var(--status-warning)'
                          : 'var(--status-success)'
                    }}
                  >
                    {result.synthetic_media_risk !== null
                      ? `${(result.synthetic_media_risk * 100).toFixed(1)}%`
                      : 'N/A'}
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span
                    className={`badge ${
                      result.calibration_status === 'CALIBRATED_PLATT'
                        ? 'badge-success'
                        : 'badge-warning'
                    }`}
                  >
                    {result.calibration_status}
                  </span>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Inference: {result.inference_latency_ms}ms
                  </div>
                </div>
              </div>

              {/* Technical Details */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8125rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Target Media:</span>
                  <span style={{ fontWeight: 500, fontFamily: 'var(--font-mono)' }}>{result.filename}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Model Architecture:</span>
                  <span style={{ fontWeight: 500 }}>ResNet-18 (PyTorch 2.14)</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Calibration Method:</span>
                  <span style={{ fontWeight: 500 }}>{result.calibration_status === 'CALIBRATED_PLATT' ? 'Platt Logistic Regression' : 'None (Uncalibrated Video)'}</span>
                </div>
              </div>

              {/* Forensic Explanation */}
              <div
                style={{
                  padding: '0.875rem',
                  backgroundColor: 'var(--bg-app)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-default)',
                  fontSize: '0.8125rem',
                  color: 'var(--text-primary)'
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Info size={14} color="var(--accent-primary)" />
                  Explanation & Recommendation:
                </div>
                {result.explanation}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <ScanEye className="empty-state-icon" />
              <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Awaiting Media Submission</div>
              <div style={{ fontSize: '0.8125rem', marginTop: '4px' }}>
                Upload an image or video to inspect synthetic manipulation probability.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
