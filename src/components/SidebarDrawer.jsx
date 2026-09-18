import React from 'react';
import { Sparkles, BookMarked, ShieldCheck, Plus, MessageSquare, Layers, X, ArrowRight } from 'lucide-react';

export default function SidebarDrawer({ 
  open, 
  onClose, 
  onSelectPrompt, 
  onNewChat,
  indexedChunksCount 
}) {
  if (!open) return null;

  const samplePrompts = [
    {
      title: "Anticipatory Bail Parameters",
      prompt: "What are the essential parameters for granting anticipatory bail under Section 438 CrPC (Section 482 BNSS)?",
      tag: "Criminal"
    },
    {
      title: "Right to Private Defense",
      prompt: "Explain the legal limits of self-defense of body and property under Indian law.",
      tag: "IPC/BNS"
    },
    {
      title: "FIR Registration Rights (हिन्दी)",
      prompt: "सीआरपीसी की धारा 154 के तहत पुलिस एफआईआर (FIR) दर्ज करने से मना करे तो क्या कानूनी अधिकार हैं?",
      tag: "Hindi"
    },
    {
      title: "Cheque Bounce Notice (ಕನ್ನಡ)",
      prompt: "ನೆಗೋಷಿಯೇಬಲ್ ಇನ್ಸ್ಟ್ರುಮೆಂಟ್ಸ್ ಕಾಯ್ದೆ ಸೆಕ್ಷನ್ 138 ಅಡಿಯಲ್ಲಿ ಚೆಕ್ ಬೌನ್ಸ್ ಪ್ರಕರಣದ ನೋಟಿಸ್ ಪ್ರಕ್ರಿಯೆ ಏನು?",
      tag: "Kannada"
    }
  ];

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-72 bg-[#0C1222] border-r border-white/10 p-4 flex flex-col justify-between shadow-2xl animate-fade-in">
      
      <div className="space-y-5">
        {/* Sidebar Header */}
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <button
            onClick={onNewChat}
            className="flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all shadow-md shadow-indigo-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>New Case Research</span>
          </button>
          
          <button
            onClick={onClose}
            className="ml-2 p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Quick Legal Prompts */}
        <div>
          <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 px-1 flex items-center gap-1.5">
            <Sparkles className="w-3 h-3 text-indigo-400" />
            <span>Quick Case Prompts</span>
          </h4>

          <div className="space-y-1.5">
            {samplePrompts.map((item, idx) => (
              <button
                key={idx}
                onClick={() => {
                  onSelectPrompt(item.prompt);
                  onClose();
                }}
                className="w-full text-left p-2.5 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-white/5 hover:border-indigo-500/30 transition-all group"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300">
                    {item.title}
                  </span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 font-bold border border-slate-700">
                    {item.tag}
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 line-clamp-1">
                  "{item.prompt}"
                </p>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-3 border-t border-white/10 space-y-2">
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <Layers className="w-4 h-4 text-indigo-400" />
            <span>Indexed Provisions</span>
          </div>
          <span className="font-extrabold text-emerald-400">{indexedChunksCount || 39}</span>
        </div>

        <div className="p-2.5 rounded-xl bg-emerald-950/20 border border-emerald-500/20 flex items-center gap-2 text-[10px] text-emerald-300">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Anti-Hallucination Guardrails Active</span>
        </div>
      </div>

    </aside>
  );
}
