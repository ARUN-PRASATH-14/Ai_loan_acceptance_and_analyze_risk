


let lastAssessmentContext = null;
let shapChart = null;


document.addEventListener('DOMContentLoaded', () => {

  const formInputs = ['loanAmt', 'intRate', 'tenureMo', 'income', 'coAppInc', 'existEmi'];
  formInputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', calculateRealtimeMetrics);
    }
  });

  
  const loanForm = document.getElementById('loanForm');
  if (loanForm) {
    loanForm.addEventListener('submit', handleFormSubmit);
    loanForm.addEventListener('reset', () => {
      setTimeout(() => {
        calculateRealtimeMetrics();
        const container = document.getElementById('resultsContainer');
        if (container) {
          container.innerHTML = `
            <div class="results-placeholder">
              <div class="placeholder-icon">⚡</div>
              <h3>SYSTEM READY</h3>
              <p>Submit applicant parameters to compute AI Risk Probability &amp; SHAP feature attribution</p>
            </div>
          `;
        }
      }, 50);
    });
  }

  
  calculateRealtimeMetrics();
});

function calculateRealtimeMetrics() {
  const loanAmt = parseFloat(document.getElementById('loanAmt')?.value) || 0;
  const intRate = parseFloat(document.getElementById('intRate')?.value) || 0;
  const tenureMo = parseFloat(document.getElementById('tenureMo')?.value) || 1;
  const income = parseFloat(document.getElementById('income')?.value) || 0;
  const coAppInc = parseFloat(document.getElementById('coAppInc')?.value) || 0;
  const existEmi = parseFloat(document.getElementById('existEmi')?.value) || 0;

  
  const monthlyRate = (intRate / 100) / 12;
  let emi = 0;
  if (monthlyRate > 0 && tenureMo > 0 && loanAmt > 0) {
    emi = (loanAmt * monthlyRate * Math.pow(1 + monthlyRate, tenureMo)) / (Math.pow(1 + monthlyRate, tenureMo) - 1);
  } else if (tenureMo > 0 && loanAmt > 0) {
    emi = loanAmt / tenureMo;
  }

  
  const grossMonthlyIncome = (income + coAppInc) / 12;
  let foir = 0;
  if (grossMonthlyIncome > 0) {
    foir = ((existEmi + emi) / grossMonthlyIncome) * 100;
  }

 
  const emiEl = document.getElementById('proposedEmi');
  if (emiEl) emiEl.textContent = '₹ ' + Math.round(emi).toLocaleString('en-IN');

  const foirEl = document.getElementById('foirPreview');
  const foirStatusEl = document.getElementById('foirStatus');
  if (foirEl) {
    foirEl.textContent = foir.toFixed(1) + '%';
  }

  if (foirStatusEl) {
    if (foir <= 50) {
      foirStatusEl.textContent = 'SAFE';
      foirStatusEl.className = 'calc-status safe';
    } else if (foir <= 65) {
      foirStatusEl.textContent = 'MODERATE';
      foirStatusEl.className = 'calc-status warning';
    } else {
      foirStatusEl.textContent = 'HIGH';
      foirStatusEl.className = 'calc-status danger';
    }
  }
}

