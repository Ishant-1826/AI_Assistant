import React, { useState, useEffect } from 'react';
import { X, Volume2, Key, Moon, Sun, CheckCircle, ShieldAlert, Cpu } from 'lucide-react';
import { AppSettings } from '../types';
import { voiceOutput } from '../utils/voice';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: AppSettings;
  onSaveSettings: (newSettings: AppSettings) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  settings,
  onSaveSettings
}) => {
  const [formData, setFormData] = useState<AppSettings>(settings);
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [backendStatus, setBackendStatus] = useState<any>(null);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  useEffect(() => {
    setFormData(settings);
  }, [settings]);

  useEffect(() => {
    if (voiceOutput.isSupported) {
      const loadVoices = () => {
        const v = voiceOutput.getVoices();
        setAvailableVoices(v);
      };
      loadVoices();
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
      }
    }

    // Check backend LLM status
    fetch('/api/chat/config')
      .then(res => res.json())
      .then(data => setBackendStatus(data))
      .catch(() => {});
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = () => {
    onSaveSettings(formData);
    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      onClose();
    }, 1000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
      <div className="bg-white rounded-3xl shadow-xl border border-gray-200 max-w-lg w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-gray-900 text-base">CampusMind Settings</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-full transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto text-xs">
          {/* Section 1: LLM Provider Configuration */}
          <div className="space-y-3">
            <h4 className="font-bold text-gray-800 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
              <Key className="w-4 h-4 text-amber-500" />
              LLM Provider & API Keys
            </h4>
            <p className="text-gray-500 text-[11px]">
              Keys are stored securely in your browser&apos;s local storage and used directly for your requests. If no key is set, the built-in educational tutor engine handles all queries with full algorithm integration.
            </p>

            <div className="space-y-2.5">
              <div>
                <label className="block text-gray-700 font-semibold mb-1">Default Provider</label>
                <select
                  value={formData.llmProvider}
                  onChange={(e) => setFormData({ ...formData, llmProvider: e.target.value as any })}
                  className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-xl text-gray-800 font-medium focus:outline-none"
                >
                  <option value="auto">Auto (Detects Available Key / Fallback)</option>
                  <option value="gemini">Google Gemini (Gemini 2.5 Flash)</option>
                  <option value="openai">OpenAI (GPT-4o Mini)</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-1">Google Gemini API Key</label>
                <input
                  type="password"
                  placeholder="AIzaSy..."
                  value={formData.geminiApiKey}
                  onChange={(e) => setFormData({ ...formData, geminiApiKey: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-xl text-gray-800 font-mono focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-1">OpenAI API Key</label>
                <input
                  type="password"
                  placeholder="sk-..."
                  value={formData.openaiApiKey}
                  onChange={(e) => setFormData({ ...formData, openaiApiKey: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-xl text-gray-800 font-mono focus:outline-none"
                />
              </div>

              <label className="flex items-center gap-2 cursor-pointer pt-1">
                <input
                  type="checkbox"
                  checked={formData.enableWebSearch}
                  onChange={(e) => setFormData({ ...formData, enableWebSearch: e.target.checked })}
                  className="accent-blue-600 rounded"
                />
                <span className="text-gray-800 font-medium">Enable real-time Google Search grounding by default</span>
              </label>

              {backendStatus && (
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-200 text-[11px] text-gray-600 space-y-1">
                  <span className="font-bold text-gray-700 block">Server Status:</span>
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${backendStatus.gemini_configured ? 'bg-emerald-500' : 'bg-gray-400'}`} />
                    <span>Gemini Server Key: {backendStatus.gemini_configured ? 'Configured' : 'Not set'}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${backendStatus.openai_configured ? 'bg-emerald-500' : 'bg-gray-400'}`} />
                    <span>OpenAI Server Key: {backendStatus.openai_configured ? 'Configured' : 'Not set'}</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Section 2: Voice Output (SpeechSynthesis) */}
          <div className="space-y-3 pt-4 border-t border-gray-100">
            <h4 className="font-bold text-gray-800 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
              <Volume2 className="w-4 h-4 text-blue-600" />
              Voice Assistant Settings (Web Speech API)
            </h4>

            <div className="space-y-3">
              <div>
                <label className="block text-gray-700 font-semibold mb-1">Preferred Voice</label>
                <select
                  value={formData.voiceGender}
                  onChange={(e) => setFormData({ ...formData, voiceGender: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-xl text-gray-800 focus:outline-none truncate"
                >
                  <option value="">Default System Voice</option>
                  {availableVoices.map((v, i) => (
                    <option key={i} value={v.name}>
                      {v.name} ({v.lang})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <div className="flex justify-between font-semibold text-gray-700 mb-1">
                  <span>Speech Rate</span>
                  <span className="text-blue-600 font-bold">{formData.voiceRate}x</span>
                </div>
                <input
                  type="range"
                  min="0.75"
                  max="1.75"
                  step="0.1"
                  value={formData.voiceRate}
                  onChange={(e) => setFormData({ ...formData, voiceRate: Number(e.target.value) })}
                  className="w-full accent-blue-600 cursor-pointer"
                />
              </div>

              <label className="flex items-center gap-2 cursor-pointer pt-1">
                <input
                  type="checkbox"
                  checked={formData.autoSpeak}
                  onChange={(e) => setFormData({ ...formData, autoSpeak: e.target.checked })}
                  className="accent-blue-600 rounded"
                />
                <span className="text-gray-800 font-medium">Automatically speak new AI assistant replies aloud</span>
              </label>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-gray-50 border-t border-gray-100 flex items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 text-xs font-semibold rounded-xl hover:bg-gray-200 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-sm transition flex items-center gap-1.5"
          >
            {savedSuccess ? <CheckCircle className="w-3.5 h-3.5" /> : null}
            {savedSuccess ? 'Saved!' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};
