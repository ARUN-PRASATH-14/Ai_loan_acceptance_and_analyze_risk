import React from 'react';
import { ArrowRight, BookOpen, ShieldCheck, Cpu, Database, Award } from 'lucide-react';

export default function OverviewTab({ setActiveTab }) {
  const supportedBanks = [
    { name: 'State Bank of India', desc: 'SBI Home & Personal Rules' },
    { name: 'HDFC Bank', desc: 'Strict NTC & FOIR Caps' },
    { name: 'ICICI Bank', desc: 'LTV 85% & Tier Norms' },
    { name: 'Indian Overseas Bank', desc: 'IOB Agriculture & Home' },
    { name: 'Canara Bank', desc: 'Tier 2/3 Regional Rules' },
    { name: 'General RBI Mode', desc: 'Baseline Regulatory Rules' },
  ];

  const glossaryTerms = [
    { term: 'CIBIL', name: 'Credit Information Bureau (India) Limited', def: "A 3-digit numerical score (300–900) rating an applicant's past credit repayment history. Scores above 700 indicate strong creditworthiness." },
    { term: 'FOIR', name: 'Fixed Obligation to Income Ratio', def: 'Percentage of monthly income spent paying total loan EMIs. Banks cap FOIR at 60%–65% to prevent over-indebtedness.' },
    { term: 'LTV', name: 'Loan to Value Ratio', def: 'Ratio of the sanctioned loan amount to the market appraised value of the collateral property. RBI maximum baseline is 90%.' },
    { term: 'EMI', name: 'Equated Monthly Installment', def: 'Fixed monthly amount paid by a borrower to clear loan principal and interest over the agreed tenure.' },
    { term: 'DTI', name: 'Debt to Income Ratio', def: 'Comparison of total recurring monthly debt liabilities against gross monthly income. Lower DTI represents safer credit risk.' },
    { term: 'NTC', name: 'New to Credit', def: 'An applicant borrowing for the first time with 0 prior credit history (No existing CIBIL score).' },
    { term: 'NPA', name: 'Non-Performing Asset', def: 'Loans in default or arrears where EMI repayments have not been paid for 90+ consecutive days.' },
    { term: 'Tenure', name: 'Loan Repayment Tenure', def: 'Total time period (in months/years) granted by the bank to repay the entire loan amount.' },
    { term: 'Collateral', name: 'Asset Security / Pledge', def: 'Property, gold, or assets pledged by the borrower as security against loan default.' },
    { term: 'Principal', name: 'Original Loan Sum', def: 'The original base amount borrowed from the bank, excluding interest charges.' },
    { term: 'Moratorium', name: 'Repayment Holiday Period', def: 'A temporary period during which the borrower is legally permitted to pause EMI payments (e.g., student studies).' },
    { term: 'Prepayment', name: 'Early Loan Closure Penalty', def: 'Settling part or all of the loan before the scheduled maturity date.' },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Hero Glass Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-indigo-200/80 bg-gradient-to-br from-white/90 via-indigo-50/50 to-slate-50/80 p-8 sm:p-10 shadow-xl backdrop-blur-xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />
        
        <div className="relative z-10 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100/80 border border-indigo-200 text-indigo-700 text-xs font-bold uppercase tracking-wider">
            <Cpu className="w-3.5 h-3.5" />
            <span>Autonomous Banking Intelligence Platform</span>
          </div>

          <h1 className="font-heading text-3xl sm:text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Loan Approval & Risk Analyzer{' '}
            <span className="bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">
              / Multi-Bank Policy System
            </span>
          </h1>

          <p className="text-slate-600 text-base sm:text-lg max-w-3xl leading-relaxed">
            Enterprise credit risk assessment platform integrating 2-tier Stacking Ensemble Machine Learning, 
            Explainable AI (SHAP), and Vector-Indexed Policy RAG across commercial banks (SBI, HDFC, ICICI, IOB, Canara Bank).
          </p>

          <div className="flex flex-wrap gap-3 pt-2">
            <button
              onClick={() => setActiveTab('formTab')}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-heading font-bold text-sm shadow-md hover:shadow-indigo-500/25 hover:-translate-y-0.5 transition-all"
            >
              <span>Evaluate Loan Application</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                const el = document.getElementById('glossarySection');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white border border-slate-200 text-slate-700 font-heading font-semibold text-sm shadow-xs hover:bg-slate-50 transition-all"
            >
              <BookOpen className="w-4 h-4 text-slate-500" />
              <span>Technical Glossary</span>
            </button>
          </div>
        </div>
      </div>

      {/* Supported Institutional Manuals */}
      <div className="space-y-4">
        <h3 className="font-heading text-xs font-bold text-slate-900 uppercase tracking-widest">
          Supported Institutional Policy Manuals
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {supportedBanks.map((bank, i) => (
            <div key={i} className="react-bits-glass p-4 rounded-2xl text-center space-y-1 group">
              <h5 className="font-heading text-sm font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                {bank.name}
              </h5>
              <p className="text-xs text-slate-500">{bank.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Technical Glossary Dictionary Table */}
      <div id="glossarySection" className="react-bits-glass rounded-3xl p-6 sm:p-8 space-y-6">
        <div>
          <h3 className="font-heading text-xl font-extrabold text-slate-900">
            Loan Parameters & Technical Dictionary
          </h3>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Standard industry definitions of banking parameters, risk metrics, and machine learning components.
          </p>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-slate-200/80">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-slate-100/70 border-b border-slate-200 text-slate-500 font-heading font-bold text-xs uppercase tracking-wider">
              <tr>
                <th className="p-3.5">Term</th>
                <th className="p-3.5">Full Parameter Name</th>
                <th className="p-3.5">Technical Definition</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/60 bg-white/60">
              {glossaryTerms.map((item, i) => (
                <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                  <td className="p-3.5 whitespace-nowrap">
                    <span className="font-mono text-xs font-bold text-indigo-600 bg-indigo-50 border border-indigo-200/80 px-2.5 py-1 rounded-md">
                      {item.term}
                    </span>
                  </td>
                  <td className="p-3.5 font-medium text-slate-800">{item.name}</td>
                  <td className="p-3.5 text-slate-600 leading-relaxed">{item.def}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
