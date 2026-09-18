import React, { useState } from 'react';
import { BookOpen, Search, Copy, Check } from 'lucide-react';

export default function StatuteVault({ onOpenCitation }) {
  const [search, setSearch] = useState('');
  const [actFilter, setActFilter] = useState('ALL');
  const [copiedSec, setCopiedSec] = useState(null);

  const statutes = [
    {
      act: "IPC 1860",
      bns: "BNS 2023 Sec 103",
      section: "Section 302",
      title: "Punishment for Murder",
      text: "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
      bailable: "Non-Bailable",
      cognizable: "Cognizable"
    },
    {
      act: "CrPC 1973",
      bns: "BNSS 2023 Sec 482",
      section: "Section 438",
      title: "Anticipatory Bail Provision",
      text: "When any person has reason to believe that he may be arrested on an accusation of having committed a non-bailable offence, he may apply to the High Court or Sessions Court for direction under this section...",
      bailable: "Discretionary",
      cognizable: "N/A"
    },
    {
      act: "CrPC 1973",
      bns: "BNSS 2023 Sec 173",
      section: "Section 154",
      title: "First Information Report (FIR)",
      text: "Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing...",
      bailable: "N/A",
      cognizable: "Cognizable"
    },
    {
      act: "IPC 1860",
      bns: "BNS 2023 Sec 318",
      section: "Section 420",
      title: "Cheating & Property Inducement",
      text: "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person...",
      bailable: "Non-Bailable",
      cognizable: "Cognizable"
    },
    {
      act: "Indian Evidence Act 1872",
      bns: "BSA 2023 Sec 61",
      section: "Section 65B",
      title: "Admissibility of Electronic Records",
      text: "Notwithstanding anything contained in this Act, any information contained in an electronic record which is printed on paper or stored in optical media shall be deemed a document...",
      bailable: "N/A",
      cognizable: "N/A"
    }
  ];

  const filtered = statutes.filter(item => {
    const matchesSearch = item.section.toLowerCase().includes(search.toLowerCase()) ||
                          item.title.toLowerCase().includes(search.toLowerCase()) ||
                          item.text.toLowerCase().includes(search.toLowerCase());
    const matchesAct = actFilter === 'ALL' || item.act.includes(actFilter);
    return matchesSearch && matchesAct;
  });

  const handleCopy = (sec, text) => {
    navigator.clipboard.writeText(text);
    setCopiedSec(sec);
    setTimeout(() => setCopiedSec(null), 2000);
  };

  return (
    <div className="flex-1 max-w-4xl mx-auto w-full p-4 lg:p-6 overflow-y-auto h-[calc(100vh-4.5rem)] space-y-6">
      
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-indigo-400" />
            <span>Statute Vault & Bharatiya Nyaya Sanhita Codes</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Search IPC, CrPC, and Evidence Act statutory sections mapped to modern BNS, BNSS, and BSA 2023 provisions.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search section number (438, 302, 154) or topic (bail, cheating)..."
              className="w-full pl-10 pr-4 py-2.5 input-sleek text-xs text-slate-100 placeholder-slate-500"
            />
          </div>

          <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-white/10 text-xs">
            {['ALL', 'IPC', 'CrPC', 'Evidence'].map(f => (
              <button
                key={f}
                onClick={() => setActFilter(f)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                  actFilter === f ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((stat, idx) => (
          <div key={idx} className="p-5 rounded-2xl card-sleek flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-base font-extrabold text-indigo-300">{stat.section}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">
                  {stat.bns}
                </span>
              </div>

              <h3 className="text-xs font-bold text-slate-100 mb-2">{stat.title}</h3>
              <p className="text-xs text-slate-300 leading-relaxed italic">"{stat.text}"</p>
            </div>

            <div className="pt-2 border-t border-white/10 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-[10px] text-slate-400">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-amber-300">{stat.bailable}</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300">{stat.cognizable}</span>
              </div>

              <button
                onClick={() => handleCopy(stat.section, `${stat.section} ${stat.act}: ${stat.title}\n\n${stat.text}`)}
                className="text-xs text-slate-400 hover:text-slate-100 flex items-center gap-1"
              >
                {copiedSec === stat.section ? (
                  <span className="text-emerald-400 font-bold">Copied</span>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy</span>
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
