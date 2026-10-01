import React from 'react';
import { LayoutDashboard, FileText, BarChart3, MessageSquareText, ShieldCheck } from 'lucide-react';

export default function Header({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'dashTab', label: 'System Overview', icon: LayoutDashboard },
    { id: 'formTab', label: 'Loan Application', icon: FileText },
    { id: 'resultTab', label: 'AI Rationale & Output', icon: BarChart3 },
    { id: 'ragTab', label: 'Policy AI Assistant', icon: MessageSquareText },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-6 py-3 shadow-sm transition-all">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand Container */}
        <div 
          onClick={() => {
            setActiveTab('dashTab');
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
          className="react-bits-shine group inline-flex items-center gap-3 px-3.5 py-1.5 bg-white/90 backdrop-blur-md border border-slate-200 rounded-2xl shadow-xs cursor-pointer hover:-translate-y-0.5 hover:border-indigo-300 hover:shadow-md transition-all duration-200"
        >
          <div className="h-16 w-auto flex items-center justify-center overflow-hidden">
            <img src="/loan_iq_logo.gif" alt="LOAN-IQ Logo GIF" className="h-16 w-auto object-contain drop-shadow-md" />
          </div>
          <div className="flex items-center font-heading text-2xl font-black text-slate-900 tracking-tight ml-1">
            LOAN-<span className="text-blue-600">IQ</span>
          </div>
          <div className="hidden sm:block w-px h-4 bg-slate-200 mx-0.5" />
          <span className="hidden sm:block text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Loan Intelligence
          </span>
        </div>

        {/* Navigation Tabs Switcher */}
        <nav className="flex items-center gap-1 bg-slate-100/80 p-1 rounded-xl border border-slate-200/80">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg font-heading text-xs font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-white text-indigo-600 font-bold shadow-xs'
                    : 'text-slate-500 hover:text-slate-900 hover:bg-white/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

      </div>
    </header>
  );
}
