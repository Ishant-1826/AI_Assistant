import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { PuzzleSolverView } from './components/PuzzleSolver/PuzzleSolverView';
import { AlgorithmLabView } from './components/AlgorithmLab/AlgorithmLabView';
import { StudyPlannerView } from './components/StudyPlanner/StudyPlannerView';
import { LearningAnalyticsView } from './components/LearningAnalytics/LearningAnalyticsView';
import { SettingsModal } from './components/SettingsModal';
import { ActiveTab, AppSettings } from './types';
import { Bot, Menu } from 'lucide-react';

const DEFAULT_SETTINGS: AppSettings = {
  llmProvider: 'auto',
  geminiApiKey: '',
  openaiApiKey: '',
  voiceGender: '',
  voiceRate: 1.0,
  autoSpeak: false,
  theme: 'light',
  enableWebSearch: true
};

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('chat');
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  // Settings from localStorage
  const [settings, setSettings] = useState<AppSettings>(() => {
    try {
      const saved = localStorage.getItem('campusmind_settings');
      return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS;
    } catch {
      return DEFAULT_SETTINGS;
    }
  });

  const handleSaveSettings = (newSettings: AppSettings) => {
    setSettings(newSettings);
    localStorage.setItem('campusmind_settings', JSON.stringify(newSettings));
  };

  // Create initial chat session if none exists
  const handleNewChat = async () => {
    try {
      const res = await fetch('/api/chat/sessions', { method: 'POST' });
      const data = await res.json();
      setCurrentSessionId(data.id);
      setActiveTab('chat');
      setMobileMenuOpen(false);
    } catch (e) {
      console.error('Error creating chat session', e);
      setCurrentSessionId(String(Date.now()));
    }
  };

  useEffect(() => {
    // Check existing sessions or create new
    fetch('/api/chat/sessions')
      .then(res => res.json())
      .then(sessions => {
        if (sessions && sessions.length > 0) {
          setCurrentSessionId(sessions[0].id);
        } else {
          handleNewChat();
        }
      })
      .catch(() => {
        handleNewChat();
      });
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#f8fafc] text-gray-800 font-sans">
      {/* Desktop & Tablet Sidebar */}
      <div className="hidden md:block shrink-0">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          currentSessionId={currentSessionId}
          onSelectSession={(id) => setCurrentSessionId(id)}
          onNewChat={handleNewChat}
          onOpenSettings={() => setIsSettingsOpen(true)}
        />
      </div>

      {/* Mobile Drawer Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 flex md:hidden">
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-xs"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative w-64 bg-white h-full z-50">
            <Sidebar
              activeTab={activeTab}
              setActiveTab={(t) => {
                setActiveTab(t);
                setMobileMenuOpen(false);
              }}
              currentSessionId={currentSessionId}
              onSelectSession={(id) => {
                setCurrentSessionId(id);
                setMobileMenuOpen(false);
              }}
              onNewChat={handleNewChat}
              onOpenSettings={() => {
                setIsSettingsOpen(true);
                setMobileMenuOpen(false);
              }}
            />
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Mobile Top Navbar */}
        <header className="md:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 shrink-0">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="p-1.5 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <Bot className="w-4 h-4" />
              </div>
              <span className="font-bold text-sm text-gray-900">CampusMind AI</span>
            </div>
          </div>
        </header>

        {/* View Switcher */}
        <main className="flex-1 overflow-y-auto">
          {activeTab === 'chat' && (
            <ChatInterface
              sessionId={currentSessionId}
              settings={settings}
            />
          )}

          {activeTab === 'puzzles' && <PuzzleSolverView />}

          {activeTab === 'algorithms' && <AlgorithmLabView />}

          {activeTab === 'planner' && <StudyPlannerView />}

          {activeTab === 'analytics' && <LearningAnalyticsView />}
        </main>
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        onSaveSettings={handleSaveSettings}
      />
    </div>
  );
}

export default App;
