"use client";

import { useState } from "react";
import { submitCaseText } from "@/lib/api";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिंदी" },
  { code: "kn", label: "ಕನ್ನಡ" },
];

export default function InputPage() {
  const [text, setText] = useState("");
  const [lang, setLang] = useState("en");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await submitCaseText(text, lang);
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6 text-[#1E3A8A]">Start a Case</h1>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Language selector */}
        <div>
          <label className="block text-sm font-medium mb-2 text-[#64748B]">Language</label>
          <div className="flex gap-2">
            {LANGUAGES.map((l) => (
              <button
                key={l.code}
                type="button"
                onClick={() => setLang(l.code)}
                className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                  lang === l.code
                    ? "bg-[#1E3A8A] text-white border-[#1E3A8A]"
                    : "bg-white text-[#1E293B] border-[#E2E8F0] hover:border-[#1E3A8A]"
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>

        {/* Case text */}
        <div>
          <label className="block text-sm font-medium mb-2 text-[#64748B]">
            Describe your legal situation
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={8}
            placeholder="Enter the details of your case here..."
            className="w-full rounded-lg border border-[#E2E8F0] px-4 py-3 text-[#1E293B] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#1E3A8A] focus:border-transparent resize-none"
          />
        </div>

        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="bg-[#1E3A8A] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#3B5FCA] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Analyzing..." : "Analyze Case"}
        </button>
      </form>

      {/* Results */}
      {result && (
        <div className="mt-10 space-y-4">
          <h2 className="text-xl font-semibold text-[#1E3A8A]">Analysis</h2>

          <Section title="Facts" content={result.facts as string} />
          <Section title="Applicable Laws" content={(result.laws as string[])?.join(", ")} />
          <Section title="Precedents" content={(result.precedents as string[])?.join(", ")} />
          <Section title="Strengths" content={result.strengths as string} variant="success" />
          <Section title="Weaknesses" content={result.weaknesses as string} variant="warning" />
          <Section title="Next Steps" content={result.nextSteps as string} />

          <div className="flex items-center gap-2 mt-4 text-sm">
            <span className="text-[#64748B]">Confidence:</span>
            <span className="font-medium text-[#1E3A8A]">{result.confidence as string}</span>
          </div>

          <p className="text-xs text-[#94A3B8] mt-4 border-t border-[#E2E8F0] pt-4">
            {result.disclaimer as string}
          </p>
        </div>
      )}
    </div>
  );
}

function Section({
  title,
  content,
  variant,
}: {
  title: string;
  content: string;
  variant?: "success" | "warning";
}) {
  const bgColor =
    variant === "success"
      ? "bg-[#F0FDF4] border-[#BBF7D0]"
      : variant === "warning"
        ? "bg-[#FFFBEB] border-[#FDE68A]"
        : "bg-white border-[#E2E8F0]";

  return (
    <div className={`rounded-lg border p-4 ${bgColor}`}>
      <h3 className="text-sm font-semibold text-[#64748B] uppercase tracking-wide mb-1">
        {title}
      </h3>
      <p className="text-[#1E293B]">{content}</p>
    </div>
  );
}
