# MODULES

![Modules Presentation Slide](file:///C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/modules_slide_1789580951279.png)

---

## Slide Text (100% English - Copy-Paste Ready)

```text
                                    MODULES

• Data Preprocessing, Feature Engineering & SMOTE Class Balancing

• Stacking Ensemble Machine Learning Engine (XGBoost, LightGBM, CatBoost, Random Forest)

• Explainable AI (XAI) & SHAP Feature Attribution Analysis

• FAISS Policy RAG & MCP Multi-Agent Dashboard Visualization
```

---

### Detailed Module Explanation for Presentation Defense

| Module Name | Core Functionality | Technologies Used | Key Output |
| :--- | :--- | :--- | :--- |
| **1. Data Preprocessing & Class Balancing** | Cleans applicant financial data, handles missing values, standardizes numeric attributes, and applies SMOTE (Synthetic Minority Over-sampling Technique) to balance 95:5 class imbalanced credit datasets. | Pandas, NumPy, Scikit-Learn, imbalanced-learn (SMOTE) | Balanced dataset matrix without default bias |
| **2. Stacking Ensemble ML Engine** | Combines 4 base gradient boosting & ensemble classifiers (XGBoost, LightGBM, CatBoost, Random Forest) with an MLP Meta-Learner to evaluate loan default risk. | XGBoost, LightGBM, CatBoost, Scikit-Learn StackingClassifier | 96.68% Accuracy, 0.9942 ROC-AUC Approval/Rejection score |
| **3. Explainable AI (XAI) & SHAP Analysis** | Calculates Shapley values for individual credit attributes (CIBIL score, FOIR, LTV, DTI) to explain why a specific loan was approved or rejected with visual waterfall charts. | SHAP (TreeExplainer), Matplotlib | Local & global feature attribution rationale |
| **4. FAISS Policy RAG & Agentic Dashboard** | Converts RBI policy PDFs into vector embeddings, performs sub-10ms semantic document retrieval with FAISS, and displays multi-agent audit results in an interactive web UI. | FAISS Vector DB, SentenceTransformers, MCP Framework, Streamlit | Automated policy Q&A and audit checklist |
