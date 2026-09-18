import React from 'react';
import { Scale, ShieldCheck, Languages, Sparkles, BookOpen, FileText, Search, PenTool, Circle } from 'lucide-react';

export default function Header({ 
  activeTab, 
  setActiveTab, 
  language, 
  setLanguage, 
  apiConnected,
  indexedChunksCount 
}) {
  const languages = [
    { code: 'en', label: 'English', script: 'English' },
    { code: 'hi', label: 'हिन्दी', script: 'Hindi' },
    { code: 'kn', label: 'ಕನ್ನಡ', script: 'Kannada' }
  ];

  const tabs = [
    { id: 'rag', label: 'Legal RAG Assistant', icon: Sparkles },
    { id: 'analyzer', label: 'Document OCR Analyzer', icon: FileText },
    { id: 'explorer', label: 'Statute Vault (IPC/CrPC/BNS)', icon: BookOpen },
    { id: 'drafting', label: 'Drafting Studio', icon: PenTool },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/10 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand & Logo */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-start">
          <div className="flex items-center gap-2.5 group cursor-pointer">
            <div className="relative p-2.5 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform duration-300">
              <Scale className="w-6 h-6 text-white" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-slate-900 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  Vakeel<span className="text-indigo-400">AI</span>
                </span>
                <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wider text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full uppercase">
                  v2.0 Nyaya
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium hidden sm:block">
                Multilingual Indian Legal Intelligence Platform
              </p>
            </div>
          </div>

          {/* API Health indicator badge for mobile/tablet */}
          <div className="md:hidden flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs">
            <Circle className={`w-2 h-2 fill-current ${apiConnected ? 'text-emerald-400 animate-pulse' : 'text-amber-400'}`} />
            <span className="text-slate-300 text-[11px]">{apiConnected ? 'API Live' : 'Offline Mode'}</span>
          </div>
        </div>

        {/* Center Tabs Navigation */}
        <nav className="flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-2xl border border-white/5 overflow-x-auto w-full md:w-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md shadow-indigo-600/30 border border-indigo-400/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-emerald-300' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Actions: Language Selector & API Status */}
        <div className="hidden lg:flex items-center gap-3">
          
          {/* Language Pills */}
          <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-white/10">
            <Languages className="w-3.5 h-3.5 text-slate-400 ml-2 mr-1" />
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => setLanguage(lang.code)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                  language === lang.code
                    ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {lang.label}
              </button>
            ))}
          </div>

          {/* System Guardrail Status Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/80 border border-emerald-500/20 text-xs">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <div className="flex flex-col text-left">
              <span className="text-[10px] text-slate-400 font-medium">Safety Guardrails</span>
              <span className="text-emerald-400 font-semibold text-[11px]">Active (0.35 Cosine Cutoff)</span>
            </div>
          </div>

        </div>

      </div>
    </header>
  );
}
