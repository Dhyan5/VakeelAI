"use client";

import { useEffect, useState } from "react";
import { getCaseHistory } from "@/lib/api";
import Link from "next/link";

interface HistoryItem {
  id: string;
  title: string;
  date: string;
}

export default function HistoryPage() {
  const [cases, setCases] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCaseHistory()
      .then((data) => setCases(data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-[#1E3A8A]">Case History</h1>
        <Link
          href="/input"
          className="bg-[#1E3A8A] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#3B5FCA] transition-colors"
        >
          + New Case
        </Link>
      </div>

      {loading ? (
        <div className="text-center py-12 text-[#64748B]">Loading...</div>
      ) : cases.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-[#64748B] mb-4">No cases yet</p>
          <Link href="/input" className="text-[#1E3A8A] font-medium hover:underline">
            Start your first case →
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {cases.map((c) => (
            <div
              key={c.id}
              className="flex items-center justify-between p-4 bg-white border border-[#E2E8F0] rounded-lg hover:shadow-md transition-shadow"
            >
              <div>
                <h2 className="font-medium text-[#1E293B]">{c.title}</h2>
                <p className="text-sm text-[#64748B]">{c.date}</p>
              </div>
              <span className="text-[#94A3B8] text-sm">→</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
