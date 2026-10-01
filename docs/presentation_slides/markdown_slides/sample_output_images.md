# STANDALONE SAMPLE OUTPUT IMAGE ASSETS (NO BLUE BACKGROUND)

Here are the 4 clean, standalone sample output images for your **Ai_loan_acceptance_and_analyze_risk (Loan-IQ)** project, with **no blue slide background**, ready to copy or insert into any presentation template:

---

## 🖼️ Standalone Output Visual Assets

````carousel
![1. Model Training & SMOTE Execution Terminal](C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/sample_output_1_training_terminal_1789618474714.png)
<!-- slide -->
![2. Terminal Loan Evaluation & MCP Agent Output](C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/sample_output_2_evaluation_terminal_1789618491330.png)
<!-- slide -->
![3. SHAP Feature Importance Bar Chart](C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/sample_output_3_shap_bar_chart_1789618507395.png)
<!-- slide -->
![4. Stacking Classifier Performance & Metrics Report](C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/sample_output_4_classification_report_box_1789618526702.png)
````

---

### 1️⃣ Model Training & SMOTE Execution Terminal

![1. Model Training Terminal Asset](C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/sample_output_1_training_terminal_1789618474714.png)

```text
PS E:\mini-project> python scripts/train_model.py
[INFO] Loading 25,000 synthetic credit records...
[SMOTE] Applying SMOTE oversampling... Class distribution balanced (23,750 Approved / 23,750 Defaulted)

[1/4] Training XGBoost Classifier...              Best Score: 0.9612
[2/4] Training LightGBM Classifier...             Best Score: 0.9645
[3/4] Training CatBoost Classifier...             Best Score: 0.9630
[4/4] Training Random Forest...                   Best Score: 0.9580

[META] Training MLP Meta-Learner...
[SUCCESS] Stacking Ensemble Training Complete!
          Accuracy: 0.9668  |  ROC-AUC: 0.9942
          Serialized Model saved to: models/loan_model.pkl
```

---

### 2️⃣ Terminal Loan Evaluation & MCP Agent Execution Output

![2. Terminal Evaluation Asset](C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/sample_output_2_evaluation_terminal_1789618491330.png)

```text
PS E:\mini-project> python scripts/test_rules.py
Executing Loan-IQ MCP Multi-Agent Evaluation Pipeline...

Applicant Parameters:
  Bank: SBI | Scheme: Home Loan | Income: ₹12,00,000 | Requested: ₹50,00,000 | CIBIL: 780

[Agent 1 - AnomalyAgent]        Sanity & Policy Check: PASSED (0 Hard Rule Violations)
[Agent 2 - RiskAgent]           Stacking Model Score: 94.2% | FOIR: 42.5% | LTV: 76.9%
[Agent 2 - RiskAgent]           SHAP Impact: CIBIL_Score (+38.2%), FOIR (-12.1%)
[Agent 3 - RecommendationAgent] Decision: APPROVED | Action: Issue Instant Sanction Letter
[Agent 4 - PolicyAgent]         Policy Audit: SBI Home Loan Guideline Clause 4.2 Compliant
```

---

### 3️⃣ SHAP Feature Importance & Attribution Bar Chart

![3. SHAP Bar Chart Asset](C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/sample_output_3_shap_bar_chart_1789618507395.png)

---

### 4️⃣ Stacking Classifier Performance & Classification Report

![4. Classification Report Asset](C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/sample_output_4_classification_report_box_1789618526702.png)

```text
Classification Report (Stacking Ensemble Classifier):

              precision    recall  f1-score   support

    Rejected       0.96      0.97      0.96      2500
    Approved       0.97      0.96      0.97      2500

    accuracy                           0.97      5000
   macro avg       0.97      0.97      0.97      5000
weighted avg       0.97      0.97      0.97      5000

ROC-AUC Score: 0.9942
Optimal Cutoff Threshold: 0.5000
```
