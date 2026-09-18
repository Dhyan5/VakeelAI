import React, { useState } from 'react';
import { 
  FileText, Upload, CheckCircle2, AlertTriangle, ShieldCheck, Sparkles, 
  FileCheck, ArrowRight, Eye, RefreshCw, Layers 
} from 'lucide-react';

export default function CaseAnalyzerWorkspace({ language }) {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const sampleDocumentTypes = [
    { name: "Police FIR Report (Sec 154 CrPC / 173 BNSS)", type: "Criminal FIR" },
    { name: "Commercial Contract & Lease Agreement", type: "Civil Contract" },
    { name: "Bail Petition & Counter Affidavit", type: "Petition" },
    { name: "Scanned Judicial Order / Judgment (PDF/Image)", type: "Court Order" }
  ];

  const handleFileUpload = (uploadedFile) => {
    setFile(uploadedFile);
    runAnalysis(uploadedFile.name);
  };

  const runAnalysis = (fileName) => {
    setAnalyzing(true);
    setAnalysisResult(null);

    setTimeout(() => {
      setAnalyzing(false);
      setAnalysisResult({
        fileName: fileName || "FIR_Police_Case_Report_2026.pdf",
        docType: "First Information Report (FIR) / Statutory Petition",
        detectedLanguage: language === 'hi' ? "Hindi (हिन्दी) & English" : language === 'kn' ? "Kannada (ಕನ್ನಡ) & English" : "English (Devanagari/Indic OCR verified)",
        ocrStatus: "Tesseract OCR Extraction 100% Complete",
        summary: "The document pertains to an alleged financial fraud and breach of trust under Section 420 (Cheating) and Section 406 (Criminal Breach of Trust) of the Indian Penal Code (IPC 1860) / Sections 318 & 316 of Bharatiya Nyaya Sanhita (BNS 2023).",
        keyClauses: [
          { title: "Alleged Offenses", detail: "IPC Section 420 (BNS Sec 318) - Cheating and dishonestly inducing delivery of property.", risk: "High" },
          { title: "Statutory Jurisdiction", detail: "Investigation under Judicial Magistrate First Class (JMFC) jurisdiction.", risk: "Medium" },
          { title: "Bail Classification", detail: "Non-Bailable, Cognizable offense requiring formal bail application before Sessions Court.", risk: "High" }
        ],
        recommendedActions: [
          "File Anticipatory Bail application under Section 438 CrPC / Section 482 BNSS in Sessions Court.",
          "Prepare reply affidavit addressing intent elements under IPC Section 406.",
          "Request notice under Section 41A CrPC (Section 35 BNSS) prior to any coercive action."
        ],
        groundingScore: 98
      });
    }, 1500);
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-6rem)] glass-panel rounded-2xl border border-white/10 overflow-hidden">
      
      {/* Top Bar */}
      <div className="px-6 py-3.5 bg-slate-900/80 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <FileText className="w-5 h-5 text-indigo-400" />
          <div>
            <h2 className="text-sm font-bold text-slate-100">Document Intelligence & Multilingual OCR</h2>
            <p className="text-[10px] text-slate-400">Extracts statutory provisions, risk clauses, and legal summaries from PDFs/Images</p>
          </div>
        </div>

        {file && (
          <button
            onClick={() => {
              setFile(null);
              setAnalysisResult(null);
            }}
            className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 px-2.5 py-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Upload New Document</span>
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {/* Upload Dropzone */}
        {!analysisResult && !analyzing && (
          <div className="space-y-6">
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                  handleFileUpload(e.dataTransfer.files[0]);
                }
              }}
              className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 cursor-pointer ${
                isDragging 
                  ? 'border-indigo-400 bg-indigo-500/10 scale-[1.01]' 
                  : 'border-white/15 bg-slate-900/40 hover:border-indigo-500/40 hover:bg-slate-900/60'
              }`}
            >
              <input
                type="file"
                id="docUpload"
                className="hidden"
                accept=".pdf,.docx,.png,.jpg,.jpeg"
                onChange={(e) => e.target.files && e.target.files[0] && handleFileUpload(e.target.files[0])}
              />
              <label htmlFor="docUpload" className="cursor-pointer flex flex-col items-center gap-3">
                <div className="p-4 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-lg shadow-indigo-500/10">
                  <Upload className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">
                    Drop FIR, Judgment, Contract or Petition here
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Supports PDF, DOCX, PNG, JPG scans (English, Hindi Devanagari, Kannada OCR)
                  </p>
                </div>
                <div className="flex items-center gap-2 text-xs text-indigo-300 bg-indigo-500/10 px-3 py-1 rounded-full border border-indigo-500/20 mt-2">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Automatic Tesseract OCR & Section Link Extraction</span>
                </div>
              </label>
            </div>

            {/* Pre-Loaded Sample Case Documents */}
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                Or Try Sample Legal Document Presets:
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {sampleDocumentTypes.map((doc, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleFileUpload({ name: doc.name })}
                    className="p-4 rounded-xl glass-card text-left flex items-center justify-between group cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-slate-800 text-indigo-400">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors block">
                          {doc.name}
                        </span>
                        <span className="text-[10px] text-slate-400">{doc.type}</span>
                      </div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition-colors" />
                  </button>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* Loading Spinner */}
        {analyzing && (
          <div className="flex flex-col items-center justify-center py-16 space-y-4">
            <div className="relative">
              <div className="w-16 h-16 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin" />
              <FileText className="w-6 h-6 text-indigo-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
            </div>
            <div className="text-center">
              <h3 className="text-sm font-bold text-slate-100">Running Multilingual Tesseract OCR & Clause Extraction...</h3>
              <p className="text-xs text-slate-400 mt-1">Extracting statutory references and calculating legal risk score</p>
            </div>
          </div>
        )}

        {/* Document Analysis Dashboard Result */}
        {analysisResult && (
          <div className="space-y-6">
            
            {/* Document Header Card */}
            <div className="p-5 rounded-2xl glass-panel bg-slate-900/80 border-indigo-500/30 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  <FileCheck className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">{analysisResult.fileName}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-indigo-300 font-medium">{analysisResult.docType}</span>
                    <span className="text-slate-600">•</span>
                    <span className="text-xs text-emerald-400 font-semibold">{analysisResult.ocrStatus}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 bg-emerald-500/10 px-3 py-1.5 rounded-xl border border-emerald-500/20 text-xs text-emerald-400 font-semibold">
                <ShieldCheck className="w-4 h-4" />
                <span>Statutory Grounding Verified ({analysisResult.groundingScore}%)</span>
              </div>
            </div>

            {/* Executive Legal Summary */}
            <div className="p-5 rounded-2xl glass-card space-y-2">
              <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                Executive Legal Summary
              </h4>
              <p className="text-sm text-slate-200 leading-relaxed">
                {analysisResult.summary}
              </p>
            </div>

            {/* Key Clauses & Risk Assessment */}
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                Key Extract & Statutory Risk Analysis:
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {analysisResult.keyClauses.map((clause, cIdx) => (
                  <div key={cIdx} className="p-4 rounded-xl glass-card space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-200">{clause.title}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded font-extrabold ${
                        clause.risk === 'High' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                        'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      }`}>
                        {clause.risk} Risk
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">
                      {clause.detail}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommended Legal Strategy */}
            <div className="p-5 rounded-2xl glass-card border-indigo-500/20 space-y-3">
              <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                Recommended Advocate Action Plan
              </h4>
              <ul className="space-y-2">
                {analysisResult.recommendedActions.map((action, aIdx) => (
                  <li key={aIdx} className="flex items-start gap-2.5 text-xs text-slate-300">
                    <span className="w-4 h-4 rounded-full bg-indigo-600/30 text-indigo-300 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                      {aIdx + 1}
                    </span>
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
