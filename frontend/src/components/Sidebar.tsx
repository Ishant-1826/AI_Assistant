import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Brain, 
  GitFork, 
  Calendar, 
  Activity, 
  Plus, 
  MessageSquare, 
  Trash2, 
  Edit2, 
  Check, 
  Settings as SettingsIcon,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { ActiveTab, ChatSession } from '../types';

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  currentSessionId: string;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onOpenSettings: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onOpenSettings
}) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState<string>('');
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  const fetchSessions = async () => {
    try {
      const res = await fetch('/api/chat/sessions');
      const data = await res.json();
      setSessions(data);
    } catch (e) {
      console.error('Failed to load chat sessions', e);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [currentSessionId]);

  const handleStartRename = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingSessionId(session.id);
    setEditingTitle(session.title);
  };

  const handleSaveRename = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!editingTitle.trim()) return;
    try {
      await fetch(`/api/chat/sessions/${sessionId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: editingTitle.trim() })
      });
      setEditingSessionId(null);
      fetchSessions();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await fetch(`/api/chat/sessions/${sessionId}`, {
        method: 'DELETE'
      });
      fetchSessions();
      if (sessionId === currentSessionId) {
        onNewChat();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const navItems = [
    { id: 'chat', label: 'AI Assistant', icon: Bot },
    { id: 'puzzles', label: 'AI Puzzle Solver', icon: Brain },
    { id: 'algorithms', label: 'Algorithm Laboratory', icon: GitFork },
    { id: 'planner', label: 'Study Planner', icon: Calendar },
    { id: 'analytics', label: 'Learning Analytics', icon: Activity },
  ];

  return (
    <aside
      className={`h-screen bg-white border-r border-gray-200 flex flex-col transition-all duration-300 z-30 select-none ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="p-4 flex items-center justify-between border-b border-gray-100">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm shrink-0">
              <Bot className="w-5 h-5" />
            </div>
            <div className="leading-tight truncate">
              <h1 className="font-bold text-sm text-gray-900 tracking-tight">CampusMind AI</h1>
              <p className="text-[10px] text-gray-400 font-medium truncate">College Assistant & Lab</p>
            </div>
          </div>
        )}

        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition"
          title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={() => {
            setActiveTab('chat');
            onNewChat();
          }}
          className={`w-full py-2.5 px-3 rounded-xl border border-gray-200 hover:border-blue-300 bg-gray-50 hover:bg-blue-50/50 text-gray-800 text-xs font-semibold flex items-center transition shadow-xs gap-2 ${
            isCollapsed ? 'justify-center' : 'justify-start'
          }`}
          title="New Chat"
        >
          <Plus className="w-4 h-4 text-blue-600 shrink-0" />
          {!isCollapsed && <span>New Chat</span>}
        </button>
      </div>

      {/* Main Navigation Links */}
      <nav className="px-3 py-1 space-y-1">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as ActiveTab)}
              className={`w-full py-2 px-3 rounded-xl text-xs font-semibold flex items-center gap-2.5 transition ${
                isActive
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              } ${isCollapsed ? 'justify-center' : 'justify-start'}`}
              title={item.label}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-gray-500'}`} />
              {!isCollapsed && <span className="truncate">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Chat History Section */}
      {!isCollapsed && (
        <div className="flex-1 overflow-y-auto px-3 py-3 border-t border-gray-100 mt-2 space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 px-2 block mb-1">
            Recent Chats
          </span>

          {sessions.length === 0 ? (
            <span className="text-xs text-gray-400 italic px-2 block">No past chats yet</span>
          ) : (
            sessions.map(s => {
              const isSelected = activeTab === 'chat' && s.id === currentSessionId;
              const isEditing = editingSessionId === s.id;

              return (
                <div
                  key={s.id}
                  onClick={() => {
                    setActiveTab('chat');
                    onSelectSession(s.id);
                  }}
                  className={`group relative flex items-center justify-between py-2 px-2.5 rounded-xl text-xs cursor-pointer transition ${
                    isSelected
                      ? 'bg-gray-100 text-gray-900 font-semibold'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate pr-1 flex-1">
                    <MessageSquare className="w-3.5 h-3.5 text-gray-400 shrink-0" />
                    {isEditing ? (
                      <input
                        type="text"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full text-xs bg-white border border-blue-400 rounded px-1.5 py-0.5 focus:outline-none"
                        autoFocus
                      />
                    ) : (
                      <span className="truncate">{s.title || 'Conversation'}</span>
                    )}
                  </div>

                  {/* Actions (Rename / Delete) */}
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                    {isEditing ? (
                      <button
                        onClick={(e) => handleSaveRename(s.id, e)}
                        className="p-1 hover:text-emerald-600"
                        title="Save title"
                      >
                        <Check className="w-3 h-3" />
                      </button>
                    ) : (
                      <button
                        onClick={(e) => handleStartRename(s, e)}
                        className="p-1 hover:text-gray-900 text-gray-400"
                        title="Rename"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                    )}
                    <button
                      onClick={(e) => handleDeleteSession(s.id, e)}
                      className="p-1 hover:text-red-600 text-gray-400"
                      title="Delete"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Settings Footer */}
      <div className="p-3 border-t border-gray-100 mt-auto">
        <button
          onClick={onOpenSettings}
          className={`w-full py-2 px-3 rounded-xl text-xs font-semibold text-gray-600 hover:bg-gray-100 hover:text-gray-900 flex items-center gap-2.5 transition ${
            isCollapsed ? 'justify-center' : 'justify-start'
          }`}
          title="Settings"
        >
          <SettingsIcon className="w-4 h-4 text-gray-500 shrink-0" />
          {!isCollapsed && <span>Settings</span>}
        </button>
      </div>
    </aside>
  );
};
