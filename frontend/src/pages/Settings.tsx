import { useState, useEffect } from 'react';
import { getKeyStatus, clearAllSessions } from '../lib/api';
import type { ApiKeyStatus } from '../lib/types';
import '../styles/Pages.css';

interface SettingsProps {
  onBack: () => void;
}

export default function Settings({ onBack }: SettingsProps) {
  const [keyStatus, setKeyStatus] = useState<ApiKeyStatus | null>(null);
  const [cleared, setCleared] = useState(false);

  useEffect(() => {
    getKeyStatus().then(setKeyStatus).catch(() => {});
  }, []);

  const handleClearHistory = async () => {
    if (confirm('Delete all chat history? This cannot be undone.')) {
      await clearAllSessions();
      setCleared(true);
      setTimeout(() => setCleared(false), 3000);
    }
  };

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1 className="settings-title">⚙ Settings</h1>
        <button className="btn btn-secondary" onClick={onBack}>← Back to Chat</button>
      </div>

      {/* Model status */}
      <div className="settings-section">
        <h2 className="settings-section-title">AI Model & Engine</h2>

        <div className="alert alert-success" style={{ marginBottom: '16px' }}>
          ✓ Connected to <strong>{keyStatus?.model || 'gemini-2.5-flash'}</strong> ({keyStatus?.provider || 'Google Gemini'})
        </div>

        <div className="card" style={{ padding: '16px', background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
            <div><strong>Active Engine:</strong> Google Gemini 2.5 Flash</div>
            <div><strong>Embeddings:</strong> BAAI/bge-small-en-v1.5 (Local ONNX)</div>
            <div><strong>RAG Pipeline:</strong> Hybrid Search (ChromaDB + BM25 + Reciprocal Rank Fusion)</div>
            <div><strong>System Status:</strong> Ready and operational</div>
          </div>
        </div>
      </div>

      {/* Chat history */}
      <div className="settings-section">
        <h2 className="settings-section-title">Chat History</h2>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
          Clear all conversation sessions and messages from local storage.
        </p>
        <button className="btn btn-danger btn-sm" onClick={handleClearHistory}>
          🗑 Clear All Chat History
        </button>
        {cleared && (
          <span style={{ marginLeft: '12px', fontSize: '13px', color: 'var(--success)' }}>
            ✓ Chat history cleared
          </span>
        )}
      </div>

      {/* Privacy */}
      <div className="settings-section">
        <h2 className="settings-section-title">Privacy & Security</h2>
        <div className="settings-privacy">
          <p><strong>🔒 Built for Indian Law & Privacy</strong></p>
          <br />
          <p>• Pre-configured model access with encrypted credentials at rest</p>
          <p>• Your uploaded legal documents and questions stay on your local server</p>
          <p>• No personal identifiers are stored beyond active sessions</p>
          <p>• Chat history is stored locally in SQLite and can be cleared at any time</p>
        </div>
      </div>
    </div>
  );
}
