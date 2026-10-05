import { useState } from 'react';
import ChatPage from './pages/ChatPage';
import KnowledgeBase from './pages/KnowledgeBase';
import Settings from './pages/Settings';
import './index.css';

type Page = 'chat' | 'kb' | 'settings';

export default function App() {
  const [page, setPage] = useState<Page>('chat');

  if (page === 'kb') {
    return <KnowledgeBase onBack={() => setPage('chat')} />;
  }

  if (page === 'settings') {
    return <Settings onBack={() => setPage('chat')} />;
  }

  return <ChatPage onNavigate={(p) => setPage(p)} />;
}
