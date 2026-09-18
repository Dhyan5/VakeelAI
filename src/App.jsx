import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import LegalRAGWorkspace from './components/LegalRAGWorkspace';
import CaseAnalyzerWorkspace from './components/CaseAnalyzerWorkspace';
import StatuteExplorer from './components/StatuteExplorer';
import DraftingAssistant from './components/DraftingAssistant';
import CitationInspector from './components/CitationInspector';

export default function App() {
  const [activeTab, setActiveTab] = useState('rag');
  const [language, setLanguage] = useState('en');
  const [selectedQuery, setSelectedQuery] = useState('');
  const [selectedCitations, setSelectedCitations] = useState([]);
  const [apiConnected, setApiConnected] = useState(true);
  const [indexedChunksCount, setIndexedChunksCount] = useState(39);

  // Poll backend health endpoint
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          const data = await res.json();
          setApiConnected(true);
          if (data.indexed_chunks) {
            setIndexedChunksCount(data.indexed_chunks);
          }
        } else {
          setApiConnected(false);
        }
      } catch (err) {
        setApiConnected(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30 selection:text-indigo-200">
      
      {/* Top Header Navbar */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={setLanguage}
        apiConnected={apiConnected}
        indexedChunksCount={indexedChunksCount}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-6 flex flex-col lg:flex-row gap-5 overflow-hidden">
        
        {/* Left Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          indexedChunksCount={indexedChunksCount}
          onSelectQuery={(query) => {
            setSelectedQuery(query);
            setActiveTab('rag');
          }}
        />

        {/* Center Main Workspace */}
        {activeTab === 'rag' && (
          <LegalRAGWorkspace
            selectedQuery={selectedQuery}
            language={language}
            apiConnected={apiConnected}
            onSelectCitation={(citations) => setSelectedCitations(citations)}
          />
        )}

        {activeTab === 'analyzer' && (
          <CaseAnalyzerWorkspace language={language} />
        )}

        {activeTab === 'explorer' && (
          <StatuteExplorer
            onSelectCitation={(citations) => setSelectedCitations(citations)}
          />
        )}

        {activeTab === 'drafting' && (
          <DraftingAssistant />
        )}

        {/* Right Citation Inspector (Visible in RAG or Explorer mode) */}
        {(activeTab === 'rag' || activeTab === 'explorer') && (
          <CitationInspector
            citations={selectedCitations}
            onClose={() => setSelectedCitations([])}
          />
        )}

      </main>

    </div>
  );
}
