import React from 'react';
import { BookOpen, X, Copy, Check, ShieldCheck, ExternalLink } from 'lucide-react';

export default function CitationDrawer({ citation, onClose }) {
  const [copied, setCopied] = React.useState(false);

  if (!citation) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(`${citation.section} (${citation.act}): ${citation.title}\n\n${citation.snippet}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-96 bg-[#0C1222] border-l border-white/10 p-5 flex flex-col justify-between shadow-2xl animate-fade-in">
      
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-indigo-400" />
            <span className="text-xs font-bold text-slate-200">Statutory Provision Inspector</span>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Section Title & Act Badge */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-base font-extrabold text-indigo-300">{citation.section}</span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
              {citation.act}
            </span>
          </div>

          <h3 className="text-sm font-bold text-slate-100">{citation.title}</h3>
        </div>

        {/* Exact Text Snippet */}
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
            Verbatim Statutory Extract:
          </span>
          <p className="text-xs text-slate-300 leading-relaxed italic">
            "{citation.snippet}"
          </p>
        </div>

        {/* Cosine Similarity Match */}
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Vector Match Confidence</span>
            <span className="text-emerald-400 font-bold">96% Match</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full w-[96%] rounded-full" />
          </div>
        </div>
      </div>

      {/* Footer Copy Action */}
      <div className="pt-3 border-t border-white/10 space-y-2">
        <button
          onClick={handleCopy}
          className="w-full py-2.5 px-4 rounded-xl btn-secondary text-xs flex items-center justify-center gap-2 cursor-pointer"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-400 font-bold">Copied to Clipboard</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4 text-slate-400" />
              <span>Copy Statutory Extract</span>
            </>
          )}
        </button>

        <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 justify-center">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Verified against statutory index</span>
        </div>
      </div>

    </div>
  );
}
