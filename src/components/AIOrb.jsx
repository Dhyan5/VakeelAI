/**
 * AIOrb - Floating, glowing AI status indicator displayed at the top of the app
 * Uses pure CSS animations for float + glow pulse effects
 */
import React from 'react';
import { Sparkles } from 'lucide-react';

export default function AIOrb({ isProcessing = false, isTyping = false }) {
  return (
    <div className="relative flex flex-col items-center gap-3 py-4 select-none">
      {/* Outer ambient glow ring (spinning) */}
      <div className="relative flex-center" style={{ width: 80, height: 80 }}>

        {/* Outermost spinning dashed ring */}
        <div
          className="spin-cw absolute inset-0 rounded-full"
          style={{
            border: '1px dashed rgba(59,130,246,0.25)',
            width: '100%',
            height: '100%',
          }}
        />

        {/* Inner counter-spin ring */}
        <div
          className="spin-ccw absolute rounded-full"
          style={{
            width: '80%',
            height: '80%',
            top: '10%',
            left: '10%',
            border: '1px solid rgba(139,92,246,0.2)',
            borderRadius: '50%',
          }}
        />

        {/* Core orb — floating + pulsing glow */}
        <div
          className="orb-floating relative flex-center rounded-full z-10"
          style={{
            width: 54,
            height: 54,
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            boxShadow: '0 0 20px rgba(59,130,246,0.5), 0 0 40px rgba(59,130,246,0.25)',
          }}
        >
          {/* Inner glow */}
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: 'radial-gradient(circle at 35% 35%, rgba(255,255,255,0.3) 0%, transparent 65%)',
            }}
          />

          {/* Icon */}
          {isProcessing ? (
            <div className="relative">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
              </svg>
            </div>
          ) : (
            <Sparkles size={20} color="white" strokeWidth={2} />
          )}
        </div>
      </div>

      {/* Status label */}
      <div className="flex items-center gap-2">
        <div className="status-dot" style={isProcessing ? { background: '#f59e0b', boxShadow: '0 0 8px #f59e0b' } : {}} />
        <span style={{ fontSize: 12, color: 'var(--clr-text-muted)', fontWeight: 500, letterSpacing: '0.05em' }}>
          {isProcessing ? 'PROCESSING' : isTyping ? 'THINKING' : 'ONLINE'}
        </span>
      </div>
    </div>
  );
}
