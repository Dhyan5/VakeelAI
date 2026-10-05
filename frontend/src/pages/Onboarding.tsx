import { useState, useEffect } from 'react';
import { getModels, testKey, saveKey } from '../lib/api';
import type { Provider } from '../lib/types';
import '../styles/Onboarding.css';

interface OnboardingProps {
  onComplete: () => void;
}

const PROVIDER_LABELS: Record<string, string> = {
  openai: 'OpenAI',
  anthropic: 'Anthropic (Claude)',
  gemini: 'Google Gemini',
};

export default function Onboarding({ onComplete }: OnboardingProps) {
  const [step, setStep] = useState(1);
  const [provider, setProvider] = useState<Provider>('openai');
  const [model, setModel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [models, setModels] = useState<Record<string, string[]>>({});
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getModels().then((data) => {
      setModels(data.providers);
      if (data.providers.openai) {
        setModel(data.providers.openai[0]);
      }
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (models[provider]) {
      setModel(models[provider][0]);
    }
    setTestResult(null);
  }, [provider, models]);

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const result = await testKey(provider, model, apiKey);
      setTestResult(result);
    } catch (err: any) {
      setTestResult({ ok: false, message: err.message });
    }
    setTesting(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await saveKey(provider, model, apiKey);
      setStep(2);
    } catch (err: any) {
      setTestResult({ ok: false, message: err.message });
    }
    setSaving(false);
  };

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-card">
        <div className="onboarding-header">
          <div className="onboarding-logo">⚖ Nyaya</div>
          <div className="onboarding-tagline">AI Legal Research Assistant for Indian Law</div>
        </div>

        {step === 1 && (
          <>
            <div className="onboarding-step">Step 1 of 2</div>
            <div className="onboarding-title">Connect your AI model</div>
            <div className="onboarding-form">
              <div className="input-group">
                <label>Provider</label>
                <select
                  className="select"
                  value={provider}
                  onChange={(e) => setProvider(e.target.value as Provider)}
                >
                  {Object.entries(PROVIDER_LABELS).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>

              <div className="input-group">
                <label>Model</label>
                <select
                  className="select"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                >
                  {(models[provider] || []).map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>

              <div className="input-group">
                <label>API Key</label>
                <div className="input-password-wrapper">
                  <input
                    className="input"
                    type={showKey ? 'text' : 'password'}
                    value={apiKey}
                    onChange={(e) => { setApiKey(e.target.value); setTestResult(null); }}
                    placeholder="Paste your API key here"
                  />
                  <button
                    className="input-password-toggle"
                    onClick={() => setShowKey(!showKey)}
                    type="button"
                  >
                    {showKey ? '🙈' : '👁'}
                  </button>
                </div>
              </div>

              <button
                className="btn btn-secondary"
                onClick={handleTest}
                disabled={!apiKey.trim() || testing}
              >
                {testing ? <><span className="spinner" /> Testing...</> : '🔗 Test connection'}
              </button>

              {testResult && (
                <div className={`test-result ${testResult.ok ? 'success' : 'error'}`}>
                  {testResult.ok ? '✓' : '✕'} {testResult.message}
                </div>
              )}

              <button
                className="btn btn-primary btn-lg"
                onClick={handleSave}
                disabled={!testResult?.ok || saving}
              >
                {saving ? 'Saving...' : 'Save & Continue →'}
              </button>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <div className="onboarding-step">Step 2 of 2</div>
            <div className="onboarding-title">Add your legal documents</div>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '20px', lineHeight: '1.6' }}>
              Upload statutes, judgments, or other legal documents to build your knowledge base.
              Nyaya will only answer from these documents — no guessing.
            </p>

            <div className="alert alert-info" style={{ marginBottom: '20px' }}>
              ℹ️ You can upload documents anytime from the Knowledge Base page.
            </div>

            <div className="onboarding-actions">
              <button className="btn btn-secondary" onClick={onComplete}>
                Skip for now
              </button>
              <button className="btn btn-primary" onClick={onComplete}>
                Go to Knowledge Base →
              </button>
            </div>
          </>
        )}

        <div className="settings-privacy" style={{ marginTop: '24px' }}>
          🔒 <strong>Privacy:</strong> Your API key is stored only on your machine/server
          and is used only to call your chosen AI provider. It is encrypted at rest
          and never logged or sent elsewhere.
        </div>
      </div>
    </div>
  );
}
