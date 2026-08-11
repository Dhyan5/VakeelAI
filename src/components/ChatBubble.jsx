/**
 * ChatBubble - Renders a single chat message bubble (user or AI)
 * Includes TTS speaker button for AI messages
 * Handles markdown-like formatting for bold text and bullet lists
 */
import React from 'react';
import { Volume2, VolumeX, User } from 'lucide-react';
import { Sparkles } from 'lucide-react';

/**
 * Parse simple markdown-like text into formatted JSX
 * Supports: **bold**, bullet points, newlines
 */
function parseMarkdown(text) {
  const lines = text.split('\n');
  return lines.map((line, i) => {
    // Bold text: **...**
    const parsed = line.split(/(\*\*[^*]+\*\*)/g).map((part, j) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={j} style={{ color: 'var(--clr-text-primary)', fontWeight: 600 }}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });

    // Bullet points
    if (line.startsWith('•') || line.startsWith('- ')) {
      return (
        <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, margin: '3px 0' }}>
          <span style={{ color: 'var(--clr-accent-cyan)', marginTop: 2, flexShrink: 0 }}>•</span>
          <span>{parsed}</span>
        </div>
      );
    }

    // Empty line → spacer
    if (line.trim() === '') {
      return <div key={i} style={{ height: 6 }} />;
    }

    return <div key={i}>{parsed}</div>;
  });
}

export default function ChatBubble({ message, speak, speakingId, ttsLangCode }) {
  const isUser = message.role === 'user';
  const isSpeaking = speakingId === message.id;

  return (
    <div
      className={`flex gap-3 ${isUser ? 'flex-row-reverse animate-slide-in-right' : 'flex-row animate-slide-in-left'}`}
      style={{ marginBottom: 16, opacity: 0, animation: `${isUser ? 'slide-in-right' : 'slide-in-left'} 0.35s cubic-bezier(0.4,0,0.2,1) forwards` }}
    >
      {/* Avatar */}
      <div
        className="flex-center flex-shrink-0 rounded-full"
        style={{
          width: 36,
          height: 36,
          background: isUser
            ? 'linear-gradient(135deg, rgba(59,130,246,0.3), rgba(99,102,241,0.3))'
            : 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          border: `1px solid ${isUser ? 'rgba(99,179,237,0.3)' : 'rgba(139,92,246,0.4)'}`,
          boxShadow: isUser ? 'none' : '0 0 12px rgba(139,92,246,0.3)',
        }}
      >
        {isUser ? (
          <User size={16} color="rgba(255,255,255,0.8)" />
        ) : (
          <Sparkles size={14} color="white" />
        )}
      </div>

      {/* Message Content */}
      <div style={{ maxWidth: '78%', display: 'flex', flexDirection: 'column', gap: 4 }}>
        {/* Sender label */}
        <span style={{
          fontSize: 11,
          fontWeight: 600,
          color: 'var(--clr-text-muted)',
          letterSpacing: '0.04em',
          alignSelf: isUser ? 'flex-end' : 'flex-start',
          textTransform: 'uppercase',
        }}>
          {isUser ? 'You' : 'VakeelAI'}
        </span>

        {/* Bubble */}
        <div
          className={isUser ? 'bubble-user' : 'bubble-ai'}
          style={{
            padding: '12px 16px',
            fontSize: 14,
            lineHeight: 1.65,
            color: 'var(--clr-text-primary)',
          }}
        >
          {isUser ? (
            <p style={{ margin: 0 }}>{message.content}</p>
          ) : (
            <div>{parseMarkdown(message.content)}</div>
          )}
        </div>

        {/* Footer: Timestamp + TTS for AI */}
        <div
          className="flex items-center gap-2"
          style={{ alignSelf: isUser ? 'flex-end' : 'flex-start' }}
        >
          <span style={{ fontSize: 11, color: 'var(--clr-text-muted)' }}>
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>

          {/* TTS Button (AI messages only) */}
          {!isUser && (
            <button
              className={`tts-btn ${isSpeaking ? 'speaking' : ''}`}
              onClick={() => speak(message.content, ttsLangCode, message.id)}
              title={isSpeaking ? 'Stop speaking' : 'Listen to this response'}
              aria-label={isSpeaking ? 'Stop speaking' : 'Read aloud'}
            >
              {isSpeaking ? (
                <>
                  <VolumeX size={11} />
                  <span>Stop</span>
                </>
              ) : (
                <>
                  <Volume2 size={11} />
                  <span>Listen</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
