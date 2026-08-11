/**
 * LanguageToggle - Dropdown to switch between English, Hindi, and Kannada
 * Styled with glassmorphism design
 */
import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check } from 'lucide-react';
import { LANGUAGES } from '../data/content';

export default function LanguageToggle({ currentLang, onChange }) {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const activeLang = LANGUAGES.find((l) => l.code === currentLang) || LANGUAGES[0];

  const handleSelect = (code) => {
    onChange(code);
    setOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Toggle Button */}
      <button
        className="btn-glass flex items-center gap-2"
        onClick={() => setOpen((p) => !p)}
        style={{ padding: '8px 14px', fontSize: 13 }}
        aria-haspopup="listbox"
        aria-expanded={open}
        title="Switch Language"
      >
        <span style={{ fontSize: 16 }}>{activeLang.flag}</span>
        <span style={{ fontWeight: 600 }}>{activeLang.native}</span>
        <ChevronDown
          size={14}
          style={{
            transition: 'transform 0.2s ease',
            transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
            color: 'var(--clr-text-secondary)',
          }}
        />
      </button>

      {/* Dropdown Menu */}
      {open && (
        <div className="lang-dropdown" role="listbox">
          {LANGUAGES.map((lang) => (
            <div
              key={lang.code}
              className={`lang-option ${currentLang === lang.code ? 'active' : ''}`}
              role="option"
              aria-selected={currentLang === lang.code}
              onClick={() => handleSelect(lang.code)}
            >
              <span style={{ fontSize: 18 }}>{lang.flag}</span>
              <div>
                <div style={{ fontWeight: 600, fontSize: 13 }}>{lang.native}</div>
                <div style={{ fontSize: 11, color: 'var(--clr-text-muted)' }}>{lang.label}</div>
              </div>
              {currentLang === lang.code && (
                <Check size={14} style={{ marginLeft: 'auto', color: 'var(--clr-accent-blue)' }} />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
