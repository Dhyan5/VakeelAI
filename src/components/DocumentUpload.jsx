/**
 * DocumentUpload - Drag-and-drop or click-to-browse document upload zone
 * Shows file preview, size info, and triggers AI analysis animation
 * Displays a scan animation and step-by-step processing progress
 */
import React, { useState, useRef, useCallback } from 'react';
import {
  Upload, File, X, CheckCircle2, AlertTriangle, FileText, Loader2
} from 'lucide-react';
import { UI_TEXT, MOCK_RESPONSES } from '../data/content';
import { LANGUAGES } from '../data/content';

// Format bytes to human readable
function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentUpload({ lang, onAnalysisComplete }) {
  const t = UI_TEXT[lang];
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);
  const stepIntervalRef = useRef(null);

  const ACCEPTED_TYPES = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

  const validateAndSetFile = useCallback((f) => {
    setError('');
    setDone(false);
    if (!f) return;

    const isValidType = ACCEPTED_TYPES.includes(f.type) || f.name.match(/\.(pdf|doc|docx)$/i);
    if (!isValidType) {
      setError('Please upload a PDF, DOC, or DOCX file.');
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File size must be under 10MB.');
      return;
    }
    setFile(f);
  }, []);

  // Drag events
  const onDragOver = (e) => { e.preventDefault(); setDragOver(true); };
  const onDragLeave = () => setDragOver(false);
  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    validateAndSetFile(e.dataTransfer.files[0]);
  };
  const onFileChange = (e) => validateAndSetFile(e.target.files[0]);

  const clearFile = () => {
    setFile(null);
    setDone(false);
    setError('');
    setStepIndex(0);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Simulate AI document analysis
  const handleAnalyze = () => {
    if (!file || analyzing) return;
    setAnalyzing(true);
    setStepIndex(0);
    setDone(false);

    const steps = t.processingSteps;
    let idx = 0;

    stepIntervalRef.current = setInterval(() => {
      idx++;
      setStepIndex(idx);
      if (idx >= steps.length) {
        clearInterval(stepIntervalRef.current);
        setTimeout(() => {
          setAnalyzing(false);
          setDone(true);
          // Send document analysis result to chat
          if (onAnalysisComplete) {
            onAnalysisComplete(MOCK_RESPONSES[lang].documentAnalysis, file.name);
          }
        }, 600);
      }
    }, 900);
  };

  const fileTypeIcon = file?.name.endsWith('.pdf') ? '📄' : '📝';

  return (
    <div style={{ padding: '8px 0' }}>
      {/* Upload Zone */}
      {!file ? (
        <div
          className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{ padding: 40, textAlign: 'center' }}
          role="button"
          tabIndex={0}
          aria-label="Upload legal document"
          onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
        >
          {/* Upload Icon with glow */}
          <div
            className="flex-center mx-auto mb-4"
            style={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              background: 'rgba(59,130,246,0.1)',
              border: '1px solid rgba(59,130,246,0.25)',
              boxShadow: dragOver ? '0 0 30px rgba(59,130,246,0.3)' : 'none',
              transition: 'all 0.3s ease',
            }}
          >
            <Upload size={26} color={dragOver ? '#3b82f6' : 'rgba(99,179,237,0.6)'} />
          </div>

          <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--clr-text-primary)', marginBottom: 8 }}>
            {t.uploadTitle}
          </h3>
          <p style={{ fontSize: 13, color: 'var(--clr-text-muted)', marginBottom: 12, lineHeight: 1.5 }}>
            {t.uploadSubtitle}
          </p>
          <span
            style={{
              display: 'inline-block',
              fontSize: 11,
              padding: '4px 12px',
              borderRadius: 50,
              background: 'rgba(59,130,246,0.08)',
              border: '1px solid rgba(59,130,246,0.15)',
              color: 'var(--clr-text-muted)',
            }}
          >
            {t.uploadFormats}
          </span>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={onFileChange}
            style={{ display: 'none' }}
            aria-label="Choose file"
          />
        </div>
      ) : (
        /* File Preview Card */
        <div
          className="glass-card"
          style={{ padding: 20, position: 'relative' }}
        >
          {/* Remove button */}
          <button
            className="btn-glass btn-icon"
            onClick={clearFile}
            style={{ position: 'absolute', top: 12, right: 12 }}
            title="Remove file"
          >
            <X size={14} />
          </button>

          {/* File Info */}
          <div className="flex items-center gap-4" style={{ marginBottom: analyzing || done ? 20 : 0 }}>
            <div
              className="flex-center flex-shrink-0 rounded-xl"
              style={{
                width: 52,
                height: 52,
                background: 'linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.15))',
                border: '1px solid rgba(99,179,237,0.2)',
                fontSize: 24,
              }}
            >
              {fileTypeIcon}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p className="truncate" style={{ fontWeight: 600, fontSize: 14, color: 'var(--clr-text-primary)', marginBottom: 4 }}>
                {file.name}
              </p>
              <p style={{ fontSize: 12, color: 'var(--clr-text-muted)' }}>
                {formatBytes(file.size)} · {file.type.includes('pdf') ? 'PDF' : 'Word Document'}
              </p>
            </div>
          </div>

          {/* Analysis Progress */}
          {analyzing && (
            <div className="animate-fade-in" style={{ marginTop: 4 }}>
              {/* Scan animation bar */}
              <div
                style={{
                  position: 'relative',
                  height: 60,
                  borderRadius: 8,
                  background: 'rgba(59,130,246,0.05)',
                  border: '1px solid rgba(59,130,246,0.1)',
                  overflow: 'hidden',
                  marginBottom: 16,
                }}
              >
                <div className="scan-line" />
                <div className="flex-center h-full gap-2">
                  <Loader2 size={16} color="var(--clr-accent-cyan)" style={{ animation: 'spin-ring 1s linear infinite' }} />
                  <span style={{ fontSize: 13, color: 'var(--clr-accent-cyan)', fontWeight: 500 }}>
                    {t.analyzing}
                  </span>
                </div>
              </div>

              {/* Step Progress */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {t.processingSteps.map((step, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3"
                    style={{
                      opacity: i <= stepIndex ? 1 : 0.3,
                      transition: 'opacity 0.4s ease',
                    }}
                  >
                    <div
                      style={{
                        width: 18,
                        height: 18,
                        borderRadius: '50%',
                        background: i < stepIndex
                          ? 'rgba(34,197,94,0.2)'
                          : i === stepIndex
                          ? 'rgba(59,130,246,0.2)'
                          : 'rgba(255,255,255,0.05)',
                        border: `1px solid ${i < stepIndex ? 'rgba(34,197,94,0.5)' : i === stepIndex ? 'rgba(59,130,246,0.4)' : 'rgba(255,255,255,0.1)'}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        transition: 'all 0.4s ease',
                      }}
                    >
                      {i < stepIndex ? (
                        <CheckCircle2 size={10} color="#22c55e" />
                      ) : i === stepIndex ? (
                        <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#3b82f6', animation: 'pulse-glow 1s infinite' }} />
                      ) : null}
                    </div>
                    <span style={{ fontSize: 12, color: i <= stepIndex ? 'var(--clr-text-secondary)' : 'var(--clr-text-muted)' }}>
                      {step}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Done State */}
          {done && (
            <div
              className="flex items-center gap-3 animate-fade-in"
              style={{
                marginTop: 16,
                padding: '10px 14px',
                borderRadius: 10,
                background: 'rgba(34,197,94,0.08)',
                border: '1px solid rgba(34,197,94,0.25)',
              }}
            >
              <CheckCircle2 size={16} color="#22c55e" />
              <span style={{ fontSize: 13, color: '#22c55e', fontWeight: 500 }}>
                {t.analysisComplete} — Results sent to chat
              </span>
            </div>
          )}

          {/* Analyze Button */}
          {!analyzing && !done && (
            <button
              className="btn-glass btn-glass-primary"
              onClick={handleAnalyze}
              style={{ marginTop: 16, width: '100%', justifyContent: 'center', padding: '12px' }}
            >
              <FileText size={16} />
              <span style={{ fontWeight: 600 }}>{t.analyzeBtn}</span>
            </button>
          )}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div
          className="flex items-center gap-2 animate-fade-in"
          style={{
            marginTop: 12,
            padding: '10px 14px',
            borderRadius: 10,
            background: 'rgba(239,68,68,0.08)',
            border: '1px solid rgba(239,68,68,0.25)',
          }}
        >
          <AlertTriangle size={14} color="#ef4444" />
          <span style={{ fontSize: 12, color: '#ef4444' }}>{error}</span>
        </div>
      )}
    </div>
  );
}
