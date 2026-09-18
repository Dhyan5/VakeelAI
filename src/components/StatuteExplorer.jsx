import React, { useState } from 'react';
import { BookOpen, Search, Filter, Copy, Check, Scale, ExternalLink, ShieldCheck } from 'lucide-react';

export default function StatuteExplorer({ onSelectCitation }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [actFilter, setActFilter] = useState('ALL');
  const [copiedSec, setCopiedSec] = useState(null);

  const statutoryDatabase = [
    {
      act: "IPC 1860",
      newAct: "BNS 2023 Sec 103",
      section: "Section 302",
      title: "Punishment for Murder",
      category: "Offenses Against Life",
      text: "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
      bailable: "Non-Bailable",
      cognizable: "Cognizable",
      court: "Court of Session"
    },
    {
      act: "CrPC 1973",
      newAct: "BNSS 2023 Sec 482",
      section: "Section 438",
      title: "Direction for grant of bail to person apprehending arrest (Anticipatory Bail)",
      category: "Bail Provisions",
      text: "When any person has reason to believe that he may be arrested on an accusation of having committed a non-bailable offence, he may apply to the High Court or the Court of Session for a direction under this section...",
      bailable: "Discretionary",
      cognizable: "N/A",
      court: "Sessions Court / High Court"
    },
    {
      act: "CrPC 1973",
      newAct: "BNSS 2023 Sec 173",
      section: "Section 154",
      title: "Information in cognizable cases (First Information Report - FIR)",
      category: "Investigation",
      text: "Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant...",
      bailable: "N/A",
      cognizable: "Cognizable",
      court: "Magistrate Court"
    },
    {
      act: "IPC 1860",
      newAct: "BNS 2023 Sec 318",
      section: "Section 420",
      title: "Cheating and dishonestly inducing delivery of property",
      category: "Property Offenses",
      text: "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security...",
      bailable: "Non-Bailable",
      cognizable: "Cognizable",
      court: "Magistrate First Class"
    },
    {
      act: "Indian Evidence Act 1872",
      newAct: "BSA 2023 Sec 61",
      section: "Section 65B",
      title: "Admissibility of electronic records",
      category: "Evidence",
      text: "Notwithstanding anything contained in this Act, any information contained in an electronic record which is printed on a paper, stored, recorded or copied in optical or magnetic media produced by a computer shall be deemed to be also a document...",
      bailable: "N/A",
      cognizable: "N/A",
      court: "All Judicial Courts"
    },
    {
      act: "IPC 1860",
      newAct: "BNS 2023 Sec 351",
      section: "Section 506",
      title: "Punishment for criminal intimidation",
      category: "Criminal Intimidation",
      text: "Whoever commits the offence of criminal intimidation shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both...",
      bailable: "Bailable",
      cognizable: "Non-Cognizable",
      court: "Any Magistrate"
    }
  ];

  const filteredStatutes = statutoryDatabase.filter(item => {
    const matchesSearch = item.section.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.act.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesAct = actFilter === 'ALL' || item.act.includes(actFilter);
    return matchesSearch && matchesAct;
  });

  const handleCopySec = (sectionKey, text) => {
    navigator.clipboard.writeText(text);
    setCopiedSec(sectionKey);
    setTimeout(() => setCopiedSec(null), 2000);
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-6rem)] glass-panel rounded-2xl border border-white/10 overflow-hidden">
      
      {/* Search Header Bar */}
      <div className="p-6 bg-slate-900/90 border-b border-white/10 space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-indigo-400" />
              <span>Statute Vault & Bharatiya Nyaya Sanhita Mapping</span>
            </h2>
            <p className="text-[10px] text-slate-400">Search IPC, CrPC, Evidence Act provisions mapped to new BNS, BNSS, BSA 2023 codes</p>
          </div>

          {/* Act Filter Tabs */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-white/10 text-xs">
            {['ALL', 'IPC', 'CrPC', 'Evidence'].map(filter => (
              <button
                key={filter}
                onClick={() => setActFilter(filter)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                  actFilter === filter
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by section number (e.g. 438, 302, 154) or keyword (bail, cheating, FIR)..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl glass-input text-xs text-slate-100 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Statutes List Grid */}
      <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredStatutes.map((statute, idx) => (
          <div
            key={idx}
            className="p-5 rounded-2xl glass-card flex flex-col justify-between space-y-4 border border-white/5 hover:border-indigo-500/40"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-base font-extrabold text-indigo-300">{statute.section}</span>
                  <span className="text-xs text-slate-400">({statute.act})</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 font-semibold border border-emerald-500/20">
                  ⚡ {statute.newAct}
                </span>
              </div>

              <h3 className="text-sm font-bold text-slate-100 mb-2">{statute.title}</h3>
              <p className="text-xs text-slate-300 leading-relaxed line-clamp-3">
                "{statute.text}"
              </p>
            </div>

            <div className="pt-3 border-t border-white/10 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-[10px]">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-amber-300 font-medium">
                  {statute.bailable}
                </span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 font-medium">
                  {statute.cognizable}
                </span>
              </div>

              <button
                onClick={() => handleCopySec(statute.section, `${statute.section} ${statute.act}: ${statute.title}\n\n${statute.text}`)}
                className="flex items-center gap-1 text-slate-400 hover:text-slate-100 text-xs px-2.5 py-1 rounded bg-slate-800/80 hover:bg-slate-700 transition-colors"
              >
                {copiedSec === statute.section ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400 font-semibold">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy Text</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