// Handle Form Submission -> Call /api/evaluate
async function handleFormSubmit(e) {
  e.preventDefault();
  showLoadingModal(true);

  const payload = {
    bank: document.getElementById('bank').value,
    loan_type: document.getElementById('loanType').value,
    age: parseInt(document.getElementById('age').value) || 30,
    gender: document.getElementById('gender').value,
    emp_type: document.getElementById('empType').value,
    employer: document.getElementById('employer').value,
    emp_years: parseInt(document.getElementById('empYears').value) || 0,
    income: parseFloat(document.getElementById('income').value) || 0,
    co_app_inc: parseFloat(document.getElementById('coAppInc').value) || 0,
    exist_emi: parseFloat(document.getElementById('existEmi').value) || 0,
    existing_customer: document.getElementById('existingCustomer').checked,
    loan_amt: parseFloat(document.getElementById('loanAmt').value) || 0,
    tenure_mo: parseInt(document.getElementById('tenureMo').value) || 12,
    int_rate: parseFloat(document.getElementById('intRate').value) || 8.5,
    prop_val: parseFloat(document.getElementById('propVal').value) || 0,
    cibil: parseInt(document.getElementById('cibil').value) || 0,
    is_ntc: document.getElementById('isNtc').checked,
    tn_city: document.getElementById('tnCity').value
  };

  try {
    const response = await fetch('/api/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    const data = await response.json();
    showLoadingModal(false);

    // Save context for chatbot follow-ups
    lastAssessmentContext = {
      bank: payload.bank,
      loan_type: payload.loan_type,
      approved: data.approved,
      probability: data.probability,
      foir: data.foir,
      ltv: data.ltv,
      cibil: payload.cibil,
      violations: data.violations || []
    };

    renderEvaluationResults(data, payload);
    showSuccessToast('EVALUATION COMPLETED SUCCESSFULLY');
  } catch (error) {
    showLoadingModal(false);
    showErrorToast('EVALUATION FAILED: ' + error.message);
  }
}

// Render Results Panel
function renderEvaluationResults(data, inputPayload) {
  const container = document.getElementById('resultsContainer');
  if (!container) return;

  const isApproved = data.approved;
  const probability = data.probability || 0;
  const foir = data.foir || 0;
  const ltv = data.ltv !== undefined ? data.ltv : 'N/A';
  const emi = data.proposed_emi || 0;
  const violations = data.violations || [];
  const recommendations = data.recommendations || [];

  let html = `
    <!-- Decision Banner -->
    <div class="decision-banner ${isApproved ? 'approved' : 'rejected'}">
      <div class="decision-header">
        <div class="decision-title">
          ${isApproved ? '⚡ STATUS: APPROVED' : '⚠️ STATUS: REJECTED'}
        </div>
        <span class="telemetry-chip ${isApproved ? 'chip-lime' : 'chip-rose'}">
          AI SCORE: ${probability}%
        </span>
      </div>
      <div class="score-bar-container">
        <div class="score-bar-fill" style="width: ${Math.min(probability, 100)}%; background: ${isApproved ? '#84CC16' : '#F43F5E'}"></div>
      </div>
      <p style="font-size: 12px; font-family: var(--font-mono); color: var(--color-text-muted);">
        ${isApproved 
          ? `[CLASSIFICATION] Meets underwriting criteria for ${inputPayload.bank} ${inputPayload.loan_type}.` 
          : `[BREACH DETECTED] Violates policy rules for ${inputPayload.bank} ${inputPayload.loan_type}.`}
      </p>
    </div>

    <!-- Financial Metrics Grid -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-label">FOIR</div>
        <div class="metric-value">${foir}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">LTV</div>
        <div class="metric-value">${ltv === 'N/A' ? 'N/A' : ltv + '%'}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">CIBIL</div>
        <div class="metric-value">${inputPayload.is_ntc ? 'NTC' : inputPayload.cibil}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">MONTHLY EMI</div>
        <div class="metric-value">₹ ${Math.round(emi).toLocaleString('en-IN')}</div>
      </div>
    </div>

    <!-- SHAP XAI Feature Attribution -->
    <div class="shap-container">
      <div class="shap-title">⚡ SHAP XAI — FEATURE ATTRIBUTION DRIVERS</div>
      <div style="height: 180px; position: relative;">
        <canvas id="shapCanvas"></canvas>
      </div>
      <div class="shap-legend">
        🟩 Positive bars push toward approval &nbsp;|&nbsp; 🟥 Negative bars push toward rejection
      </div>
    </div>
  `;

  // Policy Violations Section
  if (violations.length > 0) {
    html += `
      <div class="violations-box">
        <div class="violations-title">⚠️ HARD POLICY BREACHES</div>
        <ul class="violations-list">
          ${violations.map(v => `<li>❌ <strong>${v}</strong></li>`).join('')}
        </ul>
      </div>
    `;
  }

  // Recommendations Section
  if (recommendations.length > 0) {
    html += `
      <div class="recommendations-box">
        <div class="recommendations-title">⚡ ACTIONABLE REMEDY RECOMMENDATIONS</div>
        <ul class="recommendations-list">
          ${recommendations.map(r => `<li>• ${formatMarkdownText(r)}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  container.innerHTML = html;

  // Render SHAP Chart using Chart.js with Cyberpunk Styling
  if (data.shap && data.shap.labels && data.shap.values) {
    renderShapChart(data.shap.labels, data.shap.values);
  }
}

// Render SHAP Waterfall Bar Chart with Cyberpunk Neon theme
function renderShapChart(labels, values) {
  const ctx = document.getElementById('shapCanvas')?.getContext('2d');
  if (!ctx) return;

  if (shapChart) {
    shapChart.destroy();
  }

  const cleanLabels = labels.map(l => l.replace(/_/g, ' '));
  const bgColors = values.map(v => v >= 0 ? '#84CC16' : '#F43F5E');

  shapChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: cleanLabels,
      datasets: [{
        label: 'SHAP Feature Contribution (%)',
        data: values,
        backgroundColor: bgColors,
        borderRadius: 3
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#000',
          titleColor: '#FAFAFA',
          bodyColor: '#84CC16',
          borderColor: 'rgba(132, 204, 22, 0.4)',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => ` Contribution: ${ctx.raw > 0 ? '+' : ''}${ctx.raw}%`
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { font: { size: 10, family: 'JetBrains Mono' }, color: '#A1A1AA' }
        },
        y: {
          grid: { display: false },
          ticks: { font: { size: 10, family: 'JetBrains Mono' }, color: '#FAFAFA' }
        }
      }
    }
  });
}

