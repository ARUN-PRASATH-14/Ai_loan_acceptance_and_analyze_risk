import React, { useState } from 'react';
import Header from './components/Header';
import BackgroundBackdrop from './components/BackgroundBackdrop';
import OverviewTab from './components/OverviewTab';
import ApplicationFormTab from './components/ApplicationFormTab';
import EvaluationResultTab from './components/EvaluationResultTab';
import PolicyAssistantTab from './components/PolicyAssistantTab';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashTab');
  const [assessmentResult, setAssessmentResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [quickQuery, setQuickQuery] = useState('');

  const sendQuickChatQuery = (query) => {
    setQuickQuery(query);
    setActiveTab('ragTab');
  };

  return (
    <div className="min-h-screen flex flex-col relative font-sans text-slate-900">
      
      {/* Refresh Bank Image & Gradient Backdrop */}
      <BackgroundBackdrop />

      {/* Navigation Header */}
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Workspace View Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeTab === 'dashTab' && (
          <OverviewTab setActiveTab={setActiveTab} />
        )}

        {activeTab === 'formTab' && (
          <ApplicationFormTab
            setActiveTab={setActiveTab}
            setAssessmentResult={setAssessmentResult}
            setIsLoading={setIsLoading}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'resultTab' && (
          <EvaluationResultTab
            assessmentResult={assessmentResult}
            setActiveTab={setActiveTab}
            sendQuickChatQuery={sendQuickChatQuery}
          />
        )}

        {activeTab === 'ragTab' && (
          <PolicyAssistantTab
            quickQuery={quickQuery}
            assessmentResult={assessmentResult}
          />
        )}
      </main>

    </div>
  );
}
