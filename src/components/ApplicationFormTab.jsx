import React, { useState } from 'react';
import { Send, Sparkles, Building2, User, Landmark, DollarSign, Calculator } from 'lucide-react';
import { evaluateApplication } from '../services/api';

export default function ApplicationFormTab({ setActiveTab, setAssessmentResult, setIsLoading, isLoading }) {
  const [formData, setFormData] = useState({
    bank: 'SBI',
    loan_type: 'Home Loan',
    tn_city: 'Coimbatore (Tier 2)',
    employer: 'Tier B (Mid-Size)',
    income: 1200000,
    co_app_inc: 300000,
    loan_amt: 5000000,
    tenure_mo: 240,
    cibil: 780,
    exist_emi: 15000,
    age: 35,
    gender: 'Male',
    emp_type: 'Salaried',
    prop_val: 6500000,
    existing_customer: false,
    is_ntc: false,
  });

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleNTCToggle = (e) => {
    const isChecked = e.target.checked;
    setFormData((prev) => ({
      ...prev,
      is_ntc: isChecked,
      cibil: isChecked ? 0 : 750,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const data = await evaluateApplication(formData);
      setAssessmentResult({ payload: formData, data });
      setActiveTab('resultTab');
    } catch (err) {
      alert('Error connecting to assessment server: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div>
        <h2 className="font-heading text-2xl font-extrabold text-slate-900">
          Applicant Parameters & Loan Request Form
        </h2>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Input financial parameters to execute the Stacking Ensemble ML Model and Policy Audit Engine.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Parameters Left Column */}
        <div className="lg:col-span-2 react-bits-glass rounded-3xl p-6 sm:p-8 space-y-6">
          
          {/* Section 1 */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-200 text-xs font-heading font-extrabold text-indigo-600 uppercase tracking-widest">
              <Landmark className="w-4 h-4" />
              <span>1. Target Institution & Scheme Selection</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Target Bank / Policy Mode
                </label>
                <select
                  value={formData.bank}
                  onChange={(e) => handleChange('bank', e.target.value)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                >
                  <option value="SBI">State Bank of India (SBI)</option>
                  <option value="HDFC">HDFC Bank</option>
                  <option value="ICICI">ICICI Bank</option>
                  <option value="IOB">Indian Overseas Bank (IOB)</option>
                  <option value="Canara">Canara Bank</option>
                  <option value="General RBI">General RBI Baseline Mode</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Loan Category
                </label>
                <select
                  value={formData.loan_type}
                  onChange={(e) => handleChange('loan_type', e.target.value)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                >
                  <option value="Home Loan">Home Loan</option>
                  <option value="Personal Loan">Personal Loan</option>
                  <option value="Education Loan">Education Loan</option>
                  <option value="Agriculture/KCC">Agriculture / KCC Loan</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Location (Tamil Nadu Region)
                </label>
                <select
                  value={formData.tn_city}
                  onChange={(e) => handleChange('tn_city', e.target.value)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                >
                  <option value="Chennai (Tier 1)">Chennai (Tier 1)</option>
                  <option value="Coimbatore (Tier 2)">Coimbatore (Tier 2)</option>
                  <option value="Madurai (Tier 2)">Madurai (Tier 2)</option>
                  <option value="Trichy (Tier 2)">Trichy (Tier 2)</option>
                  <option value="Salem (Tier 2)">Salem (Tier 2)</option>
                  <option value="Vellore (Tier 3)">Vellore (Tier 3)</option>
                  <option value="Rural TN (Tier 3)">Rural TN (Tier 3)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Employer Category
                </label>
                <select
                  value={formData.employer}
                  onChange={(e) => handleChange('employer', e.target.value)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                >
                  <option value="Tier A (Top MNC)">Tier A (Top MNC / Govt)</option>
                  <option value="Tier B (Mid-Size)">Tier B (Mid-Size Firm)</option>
                  <option value="Tier C (Small)">Tier C (Small Business)</option>
                  <option value="Unlisted/Startup">Unlisted / Startup</option>
                  <option value="Not Applicable">Not Applicable</option>
                </select>
              </div>
            </div>
          </div>

          {/* Section 2 */}
          <div className="space-y-4 pt-2">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-200 text-xs font-heading font-extrabold text-indigo-600 uppercase tracking-widest">
              <DollarSign className="w-4 h-4" />
              <span>2. Applicant Financial Telemetry</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Annual Income (₹)
                </label>
                <input
                  type="number"
                  value={formData.income}
                  step="50000"
                  onChange={(e) => handleChange('income', parseFloat(e.target.value) || 0)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Co-Applicant Income (₹)
                </label>
                <input
                  type="number"
                  value={formData.co_app_inc}
                  step="50000"
                  onChange={(e) => handleChange('co_app_inc', parseFloat(e.target.value) || 0)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Requested Amount (₹)
                </label>
                <input
                  type="number"
                  value={formData.loan_amt}
                  step="100000"
                  onChange={(e) => handleChange('loan_amt', parseFloat(e.target.value) || 0)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Tenure (Months)
                </label>
                <input
                  type="number"
                  value={formData.tenure_mo}
                  step="12"
                  onChange={(e) => handleChange('tenure_mo', parseInt(e.target.value) || 12)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  CIBIL Credit Score (300-900)
                </label>
                <input
                  type="number"
                  value={formData.cibil}
                  min="0"
                  max="900"
                  disabled={formData.is_ntc}
                  onChange={(e) => handleChange('cibil', parseInt(e.target.value) || 0)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 disabled:bg-slate-100 disabled:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Existing Monthly EMIs (₹)
                </label>
                <input
                  type="number"
                  value={formData.exist_emi}
                  step="1000"
                  onChange={(e) => handleChange('exist_emi', parseFloat(e.target.value) || 0)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                />
              </div>
            </div>

          </div>

        </div>

        {/* Profile & Submit Right Column */}
        <div className="react-bits-glass rounded-3xl p-6 sm:p-8 flex flex-col justify-between space-y-6">
          <div className="space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-200 text-xs font-heading font-extrabold text-indigo-600 uppercase tracking-widest">
              <User className="w-4 h-4" />
              <span>3. Profile & Customer Relationship</span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Age (Years)
                </label>
                <input
                  type="number"
                  value={formData.age}
                  min="18"
                  max="80"
                  onChange={(e) => handleChange('age', parseInt(e.target.value) || 18)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Gender
                </label>
                <select
                  value={formData.gender}
                  onChange={(e) => handleChange('gender', e.target.value)}
                  className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Employment Type
              </label>
              <select
                value={formData.emp_type}
                onChange={(e) => handleChange('emp_type', e.target.value)}
                className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              >
                <option value="Salaried">Salaried</option>
                <option value="Self-employed">Self-employed</option>
                <option value="Agriculturist">Agriculturist</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-heading font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Property Valuation (₹) - For LTV Cap
              </label>
              <input
                type="number"
                value={formData.prop_val}
                onChange={(e) => handleChange('prop_val', parseFloat(e.target.value) || 0)}
                className="w-full bg-white/90 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              />
            </div>

            <label className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer hover:bg-white transition-colors">
              <input
                type="checkbox"
                checked={formData.existing_customer}
                onChange={(e) => handleChange('existing_customer', e.target.checked)}
                className="w-4 h-4 accent-indigo-600 rounded"
              />
              <span className="text-xs font-semibold text-slate-800">
                Existing Salary Account Holder (+CIBIL Leniency)
              </span>
            </label>

            <label className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer hover:bg-white transition-colors">
              <input
                type="checkbox"
                checked={formData.is_ntc}
                onChange={handleNTCToggle}
                className="w-4 h-4 accent-indigo-600 rounded"
              />
              <span className="text-xs font-semibold text-slate-800">
                New to Credit (NTC - No Prior Credit History)
              </span>
            </label>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 px-6 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-heading font-extrabold text-sm shadow-lg hover:shadow-indigo-500/30 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Executing AI Risk Engine...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Run AI Risk & Underwriting Assessment</span>
              </>
            )}
          </button>

        </div>

      </form>
    </div>
  );
}
