import React, { useState } from 'react';
import { PenTool, Copy, Check, Sparkles } from 'lucide-react';

export default function DraftStudio() {
  const [selectedTpl, setSelectedTpl] = useState('bail');
  const [copied, setCopied] = useState(false);

  const tpls = [
    { id: 'bail', title: 'Anticipatory Bail Application (Sec 438 CrPC / 482 BNSS)', desc: 'Sessions Court / High Court petition format for apprehension of arrest.' },
    { id: 'notice', title: 'Legal Notice for Cheating (Sec 420 IPC / 138 NI Act)', desc: 'Pre-litigation legal demand notice served prior to criminal complaint.' },
    { id: 'affidavit', title: 'Sworn General Affidavit', desc: 'Supporting affidavit for court petitions certified before Oath Commissioner.' }
  ];

  const drafts = {
    bail: `IN THE COURT OF THE SESSIONS JUDGE AT [CITY]

IN THE MATTER OF:
[APPLICANT NAME] ... APPLICANT
VERSUS
STATE OF [STATE] ... RESPONDENT

APPLICATION FOR ANTICIPATORY BAIL UNDER SECTION 438 CrPC / SECTION 482 BNSS 2023

MOST RESPECTFULLY SHOWETH:
1. That the Applicant has reasonable apprehension of arrest under FIR No. [NUMBER] registered at Police Station [NAME].
2. That the allegations are false, frivolous, and motivated by personal enmity.
3. That the Applicant undertakes to join investigation as and when required.

PRAYER:
Grant anticipatory bail to the Applicant in the event of arrest.

ADVOCATE FOR APPLICANT`,

    notice: `LEGAL NOTICE

TO:
[OPPOSITE PARTY NAME]

SIR / MADAM,
UNDER INSTRUCTIONS FROM MY CLIENT, [CLIENT NAME], I SERVE UPON YOU THIS LEGAL NOTICE:

1. That you dishonestly induced my Client to advance Rs. [AMOUNT] under agreement dated [DATE].
2. That despite demands, you defaulted, committing cheating under Section 420 IPC / Section 318 BNS 2023.

PAY RS. [AMOUNT] WITHIN 15 DAYS FAILING WHICH CRIMINAL PROCEEDINGS SHALL ENSUE.

ADVOCATE SIGNATURE`,

    affidavit: `AFFIDAVIT

I, [DEPONENT NAME], aged [AGE] years, R/o [ADDRESS], do hereby state on solemn affirmation:
1. That the statements in the accompanying petition are true to my knowledge and belief.
2. That no material facts have been concealed.

DEPONENT`
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(drafts[selectedTpl]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex-1 max-w-4xl mx-auto w-full p-4 lg:p-6 overflow-y-auto h-[calc(100vh-4.5rem)] space-y-6">
      
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <PenTool className="w-5 h-5 text-indigo-400" />
            <span>Legal Template & Drafting Studio</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">Formatted petitions and notices for Indian courts</p>
        </div>

        <button
          onClick={handleCopy}
          className="btn-primary py-2 px-4 text-xs flex items-center gap-1.5 cursor-pointer"
        >
          {copied ? (
            <span className="text-emerald-300 font-bold">Copied!</span>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>Copy Draft</span>
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {tpls.map(t => (
          <button
            key={t.id}
            onClick={() => setSelectedTpl(t.id)}
            className={`p-4 rounded-xl card-sleek text-left space-y-1 transition-all cursor-pointer ${
              selectedTpl === t.id ? 'border-indigo-500/50 bg-indigo-600/10' : 'hover:border-white/20'
            }`}
          >
            <h4 className="text-xs font-bold text-indigo-300">{t.title}</h4>
            <p className="text-[11px] text-slate-400 leading-relaxed">{t.desc}</p>
          </button>
        ))}
      </div>

      <div className="p-4 rounded-2xl bg-slate-950/80 border border-white/10">
        <textarea
          readOnly
          value={drafts[selectedTpl]}
          className="w-full h-80 bg-transparent font-mono text-xs text-slate-200 leading-relaxed resize-none focus:outline-none"
        />
      </div>

    </div>
  );
}
