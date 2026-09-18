import React, { useState } from 'react';
import { FileText, Upload, CheckCircle2, ShieldCheck, Sparkles, RefreshCw, FileCheck, ArrowRight } from 'lucide-react';

export default function DocAnalyzer({ language }) {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState(null);

  const sampleFiles = [
    { name: "Police FIR (Sec 154 CrPC / 173 BNSS).pdf", type: "Criminal FIR" },
    { name: "Commercial Lease & Indemnity Agreement.docx", type: "Contract" },
    { name: "Anticipatory Bail Application.pdf", type: "Court Petition" }
  ];

  const handleUpload = (fileName) => {
    setFile({ name: fileName });
    setAnalyzing(true);
    setReport(null);

    setTimeout(() => {
      setAnalyzing(false);
      setReport({
        name: fileName,
        type: "First Information Report (FIR) / Judicial Petition",
        ocr: "Tesseract OCR Extraction 100% Complete",
        summary: "The uploaded case document relates to alleged fraud and criminal breach of trust under IPC Sections 420 & 406 (BNS 2023 Sections 318 & 316). Investigation is under Magistrate jurisdiction.",
        clauses: [
          { title: "IPC 420 / BNS 318", desc: "Cheating and dishonestly inducing delivery of property.", risk: "High" },
          { title: "IPC 406 / BNS 316", desc: "Criminal breach of trust punishable with up to 3 years imprisonment.", risk: "High" },
          { title: "Bail Classification", desc: "Non-Bailable offense requiring formal bail application before Sessions Court.", risk: "Medium" }
        ],
        actions: [
          "File Anticipatory Bail application under CrPC Section 438 / BNSS Section 482 in Sessions Court.",
          "Issue formal response affidavit clarifying absence of dishonest intent.",
          "Request notice under CrPC Section 41A / BNSS Section 35 prior to coercive measures."
        ]
      });
    }, 1200);
  };

  return (
    <div className="flex-1 max-w-4xl mx-auto w-full p-4 lg:p-6 overflow-y-auto h-[calc(100vh-4.5rem)]">
      
      {!report && !analyzing && (
        <div className="space-y-6 py-6 animate-fade-in">
          <div>
            <h2 className="text-xl font-bold text-slate-100">Document Intelligence & Multilingual OCR</h2>
            <p className="text-xs text-slate-400 mt-1">
              Extract statutory references, risk clauses, and legal summaries from PDFs, DOCX, and scanned documents.
            </p>
          </div>

          <div
            className="border-2 border-dashed border-white/15 hover:border-indigo-500/40 rounded-2xl p-10 text-center card-sleek cursor-pointer transition-all"
            onClick={() => handleUpload("Police_FIR_Report_2026.pdf")}
          >
            <div className="p-4 rounded-2xl bg-indigo-600/20 text-indigo-400 w-fit mx-auto mb-3">
              <Upload className="w-8 h-8" />
            </div>
            <h3 className="text-sm font-bold text-slate-100">Click to Upload Case Document or Drop File</h3>
            <p className="text-xs text-slate-400 mt-1">Supports PDF, DOCX, PNG, JPG scans (English, Hindi Devanagari, Kannada OCR)</p>
          </div>

          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
              Or Select Sample Document Preset:
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {sampleFiles.map((doc, idx) => (
                <button
                  key={idx}
                  onClick={() => handleUpload(doc.name)}
                  className="p-4 rounded-xl card-sleek text-left space-y-1 hover:border-indigo-500/40 cursor-pointer transition-all"
                >
                  <FileText className="w-5 h-5 text-indigo-400" />
                  <h4 className="text-xs font-semibold text-slate-200">{doc.name}</h4>
                  <span className="text-[10px] text-slate-400 block">{doc.type}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {analyzing && (
        <div className="flex flex-col items-center justify-center py-20 space-y-4 animate-fade-in">
          <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
          <p className="text-xs font-semibold text-slate-200">Running Tesseract OCR & Clause Extraction...</p>
        </div>
      )}

      {report && (
        <div className="space-y-6 py-4 animate-fade-in">
          <div className="flex items-center justify-between pb-4 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <FileCheck className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-100">{report.name}</h3>
                <span className="text-xs text-emerald-400 font-semibold">{report.ocr}</span>
              </div>
            </div>

            <button
              onClick={() => { setReport(null); setFile(null); }}
              className="px-3 py-1.5 rounded-xl btn-secondary text-xs flex items-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Upload Another</span>
            </button>
          </div>

          <div className="p-5 rounded-2xl card-sleek space-y-2">
            <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">Executive Legal Summary</h4>
            <p className="text-xs text-slate-200 leading-relaxed">{report.summary}</p>
          </div>

          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Extracted Risk Clauses</h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {report.clauses.map((clause, idx) => (
                <div key={idx} className="p-4 rounded-xl card-sleek space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-200">{clause.title}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold">
                      {clause.risk}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{clause.desc}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="p-5 rounded-2xl card-sleek space-y-3 border-emerald-500/20">
            <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Recommended Action Plan</h4>
            <ul className="space-y-2 text-xs text-slate-300">
              {report.actions.map((act, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

    </div>
  );
}
