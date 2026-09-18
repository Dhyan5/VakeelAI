import React from 'react';
import { Scale, Sparkles, FileText, BookOpen, PenTool, Globe, PanelLeft, ShieldCheck, Activity } from 'lucide-react';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  language, 
  setLanguage, 
  sidebarOpen, 
  setSidebarOpen,
  apiConnected 
}) {
  const tabs = [
    { id: 'chat', label: 'Legal Copilot', icon: Sparkles },
    { id: 'analyzer', label: 'Document Analyzer', icon: FileText },
    { id: 'statutes', label: 'Statute Vault (BNS/IPC)', icon: BookOpen },
    { id: 'drafting', label: 'Drafting Studio', icon: PenTool },
  ];

  const languages = [
    { code: 'en', label: 'EN' },
    { code: 'hi', label: 'हिन्दी' },
    { code: 'kn', label: 'ಕನ್ನಡ' }
  ];

  return (
    <header className="sticky top-0 z-40 bg-[#070A12]/80 backdrop-blur-xl border-b border-white/10 px-4 lg:px-6 py-2.5 flex items-center justify-between">
      
      {/* Left: Sidebar Toggle + Brand */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-800/60 transition-colors"
          title="Toggle Sidebar"
        >
          <PanelLeft className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => setActiveTab('chat')}>
          <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-emerald-400 shadow-lg shadow-indigo-500/20">
            <Scale className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-base font-bold text-slate-100 tracking-tight">Vakeel<span className="text-indigo-400">AI</span></span>
              <span className="px-1.5 py-0.5 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded">2.0</span>
            </div>
          </div>
        </div>
      </div>

      {/* Center: Mode Tabs */}
      <nav className="hidden md:flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-white/10">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Right: Language Selector & API Status */}
      <div className="flex items-center gap-3">
        
        {/* Language Selector */}
        <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-lg border border-white/10">
          <Globe className="w-3.5 h-3.5 text-slate-400 ml-1.5 mr-0.5" />
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setLanguage(lang.code)}
              className={`px-2 py-0.5 rounded text-xs font-medium transition-all ${
                language === lang.code
                  ? 'bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {lang.label}
            </button>
          ))}
        </div>

        {/* API Status */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
          <div className={`w-2 h-2 rounded-full ${apiConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
          <span>{apiConnected ? 'Backend Connected' : 'Offline'}</span>
        </div>

      </div>

    </header>
  );
}
