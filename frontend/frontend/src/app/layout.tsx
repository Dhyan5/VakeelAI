import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import React from "react";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Legal RAG Platform",
  description: "Multilingual legal research aid",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600&family=Noto+Sans+Kannada:wght@400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body className="min-h-full font-sans text-body bg-background">
        <header className="flex items-center justify-between p-4 border-b border-gray-200">
          <Link href="/" className="text-xl font-semibold text-accent">LegalRAG</Link>
          <div className="flex gap-4 items-center">
            <Link href="/history">History</Link>
            <Link href="/input" className="bg-accent text-white px-3 py-1 rounded">Start Case</Link>
          </div>
        </header>
        <main className="p-4">{children}</main>
      </body>
    </html>
  );
}
