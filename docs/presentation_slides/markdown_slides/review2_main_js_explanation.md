# REVIEW 2 DEFENSE GUIDE: MAIN.JS EXPLANATION

This document provides a line-by-line breakdown of **`main.js`** for your **Review 2 Defense**.

---

## 🏛️ Executive Summary: What `main.js` Does

`main.js` is the **Client-Side Vanilla JavaScript Orchestrator** for the web application UI. It bridges the user interface with the backend Flask API (`app.py`), handles real-time mathematical calculations, renders interactive Chart.js SHAP charts, and manages the Policy RAG Chatbot conversation loop.

---

## 📂 Function-by-Function Breakdown of `main.js`

```text
========================================================================================
                                  MAIN.JS CODE MAP
========================================================================================
 1. DOM Initialization & Listeners    (Lines 1 - 45)   -> Binds input listeners & form events
 2. Real-Time EMI & FOIR Calculator   (Lines 47 - 93)  -> Instant client-side formula preview
 3. Loan Form Handler & API Call      (Lines 95 - 153) -> POST /api/evaluate async fetch
 4. Results Panel & Decision Banner   (Lines 155 - 251)-> Renders APPROVED/REJECTED status
 5. SHAP Chart.js Bar Chart Renderer  (Lines 253 - 305)-> Cyberpunk horizontal waterfall chart
 6. Policy Chatbot Engine             (Lines 307 - 396)-> POST /api/chat & cited PDF cards
 7. Knowledge Base Search & Filter    (Lines 397 - 463)-> Vector snippet search & bank filter
 8. Markdown Parser & UI Toast Helpers(Lines 464 - 525)-> Markdown renderer & toast alerts
========================================================================================
```

---

## 🛠️ Key Function Deep-Dive

### 1️⃣ `calculateRealtimeMetrics()` (Lines 47 - 93)
* **What it does**: Computes monthly EMI ($\text{EMI} = \frac{P \cdot r \cdot (1+r)^n}{(1+r)^n - 1}$) and FOIR ($\text{FOIR} = \frac{\text{Existing EMI} + \text{Proposed EMI}}{\text{Gross Monthly Income}} \times 100$) in real time as the user types or moves sliders.
* **Why it matters**: Gives the applicant instant visual feedback (SAFE ≤ 50%, MODERATE ≤ 65%, HIGH > 65%) **before** submitting the form to the server.

### 2️⃣ `handleFormSubmit(e)` (Lines 95 - 153)
* **What it does**: Collects all applicant form parameters (Bank, Loan Type, Age, CIBIL, Income, EMI, Property Value, City Tier) and executes `fetch('/api/evaluate', { method: 'POST' })`.
* **Session Storage**: Saves `lastAssessmentContext` in memory so the Policy Chatbot knows the applicant's latest evaluation state.

### 3️⃣ `renderEvaluationResults(data, inputPayload)` (Lines 155 - 251)
* **What it does**: Dynamically builds the HTML decision banner:
  * **Green Banner**: `STATUS: APPROVED` with AI score badge.
  * **Red Banner**: `STATUS: REJECTED` with list of hard policy violations.
  * **Financial Metrics Grid**: Displays FOIR, LTV, CIBIL, and monthly EMI.
  * **Actionable Remedy Recommendations**: Lists specific steps to fix credit eligibility.

### 4️⃣ `renderShapChart(labels, values)` (Lines 253 - 305)
* **What it does**: Destroys previous chart instance and initializes a new **Chart.js horizontal bar chart** (`#shapCanvas`):
  * **Green Bars (`#84CC16`)**: Positive attributions pushing toward loan approval.
  * **Red Bars (`#F43F5E`)**: Negative attributions pushing toward loan rejection.

### 5️⃣ `sendMessage(query)` (Lines 319 - 396)
* **What it does**: Sends user questions to `POST /api/chat` alongside `lastAssessmentContext`. Parses markdown answers and displays cited bank policy PDF document cards.

---

## 🎓 Expected Review 2 Questions on `main.js`

### Q1: "How does `main.js` compute EMI without calling the backend?"
> **Answer**: `main.js` implements the standard banking amortization formula in JavaScript (`calculateRealtimeMetrics()`), calculating EMI and FOIR on every input event for instant UI feedback.

### Q2: "How does `main.js` remember the user's latest loan result for the chatbot?"
> **Answer**: Upon receiving the response from `/api/evaluate`, `main.js` stores the applicant's score, FOIR, LTV, and violations inside a global variable `lastAssessmentContext`. When the user asks a question in the chatbot, `lastAssessmentContext` is sent in the payload to `/api/chat` so the RAG chatbot provides personalized context.

### Q3: "How are SHAP feature attributions rendered visually?"
> **Answer**: `renderShapChart()` uses `Chart.js` with `indexAxis: 'y'`. It assigns green background colors to positive Shapley values and red to negative values, creating a visual waterfall feature attribution chart.
