/**
 * VakeelAI — Virtual Legal Assistant
 * Main Application Component
 *
 * Features:
 * - Dark glassmorphism UI with animated background mesh
 * - Floating AI orb with status indicators
 * - Multilingual chat (English, Hindi, Kannada)
 * - Document analysis with scan animation
 * - Text-to-Speech via Web Speech API
 * - Suggestion chips for quick queries
 * - Responsive two-panel layout (sidebar + chat)
 */

import React, { useState, useEffect, useRef, useCallback, useId } from 'react';
import {
  Send, Scale, MessageSquare, FileText, Trash2,
  History, Info, Shield, BookOpen, ChevronRight, Gavel
} from 'lucide-react';

import AIOrb from './components/AIOrb';
import LanguageToggle from './components/LanguageToggle';
import ChatBubble from './components/ChatBubble';
import TypingIndicator from './components/TypingIndicator';
import DocumentUpload from './components/DocumentUpload';

import { useTTS } from './hooks/useTTS';
import { UI_TEXT, MOCK_RESPONSES, getAIResponse, LANGUAGES } from './data/content';

// ─── Unique ID generator for messages ────────────────────────────────────────
let msgCounter = 0;
const makeId = () => `msg-${++msgCounter}-${Date.now()}`;

// ─── Initial greeting message factory ────────────────────────────────────────
const makeGreeting = (lang) => ({
  id: makeId(),
  role: 'ai',
  content: MOCK_RESPONSES[lang].greetings[0],
  timestamp: Date.now(),
});

