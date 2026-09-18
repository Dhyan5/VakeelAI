import React, { useState } from 'react';
import { PenTool, FileText, Copy, Check, Download, Sparkles, Scale, AlertCircle } from 'lucide-react';

export default function DraftingAssistant() {
  const [selectedTemplate, setSelectedTemplate] = useState('bail');
  const [copiedDraft, setCopiedDraft] = useState(false);

  const templates = [
    {
      id: 'bail',
      title: 'Anticipatory Bail Application (Sec 438 CrPC / 482 BNSS)',
      desc: 'Standard petition format for High Court or Court of Sessions for apprehending arrest.'
    },
    {
      id: 'notice',
      title: 'Legal Notice for Cheating & Non-Payment (Sec 420 IPC / Sec 138 NI Act)',
      desc: 'Pre-litigation legal notice served prior to criminal complaint.'
    },
    {
      id: 'affidavit',
      title: 'General Supporting Affidavit for Legal Petitions',
      desc: 'Sworn affidavit before Notary Public / Oath Commissioner.'
    },
    {
      id: 'rti',
      title: 'RTI Application (Right to Information Act 2005)',
      desc: 'Formal request to Public Information Officer (PIO) for official records.'
    }
  ];

  const drafts = {
    bail: `IN THE COURT OF THE SESSIONS JUDGE AT [CITY NAME]

IN THE MATTER OF:
[APPLICANT NAME], S/o [FATHER'S NAME],
R/o [ADDRESS], ... APPLICANT

VERSUS

STATE OF [STATE NAME] THROUGH POLICE STATION [STATION NAME] ... RESPONDENT

APPLICATION FOR GRANT OF ANTICIPATORY BAIL UNDER SECTION 438 OF THE CODE OF CRIMINAL PROCEDURE, 1973 (SECTION 482 OF BHARATIYA NAGARIK SURAKSHA SANHITA, 2023)

MOST RESPECTFULLY SHOWETH:

1. That the Applicant is a law-abiding citizen of India residing at the above-mentioned address.
2. That the Applicant has reasonable apprehension of being arrested in connection with FIR No. [FIR NO.] registered at Police Station [STATION NAME] for alleged offenses under Section(s) [SECTIONS].
3. That the allegations made against the Applicant are false, frivolous, and motivated by personal enmity.
4. That the Applicant undertakes to fully co-operate with the investigation and make himself available whenever required by the Investigating Officer.

PRAYER:
It is therefore respectfully prayed that this Hon'ble Court may be pleased to grant anticipatory bail to the Applicant in the event of arrest in connection with the aforementioned case.

AND FOR THIS ACT OF KINDNESS, THE APPLICANT SHALL EVER PRAY.

ADVOCATE FOR APPLICANT
DATE: [CURRENT DATE]`,

    notice: `LEGAL NOTICE

TO:
[OPPOSITE PARTY NAME]
[OPPOSITE PARTY ADDRESS]

SIR / MADAM,

UNDER INSTRUCTIONS AND ON BEHALF OF MY CLIENT, [CLIENT NAME], I HEREBY SERVE UPON YOU THIS LEGAL NOTICE:

1. That my Client is engaged in [BUSINESS / PROFESSION] and entered into an agreement dated [DATE] with you.
2. That pursuant to the contract, my Client fulfilled all obligations, whereupon an amount of Rs. [AMOUNT] became due and payable by you.
3. That despite repeated demands, you dishonestly failed to discharge your liability and committed cheating punishable under Section 420 of the Indian Penal Code (Section 318 of BNS 2023).

I HEREBY CALL UPON YOU TO PAY THE SAID SUM OF RS. [AMOUNT] WITHIN 15 DAYS OF RECEIPT OF THIS NOTICE, FAILING WHICH MY CLIENT SHALL INITIATE APPROPRIATE CIVIL AND CRIMINAL PROCEEDINGS AGAINST YOU.

ADVOCATE SIGNATURE
PLACE: [CITY]`,

    affidavit: `AFFIDAVIT

I, [DEPONENT NAME], aged about [AGE] years, S/o [FATHER NAME], residing at [ADDRESS], do hereby solemnly affirm and state as under:

1. That I am the Deponent herein and fully conversant with the facts of the present case.
2. That the contents of paragraphs 1 to [N] of the accompanying petition are true to my personal knowledge and belief.
3. That no material facts have been concealed therefrom.

DEPONENT

VERIFICATION:
Verified at [PLACE] on this [DATE] that the contents of the above affidavit are true and correct.

DEPONENT`,

    rti: `FORM OF APPLICATION FOR SEEKING INFORMATION UNDER THE RIGHT TO INFORMATION ACT, 2005

TO:
THE PUBLIC INFORMATION OFFICER (PIO),
[NAME OF PUBLIC AUTHORITY / DEPARTMENT],
[ADDRESS]

1. FULL NAME OF APPLICANT: [APPLICANT NAME]
2. ADDRESS: [ADDRESS]
3. PARTICULARS OF INFORMATION REQUIRED:
   a) Certified copies of official records concerning [SUBJECT].
   b) Period to which information relates: [START DATE] TO [END DATE].
4. APPLICATION FEE: Postal Order / Demand Draft No. [NO.] for Rs. 10/- attached herewith.

DATE: [DATE]
APPLICANT SIGNATURE`
  };

  const handleCopyDraft = () => {
    navigator.clipboard.writeText(drafts[selectedTemplate]);
    setCopiedDraft(true);
    setTimeout(() => setCopiedDraft(false), 2000);
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-6rem)] glass-panel rounded-2xl border border-white/10 overflow-hidden">
      
      {/* Top Header */}
      <div className="px-6 py-3.5 bg-slate-900/80 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <PenTool className="w-5 h-5 text-indigo-400" />
          <div>
            <h2 className="text-sm font-bold text-slate-100">Legal Template & Drafting Studio</h2>
            <p className="text-[10px] text-slate-400">Automated Indian court petition, notice, affidavit & RTI drafting engine</p>
          </div>
        </div>

        <button
          onClick={handleCopyDraft}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white text-xs font-bold shadow-md shadow-indigo-600/20 transition-all cursor-pointer"
        >
          {copiedDraft ? (
            <>
              <Check className="w-4 h-4 text-emerald-300" />
              <span className="text-emerald-300">Draft Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>Copy Full Draft</span>
            </>
          )}
        </button>
      </div>

      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        
        {/* Template List Sidebar */}
        <div className="w-full md:w-80 p-4 border-r border-white/10 bg-slate-900/40 space-y-2 overflow-y-auto">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 px-1">
            Select Legal Template:
          </h4>
          {templates.map(tpl => (
            <button
              key={tpl.id}
              onClick={() => setSelectedTemplate(tpl.id)}
              className={`w-full text-left p-3.5 rounded-xl border transition-all ${
                selectedTemplate === tpl.id
                  ? 'bg-indigo-600/20 border-indigo-500/50 text-slate-100 shadow-lg shadow-indigo-500/10'
                  : 'bg-slate-900/60 border-white/5 text-slate-300 hover:bg-slate-800/60'
              }`}
            >
              <h5 className="text-xs font-bold text-indigo-300 mb-1">{tpl.title}</h5>
              <p className="text-[11px] text-slate-400 leading-relaxed">{tpl.desc}</p>
            </button>
          ))}
        </div>

        {/* Draft Preview & Editor */}
        <div className="flex-1 p-6 overflow-y-auto bg-slate-950/60 flex flex-col space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400 pb-2 border-b border-white/10">
            <span className="font-semibold text-slate-200">Interactive Draft Preview:</span>
            <span className="text-[10px] text-emerald-400 font-medium">✨ Formatted for Indian Judicial Courts</span>
          </div>

          <textarea
            readOnly
            value={drafts[selectedTemplate]}
            className="flex-1 w-full p-4 rounded-xl bg-slate-900/90 border border-white/10 font-mono text-xs text-slate-200 leading-relaxed resize-none focus:outline-none"
            rows={18}
          />
        </div>

      </div>

    </div>
  );
}