// ─── CHATBOT INTERACTIVITY ───

async function handleChatSubmit(e) {
  e.preventDefault();
  const inputEl = document.getElementById('chatInput');
  const query = inputEl ? inputEl.value.trim() : '';
  if (!query) return;

  inputEl.value = '';
  sendMessage(query);
}

async function sendMessage(query) {
  const chatMessages = document.getElementById('chatMessages');
  if (!chatMessages) return;

  // Append User Message
  appendChatMessage('user', query);

  // Append Loading Bot Message
  const loadingId = 'loading-' + Date.now();
  appendChatMessage('bot', '⚡ SYNTHESIZING RESPONSE FROM RAG VECTOR INDEX...', loadingId);

  try {
    const payload = {
      prompt: query,
      context: lastAssessmentContext || {}
    };

    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    // Remove loading message
    const loadingMsgEl = document.getElementById(loadingId);
    if (loadingMsgEl) loadingMsgEl.remove();

    // Append AI Response
    appendChatMessage('bot', data.answer || 'No response returned.');

    // Update Sources Panel if citations exist
    if (data.sources && data.sources.length > 0) {
      renderSourcesPanel(data.sources);
    }
  } catch (error) {
    const loadingMsgEl = document.getElementById(loadingId);
    if (loadingMsgEl) loadingMsgEl.remove();
    appendChatMessage('bot', '❌ TERMINAL ERROR: Failed to process query.');
  }
}

