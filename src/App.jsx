import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import SidebarDrawer from './components/SidebarDrawer';
import ChatCopilot from './components/ChatCopilot';
import CitationDrawer from './components/CitationDrawer';
import DocAnalyzer from './components/DocAnalyzer';
import StatuteVault from './components/StatuteVault';
import DraftStudio from './components/DraftStudio';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [language, setLanguage] = useState('en');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeCitation, setActiveCitation] = useState(null);
  const [prefillQuery, setPrefillQuery] = useState('');
  const [apiConnected, setApiConnected] = useState(true);
  const [indexedChunksCount, setIndexedChunksCount] = useState(39);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          const data = await res.json();
          setApiConnected(true);
          if (data.indexed_chunks) setIndexedChunksCount(data.indexed_chunks);
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
    <div className="min-h-screen bg-[#070A12] text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30 selection:text-indigo-200 relative">
      
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={setLanguage}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        apiConnected={apiConnected}
      />

      {/* Collapsible Left Sidebar Drawer */}
      <SidebarDrawer
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        indexedChunksCount={indexedChunksCount}
        onSelectPrompt={(promptText) => {
          setPrefillQuery(promptText);
          setActiveTab('chat');
        }}
        onNewChat={() => {
          setPrefillQuery('');
          setActiveTab('chat');
          setSidebarOpen(false);
        }}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {activeTab === 'chat' && (
          <ChatCopilot
            language={language}
            prefillQuery={prefillQuery}
            apiConnected={apiConnected}
            onOpenCitation={(citation) => setActiveCitation(citation)}
          />
        )}

        {activeTab === 'analyzer' && (
          <DocAnalyzer language={language} />
        )}

        {activeTab === 'statutes' && (
          <StatuteVault onOpenCitation={(citation) => setActiveCitation(citation)} />
        )}

        {activeTab === 'drafting' && (
          <DraftStudio />
        )}
      </main>

      {/* Slide-Over Right Citation Drawer */}
      <CitationDrawer
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />

    </div>
  );
}
