import { useState, useRef, useEffect, useCallback } from 'react';
import {
  streamChat, listSessions, getSessionMessages, deleteSession,
  getSource, submitFeedback, getKeyStatus, getDocumentStats
} from '../lib/api';
import type { ChatMessage, ChatSession, Citation, SourceChunk, ApiKeyStatus, DocumentStats, LawMapping } from '../lib/types';
import '../styles/Chat.css';

interface ChatPageProps {
  onNavigate: (page: 'kb' | 'settings') => void;
}

const SUGGESTIONS = [
  'What is the punishment for cheque bounce under Section 138 NI Act?',
  'How do I file a consumer complaint?',
  'What are my rights upon arrest?',
  'What is anticipatory bail and how to apply?',
  'Difference between IPC Section 302 and BNS Section 103?',
  'How to file a domestic violence complaint?',
];

export default function ChatPage({ onNavigate }: ChatPageProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sourceDrawer, setSourceDrawer] = useState<SourceChunk | null>(null);
  const [keyStatus, setKeyStatus] = useState<ApiKeyStatus | null>(null);
  const [docStats, setDocStats] = useState<DocumentStats>({ total_documents: 0, total_chunks: 0 });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const controllerRef = useRef<AbortController | null>(null);

  // Load sessions and status
  useEffect(() => {
    listSessions().then((d) => setSessions(d.sessions)).catch(() => {});
    getKeyStatus().then(setKeyStatus).catch(() => {});
    getDocumentStats().then(setDocStats).catch(() => {});
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSession = async (sessionId: string) => {
    setCurrentSessionId(sessionId);
    try {
      const data = await getSessionMessages(sessionId);
      setMessages(data.messages);
    } catch { setMessages([]); }
  };

  const newChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
    inputRef.current?.focus();
  };

  const handleSend = useCallback(async (text?: string) => {
    const query = text || input.trim();
    if (!query || streaming) return;

    setInput('');

    // Add user message
    const userMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: query,
    };
    setMessages((prev) => [...prev, userMsg]);

    // Add placeholder assistant message
    const assistantId = `temp-assistant-${Date.now()}`;
    const assistantMsg: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      citations: [],
      mappings: [],
    };
    setMessages((prev) => [...prev, assistantMsg]);
    setStreaming(true);

    let sessionId = currentSessionId;
    let currentMappings: LawMapping[] = [];

    controllerRef.current = streamChat(
      query,
      sessionId,
      'en',
      // onMeta
      (meta) => {
        if (meta.session_id && !sessionId) {
          sessionId = meta.session_id;
          setCurrentSessionId(meta.session_id);
        }
        if (meta.citations) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, citations: meta.citations } : m
            )
          );
        }
        if (meta.mappings) {
          currentMappings = meta.mappings;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, mappings: meta.mappings } : m
            )
          );
        }
        if (meta.message_id) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, id: meta.message_id } : m
            )
          );
        }
      },
      // onToken
      (token) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId || m.content === ''
              ? { ...m, content: (m.role === 'assistant' && (m.id === assistantId || m.content.length < 10000)) ? m.content + token : m.content }
              : m
          )
        );
      },
      // onDone
      (data) => {
        setStreaming(false);
        if (data.message_id) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, id: data.message_id } : m
            )
          );
        }
        listSessions().then((d) => setSessions(d.sessions)).catch(() => {});
      },
      // onError
      (error) => {
        setStreaming(false);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: `⚠️ ${error}` }
              : m
          )
        );
      }
    );
  }, [input, streaming, currentSessionId]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const openSource = async (chunkId: string) => {
    try {
      const source = await getSource(chunkId);
      setSourceDrawer(source);
    } catch { }
  };

  const handleFeedback = async (msgId: string, fb: string) => {
    try {
      await submitFeedback(msgId, fb);
      setMessages((prev) =>
        prev.map((m) => m.id === msgId ? { ...m, feedback: fb } : m)
      );
    } catch {}
  };

  const handleDeleteSession = async (e: React.MouseEvent, sid: string) => {
    e.stopPropagation();
    await deleteSession(sid);
    setSessions((prev) => prev.filter((s) => s.id !== sid));
    if (currentSessionId === sid) newChat();
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const isLanding = messages.length === 0 && !streaming;

  return (
    <div className="chat-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? '' : 'collapsed'}`}>
        <div className="sidebar-header">
          <span className="sidebar-logo">⚖ Nyaya</span>
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(false)}>✕</button>
        </div>

        <button className="new-chat-btn" onClick={newChat}>＋ New Chat</button>

        <div className="sidebar-sessions">
          {sessions.map((s) => (
            <div
              key={s.id}
              className={`session-item ${currentSessionId === s.id ? 'active' : ''}`}
              onClick={() => loadSession(s.id)}
            >
              <span>💬</span>
              <span className="session-item-text">{s.title}</span>
              <button
                className="session-item-delete"
                onClick={(e) => handleDeleteSession(e, s.id)}
              >🗑</button>
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <button className="sidebar-link" onClick={() => onNavigate('kb')}>
            📚 Knowledge Base
            {docStats.total_documents > 0 && (
              <span className="badge badge-neutral" style={{ marginLeft: 'auto' }}>{docStats.total_documents}</span>
            )}
          </button>
          <button className="sidebar-link" onClick={() => onNavigate('settings')}>
            ⚙ Settings
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="chat-main">
        <div className="chat-header">
          <div className="chat-header-left">
            {!sidebarOpen && (
              <button className="sidebar-toggle" onClick={() => setSidebarOpen(true)}>☰</button>
            )}
            <button className="mobile-menu-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>☰</button>
          </div>
          <div className="chat-header-right">
            <div className="status-pill">
              <span className="dot" />
              {keyStatus?.model || "Gemini 2.5 Flash"} · {docStats.total_chunks} legal sources
            </div>
          </div>
        </div>

        <div className="chat-messages">
          <div className="chat-messages-inner">
            {isLanding ? (
              <div className="chat-landing">
                <div className="chat-landing-logo">⚖ Nyaya</div>
                <div className="chat-landing-tagline">Ask any question about Indian law</div>

                {docStats.total_documents === 0 && (
                  <div className="empty-kb-banner">
                    ⚠ No documents uploaded yet. Answers require a knowledge base.
                    <button className="btn btn-sm btn-secondary" onClick={() => onNavigate('kb')}>Upload Documents</button>
                  </div>
                )}

                <div className="suggestion-chips">
                  {SUGGESTIONS.map((s) => (
                    <button key={s} className="suggestion-chip" onClick={() => handleSend(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg) => (
                  <div key={msg.id} className={`message message-${msg.role}`}>
                    {msg.role === 'user' ? (
                      <div className="message-user-bubble">{msg.content}</div>
                    ) : (
                      <div className="message-assistant">
                        <div className="message-avatar">N</div>
                        <div className="message-content">
                          {msg.content ? (
                            <div className="message-body markdown-content">
                              {msg.content.split('\n').map((line, i) => {
                                if (line.startsWith('## ') || line.startsWith('**') && line.endsWith('**')) {
                                  return <h3 key={i}>{line.replace(/^##\s*/, '').replace(/\*\*/g, '')}</h3>;
                                }
                                if (line.startsWith('- ') || line.startsWith('* ')) {
                                  return <p key={i} style={{ paddingLeft: '16px' }}>• {line.slice(2)}</p>;
                                }
                                if (line.startsWith('> ')) {
                                  return <blockquote key={i}>{line.slice(2)}</blockquote>;
                                }
                                if (line.trim() === '') return <br key={i} />;
                                return <p key={i} dangerouslySetInnerHTML={{
                                  __html: line
                                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                                    .replace(/\*(.+?)\*/g, '<em>$1</em>')
                                }} />;
                              })}
                            </div>
                          ) : (
                            <div className="typing-indicator">
                              <span /><span /><span />
                            </div>
                          )}

                          {/* Mappings */}
                          {msg.mappings && msg.mappings.length > 0 && (
                            <div style={{ marginTop: '8px' }}>
                              {msg.mappings.map((m, i) => (
                                <span key={i} className="mapping-badge">
                                  {m.old_law} §{m.old_section} → {m.new_law} §{m.new_section}
                                </span>
                              ))}
                            </div>
                          )}


                          {/* Actions */}
                          {msg.content && !msg.content.startsWith('⚠') && (
                            <div className="message-actions">
                              <button
                                className="message-action-btn"
                                onClick={() => copyMessage(msg.content)}
                                title="Copy"
                              >📋</button>
                              <button
                                className={`message-action-btn ${msg.feedback === 'up' ? 'active' : ''}`}
                                onClick={() => handleFeedback(msg.id, 'up')}
                                title="Helpful"
                              >👍</button>
                              <button
                                className={`message-action-btn ${msg.feedback === 'down' ? 'active' : ''}`}
                                onClick={() => handleFeedback(msg.id, 'down')}
                                title="Not helpful"
                              >👎</button>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </div>

        {/* Input */}
        <div className="chat-input-area">
          <div className="chat-input-wrapper">
            <textarea
              ref={inputRef}
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a legal question..."
              rows={1}
              disabled={streaming}
            />
            <button
              className="chat-send-btn"
              onClick={() => handleSend()}
              disabled={!input.trim() || streaming}
            >
              ↑
            </button>
          </div>
          <div className="disclaimer">
            ⚖️ General legal information, not legal advice. Consult a qualified advocate for your specific situation.
          </div>
        </div>
      </main>

      {/* Source drawer */}
      {sourceDrawer && (
        <>
          <div className="source-drawer-overlay" onClick={() => setSourceDrawer(null)} />
          <div className="source-drawer">
            <div className="source-drawer-header">
              <span className="source-drawer-title">Source Document</span>
              <button className="source-drawer-close" onClick={() => setSourceDrawer(null)}>✕</button>
            </div>
            <div className="source-drawer-body">
              <div className="source-meta">
                {sourceDrawer.metadata.act_name && (
                  <span className="badge badge-accent">{sourceDrawer.metadata.act_name}</span>
                )}
                {sourceDrawer.metadata.section_or_article && (
                  <span className="badge badge-neutral">§{sourceDrawer.metadata.section_or_article}</span>
                )}
                {sourceDrawer.metadata.document_type && (
                  <span className="badge badge-neutral">{sourceDrawer.metadata.document_type}</span>
                )}
                {sourceDrawer.metadata.year && (
                  <span className="badge badge-neutral">{sourceDrawer.metadata.year}</span>
                )}
              </div>
              <div className="source-text">{sourceDrawer.text}</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
