# AI LOAN ACCEPTANCE & RISK ANALYSIS SYSTEM - MODULE SLIDES

This document provides the 3 module presentation slides tailored specifically for **Ai_loan_acceptance_and_analyze_risk (Loan-IQ)**, matching your exact codebase agents: **AnomalyAgent, RiskAgent, RecommendationAgent, and PolicyAgent**.

---

## 🎨 Presentation Slide Visuals (Slides 15, 16, 17)

````carousel
![Slide 15: Stacking Ensemble Risk Prediction Engine](file:///C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/slide_15_stacking_ensemble_1789615714197.png)
<!-- slide -->
![Slide 16: Explainable AI (XAI) Using SHAP Attribution](file:///C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/slide_16_explainable_ai_1789615754680.png)
<!-- slide -->
![Slide 17: FAISS Policy RAG Engine and Agent Visualization](file:///C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/slide_17_faiss_rag_agent_v2_1789617593564.png)
````

---

## 📋 Copy-Paste Ready Text for PowerPoint

### SLIDE 15: STACKING ENSEMBLE RISK PREDICTION ENGINE

```text
               STACKING ENSEMBLE RISK PREDICTION ENGINE

❖ The system combines four base classifiers—XGBoost, LightGBM, CatBoost, and Random Forest—with an MLP Neural Network meta-learner.

❖ It achieves 96.68% prediction accuracy and 0.9942 ROC-AUC score for robust credit risk assessment.

❖ It evaluates complex non-linear relationships between applicant income, CIBIL score, loan amount, and collateral value.

❖ The ensemble model dynamically computes default probabilities to minimize Non-Performing Asset (NPA) exposure for banks.

❖ It utilizes optimal probability thresholds (0.50 cutoff) to automate instant credit approval and risk classification.

                                                                               15
```

---

### SLIDE 16: EXPLAINABLE AI (XAI) USING SHAP ATTRIBUTION

```text
              EXPLAINABLE AI (XAI) USING SHAP ATTRIBUTION

❖ The system uses SHAP (SHapley Additive exPlanations) TreeExplainer to deliver complete model transparency for credit decisions.

❖ It calculates exact Shapley feature attributions for key financial metrics including CIBIL score, FOIR, LTV, and DTI ratios.

❖ Local waterfall charts visualize how specific applicant attributes push the approval probability higher or lower.

❖ It provides global feature importance rankings to ensure strict compliance with central banking audit standards.

❖ The XAI framework translates complex ensemble predictions into human-readable audit rationales for loan officers.

                                                                               16
```

---

### SLIDE 17: FAISS POLICY RAG ENGINE AND AGENT VISUALIZATION

```text
          FAISS POLICY RAG ENGINE AND AGENT VISUALIZATION

❖ The system indexes RBI banking policy guidelines using a FAISS vector database and SentenceTransformers embeddings.

❖ It performs sub-10ms semantic similarity retrieval for rapid regulatory policy compliance verification.

❖ Model Context Protocol (MCP) coordinates four specialized agents: AnomalyAgent, RiskAgent, RecommendationAgent, and PolicyAgent.

❖ An interactive Streamlit and Web dashboard visually displays loan decision metrics, SHAP rationales, and compliance checklists.

❖ The unified solution combines machine learning risk prediction, XAI transparency, and RAG policy verification into one interface.

                                                                               17
```

---

### 💡 MCP Agent Alignment Matrix (Matching `app.py`)

| MCP Agent Class Name | Tool Function Name | Core Responsibility in Project |
| :--- | :--- | :--- |
| **`AnomalyAgent`** | `run_anomaly_check_tool` | Validates input payload sanity, checks for out-of-bound inputs, and enforces hard bank policy rules. |
| **`RiskAgent`** | `run_risk_scoring_tool` & `run_shap_explainer_tool` | Preprocesses features, runs Stacking ML Ensemble inference, and generates SHAP waterfall feature attributions. |
| **`RecommendationAgent`** | `run_recommendation_tool` | Evaluates approval/rejection conditions and generates actionable financial improvement steps for applicants. |
| **`PolicyAgent`** | `run_policy_lookup_tool` | Performs hybrid FAISS + BM25 vector search and orchestrates policy Q&A chat. |
