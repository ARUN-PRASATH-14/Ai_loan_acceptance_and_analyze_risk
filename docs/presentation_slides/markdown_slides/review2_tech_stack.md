# LOAN-IQ CURRENT TECHNOLOGY STACK (REVIEW 2)

This document provides a comprehensive breakdown of the complete **Technology Stack** used in the **AI Loan Acceptance & Risk Analysis System (Loan-IQ)** for your **Review 2 Defense**.

---

## 🏛️ Executive Summary Table: Tech Stack Overview

| System Layer | Technology / Library | Version / Details | Purpose in Loan-IQ System |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | **React 18** | `^18.3.1` | Building modular single-page user interface (Tabs 1-4). |
| **Frontend Build Tool** | **Vite** | `^6.0.7` | Fast HMR dev server & production asset bundling. |
| **UI & Styling** | **TailwindCSS 3 + CSS3** | `^3.4.17` | Dark mode themes, glassmorphism cards & Tamil glossary typography. |
| **Data Visualization** | **Chart.js + React-ChartJS-2** | `^4.4.7` | Interactive horizontal SHAP waterfall feature attribution charts. |
| **UI Iconography** | **Lucide React** | `^0.469.0` | Sleek modern icons for navigation, badges & metrics. |
| **Backend Framework** | **Python 3.12 + Flask** | `3.x` / `Flask-CORS` | Central web server & REST API orchestrator (`/api/evaluate`, `/api/chat`). |
| **Multi-Agent System** | **MCP Framework** | Custom 4-Agent Protocol | Coordinates `AnomalyAgent`, `RiskAgent`, `RecommendationAgent`, `PolicyAgent`. |
| **ML Stacking Ensemble** | **XGBoost, LightGBM, CatBoost, RF** | `xgboost`, `lightgbm`, `catboost` | Base classifiers for 96.68% accuracy loan default prediction. |
| **ML Meta-Learner** | **ANN / MLP Classifier** | `scikit-learn` | Meta-learner blending base model probabilities into final risk score. |
| **Class Balancing** | **SMOTE** | `imbalanced-learn` | Resolves 95:5 class imbalance in credit default datasets. |
| **Data Preprocessing** | **Scikit-Learn** | `StandardScaler`, `OneHotEncoder` | Feature scaling and categorical vectorization. |
| **Explainable AI (XAI)** | **SHAP** | `shap` (TreeExplainer) | Game-theoretic Shapley value feature attributions for credit transparency. |
| **Vector Database** | **FAISS (CPU)** | `faiss-cpu` / `langchain` | Dense similarity vector search over bank policy PDFs. |
| **Sparse Search** | **BM25 Okapi** | `rank-bm25` | Sparse keyword matching for hybrid RAG search. |
| **Re-Ranking Algorithm** | **RRF (Reciprocal Rank Fusion)** | Custom Hybrid Search | Merges FAISS & BM25 search results with bank-aware boosting. |
| **Embedding Model** | **SentenceTransformers** | `all-MiniLM-L6-v2` | Converts policy PDF text into normalized 384-dim vector embeddings. |
| **LLM Cloud Inference** | **Groq Cloud API** | `llama3-70b-8192` | Llama-3.3-70B model inference for instant policy synthesis (~400ms). |
| **Test Suite** | **Pytest** | `pytest` / `pytest.ini` | Automated unit, API integration, and RAG precision testing. |

---

## 💻 Tech Stack Layers Breakdown

```text
========================================================================================
                              LOAN-IQ TECH STACK ARCHITECTURE
========================================================================================
[1. FRONTEND UI LAYER]   : React 18 | Vite 6 | TailwindCSS | Lucide Icons | Chart.js
[2. BACKEND API LAYER]    : Python 3.12 | Flask | Flask-CORS | Python-Dotenv
[3. MULTI-AGENT LAYER]   : MCP Protocol (AnomalyAgent, RiskAgent, RecommendationAgent, PolicyAgent)
[4. MACHINE LEARNING]    : XGBoost | LightGBM | CatBoost | Random Forest | MLP | SMOTE | SHAP
[5. VECTOR RAG SEARCH]   : FAISS Dense DB | BM25 Sparse Index | RRF Re-Ranking | all-MiniLM-L6-v2
[6. GENERATIVE AI CLOUD] : Groq Cloud API | Llama-3.3-70B Versatile LLM
[7. TESTING & DEVOPS]    : Pytest | Gunicorn / WSGI Server | GitHub Workspace
========================================================================================
```

---

## 🎓 Expected Review 2 Questions on Tech Stack

### Q1: "Why did you choose React + Vite for the frontend instead of HTML/JS?"
> **Answer**: React 18 provides component-based state management, making it easy to handle real-time tab switching, dynamic form presets, and SHAP chart re-rendering. Vite 6 provides sub-second Hot Module Replacement (HMR) and optimized production bundling into `dist/`.

### Q2: "Why use Groq API instead of standard OpenAI or local Ollama?"
> **Answer**: Groq's LPU (Language Processing Unit) architecture delivers ultrafast inference (~400ms response time for Llama-3.3-70B), ensuring sub-second policy chatbot answers while avoiding heavy local GPU requirements.

### Q3: "What is your RAG hybrid search technology?"
> **Answer**: We use a **Hybrid Search Engine** combining **FAISS** for Dense Semantic Vector Retrieval (`all-MiniLM-L6-v2`) and **BM25 Okapi** for Sparse Keyword Retrieval. Results are re-ranked using **Reciprocal Rank Fusion (RRF)** to ensure high precision on specific bank policy terms.