function appendChatMessage(sender, text, msgId) {
  const chatMessages = document.getElementById('chatMessages');
  if (!chatMessages) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = `chat-message ${sender}-message`;
  if (msgId) msgDiv.id = msgId;

  const avatar = sender === 'bot' ? '🤖' : '👤';
  const formattedText = sender === 'bot' ? formatMarkdownText(text) : escapeHtml(text);

  msgDiv.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-content">
      ${formattedText}
    </div>
  `;

  chatMessages.appendChild(msgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderSourcesPanel(sources) {
  const panel = document.getElementById('sourcesPanel');
  const list = document.getElementById('sourcesList');
  if (!panel || !list) return;

  panel.style.display = 'block';
  list.innerHTML = sources.slice(0, 3).map((s, idx) => `
    <div style="margin-bottom: 4px;">
      <strong>[${idx + 1}] ${s.document || s.bank || 'POLICY MANUAL'}</strong> (Relevance: ${(s.score * 100).toFixed(1)}%)
    </div>
  `).join('');
}

// ─── KNOWLEDGE BASE RAG SEARCH & FILTERS ───

async function handlePolicySearch(e) {
  e.preventDefault();
  const inputEl = document.getElementById('policyQueryInput');
  const query = inputEl ? inputEl.value.trim() : '';
  if (!query) return;

  const resultsSection = document.getElementById('searchResultsSection');
  const resultsGrid = document.getElementById('searchResultsGrid');
  if (!resultsSection || !resultsGrid) return;

  resultsSection.style.display = 'block';
  resultsGrid.innerHTML = '<p style="color: var(--color-text-muted); font-size: 12px; font-family: var(--font-mono);">⚡ SEARCHING FAISS + BM25 VECTOR INDEX...</p>';

  try {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });

    const data = await response.json();
    const results = data.results || [];

    if (results.length === 0) {
      resultsGrid.innerHTML = '<p style="color: var(--color-text-muted); font-size: 12px; font-family: var(--font-mono);">No matching vector chunks found.</p>';
      return;
    }

    resultsGrid.innerHTML = results.map(r => `
      <div class="search-result-card">
        <div class="search-result-meta">
          <span class="bank-badge ${r.bank.toLowerCase()}">${r.bank}</span>
          <span>Doc: <strong>${r.file}</strong></span>
          <span>Rank: <strong>#${r.rank}</strong></span>
          <span>Relevance: <strong>${(r.score * 100).toFixed(1)}%</strong></span>
        </div>
        <div class="result-snippet">${escapeHtml(r.content)}</div>
      </div>
    `).join('');
  } catch (error) {
    resultsGrid.innerHTML = '<p style="color: var(--color-accent-rose); font-size: 12px; font-family: var(--font-mono);">❌ VECTOR SEARCH ERROR.</p>';
  }
}

function filterPolicyCards(bankFilter) {
  const chips = document.querySelectorAll('.filter-chip');
  chips.forEach(chip => {
    if (chip.textContent.includes(bankFilter) || (bankFilter === 'ALL' && chip.textContent.includes('ALL'))) {
      chip.classList.add('active');
    } else {
      chip.classList.remove('active');
    }
  });

  const cards = document.querySelectorAll('.policy-card');
  cards.forEach(card => {
    const cardBank = card.getAttribute('data-bank');
    if (bankFilter === 'ALL' || cardBank === bankFilter) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

// Formatting Helper: Basic Markdown Parser
function formatMarkdownText(text) {
  if (!text) return '';
  let formatted = escapeHtml(text);

  // Bold
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Headings
  formatted = formatted.replace(/^### (.*$)/gim, '<h4>$1</h4>');
  formatted = formatted.replace(/^## (.*$)/gim, '<h3>$1</h3>');

  // Bullets
  formatted = formatted.replace(/^\• (.*$)/gim, '<li>$1</li>');
  formatted = formatted.replace(/^- (.*$)/gim, '<li>$1</li>');

  // Wrap loose list items in <ul>
  formatted = formatted.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');

  // Line breaks
  formatted = formatted.replace(/\n/g, '<br>');

  return formatted;
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Helper Modals & Toasts
function showLoadingModal(show) {
  const modal = document.getElementById('loadingModal');
  if (modal) {
    if (show) modal.classList.remove('hidden');
    else modal.classList.add('hidden');
  }
}

function showErrorToast(message) {
  const toast = document.getElementById('errorToast');
  const msgEl = document.getElementById('errorMessage');
  if (toast && msgEl) {
    msgEl.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 4000);
  }
}

function showSuccessToast(message) {
  const toast = document.getElementById('successToast');
  const msgEl = document.getElementById('successMessage');
  if (toast && msgEl) {
    msgEl.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 4000);
  }
}
