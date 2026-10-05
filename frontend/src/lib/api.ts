/* Nyaya – API client */

const API_BASE = 'http://localhost:8000';

async function fetchJSON(url: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Keys ────────────────────────────────────────────────────────────────

export async function getKeyStatus() {
  return fetchJSON('/api/keys/status');
}

export async function getModels() {
  return fetchJSON('/api/keys/models');
}

export async function testKey(provider: string, model: string, api_key: string) {
  return fetchJSON('/api/keys/test', {
    method: 'POST',
    body: JSON.stringify({ provider, model, api_key }),
  });
}

export async function saveKey(provider: string, model: string, api_key: string) {
  return fetchJSON('/api/keys', {
    method: 'POST',
    body: JSON.stringify({ provider, model, api_key }),
  });
}

export async function deleteKey() {
  return fetchJSON('/api/keys', { method: 'DELETE' });
}

// ── Documents ─────────────────────────────────────────────────────────

export async function listDocuments() {
  return fetchJSON('/api/documents');
}

export async function uploadDocument(file: File, category: string, actName?: string, year?: number) {
  const form = new FormData();
  form.append('file', file);
  form.append('category', category);
  if (actName) form.append('act_name', actName);
  if (year) form.append('year', String(year));

  const res = await fetch(`${API_BASE}/api/documents`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function deleteDocument(docId: string) {
  return fetchJSON(`/api/documents/${docId}`, { method: 'DELETE' });
}

export async function getIngestProgress(jobId: string) {
  return fetchJSON(`/api/documents/progress/${jobId}`);
}

export async function getDocumentStats() {
  return fetchJSON('/api/documents/stats');
}

// ── Chat ──────────────────────────────────────────────────────────────

export function streamChat(
  query: string,
  sessionId: string | null,
  language: string,
  onMeta: (data: any) => void,
  onToken: (token: string) => void,
  onDone: (data: any) => void,
  onError: (error: string) => void,
) {
  const controller = new AbortController();

  fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, session_id: sessionId, language, stream: true }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        onError(err.detail || `HTTP ${res.status}`);
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) { onError('No stream reader'); return; }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            const eventType = line.slice(7).trim();
            // Next line should be data
            continue;
          }
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            try {
              const data = JSON.parse(dataStr);
              // Determine event type from the data structure
              if (data.classification !== undefined) onMeta(data);
              else if (data.token !== undefined) onToken(data.token);
              else if (data.session_id !== undefined && data.message_id !== undefined && !data.token) onDone(data);
              else if (data.error) onError(data.error);
            } catch {}
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onError(err.message || 'Connection failed');
      }
    });

  return controller;
}

// ── Sessions ──────────────────────────────────────────────────────────

export async function listSessions() {
  return fetchJSON('/api/sessions');
}

export async function getSessionMessages(sessionId: string) {
  return fetchJSON(`/api/sessions/${sessionId}/messages`);
}

export async function deleteSession(sessionId: string) {
  return fetchJSON(`/api/sessions/${sessionId}`, { method: 'DELETE' });
}

export async function clearAllSessions() {
  return fetchJSON('/api/sessions', { method: 'DELETE' });
}

// ── Sources ───────────────────────────────────────────────────────────

export async function getSource(chunkId: string) {
  return fetchJSON(`/api/sources/${chunkId}`);
}

// ── Feedback ──────────────────────────────────────────────────────────

export async function submitFeedback(messageId: string, feedback: string) {
  return fetchJSON('/api/feedback', {
    method: 'POST',
    body: JSON.stringify({ message_id: messageId, feedback }),
  });
}

// ── Health ────────────────────────────────────────────────────────────

export async function checkHealth() {
  return fetchJSON('/api/health');
}
