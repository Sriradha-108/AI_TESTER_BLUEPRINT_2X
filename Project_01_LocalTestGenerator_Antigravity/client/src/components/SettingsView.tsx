import React, { useState, useEffect } from 'react';
import { Save, PlugZap } from 'lucide-react';
import axios from 'axios';

export default function SettingsView() {
  const [settings, setSettings] = useState({
    ollamaEndpoint: 'http://localhost:11434',
    lmStudioEndpoint: 'http://localhost:1234/v1',
    groqApiKey: '',
    openAIApiKey: '',
    claudeApiKey: '',
    geminiApiKey: ''
  });

  useEffect(() => {
    const saved = localStorage.getItem('ai_test_gen_settings');
    if (saved) {
      setSettings(JSON.parse(saved));
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSettings({ ...settings, [e.target.name]: e.target.value });
  };

  const testConnection = async (provider: string) => {
    try {
      const res = await axios.post('http://localhost:4000/api/test-connection', {
        provider: provider.toLowerCase().replace(' ', ''),
        settings
      });
      alert(res.data.message);
    } catch (error: any) {
      alert(`Connection failed: ${error.response?.data?.message || error.message}`);
    }
  };

  const saveSettings = () => {
    localStorage.setItem('ai_test_gen_settings', JSON.stringify(settings));
    alert("Settings saved successfully!");
  };

  return (
    <div className="p-6 md:p-10 max-w-3xl mx-auto w-full pt-20 md:pt-10">
      <h2 className="text-2xl font-bold mb-6 text-white">Target LLM Configurations</h2>
      <p className="text-slate-400 mb-8">Configure your local and cloud AI providers here. Local providers only require endpoints, while external providers require API keys.</p>

      <div className="space-y-6">
        {/* Local Settings */}
        <div className="bg-surface border border-slate-700/50 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-white mb-4">Local Providers (Free)</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Ollama API Endpoint</label>
              <div className="flex gap-2">
                <input type="text" name="ollamaEndpoint" value={settings.ollamaEndpoint} onChange={handleChange} className="input-field flex-1" />
                <button type="button" onClick={() => testConnection('ollama')} className="btn-secondary whitespace-nowrap"><PlugZap size={16} /> Test</button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">LM Studio API Endpoint</label>
              <div className="flex gap-2">
                <input type="text" name="lmStudioEndpoint" value={settings.lmStudioEndpoint} onChange={handleChange} className="input-field flex-1" />
                <button type="button" onClick={() => testConnection('lmstudio')} className="btn-secondary whitespace-nowrap"><PlugZap size={16} /> Test</button>
              </div>
            </div>
          </div>
        </div>

        {/* Cloud Settings */}
        <div className="bg-surface border border-slate-700/50 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-white mb-4">Cloud Providers (Paid)</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Groq API Key</label>
              <div className="flex gap-2">
                 <input type="password" name="groqApiKey" value={settings.groqApiKey} onChange={handleChange} placeholder="gsk_..." className="input-field flex-1" />
                 <button type="button" onClick={() => testConnection('groq')} className="btn-secondary whitespace-nowrap"><PlugZap size={16} /> Test</button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">OpenAI API Key</label>
              <div className="flex gap-2">
                 <input type="password" name="openAIApiKey" value={settings.openAIApiKey} onChange={handleChange} placeholder="sk-..." className="input-field flex-1" />
                 <button type="button" onClick={() => testConnection('openai')} className="btn-secondary whitespace-nowrap"><PlugZap size={16} /> Test</button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Claude (Anthropic) API Key</label>
              <div className="flex gap-2">
                 <input type="password" name="claudeApiKey" value={settings.claudeApiKey} onChange={handleChange} placeholder="sk-ant-..." className="input-field flex-1" />
                 <button type="button" onClick={() => testConnection('claude')} className="btn-secondary whitespace-nowrap"><PlugZap size={16} /> Test</button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Gemini API Key</label>
              <div className="flex gap-2">
                 <input type="password" name="geminiApiKey" value={settings.geminiApiKey} onChange={handleChange} placeholder="AIza..." className="input-field flex-1" />
                 <button type="button" onClick={() => testConnection('gemini')} className="btn-secondary whitespace-nowrap"><PlugZap size={16} /> Test</button>
              </div>
            </div>
          </div>
        </div>

        {/* Actions - Save */}
        <div className="flex justify-end pt-4">
          <button onClick={saveSettings} className="btn-primary w-full md:w-auto">
            <Save size={18} />
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
}
