import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Settings, MessageSquare, Menu, X } from 'lucide-react';
import GeneratorView from './components/GeneratorView';
import SettingsView from './components/SettingsView';

function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  return (
    <div className="flex h-screen w-full bg-slate-900 text-slate-100 font-sans overflow-hidden">
      {/* Mobile Sidebar Toggle */}
      <div className="md:hidden absolute z-50 p-4">
        <button className="text-white focus:outline-none" onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`fixed md:relative z-40 bg-surface w-64 h-full border-r border-slate-700/50 flex flex-col transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="p-6">
          <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">AI TestGen</h1>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          <Link to="/" className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${location.pathname === '/' ? 'bg-slate-700/50 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-700/30'}`}>
            <MessageSquare size={20} />
            <span className="font-medium">Generator</span>
          </Link>
          <Link to="/settings" className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${location.pathname === '/settings' ? 'bg-slate-700/50 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-700/30'}`}>
            <Settings size={20} />
            <span className="font-medium">Settings</span>
          </Link>
        </nav>

        {/* Local History Section */}
        <div className="p-4 border-t border-slate-700/50 flex-1 overflow-y-auto">
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">History</h3>
          <div className="space-y-2">
            {/* Dummy History Items */}
            <div className="text-sm text-slate-400 truncate hover:text-white cursor-pointer py-1">Login API tests</div>
            <div className="text-sm text-slate-400 truncate hover:text-white cursor-pointer py-1">Register web test</div>
            <div className="text-sm text-slate-400 truncate hover:text-white cursor-pointer py-1">Payment failure E2E</div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto w-full md:w-auto h-full relative">
        <Routes>
          <Route path="/" element={<GeneratorView />} />
          <Route path="/settings" element={<SettingsView />} />
        </Routes>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AppLayout />
    </Router>
  );
}
