import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Mic, 
  MicOff, 
  Square, 
  Sparkles, 
  Globe,
  AlertCircle
} from 'lucide-react';
import { Message, AppSettings, WebSource } from '../types';
import { MessageItem } from './MessageItem';
import { voiceInput, voiceOutput } from '../utils/voice';

interface ChatInterfaceProps {
  sessionId: string;
  settings: AppSettings;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  sessionId,
  settings
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [voiceError, setVoiceError] = useState<string>('');
  const [webSearchActive, setWebSearchActive] = useState<boolean>(settings.enableWebSearch || false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSessionMessages = async (id: string) => {
    try {
      const res = await fetch(`/api/chat/sessions/${id}`);
      if (!res.ok) return;
      const data = await res.json();
      setMessages(data.messages || []);
      setTimeout(scrollToBottom, 100);
    } catch (e) {
      console.error('Failed to load session messages', e);
    }
  };

  useEffect(() => {
    if (sessionId) {
      loadSessionMessages(sessionId);
    }
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Adjust textarea height dynamically
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [inputText]);

  // Voice Input Toggle
  const toggleVoiceRecording = () => {
    setVoiceError('');
    if (isRecording) {
      voiceInput.stop();
      setIsRecording(false);
    } else {
      setIsRecording(true);
      voiceInput.start(
        (recognizedText: string, isFinal: boolean) => {
          setInputText(prev => {
            const trimmed = prev.trim();
            return trimmed ? `${trimmed} ${recognizedText}` : recognizedText;
          });
          if (isFinal) {
            setIsRecording(false);
          }
        },
        (errorMsg: string) => {
          setVoiceError(errorMsg);
          setIsRecording(false);
        },
        () => {
          setIsRecording(false);
        }
      );
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputText;
    if (!text.trim() || isStreaming) return;

    if (isRecording) {
      voiceInput.stop();
      setIsRecording(false);
    }

    const userMessage: Message = {
      id: String(Date.now()),
      role: 'user',
      content: text.trim(),
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsStreaming(true);

    // Placeholder streaming assistant message
    const assistantMsgId = String(Date.now() + 1);
    const initialAssistantMsg: Message = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
      isStreaming: true,
      isSearching: false
    };
    setMessages(prev => [...prev, initialAssistantMsg]);

    // Send to backend stream endpoint
    abortControllerRef.current = new AbortController();

    try {
      const activeApiKey = settings.llmProvider === 'gemini' 
        ? settings.geminiApiKey 
        : (settings.llmProvider === 'openai' ? settings.openaiApiKey : undefined);

      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: abortControllerRef.current.signal,
        body: JSON.stringify({
          session_id: sessionId,
          message: text.trim(),
          provider: settings.llmProvider,
          api_key: activeApiKey,
          web_search_enabled: webSearchActive
        })
      });

      if (!response.body) throw new Error('No readable stream');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let accumulatedText = '';
      let toolDataReceived: any = null;
      let sourcesReceived: WebSource[] = [];
      let searchQueriesReceived: string[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunkStr = decoder.decode(value, { stream: true });
        const lines = chunkStr.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.replace('data: ', '').trim();
            if (!jsonStr) continue;
            try {
              const event = JSON.parse(jsonStr);

              if (event.type === 'search_status') {
                setMessages(prev =>
                  prev.map(m =>
                    m.id === assistantMsgId
                      ? { ...m, isSearching: true, searchQuery: event.query }
                      : m
                  )
                );
              } else if (event.type === 'sources') {
                sourcesReceived = event.sources || [];
                searchQueriesReceived = event.queries || [];
                setMessages(prev =>
                  prev.map(m =>
                    m.id === assistantMsgId
                      ? {
                          ...m,
                          isSearching: false,
                          sources: sourcesReceived,
                          search_queries: searchQueriesReceived
                        }
                      : m
                  )
                );
              } else if (event.type === 'tool') {
                toolDataReceived = event.tool_data;
                setMessages(prev =>
                  prev.map(m =>
                    m.id === assistantMsgId ? { ...m, tool_data: event.tool_data } : m
                  )
                );
              } else if (event.type === 'chunk' || event.type === 'info') {
                accumulatedText += event.text;
                setMessages(prev =>
                  prev.map(m =>
                    m.id === assistantMsgId
                      ? { ...m, content: accumulatedText, isSearching: false }
                      : m
                  )
                );
              } else if (event.type === 'done') {
                setMessages(prev =>
                  prev.map(m =>
                    m.id === assistantMsgId
                      ? {
                          ...m,
                          content: accumulatedText,
                          isStreaming: false,
                          isSearching: false,
                          tool_data: toolDataReceived,
                          sources: sourcesReceived,
                          search_queries: searchQueriesReceived
                        }
                      : m
                  )
                );

                // Auto-speak if setting is enabled
                if (settings.autoSpeak && accumulatedText) {
                  voiceOutput.speak(accumulatedText, settings.voiceRate, settings.voiceGender);
                }
              }
            } catch {
              // Ignore malformed event chunk
            }
          }
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantMsgId
              ? { ...m, content: 'Communication error with AI service: ' + e.message, isStreaming: false, isSearching: false }
              : m
          )
        );
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
      setMessages(prev =>
        prev.map(m => (m.isStreaming ? { ...m, isStreaming: false, isSearching: false } : m))
      );
    }
  };

  const handleRegenerate = () => {
    const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
    if (lastUserMsg) {
      handleSendMessage(lastUserMsg.content);
    }
  };

  const promptSuggestions = [
    { label: 'What is Laplace Transformation?', text: 'What is Laplace Transformation?' },
    { label: 'Explain Laplace in Hinglish', text: 'Explain Laplace Transformation in Hinglish with formulas and solved examples' },
    { label: 'What are eigenvalues & eigenvectors?', text: 'What are eigenvalues and eigenvectors? Explain with a 2x2 matrix example' },
    { label: 'Explain PCA with an example', text: 'Explain Principal Component Analysis (PCA) with a practical example' },
    { label: 'What is the latest version of Python?', text: 'What is the latest version of Python and its key features?' },
    { label: 'Solve 8-puzzle with A*', text: 'Solve 8-puzzle with initial state 1, 2, 3, 4, 5, 6, 7, 0, 8 using A*' },
    { label: 'Find shortest path using BFS', text: 'Find the shortest path from node A to node G using BFS' },
    { label: 'Optimize exam study timetable', text: 'Create an optimized study timetable for my exams using Simulated Annealing' }
  ];

  return (
    <div className="flex flex-col h-full bg-[#f8fafc] relative">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-36 max-w-4xl w-full mx-auto">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
            <div className="w-14 h-14 rounded-2xl bg-blue-600 text-white flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Sparkles className="w-8 h-8" />
            </div>

            <div className="space-y-2 max-w-md">
              <h2 className="text-xl font-bold text-gray-900 tracking-tight">
                CampusMind AI Assistant & Lab
              </h2>
              <p className="text-xs text-gray-500 leading-relaxed">
                General-purpose educational AI assistant with real-time Google Search grounding, verified citations, voice interaction, and genuine Python algorithm execution.
              </p>
            </div>

            {/* Prompt suggestions pills */}
            <div className="flex flex-wrap gap-2 justify-center max-w-2xl pt-2">
              {promptSuggestions.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(s.text)}
                  className="px-3 py-2 bg-white hover:bg-blue-50/70 border border-gray-200 hover:border-blue-300 text-gray-700 text-xs font-medium rounded-xl shadow-2xs transition"
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m, idx) => (
            <MessageItem
              key={m.id}
              message={m}
              isLatest={idx === messages.length - 1}
              onRegenerate={handleRegenerate}
              preferredVoice={settings.voiceGender}
              voiceRate={settings.voiceRate}
            />
          ))
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Fixed Bottom Input Bar */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[#f8fafc] via-[#f8fafc]/90 to-transparent">
        <div className="max-w-4xl mx-auto">
          {/* Voice Error Notice */}
          {voiceError && (
            <div className="mb-2 p-2.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{voiceError}</span>
            </div>
          )}

          {/* Input Box Card */}
          <div className="relative bg-white rounded-3xl border border-gray-300 shadow-md focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent transition-all duration-200 flex items-center p-1.5 pl-3">
            {/* Search the Web Globe Toggle Button */}
            <button
              type="button"
              onClick={() => setWebSearchActive(!webSearchActive)}
              className={`p-2 rounded-full transition flex items-center gap-1.5 text-xs font-semibold mr-1 ${
                webSearchActive
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-gray-400 hover:text-gray-700 hover:bg-gray-100'
              }`}
              title={webSearchActive ? 'Web Search Enabled (Google Grounding)' : 'Enable Real-time Web Search'}
            >
              <Globe className={`w-4 h-4 ${webSearchActive ? 'text-blue-600' : ''}`} />
              {webSearchActive && <span className="hidden sm:inline text-[11px]">Search</span>}
            </button>

            <textarea
              ref={textareaRef}
              rows={1}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder={isRecording ? 'Listening... Speak into your microphone' : (webSearchActive ? 'Ask or search the web for any academic or real-time question...' : 'Ask CampusMind about mathematics, physics, algorithms, code, or exams...')}
              className="w-full text-sm text-gray-800 bg-transparent resize-none focus:outline-none placeholder:text-gray-400 py-1.5 max-h-36 font-normal"
            />

            {/* Input Action Buttons */}
            <div className="flex items-center gap-1.5 ml-2 shrink-0">
              {/* Microphone Button */}
              <button
                type="button"
                onClick={toggleVoiceRecording}
                className={`p-2.5 rounded-full transition ${
                  isRecording
                    ? 'bg-red-500 text-white animate-pulse shadow-md ring-2 ring-red-300'
                    : 'text-gray-500 hover:text-gray-800 hover:bg-gray-100'
                }`}
                title={isRecording ? 'Stop Recording' : 'Voice Input (Web Speech API)'}
              >
                {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>

              {/* Stop Generation or Send Button */}
              {isStreaming ? (
                <button
                  type="button"
                  onClick={handleStopGeneration}
                  className="p-2.5 bg-gray-900 text-white hover:bg-black rounded-full transition shadow-sm"
                  title="Stop Generating"
                >
                  <Square className="w-4 h-4" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => handleSendMessage()}
                  disabled={!inputText.trim()}
                  className="p-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded-full transition shadow-sm active:scale-95"
                  title="Send Message"
                >
                  <Send className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          <p className="text-[11px] text-gray-400 text-center mt-2">
            CampusMind AI integrates real-time web knowledge with genuine algorithm execution. Verified sources and citations are highlighted.
          </p>
        </div>
      </div>
    </div>
  );
};