export default function App() {
  // ─── State ────────────────────────────────────────────────────────────────
  const [lang, setLang] = useState('en');
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'upload'
  const [messages, setMessages] = useState(() => [makeGreeting('en')]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);    // AI is "thinking"
  const [isProcessing, setIsProcessing] = useState(false); // Doc analysis
  const [toast, setToast] = useState(null);

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const t = UI_TEXT[lang];
  const activeLang = LANGUAGES.find((l) => l.code === lang);

  // ─── TTS Hook ─────────────────────────────────────────────────────────────
  const { speak, stop, speakingId } = useTTS();

  // ─── Auto-scroll chat to bottom ──────────────────────────────────────────
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // ─── Language Switch: Reset with new greeting ─────────────────────────────
  const handleLangChange = useCallback((newLang) => {
    stop(); // Stop any active TTS
    setLang(newLang);
    setMessages([makeGreeting(newLang)]);
    setInputValue('');
    setIsTyping(false);
    showToast(`Language: ${LANGUAGES.find(l => l.code === newLang)?.native}`);
  }, [stop]);

  // ─── Toast helper ─────────────────────────────────────────────────────────
  const showToast = (msg, duration = 2500) => {
    setToast(msg);
    setTimeout(() => setToast(null), duration);
  };

  // ─── Send a chat message ──────────────────────────────────────────────────
  const sendMessage = useCallback(async (text) => {
    const content = (text || inputValue).trim();
    if (!content || isTyping) return;

    // Add user message
    const userMsg = { id: makeId(), role: 'user', content, timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response delay (800ms – 2.5s based on content length)
    const delay = Math.min(800 + content.length * 12, 2500);
    await new Promise((r) => setTimeout(r, delay));

    const aiContent = getAIResponse(content, lang);
    const aiMsg = { id: makeId(), role: 'ai', content: aiContent, timestamp: Date.now() };
    setMessages((prev) => [...prev, aiMsg]);
    setIsTyping(false);
  }, [inputValue, isTyping, lang]);

  // ─── Handle Enter key in input ────────────────────────────────────────────
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // ─── Handle document analysis completion ──────────────────────────────────
  const handleDocAnalysis = useCallback((analysisText, fileName) => {
    setIsProcessing(false);
    const aiMsg = {
      id: makeId(),
      role: 'ai',
      content: `📄 **Analysis for "${fileName}"**\n\n${analysisText}`,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, aiMsg]);
    setActiveTab('chat'); // Switch to chat to show results
    showToast(t.documentUploaded);
  }, [t]);

  // ─── Clear chat ───────────────────────────────────────────────────────────
  const clearChat = () => {
    stop();
    setMessages([makeGreeting(lang)]);
    setIsTyping(false);
    showToast('Chat cleared');
  };

  // ─── Quick Suggestion click ───────────────────────────────────────────────
  const handleSuggestion = (text) => {
    if (activeTab !== 'chat') setActiveTab('chat');
    sendMessage(text);
  };

  return (
    <div style={{ minHeight: '100vh', position: 'relative' }}>
      {/* Animated background mesh */}
      <div className="bg-mesh" />

      {/* ── Navbar ─────────────────────────────────────────────────────────── */}
      <nav
        className="navbar sticky top-0 z-50"
        style={{ padding: '0 24px', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div
            className="flex-center rounded-xl"
            style={{
              width: 38,
              height: 38,
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              boxShadow: '0 0 16px rgba(59,130,246,0.4)',
            }}
          >
            <Gavel size={18} color="white" />
          </div>
          <div>
            <span className="text-shimmer" style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 20, fontWeight: 700 }}>
              {t.appName}
            </span>
            <div style={{ fontSize: 10, color: 'var(--clr-text-muted)', letterSpacing: '0.06em', fontWeight: 500 }}>
              {t.tagline}
            </div>
          </div>
        </div>

        {/* Nav Right: Language Toggle + Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 hidden sm:flex">
            <div className="status-dot" />
            <span style={{ fontSize: 12, color: 'var(--clr-text-muted)', fontWeight: 500 }}>AI Active</span>
          </div>
          <LanguageToggle currentLang={lang} onChange={handleLangChange} />
        </div>
      </nav>

      {/* ── Main Layout ─────────────────────────────────────────────────────── */}
      <div
        style={{
          display: 'flex',
          height: 'calc(100vh - 64px)',
          maxWidth: 1400,
          margin: '0 auto',
          padding: '16px',
          gap: 16,
          position: 'relative',
          zIndex: 1,
        }}
      >
        {/* ── Left Sidebar ──────────────────────────────────────────────────── */}
        <aside
          className="glass-card hidden md:flex"
          style={{
            width: 260,
            flexShrink: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: 0,
            overflow: 'hidden',
          }}
        >
          {/* AI Orb Header */}
          <div style={{ padding: '8px 16px 0' }}>
            <AIOrb isProcessing={isProcessing} isTyping={isTyping} />
          </div>

          {/* Divider */}
          <div style={{ height: 1, background: 'var(--clr-border)', margin: '0 16px 12px' }} />

          {/* Navigation Tabs */}
          <div style={{ padding: '0 10px', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <button
              className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <MessageSquare size={16} />
              <span>{t.tabs.chat}</span>
              {activeTab === 'chat' && <ChevronRight size={12} style={{ marginLeft: 'auto' }} />}
            </button>
            <button
              className={`tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              <FileText size={16} />
              <span>{t.tabs.upload}</span>
              {activeTab === 'upload' && <ChevronRight size={12} style={{ marginLeft: 'auto' }} />}
            </button>
          </div>

          {/* Divider */}
          <div style={{ height: 1, background: 'var(--clr-border)', margin: '12px 16px' }} />

          {/* Quick Suggestions */}
          <div style={{ padding: '0 10px', flex: 1, overflowY: 'auto' }}>
            <p style={{ fontSize: 10, fontWeight: 600, color: 'var(--clr-text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', padding: '0 6px', marginBottom: 8 }}>
              Quick Questions
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {t.suggestions.map((s, i) => (
                <button
                  key={i}
                  className="tab-btn"
                  onClick={() => handleSuggestion(s)}
                  style={{ fontSize: 12, padding: '8px 12px' }}
                >
                  <BookOpen size={12} style={{ flexShrink: 0 }} />
                  <span style={{ textAlign: 'left', lineHeight: 1.4 }}>{s}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Footer info */}
          <div style={{ padding: '12px 16px', borderTop: '1px solid var(--clr-border)' }}>
            <div
              className="flex gap-2"
              style={{
                padding: '10px 12px',
                borderRadius: 10,
                background: 'rgba(59,130,246,0.06)',
                border: '1px solid rgba(59,130,246,0.12)',
              }}
            >
              <Info size={13} style={{ color: 'var(--clr-accent-blue)', flexShrink: 0, marginTop: 1 }} />
              <p style={{ fontSize: 11, color: 'var(--clr-text-muted)', lineHeight: 1.5 }}>
                {t.disclaimer}
              </p>
            </div>
          </div>
        </aside>

        {/* ── Main Content Area ──────────────────────────────────────────────── */}
        <main
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            minWidth: 0,
          }}
        >
          {/* ── Tab: Chat ─────────────────────────────────────────────────── */}
          {activeTab === 'chat' && (
            <div
              className="glass-card"
              style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
            >
              {/* Chat Header */}
              <div
                className="flex items-center justify-between"
                style={{ padding: '16px 20px', borderBottom: '1px solid var(--clr-border)', flexShrink: 0 }}
              >
                <div className="flex items-center gap-3">
                  <div className="md:hidden">
                    <AIOrb isProcessing={isProcessing} isTyping={isTyping} />
                  </div>
                  <div>
                    <h1 style={{ fontSize: 16, fontWeight: 700, color: 'var(--clr-text-primary)' }}>
                      {t.tabs.chat}
                    </h1>
                    <div className="flex items-center gap-2">
                      <span style={{ fontSize: 11, color: 'var(--clr-text-muted)' }}>
                        {activeLang?.native} · {messages.length - 1} messages
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  className="btn-glass btn-glass-danger btn-icon"
                  onClick={clearChat}
                  title="Clear chat"
                  aria-label="Clear chat history"
                >
                  <Trash2 size={15} />
                </button>
              </div>

              {/* Chat Messages Scrollable Area */}
              <div
                style={{
                  flex: 1,
                  overflowY: 'auto',
                  padding: '20px 20px 8px',
                }}
              >
                {/* Welcome Message (when only greeting) */}
                {messages.length === 1 && (
                  <div
                    className="text-center animate-fade-in"
                    style={{ padding: '24px 0 32px' }}
                  >
                    <div
                      className="flex-center mx-auto mb-4"
                      style={{
                        width: 72,
                        height: 72,
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2))',
                        border: '1px solid rgba(99,179,237,0.2)',
                        fontSize: 32,
                      }}
                    >
                      ⚖️
                    </div>
                    <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8, color: 'var(--clr-text-primary)' }}>
                      {t.greeting}
                    </h2>
                    <p style={{ fontSize: 13, color: 'var(--clr-text-muted)', maxWidth: 500, margin: '0 auto 24px', lineHeight: 1.7 }}>
                      {t.greetingSubtitle}
                    </p>

                    {/* Suggestion chips */}
                    <div className="flex flex-wrap gap-2" style={{ justifyContent: 'center' }}>
                      {t.suggestions.slice(0, 3).map((s, i) => (
                        <button
                          key={i}
                          className="suggestion-chip"
                          onClick={() => handleSuggestion(s)}
                        >
                          <Scale size={12} />
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Messages */}
                {messages.map((msg) => (
                  <ChatBubble
                    key={msg.id}
                    message={msg}
                    speak={speak}
                    speakingId={speakingId}
                    ttsLangCode={activeLang?.ttsCode || 'en-IN'}
                  />
                ))}

                {/* Typing Indicator */}
                {isTyping && <TypingIndicator />}

                {/* Scroll anchor */}
                <div ref={chatEndRef} />
              </div>

              {/* ── Chat Input Bar ─────────────────────────────────────────── */}
              <div
                style={{ padding: '12px 16px 16px', borderTop: '1px solid var(--clr-border)', flexShrink: 0 }}
              >
                {/* Mobile quick suggestions */}
                <div
                  className="md:hidden flex gap-2 overflow-x-auto pb-2"
                  style={{ scrollbarWidth: 'none', marginBottom: 10 }}
                >
                  {t.suggestions.slice(0, 3).map((s, i) => (
                    <button
                      key={i}
                      className="suggestion-chip flex-shrink-0"
                      onClick={() => handleSuggestion(s)}
                      style={{ fontSize: 11 }}
                    >
                      {s}
                    </button>
                  ))}
                </div>

                <div className="flex items-center gap-3">
                  <input
                    ref={inputRef}
                    className="glass-input flex-1"
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={t.inputPlaceholder}
                    style={{ padding: '13px 20px' }}
                    disabled={isTyping}
                    aria-label="Type your legal question"
                    maxLength={1000}
                  />
                  <button
                    className="btn-glass btn-glass-primary"
                    onClick={() => sendMessage()}
                    disabled={!inputValue.trim() || isTyping}
                    style={{
                      padding: '12px 20px',
                      opacity: (!inputValue.trim() || isTyping) ? 0.5 : 1,
                      cursor: (!inputValue.trim() || isTyping) ? 'not-allowed' : 'pointer',
                    }}
                    title="Send message"
                    aria-label="Send message"
                  >
                    <Send size={16} />
                    <span className="hidden sm:inline" style={{ fontWeight: 600 }}>{t.sendBtn}</span>
                  </button>
                </div>

                {/* Disclaimer */}
                <p style={{ fontSize: 10, color: 'var(--clr-text-muted)', textAlign: 'center', marginTop: 10 }}>
                  <Shield size={10} style={{ display: 'inline', marginRight: 4, verticalAlign: 'middle' }} />
                  VakeelAI provides general legal information. Not a substitute for professional legal advice.
                </p>
              </div>
            </div>
          )}

          {/* ── Tab: Document Upload ───────────────────────────────────────── */}
          {activeTab === 'upload' && (
            <div
              className="glass-card"
              style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
            >
              {/* Upload Tab Header */}
              <div
                className="flex items-center gap-3"
                style={{ padding: '16px 20px', borderBottom: '1px solid var(--clr-border)', flexShrink: 0 }}
              >
                <div
                  className="flex-center rounded-xl"
                  style={{
                    width: 36,
                    height: 36,
                    background: 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.15))',
                    border: '1px solid rgba(99,179,237,0.2)',
                  }}
                >
                  <FileText size={16} color="var(--clr-accent-blue)" />
                </div>
                <div>
                  <h1 style={{ fontSize: 16, fontWeight: 700, color: 'var(--clr-text-primary)' }}>
                    {t.tabs.upload}
                  </h1>
                  <p style={{ fontSize: 11, color: 'var(--clr-text-muted)' }}>
                    Upload a legal document for AI-powered analysis
                  </p>
                </div>
              </div>

              {/* Upload Content */}
              <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
                <DocumentUpload
                  lang={lang}
                  onAnalysisComplete={handleDocAnalysis}
                />

                {/* Info cards */}
                <div style={{ marginTop: 24, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  {[
                    { icon: '🔍', title: 'Clause Detection', desc: 'Identify risky or unusual legal clauses' },
                    { icon: '⚖️', title: 'Law Matching', desc: 'Cross-reference with applicable Indian laws' },
                    { icon: '📋', title: 'Summary Report', desc: 'Get a plain-language summary of the document' },
                    { icon: '🛡️', title: 'Rights Analysis', desc: 'Understand your rights and obligations' },
                  ].map((card, i) => (
                    <div
                      key={i}
                      className="glass-card"
                      style={{ padding: '14px', borderRadius: 12 }}
                    >
                      <div style={{ fontSize: 22, marginBottom: 8 }}>{card.icon}</div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--clr-text-primary)', marginBottom: 4 }}>
                        {card.title}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--clr-text-muted)', lineHeight: 1.5 }}>
                        {card.desc}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* ── Toast Notification ─────────────────────────────────────────────── */}
      {toast && (
        <div className="toast flex items-center gap-2">
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 6px #22c55e', flexShrink: 0 }} />
          {toast}
        </div>
      )}
    </div>
  );
}
