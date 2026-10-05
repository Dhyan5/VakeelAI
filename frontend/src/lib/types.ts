/* Nyaya – Type definitions */

export interface ApiKeyStatus {
  configured: boolean;
  provider: string | null;
  model: string | null;
  last4: string | null;
}

export interface KeyTestResult {
  ok: boolean;
  message: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  category: string;
  act_name: string | null;
  year: number | null;
  chunk_count: number;
  status: string;
  error_message: string | null;
  file_size: number;
  created_at: string | null;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  confidence?: number;
  feedback?: string | null;
  created_at?: string;
  mappings?: LawMapping[];
}

export interface Citation {
  chunk_id: string;
  act_name: string;
  section: string;
  document_type: string;
  year: number | null;
  score?: number;
}

export interface LawMapping {
  old_law: string;
  old_section: string;
  new_law: string;
  new_section: string;
  title: string;
}

export interface SourceChunk {
  chunk_id: string;
  text: string;
  metadata: Record<string, any>;
}

export type Provider = 'openai' | 'anthropic' | 'gemini';

export interface DocumentStats {
  total_documents: number;
  total_chunks: number;
}
