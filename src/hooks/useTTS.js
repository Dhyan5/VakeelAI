/**
 * useTTS - Custom React Hook for Web Speech API (SpeechSynthesis)
 * Handles text-to-speech playback with language support
 */
import { useState, useCallback, useEffect, useRef } from 'react';

export function useTTS() {
  const [speakingId, setSpeakingId] = useState(null); // Track which message is being spoken
  const utteranceRef = useRef(null);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      window.speechSynthesis?.cancel();
    };
  }, []);

  /**
   * Speak a given text in a given language
   * @param {string} text - Text to speak
   * @param {string} lang - BCP 47 language code (e.g. 'hi-IN', 'kn-IN', 'en-IN')
   * @param {string|number} id - Unique ID for this message
   */
  const speak = useCallback((text, lang, id) => {
    if (!('speechSynthesis' in window)) {
      console.warn('Web Speech API not supported in this browser.');
      return;
    }

    // If currently speaking the same message, stop it
    if (speakingId === id) {
      window.speechSynthesis.cancel();
      setSpeakingId(null);
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    // Strip markdown formatting for cleaner TTS
    const cleanText = text
      .replace(/\*\*(.*?)\*\*/g, '$1')  // Bold
      .replace(/\*(.*?)\*/g, '$1')        // Italic
      .replace(/#{1,6}\s/g, '')           // Headers
      .replace(/•/g, '')                   // Bullets
      .replace(/\n{2,}/g, '. ')           // Double newlines
      .replace(/\n/g, ' ')                 // Single newlines
      .replace(/[📄⚠️✅]/g, '');          // Emojis

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = lang;
    utterance.rate = 0.9;   // Slightly slower for clarity
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utteranceRef.current = utterance;

    utterance.onstart = () => setSpeakingId(id);
    utterance.onend = () => setSpeakingId(null);
    utterance.onerror = (e) => {
      console.error('SpeechSynthesis error:', e);
      setSpeakingId(null);
    };

    window.speechSynthesis.speak(utterance);
  }, [speakingId]);

  /**
   * Stop all speech
   */
  const stop = useCallback(() => {
    window.speechSynthesis?.cancel();
    setSpeakingId(null);
  }, []);

  return { speak, stop, speakingId };
}
