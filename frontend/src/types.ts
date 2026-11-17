export interface WebSource {
  title: string;
  url: string;
  snippet?: string;
  source_name?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_data?: any;
  sources?: WebSource[];
  search_queries?: string[];
  created_at?: string;
  isStreaming?: boolean;
  isSearching?: boolean;
  searchQuery?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export type ActiveTab = 
  | 'chat'
  | 'puzzles'
  | 'algorithms'
  | 'planner'
  | 'analytics'
  | 'settings';

export interface AppSettings {
  llmProvider: 'auto' | 'gemini' | 'openai';
  geminiApiKey: string;
  openaiApiKey: string;
  voiceGender: string;
  voiceRate: number;
  autoSpeak: boolean;
  theme: 'light' | 'dark';
  enableWebSearch: boolean;
}
