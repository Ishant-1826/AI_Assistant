import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  Bot, 
  User, 
  Copy, 
  Check, 
  Volume2, 
  VolumeX, 
  RotateCcw,
  Globe,
  Loader2
} from 'lucide-react';
import { Message } from '../types';
import { ToolResultCard } from './ToolResultCard';
import { SourceCards } from './SourceCards';
import { voiceOutput } from '../utils/voice';

interface MessageItemProps {
  message: Message;
  isLatest: boolean;
  onRegenerate?: () => void;
  preferredVoice?: string;
  voiceRate?: number;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  isLatest,
  onRegenerate,
  preferredVoice,
  voiceRate = 1.0
}) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSpeak = () => {
    if (isSpeaking) {
      voiceOutput.stop();
      setIsSpeaking(false);
    } else {
      setIsSpeaking(true);
      voiceOutput.speak(
        message.content,
        voiceRate,
        preferredVoice,
        () => setIsSpeaking(true),
        () => setIsSpeaking(false)
      );
    }
  };

  const formatTimestamp = (dateStr?: string) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  // Determine tool data and sources whether nested or direct
  const actualToolData = message.tool_data?.tool_data || (message.tool_data?.algorithm || message.tool_data?.num_disks ? message.tool_data : null);
  const actualSources = message.sources || message.tool_data?.sources || [];
  const actualQueries = message.search_queries || message.tool_data?.queries || [];

  return (
    <div className={`flex gap-3 mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* AI Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs mt-1">
          <Bot className="w-4 h-4" />
        </div>
      )}

      {/* Message Bubble Container */}
      <div className={`flex flex-col max-w-[85%] md:max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`p-4 rounded-2xl shadow-xs transition-all duration-200 text-sm leading-relaxed ${
            isUser
              ? 'bg-blue-600 text-white rounded-tr-xs shadow-blue-500/10'
              : 'bg-white border border-gray-200/80 text-gray-800 rounded-tl-xs shadow-xs'
          }`}
        >
          {/* Searching Status Indicator */}
          {!isUser && message.isSearching && (
            <div className="mb-3 px-3 py-1.5 bg-blue-50 text-blue-700 text-xs font-medium rounded-xl flex items-center gap-2 border border-blue-200/60 animate-pulse">
              <Globe className="w-3.5 h-3.5 text-blue-600 animate-spin" />
              <span>
                Searching the web{message.searchQuery ? `: "${message.searchQuery}"` : '...'}
              </span>
            </div>
          )}

          {/* Tool Result Card if executed */}
          {!isUser && actualToolData && (
            <ToolResultCard toolData={actualToolData} />
          )}

          {/* Markdown Content */}
          <div className={`prose prose-sm max-w-none ${isUser ? 'text-white' : 'text-gray-800'}`}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, className, children, ...props }: any) {
                  const match = /language-(\w+)/.exec(className || '');
                  const isInline = !match && !String(children).includes('\n');
                  return isInline ? (
                    <code
                      className={`px-1.5 py-0.5 rounded text-xs font-mono ${
                        isUser ? 'bg-blue-700/60 text-white' : 'bg-gray-100 text-blue-700'
                      }`}
                      {...props}
                    >
                      {children}
                    </code>
                  ) : (
                    <div className="relative my-2 rounded-xl overflow-hidden border border-gray-700/30">
                      <div className="bg-gray-900 px-3 py-1 flex items-center justify-between text-[11px] text-gray-400 font-mono">
                        <span>{match ? match[1] : 'code'}</span>
                        <button
                          onClick={() => navigator.clipboard.writeText(String(children))}
                          className="hover:text-white transition flex items-center gap-1 text-[10px]"
                        >
                          <Copy className="w-3 h-3" /> Copy
                        </button>
                      </div>
                      <pre className="p-3 bg-gray-950 text-gray-100 text-xs overflow-x-auto font-mono">
                        <code>{children}</code>
                      </pre>
                    </div>
                  );
                },
                table({ children }) {
                  return (
                    <div className="overflow-x-auto my-3">
                      <table className="w-full text-xs text-left border border-gray-200 rounded-lg overflow-hidden">
                        {children}
                      </table>
                    </div>
                  );
                },
                th({ children }) {
                  return (
                    <th className="bg-gray-100 p-2 font-bold text-gray-800 border-b border-gray-200">
                      {children}
                    </th>
                  );
                },
                td({ children }) {
                  return (
                    <td className="p-2 border-b border-gray-100 text-gray-700">
                      {children}
                    </td>
                  );
                }
              }}
            >
              {message.content}
            </ReactMarkdown>

            {message.isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-blue-600 animate-pulse align-middle" />
            )}
          </div>

          {/* Clickable Verified Source Cards */}
          {!isUser && actualSources.length > 0 && (
            <SourceCards sources={actualSources} queries={actualQueries} />
          )}
        </div>

        {/* Action Toolbar & Timestamp */}
        <div className="flex items-center gap-2 mt-1.5 px-1 text-xs text-gray-400">
          <span>{formatTimestamp(message.created_at)}</span>

          {!isUser && !message.isStreaming && (
            <div className="flex items-center gap-1 ml-1">
              {/* Copy Response Button */}
              <button
                onClick={handleCopy}
                className="p-1 hover:text-gray-700 rounded transition"
                title="Copy response"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              </button>

              {/* Text-to-Speech Button */}
              <button
                onClick={handleSpeak}
                className={`p-1 rounded transition ${
                  isSpeaking ? 'text-blue-600 font-bold' : 'hover:text-gray-700'
                }`}
                title={isSpeaking ? 'Stop speaking' : 'Read aloud'}
              >
                {isSpeaking ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
              </button>

              {/* Regenerate Button */}
              {isLatest && onRegenerate && (
                <button
                  onClick={onRegenerate}
                  className="p-1 hover:text-gray-700 rounded transition flex items-center gap-0.5 text-[11px]"
                  title="Regenerate response"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center shrink-0 shadow-xs mt-1">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
};
