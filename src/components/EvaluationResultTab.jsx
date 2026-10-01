import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { CheckCircle2, XCircle, AlertCircle, MessageSquareText } from 'lucide-react';

// Register ChartJS modules
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function EvaluationResultTab({ assessmentResult, setActiveTab, sendQuickChatQuery }) {
  if (!assessmentResult) {
    return (
      <div className="react-bits-glass rounded-3xl p-12 text-center space-y-4 max-w-xl mx-auto my-12 animate-fadeIn">
        <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto shadow-xs">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h3 className="font-heading text-xl font-extrabold text-slate-900">Awaiting Evaluation Data</h3>
        <p className="text-sm text-slate-500">
          Please complete applicant parameters in the Loan Application form and submit to generate AI risk assessment results.
        </p>
        <button
          onClick={() => setActiveTab('formTab')}
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-heading font-bold text-xs shadow-md hover:shadow-indigo-500/25 transition-all"
        >
          Go to Application Form
        </button>
      </div>
    );
  }

  const { payload, data } = assessmentResult;
  const isApproved = data.approved;

  // Prepare SHAP chart data
  const shapLabels = (data.shap?.labels || []).map((l) => l.replace(/_/g, ' '));
  const shapValues = data.shap?.values || [];

  const chartData = {
    labels: shapLabels,
    datasets: [
      {
        data: shapValues,
        backgroundColor: shapValues.map((v) => (v >= 0 ? '#10B981' : '#F43F5E')),
        borderRadius: 6,
      },
    ],
  };

  const chartOptions = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      x: { ticks: { color: '#64748B' }, grid: { color: 'rgba(226, 232, 240, 0.8)' } },
      y: { ticks: { color: '#0F172A', font: { weight: '600' } }, grid: { display: false } },
    },
  };

  const handleAskAIClick = () => {
    const query = `Why was the ${payload.bank} ${payload.loan_type} application ${isApproved ? 'Approved' : 'Rejected'} for ${payload.tn_city} with CIBIL ${payload.cibil} and FOIR ${data.foir}%?`;
    sendQuickChatQuery(query);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Decision Banner */}
      <div
        className={`rounded-3xl p-6 sm:p-8 text-center border shadow-md transition-all ${
          isApproved
            ? 'bg-emerald-50/90 border-emerald-200 text-emerald-900'
            : 'bg-rose-50/90 border-rose-200 text-rose-900'
        }`}
      >
        <div className="inline-flex items-center gap-2 mb-2">
          {isApproved ? (
            <CheckCircle2 className="w-8 h-8 text-emerald-600" />
          ) : (
            <XCircle className="w-8 h-8 text-rose-600" />
          )}
          <h2 className="font-heading text-2xl sm:text-3xl font-black uppercase tracking-tight">
            {isApproved ? 'LOAN APPLICATION APPROVED' : 'LOAN APPLICATION REJECTED'}
          </h2>
        </div>

        <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto">
          Application {isApproved ? 'satisfies underwriting criteria' : 'breaches risk policy thresholds'} for{' '}
          <strong className="font-bold text-slate-900">{payload.bank} {payload.loan_type}</strong>. AI Score: <strong className="font-bold">{data.probability}%</strong>
        </p>

        <button
          onClick={handleAskAIClick}
          className="mt-4 inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-heading font-bold text-xs shadow-md hover:shadow-indigo-500/25 transition-all"
        >
          <MessageSquareText className="w-3.5 h-3.5" />
          <span>Ask AI Assistant Why This Result Was Returned</span>
        </button>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="react-bits-glass rounded-2xl p-5 text-center">
          <div className="text-xs font-heading font-bold uppercase tracking-wider text-slate-500 mb-1">
            AI Approval Probability
          </div>
          <div className="font-mono text-2xl sm:text-3xl font-extrabold text-indigo-600">
            {data.probability || 0}%
          </div>
          <div className="text-xs text-slate-400 mt-1">Stacking Ensemble Score</div>
        </div>

        <div className="react-bits-glass rounded-2xl p-5 text-center">
          <div className="text-xs font-heading font-bold uppercase tracking-wider text-slate-500 mb-1">
            Calculated FOIR Ratio
          </div>
          <div className="font-mono text-2xl sm:text-3xl font-extrabold text-indigo-600">
            {data.foir || 0}%
          </div>
          <div className="text-xs text-slate-400 mt-1">Max Threshold: 65.0%</div>
        </div>

        <div className="react-bits-glass rounded-2xl p-5 text-center">
          <div className="text-xs font-heading font-bold uppercase tracking-wider text-slate-500 mb-1">
            Calculated LTV Ratio
          </div>
          <div className="font-mono text-2xl sm:text-3xl font-extrabold text-indigo-600">
            {data.ltv !== undefined ? `${data.ltv}%` : 'N/A'}
          </div>
          <div className="text-xs text-slate-400 mt-1">Max Threshold: 90.0%</div>
        </div>

        <div className="react-bits-glass rounded-2xl p-5 text-center">
          <div className="text-xs font-heading font-bold uppercase tracking-wider text-slate-500 mb-1">
            Proposed Monthly EMI
          </div>
          <div className="font-mono text-2xl sm:text-3xl font-extrabold text-indigo-600">
            ₹ {Math.round(data.proposed_emi || 0).toLocaleString('en-IN')}
          </div>
          <div className="text-xs text-slate-400 mt-1">Tenure: {payload.tenure_mo} mos</div>
        </div>
      </div>

      {/* SHAP Chart & Checklist Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* SHAP Chart Card */}
        <div className="react-bits-glass rounded-3xl p-6 space-y-4">
          <div>
            <h3 className="font-heading text-lg font-extrabold text-slate-900">
              Explainable AI Rationale (SHAP Waterfall Attribution)
            </h3>
            <p className="text-xs text-slate-500">
              Green bars push toward Approval | Red bars push toward Rejection
            </p>
          </div>
          <div className="h-80 relative">
            <Bar data={chartData} options={chartOptions} />
          </div>
        </div>

        {/* Audit Checklist & Recommendations */}
        <div className="space-y-6">
          
          <div className="react-bits-glass rounded-3xl p-6 space-y-4">
            <h3 className="font-heading text-lg font-extrabold text-slate-900">
              Institutional Policy Audit Checklist
            </h3>
            
            <div className="space-y-2">
              {(data.violations || []).length === 0 ? (
                <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Passed: All mandatory policy rules satisfied (Age, CIBIL, FOIR, LTV caps met).</span>
                </div>
              ) : (
                (data.violations || []).map((v, i) => (
                  <div key={i} className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs font-semibold flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
                    <span>Breached Policy Rule: {v}</span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="react-bits-glass rounded-3xl p-6 space-y-4">
            <h3 className="font-heading text-lg font-extrabold text-slate-900">
              Decision Insights & Recommendations
            </h3>
            
            <div className="space-y-2.5">
              {(data.recommendations || []).map((rec, i) => {
                const cleanRec = rec.replace(/^[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}•\-\*]\s*/gu, '');
                return (
                  <div
                    key={i}
                    className="p-3.5 rounded-xl bg-white/90 border border-slate-200 border-l-4 border-l-emerald-500 text-slate-700 text-xs leading-relaxed"
                    dangerouslySetInnerHTML={{
                      __html: cleanRec.replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-900 font-bold">$1</strong>'),
                    }}
                  />
                );
              })}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
