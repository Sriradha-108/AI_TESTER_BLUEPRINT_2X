import React, { useState } from 'react';
import { Send, Bot, User, Code2 } from 'lucide-react';
import axios from 'axios';

export default function GeneratorView() {
  const [provider, setProvider] = useState('ollama');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', content: string}[]>([
    { role: 'assistant', content: 'Hello! Select your desired LLM Provider from the dropdown above, paste your Jira requirements here, and I will generate structured test cases for you.' }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input;
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setLoading(true);

    try {
      const savedSettings = localStorage.getItem('ai_test_gen_settings');
      const settings = savedSettings ? JSON.parse(savedSettings) : {};

      const response = await axios.post('http://localhost:4000/api/generate', {
        provider,
        requirement: userMessage,
        settings
      });

      setMessages(prev => [...prev, { role: 'assistant', content: response.data.tests }]);
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error generating tests: ${err.response?.data?.message || err.message}\nMake sure your backend is running and settings are saved.` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background relative pt-16 md:pt-0">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-700/50 bg-surface/50 backdrop-blur-md sticky top-0 z-10 flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Code2 className="text-primary" />
            Test Case Generation
          </h2>
          <p className="text-sm text-slate-400">Jira Formatted Outputs</p>
        </div>
        
        <div>
          <select 
             value={provider} 
             onChange={(e) => setProvider(e.target.value)}
             className="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5 outline-none"
          >
            <option value="ollama">Ollama (Local)</option>
            <option value="lmstudio">LM Studio (Local)</option>
            <option value="groq">Groq</option>
            <option value="openai">OpenAI</option>
            <option value="claude">Claude</option>
            <option value="gemini">Gemini</option>
          </select>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto w-full max-w-4xl mx-auto p-6 space-y-6 pb-32">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-primary' : 'bg-accent'}`}>
              {msg.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
            </div>
            
            <div className={`chat-bubble max-w-[85%] ${msg.role === 'user' ? 'bg-primary/10 border-primary/20 text-slate-200' : 'bg-surface border-slate-700/50 text-slate-300'}`}>
               <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed" style={{fontFamily: 'Consolas, Monaco, monospace'}}>
                 {msg.content}
               </pre>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center shrink-0">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-surface border-slate-700/50 p-4 rounded-xl shadow-sm text-slate-400 animate-pulse text-sm">
              Analyzing Jira requirements and generating tests via {provider}...
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-slate-700/50 bg-slate-900/90 backdrop-blur-md absolute bottom-0 w-full left-0 right-0">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="relative">
            <textarea
              className="input-field pr-12 min-h-[60px] resize-none pb-4"
              placeholder="Paste your Jira requirement here to generate test cases..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              rows={3}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="absolute right-3 bottom-3 p-2 bg-primary hover:bg-blue-600 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={18} />
            </button>
          </form>
          <div className="text-xs text-slate-500 mt-2 text-center">Press Enter to send, Shift + Enter for new line. Outputs will adhere strictly to Jira syntax.</div>
        </div>
      </div>
    </div>
  );
}
