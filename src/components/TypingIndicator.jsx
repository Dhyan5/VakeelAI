/**
 * TypingIndicator - Animated "AI is thinking" indicator
 * Shows animated bouncing dots inside a chat bubble
 */
import React from 'react';
import { Sparkles } from 'lucide-react';

export default function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-slide-in-left" style={{ marginBottom: 16 }}>
      {/* AI Avatar */}
      <div
        className="flex-center flex-shrink-0 rounded-full"
        style={{
          width: 36,
          height: 36,
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          border: '1px solid rgba(139,92,246,0.4)',
          boxShadow: '0 0 12px rgba(139,92,246,0.3)',
        }}
      >
        <Sparkles size={14} color="white" />
      </div>

      {/* Typing Bubble */}
      <div>
        <span style={{
          display: 'block',
          fontSize: 11,
          fontWeight: 600,
          color: 'var(--clr-text-muted)',
          letterSpacing: '0.04em',
          textTransform: 'uppercase',
          marginBottom: 4,
        }}>
          VakeelAI
        </span>
        <div
          className="bubble-ai flex items-center gap-2"
          style={{ padding: '14px 18px', display: 'inline-flex' }}
        >
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      </div>
    </div>
  );
}
