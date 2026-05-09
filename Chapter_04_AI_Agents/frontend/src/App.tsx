import React, { useState } from 'react';
import { Settings, Target, ClipboardList, PenLine, ChevronRight, Activity, CheckCircle2, AlertCircle } from 'lucide-react';

function App() {
  const [activeStep, setActiveStep] = useState(1);
  const [connectionData, setConnectionData] = useState({ url: '', email: '', token: '' });
  const [llmProvider, setLlmProvider] = useState('Groq');
  const [llmKey, setLlmKey] = useState('');
  
  const [fetchData, setFetchData] = useState({ projectName: '', projectKey: '', context: '' });
  
  const [testPlan, setTestPlan] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const steps = [
    { id: 1, label: '1. Setup Connections' },
    { id: 2, label: '2. Fetch Issues' },
    { id: 3, label: '3. Review' },
    { id: 4, label: '4. Test Plan' }
  ];

  const handleFetchJira = async () => {
    setActiveStep(3);
  };

  const handleGeneratePlan = async () => {
    setIsGenerating(true);
    // Simulate generation delay
    setTimeout(() => {
      setTestPlan("# Generated Test Plan\n\n## Scope\nBased on Jira issue... ");
      setIsGenerating(false);
      setActiveStep(4);
    }, 2000);
  };

  return (
    <div className="w-full flex justify-center p-8">
      <div className="max-w-4xl w-full flex flex-col gap-6 animate-fade-in">
        
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white rounded-xl shadow-sm text-primary">
              <Target size={32} />
            </div>
            <div>
              <h1 className="text-2xl font-semibold">Intelligent Test Planning Agent</h1>
              <p className="text-muted text-sm mt-1">Generate comprehensive test plans from Jira requirements using AI</p>
            </div>
          </div>
          <button className="btn btn-outline">View History</button>
        </header>

        <div className="stepper">
          {steps.map(step => (
            <div 
              key={step.id} 
              className={`step-item ${activeStep === step.id ? 'active' : ''} ${activeStep > step.id ? 'text-primary' : ''}`}
              onClick={() => setActiveStep(step.id)}
            >
              {step.label}
            </div>
          ))}
        </div>

        {activeStep === 1 && (
          <div className="glass-panel p-8 flex flex-col gap-8 animate-slide-in">
            <div>
              <h2 className="text-xl mb-1">ALM Integration (Jira)</h2>
              <p className="text-muted text-sm mb-6">Connect to your Jira instance to fetch user stories.</p>
              
              <div className="flex flex-col gap-4 max-w-xl">
                <div className="input-group">
                  <label className="input-label">Jira URL</label>
                  <input type="text" className="input-field" placeholder="https://yourcompany.atlassian.net" value={connectionData.url} onChange={e => setConnectionData({...connectionData, url: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Jira Email</label>
                  <input type="email" className="input-field" placeholder="you@example.com" value={connectionData.email} onChange={e => setConnectionData({...connectionData, email: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">API Token</label>
                  <input type="password" className="input-field" placeholder="••••••••••••" value={connectionData.token} onChange={e => setConnectionData({...connectionData, token: e.target.value})}/>
                </div>
              </div>
            </div>

            <hr style={{ borderColor: 'hsla(var(--border) / 1)' }} />

            <div>
              <h2 className="text-xl mb-1">LLM Configuration</h2>
              <p className="text-muted text-sm mb-6">Select the AI engine for generating your test plans.</p>
              
              <div className="flex flex-col gap-4 max-w-xl">
                <div className="input-group">
                  <label className="input-label">Provider</label>
                  <select className="input-field" value={llmProvider} onChange={e => setLlmProvider(e.target.value)}>
                    <option>Groq</option>
                    <option>Ollama</option>
                    <option>OpenAI</option>
                  </select>
                </div>
                <div className="input-group">
                  <label className="input-label">API Key</label>
                  <input type="password" className="input-field" placeholder="your_api_key" value={llmKey} onChange={e => setLlmKey(e.target.value)} />
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <button className="btn btn-primary" onClick={() => setActiveStep(2)}>
                Save Connections <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}

        {activeStep === 2 && (
          <div className="glass-panel p-8 flex flex-col gap-6 animate-slide-in">
             <h2 className="text-xl mb-1">Fetch Requirements</h2>
             <p className="text-muted text-sm mb-6">Specify the product details and user story ID you want to build a plan for.</p>
             
             <div className="grid grid-cols-2 gap-6">
               <div className="input-group">
                  <label className="input-label">Product Name</label>
                  <input type="text" className="input-field" placeholder="e.g. VWO Web App" value={fetchData.projectName} onChange={e => setFetchData({...fetchData, projectName: e.target.value})} />
               </div>
               <div className="input-group">
                  <label className="input-label">Project Key / Sprint ID</label>
                  <input type="text" className="input-field" placeholder="e.g. VWOAPP-1" value={fetchData.projectKey} onChange={e => setFetchData({...fetchData, projectKey: e.target.value})} />
               </div>
             </div>
             
             <div className="input-group">
                <label className="input-label">Additional Context (Optional)</label>
                <textarea className="input-field" placeholder="Any special rules, focus areas, or edge cases the AI should consider..." value={fetchData.context} onChange={e => setFetchData({...fetchData, context: e.target.value})}></textarea>
             </div>

             <div className="flex justify-end pt-4">
              <button className="btn btn-primary" onClick={handleFetchJira}>
                Fetch Jira Issue <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}

        {activeStep === 3 && (
          <div className="glass-panel p-8 flex flex-col gap-6 animate-slide-in">
             <div className="flex items-center gap-3 text-success mb-4">
               <CheckCircle2 size={24} />
               <h2 className="text-xl">Requirements Fetched</h2>
             </div>
             
             <div className="glass-card p-6 border-success bg-green-50/30">
               <h3 className="font-semibold mb-2">Issue: {fetchData.projectKey || "KAN-1"}</h3>
               <p className="text-muted text-sm line-clamp-2">Summary retrieved from Jira ALM dynamically based on the configuration.</p>
             </div>

             <div className="flex justify-between items-center pt-8">
              <button className="btn btn-ghost" onClick={() => setActiveStep(2)}>Back</button>
              <button className="btn btn-primary" onClick={handleGeneratePlan} disabled={isGenerating}>
                {isGenerating ? <><Activity size={16} className="animate-spin" /> Generating Plan...</> : <><PenLine size={16} /> Generate Test Plan</>}
              </button>
            </div>
          </div>
        )}

        {activeStep === 4 && (
          <div className="glass-panel p-8 flex flex-col items-center justify-center min-h-[400px] animate-slide-in">
             {!testPlan ? (
               <div className="flex flex-col items-center gap-4 text-muted">
                 <ClipboardList size={48} opacity={0.5} />
                 <h2 className="text-xl text-text-main">No test plan generated yet</h2>
                 <p className="text-sm">Complete the previous steps to generate your test plan</p>
               </div>
             ) : (
               <div className="w-full h-full flex flex-col">
                 <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold flex items-center gap-2"><CheckCircle2 size={20} className="text-success" /> Generated Test Plan</h2>
                    <button className="btn btn-outline">Export to Jira / PDF</button>
                 </div>
                 <div className="glass-card p-6 bg-white flex-1 overflow-auto whitespace-pre-wrap font-mono text-sm">
                   {testPlan}
                 </div>
               </div>
             )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
