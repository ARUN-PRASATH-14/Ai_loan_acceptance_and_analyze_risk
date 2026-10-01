# REVIEW 2 DEFENSE GUIDE: FRONTEND, COMPONENTS, TESTS & CONFIGURATION

This document provides a detailed breakdown of the React frontend architecture (`src/`), components, services, test suite (`tests/`), `index.html`, `pytest.ini`, and `styles.css` for your **Review 2 Presentation Defense**.

---

## 📂 Overview of Frontend & Testing Architecture

```text
e:\flutter\Ai_loan_acceptance_and_analyze_risk\Ai_loan_acceptance_and_analyze_risk\
├── index.html                   <-- Root Vite HTML template
├── pytest.ini                   <-- Pytest test runner configuration
├── styles.css                   <-- Standalone global CSS theme & glassmorphism styling
├── tests/                       <-- Automated Pytest suite
│   └── test_app.py              <-- 28.7 KB unit & API integration test suite
└── src/                         <-- React 18 + Vite Frontend Root
    ├── main.jsx                 <-- React DOM entry point
    ├── App.jsx                  <-- Main React container & state manager
    ├── index.css                <-- Tailwind directives & utility classes
    ├── services/
    │   └── api.js               <-- Centralized REST API service module
    └── components/
        ├── Header.jsx           <-- Navigation bar & bank badges
        ├── OverviewTab.jsx      <-- System Overview & Tamil Glossary
        ├── ApplicationFormTab.jsx <-- Streamlit-style form with auto-fill presets
        ├── EvaluationResultTab.jsx <-- Approved/Rejected status, SHAP Chart & Audit Log
        ├── PolicyAssistantTab.jsx  <-- FAISS Policy RAG Chatbot with source cards
        └── BackgroundBackdrop.jsx  <-- Animated glassmorphism backdrop container
```

---

## 1️⃣ `src/` Root Files

* **`main.jsx`**: The Vite entry point file that initializes the React 18 virtual DOM and mounts `<App />` into `<div id="root">` in `index.html`.
* **`App.jsx`**: The main container component that manages active tab navigation state (`overview`, `form`, `result`, `chat`), global evaluation session context, and toast notifications.
* **`index.css`**: Configures Tailwind CSS `@tailwind` layers, glassmorphism utility classes (`backdrop-blur-md`), and scrollbar styling.

---

## 2️⃣ `src/components/` (React Component Architecture)

### 🧩 `Header.jsx`
* Displays the top navigation bar with the Loan-IQ animated logo, active tab navigation buttons, and status indicator badges.

### 🧩 `OverviewTab.jsx` (Tab 1)
* Presents the system architecture summary and **Bilingual Tamil Glossary** explaining key credit terms:
  * **CIBIL** (கிரெடிட் ஸ்கோர்)
  * **FOIR** (நிலையான கடமை விகிதம்)
  * **LTV** (கடன் மதிப்பு விகிதம்)
  * **EMI** (மாதாந்திர தவணை)
  * **DTI, NTC, NPA, Moratorium, SMOTE, RAG**.

### 🧩 `ApplicationFormTab.jsx` (Tab 2)
* Provides a Streamlit-equivalent loan application interface with **auto-fill sample presets** (SBI Home Loan, HDFC Personal Loan, Canara Education Loan).
* Captures applicant age, income, requested loan, bank choice, CIBIL score, property value, and employment category.

### 🧩 `EvaluationResultTab.jsx` (Tab 3)
* Displays evaluation results upon submission:
  * **Approval Status Badge**: `APPROVED` (Green) or `REJECTED` (Red).
  * **AI Confidence Probability**: Computed Stacking Ensemble percentage.
  * **Calculated Ratios**: FOIR and LTV gauges.
  * **Chart.js SHAP Waterfall Chart**: Visualizes feature impacts pushing approval probability higher or lower.
  * **Bank Audit Checklist**: Pass/Fail breakdown against bank policy rules.
  * **Actionable Recommendations**: Clear steps to improve credit eligibility.

### 🧩 `PolicyAssistantTab.jsx` (Tab 4)
* Renders the interactive Policy RAG Chatbot connecting to `/api/chat`.
* Displays response text alongside **cited policy document cards** (showing source filename, bank tag, and RRF relevance score).

### 🧩 `BackgroundBackdrop.jsx`
* Provides a high-contrast dark theme background canvas with glowing gradients and bank vault backdrop images.

---

## 3️⃣ `src/services/api.js` (Frontend Service Layer)

* **`api.js`**: Centralized API service layer powering backend communication:
  * `evaluateLoan(formData)`: Sends POST request to `/api/evaluate` for ML inference and SHAP attributions.
  * `sendChatMessage(prompt, context)`: Sends POST request to `/api/chat` for FAISS vector RAG lookup.

---

## 4️⃣ Testing & Configuration Files

### 🧪 `tests/test_app.py` (Automated Test Suite)
* Comprehensive 28.7 KB Pytest suite validating:
  1. API endpoint health (`/api/evaluate` & `/api/chat`).
  2. Preprocessing & SMOTE data shape assertions.
  3. Hard rule violations (FOIR caps, CIBIL cutoffs, Age limits).
  4. FAISS RAG vector retrieval accuracy and citation formatting.

### ⚙️ `pytest.ini` (Pytest Configuration)
* Specifies test runner flags: `testpaths = tests`, `python_files = test_*.py`, and `filterwarnings = ignore::DeprecationWarning`.

### 📄 `index.html` (Vite HTML Template)
* The single-page entry HTML document containing viewport meta tags, Google Fonts imports (`Inter`, `Outfit`), title tag, and root mount `<div id="root">`.

### 🎨 `styles.css` (Standalone Custom CSS)
* A 23.8 KB standalone stylesheet defining custom CSS variables (`--primary`, `--accent`), glassmorphism card blur rules, dark mode themes, and responsive layout breakpoints.

---

## 🎓 Expected Review 2 Defense Questions

### Q1: "How do React components communicate with Flask?"
> **Answer**: `src/services/api.js` acts as an abstraction layer. Components like `ApplicationFormTab.jsx` and `PolicyAssistantTab.jsx` invoke `evaluateLoan()` or `sendChatMessage()`, which execute asynchronous HTTP POST requests to Flask endpoints (`/api/evaluate` and `/api/chat`).

### Q2: "How is SHAP feature importance visualized in the frontend?"
> **Answer**: `EvaluationResultTab.jsx` receives top Shapley values from `/api/evaluate` and renders a dynamic horizontal bar chart using `react-chartjs-2` (Chart.js), displaying positive drivers in green and negative risk factors in red.

### Q3: "What automated tests do you have in `tests/test_app.py`?"
> **Answer**: `tests/test_app.py` contains automated unit and integration tests verifying API endpoint availability, SMOTE preprocessor scaling, hard rule boundary conditions for all 5 banks, and FAISS RAG document retrieval precision.
