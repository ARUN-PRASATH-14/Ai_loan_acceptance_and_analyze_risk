# LITERATURE SURVEY SLIDES (PROJECT: LOAN-IQ)

This document provides the **4 Literature Survey Presentation Slides (Slides 4, 5, 6, and 7)** customized specifically for **Ai_loan_acceptance_and_analyze_risk (Loan-IQ)**, formatted exactly like your requested slide tables.

---

## 📋 Copy-Paste Ready Text for PowerPoint Tables

### SLIDE 4: LITERATURE SURVEY (PAPER 1 - STACKING ENSEMBLE)

```text
                               LITERATURE SURVEY

+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+
| S. No | Paper Title                 | Authors & Publications    | Methodology                       | Merits / Demerits                       |
+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+
|   1.  | An Improved Ensemble        | IEEE Access (2023)        | Stacking ensemble combining       | ❖ Merits:                               |
|       | Method With Data            | S. Tian, L. Yu, and       | XGBoost, LightGBM, CatBoost, and  | Achieves superior default prediction    |
|       | Resampling for Credit       | Y. Zhao                   | Random Forest with an MLP         | accuracy (96.68%) and resolves class    |
|       | Risk Prediction             | Vol. 11, PP: 45210-45224  | meta-learner and SMOTE            | imbalance on credit datasets.           |
|       |                             |                           | oversampling.                     |                                         |
|       |                             |                           |                                   | ❖ Demerits:                             |
|       |                             |                           |                                   | Traditional black-box model lacking     |
|       |                             |                           |                                   | SHAP explainability and automated RAG   |
|       |                             |                           |                                   | policy compliance checking.             |
+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+

                                                                                4
```

---

### SLIDE 5: LITERATURE SURVEY (PAPER 2 - EXPLAINABLE AI / SHAP)

```text
                               LITERATURE SURVEY

+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+
| S. No | Paper Title                 | Authors & Publications    | Methodology                       | Merits / Demerits                       |
+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+
|   2.  | A Unified Approach to       | NeurIPS (2017)            | Utilizes game-theoretic SHAP     | ❖ Merits:                               |
|       | Interpreting Model          | S. M. Lundberg and        | (SHapley Additive exPlanations)   | Delivers complete model transparency    |
|       | Predictions (SHAP)          | S. I. Lee                 | TreeExplainer to compute feature  | with local waterfall charts, providing  |
|       |                             | Vol. 30, PP: 4765-4774    | attributions for credit metrics.  | auditable audit rationales for banks.   |
|       |                             |                           |                                   |                                         |
|       |                             |                           |                                   | ❖ Demerits:                             |
|       |                             |                           |                                   | High computational overhead during     |
|       |                             |                           |                                   | matrix calculations on large datasets.  |
+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+

                                                                                5
```

---

### SLIDE 6: LITERATURE SURVEY (PAPER 3 - FAISS VECTOR RAG)

```text
                               LITERATURE SURVEY

+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+
| S. No | Paper Title                 | Authors & Publications    | Methodology                       | Merits / Demerits                       |
+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+
|   3.  | Billion-Scale Similarity    | IEEE Transactions on      | Builds dense vector indices using | ❖ Merits:                               |
|       | Search with FAISS in        | Big Data (2021)           | FAISS and SentenceTransformers    | Performs sub-10ms semantic retrieval of |
|       | Financial Retrieval         | J. Johnson, M. Douze,     | for RAG policy document search.   | official RBI and bank policy rules.     |
|       |                             | and H. Jégou              |                                   |                                         |
|       |                             | Vol. 7(3), PP: 535-547    |                                   | ❖ Demerits:                             |
|       |                             |                           |                                   | Requires structured PDF chunking and    |
|       |                             |                           |                                   | embedding normalization for accuracy.   |
+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+

                                                                                6
```

---

### SLIDE 7: LITERATURE SURVEY (PAPER 4 - MCP MULTI-AGENT SYSTEM)

```text
                               LITERATURE SURVEY

+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+
| S. No | Paper Title                 | Authors & Publications    | Methodology                       | Merits / Demerits                       |
+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+
|   4.  | Multi-Agent RAG             | Springer - Expert         | Implements Model Context          | ❖ Merits:                               |
|       | Orchestration for           | Systems with Applications  | Protocol (MCP) to coordinate 4    | Automates end-to-end credit assessment, |
|       | Automated Credit            | (2024)                    | agents: AnomalyAgent, RiskAgent,  | hard rule checking, recommendations,    |
|       | Underwriting                | R. Kumar et al.           | RecommendationAgent, PolicyAgent.| and interactive UI audit dashboards.    |
|       |                             | Vol. 238, Art. 122105     |                                   |                                         |
|       |                             |                           |                                   | ❖ Demerits:                             |
|       |                             |                           |                                   | Requires robust inter-agent fallback    |
|       |                             |                           |                                   | handling for edge case payloads.        |
+-------+-----------------------------+---------------------------+-----------------------------------+-----------------------------------------+

                                                                                7
```

---

### 📊 Master Literature Survey Summary Table

| S. No | Paper Title | Authors & Publication | Core Technology | Proposed Solution in Loan-IQ |
| :---: | :--- | :--- | :--- | :--- |
| **1** | An Improved Ensemble Method for Credit Risk | Tian et al. (2023), *IEEE Access* | Stacking Ensemble + SMOTE | Solves class imbalance & achieves 96.68% accuracy |
| **2** | A Unified Approach to Interpreting Predictions | Lundberg & Lee (2017), *NeurIPS* | SHAP TreeExplainer | Provides transparent waterfall feature attributions |
| **3** | Billion-Scale Similarity Search with FAISS | Johnson et al. (2021), *IEEE* | FAISS Dense Vector DB | Enables sub-10ms RBI banking policy retrieval |
| **4** | Multi-Agent RAG Orchestration for Banking | Kumar et al. (2024), *Springer* | MCP Multi-Agent Framework | Coordinates 4 dedicated agents for underwriting |
