import { useState, useEffect, useRef, useCallback } from 'react';
import { listDocuments, uploadDocument, deleteDocument, getIngestProgress } from '../lib/api';
import type { DocumentInfo } from '../lib/types';
import '../styles/Pages.css';

interface KnowledgeBaseProps {
  onBack: () => void;
}

const CATEGORIES = [
  { value: 'statute', label: 'Statute / Act' },
  { value: 'supreme_court', label: 'Supreme Court Judgment' },
  { value: 'high_court', label: 'High Court Judgment' },
  { value: 'rules', label: 'Rules & Regulations' },
  { value: 'notification', label: 'Notification / Circular' },
  { value: 'law_commission', label: 'Law Commission Report' },
  { value: 'other', label: 'Other' },
];

export default function KnowledgeBase({ onBack }: KnowledgeBaseProps) {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [totalChunks, setTotalChunks] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ status: string; progress: number; message: string } | null>(null);
  const [category, setCategory] = useState('statute');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadDocs = useCallback(async () => {
    try {
      const data = await listDocuments();
      setDocuments(data.documents);
      setTotalChunks(data.total_chunks);
    } catch {}
  }, []);

  useEffect(() => { loadDocs(); }, [loadDocs]);

  const handleFiles = async (files: FileList) => {
    setUploading(true);
    for (const file of Array.from(files)) {
      try {
        setUploadProgress({ status: 'uploading', progress: 0.05, message: `Uploading ${file.name}...` });
        const result = await uploadDocument(file, category);

        if (result.job_id) {
          // Poll progress
          const pollInterval = setInterval(async () => {
            try {
              const progress = await getIngestProgress(result.job_id);
              setUploadProgress(progress);
              if (progress.status === 'ready' || progress.status === 'error' || progress.status === 'skipped') {
                clearInterval(pollInterval);
                await loadDocs();
                setTimeout(() => setUploadProgress(null), 2000);
              }
            } catch {
              clearInterval(pollInterval);
            }
          }, 1000);
        }
      } catch (err: any) {
        setUploadProgress({ status: 'error', progress: 0, message: err.message });
        setTimeout(() => setUploadProgress(null), 3000);
      }
    }
    setUploading(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      await deleteDocument(docId);
      await loadDocs();
    } catch {}
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="kb-page">
      <div className="kb-header">
        <h1 className="kb-title">📚 Knowledge Base</h1>
        <button className="btn btn-secondary kb-back-btn" onClick={onBack}>← Back to Chat</button>
      </div>

      {/* Stats */}
      <div className="doc-stats">
        <div className="doc-stat">
          <div className="doc-stat-value">{documents.length}</div>
          <div className="doc-stat-label">Documents</div>
        </div>
        <div className="doc-stat">
          <div className="doc-stat-value">{totalChunks}</div>
          <div className="doc-stat-label">Indexed Chunks</div>
        </div>
      </div>

      {/* Upload */}
      <div className="upload-section">
        <div
          className={`drop-zone ${dragActive ? 'active' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="drop-zone-icon">📄</div>
          <div className="drop-zone-text">
            Drag & drop legal documents here, or click to browse
          </div>
          <div className="drop-zone-hint">
            Supports PDF, DOCX, TXT, HTML · Max 50MB per file
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.html,.htm"
          style={{ display: 'none' }}
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
        />

        <div className="upload-form">
          <div className="input-group">
            <label>Document Category</label>
            <select className="select" value={category} onChange={(e) => setCategory(e.target.value)}>
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>
        </div>

        {uploadProgress && (
          <div className="upload-progress">
            <div className="progress-bar">
              <div className="progress-bar-fill" style={{ width: `${uploadProgress.progress * 100}%` }} />
            </div>
            <div className="upload-progress-text">
              {uploadProgress.status === 'error' ? '❌' : uploadProgress.status === 'ready' ? '✓' : '⏳'} {uploadProgress.message}
            </div>
          </div>
        )}
      </div>

      {/* Document table */}
      {documents.length > 0 && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Document</th>
                <th>Category</th>
                <th>Act/Source</th>
                <th>Year</th>
                <th>Chunks</th>
                <th>Status</th>
                <th>Size</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id}>
                  <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {doc.filename}
                  </td>
                  <td>
                    <span className="badge badge-neutral">{doc.category}</span>
                  </td>
                  <td>{doc.act_name || '—'}</td>
                  <td>{doc.year || '—'}</td>
                  <td>{doc.chunk_count}</td>
                  <td>
                    <span className={`badge ${doc.status === 'ready' ? 'badge-success' : doc.status === 'error' ? 'badge-error' : 'badge-warning'}`}>
                      {doc.status}
                    </span>
                  </td>
                  <td>{formatSize(doc.file_size)}</td>
                  <td>
                    <div className="doc-actions">
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(doc.id)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {documents.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-tertiary)' }}>
          No documents uploaded yet. Upload legal documents above to get started.
        </div>
      )}
    </div>
  );
}
