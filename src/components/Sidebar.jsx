import React from 'react';
import { MessageSquare, Scale, BookMarked, ShieldCheck, Sparkles, ChevronRight, Layers, HelpCircle, FileCheck2 } from 'lucide-react';

export default function Sidebar({ 
  onSelectQuery, 
  activeTab, 
  setActiveTab,
  indexedChunksCount,
  historySessions = [],
  onSelectSession
}) {
  const sampleQueries = [
    {
      title: "Anticipatory Bail under CrPC 438 / BNSS 482",
      query: "What is the procedure and parameters for granting anticipatory bail under Section 438 CrPC (Section 482 BNSS)?",
      lang: "EN",
      category: "Criminal Law"
    },
    {
      title: "Self Defense Rights under IPC 96-106",
      query: "What are the legal limitations of private defense of body and property under Indian law?",
      lang: "EN",
      category: "IPC / BNS"
    },
    {
      title: "एफआईआर दर्ज करने की प्रक्रिया (Hindi)",
      query: "सीआरपीसी की धारा 154 के तहत पुलिस एफआईआर (FIR) दर्ज करने से मना करे तो क्या कानूनी अधिकार हैं?",
      lang: "HI",
      category: "CrPC"
    },
    {
      title: "ಚೆಕ್ ಬೌನ್ಸ್ ಪ್ರಕರಣದ ಪ್ರಕ್ರಿಯೆ (Kannada)",
      query: "ನೆಗೋಷಿಯೇಬಲ್ ಇನ್ಸ್ಟ್ರುಮೆಂಟ್ಸ್ ಕಾಯ್ದೆ ಸೆಕ್ಷನ್ 138 ಅಡಿಯಲ್ಲಿ ಚೆಕ್ ಬೌನ್ಸ್ ಪ್ರಕರಣದ ನೋಟಿಸ್ ಪ್ರಕ್ರಿಯೆ ಏನು?",
      lang: "KN",
      category: "NI Act"
    },
    {
      title: "Cognizable vs Non-Cognizable Offenses",
      query: "Explain the classification of cognizable and non-cognizable offenses with statutory provisions.",
      lang: "EN",
      category: "Procedure"
    }
  ];

  return (
    <aside className="w-full lg:w-80 glass-panel rounded-2xl p-4 flex flex-col gap-5 border border-white/10 shrink-0">
      
      {/* Quick Action Sample Queries */}
      <div>
        <div className="flex items-center justify-between mb-3 px-1">
          <div className="flex items-center gap-2 text-indigo-400 font-semibold text-xs tracking-wider uppercase">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Legal Prompts & Cases</span>
          </div>
          <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full border border-slate-700">
            Cross-Lingual
          </span>
        </div>

        <div className="flex flex-col gap-2">
          {sampleQueries.map((item, idx) => (
            <button
              key={idx}
              onClick={() => {
                setActiveTab('rag');
                onSelectQuery(item.query);
              }}
              className="group text-left p-3 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-white/5 hover:border-indigo-500/30 transition-all duration-200"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors">
                  {item.title}
                </span>
                <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                  item.lang === 'HI' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                  item.lang === 'KN' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                  'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                }`}>
                  {item.lang}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                "{item.query}"
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Knowledge Base Status Card */}
      <div className="p-3.5 rounded-xl bg-gradient-to-br from-indigo-950/40 via-slate-900/80 to-slate-900 border border-indigo-500/20">
        <div className="flex items-center gap-2 mb-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          <span className="text-xs font-bold text-indigo-200">Statutory Knowledge Base</span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-center mt-2">
          <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800">
            <span className="text-base font-extrabold text-emerald-400 block">{indexedChunksCount || 39}</span>
            <span className="text-[10px] text-slate-400">Indexed Chunks</span>
          </div>
          <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800">
            <span className="text-base font-extrabold text-indigo-400 block">3</span>
            <span className="text-[10px] text-slate-400">Languages</span>
          </div>
        </div>
        <div className="mt-2.5 flex items-center justify-between text-[10px] text-slate-400 px-1 pt-2 border-t border-slate-800">
          <span>Embedding: MiniLM-L12-v2</span>
          <span className="text-emerald-400 font-medium">Cosine: &ge; 0.35</span>
        </div>
      </div>

      {/* Safety Guardrail Policy Note */}
      <div className="p-3 rounded-xl bg-slate-900/40 border border-slate-800 text-[11px] text-slate-400 space-y-1.5">
        <div className="flex items-center gap-1.5 font-semibold text-slate-300">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Anti-Hallucination Guardrails</span>
        </div>
        <p className="text-[10px] leading-relaxed text-slate-400">
          All AI answers undergo citation validation against official statutory provisions (IPC, CrPC, BNS, BNSS, BSA). Ungrounded claims are automatically flagged.
        </p>
      </div>

    </aside>
  );
}
