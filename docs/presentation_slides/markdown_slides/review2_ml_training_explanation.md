# SIMPLE GUIDE: HOW ML MODELS ARE TRAINED & PROCESSED (REVIEW 2)

This guide provides a simple, easy-to-understand breakdown of how machine learning models are trained in `scripts/train_model.py` and how algorithms process applicant data in `app.py` for your **Review 2 Defense**.

---

## 💡 The Simple 3-Expert Analogy

Imagine a bank with **4 Senior Credit Experts (Base Models)** and **1 Chief Credit Officer (Meta-Learner)**:

```text
                  +-----------------------------------+
                  |        APPLICANT FEATURES         |
                  | (CIBIL 780, Income 12L, FOIR 42%) |
                  +-----------------------------------+
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
  [ Expert 1: XGBoost ]    [ Expert 2: LightGBM ]    [ Expert 3: CatBoost ]
  (Complex Patterns)       (Fast Number Analysis)    (Category Specialist)
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    ▼
                     [ Chief Officer: MLP Meta-Learner ]
                     (Blends all opinions into 94.2%)
                                    │
                                    ▼
                    FINAL DECISION: ⚡ APPROVED (94.2%)
```

---

## 🛠️ Step 1: How the Models are Trained (`scripts/train_model.py`)

### Phase 1: Data Preparation & Preprocessing
* **The Problem**: Machine Learning algorithms do not understand text words like `"Salaried"` or raw rupee numbers like `₹12,00,000`.
* **The Solution (`preprocessor.pkl`)**:
  1. **`StandardScaler`**: Normalizes large numbers (Income ₹12,00,000, Loan ₹50,00,000) so they don't overpower small numbers (Age 32, CIBIL 780).
  2. **`OneHotEncoder`**: Converts category text into 0s and 1s (`Employment_Salaried = 1`, `Employment_SelfEmployed = 0`).

---

### Phase 2: Solving Default Bias with SMOTE
* **The Problem (Class Imbalance)**: In real credit data, 95% of applicants repay loans and only 5% default. If trained on raw data, the AI would blindly approve everyone just to get 95% accuracy!
* **The Solution (SMOTE)**:
  * **Synthetic Minority Over-sampling Technique (SMOTE)** finds default cases, draws mathematical lines between them, and creates synthetic default examples until the dataset is balanced **50% Approved / 50% Defaulted**.
  * **SMOTE Formula**: $$X_{\text{new}} = X_i + \lambda(X_{zi} - X_i)$$

---

### Phase 3: Stacking Ensemble Algorithm Training
We train four diverse algorithms on the balanced dataset:
1. **XGBoost**: Gradient boosted decision trees optimizing log-loss.
2. **LightGBM**: Fast leaf-wise tree growth for high numerical precision.
3. **CatBoost**: Specialized categorical feature target encoding.
4. **Random Forest**: Bagged decision tree voting ensemble.
5. **ANN / MLP Meta-Learner**: Neural network taking base predictions and learning the final master decision.

* **Result**: **96.68% Training Accuracy** & **0.9942 ROC-AUC Score**!
* **Saved Models**: Saved to `models/loan_model.pkl` and `models/preprocessor.pkl`.

---

## ⚡ Step 2: How Algorithms Process a New Applicant (`app.py`)

When an applicant fills out the loan form and clicks **"Evaluate Application"**:

```text
[1. RAW INPUT]  --->  [2. PREPROCESSOR]  --->  [3. STACKING MODEL]  --->  [4. SHAP XAI ENGINE]
Age: 32               StandardScaler           XGBoost  : 0.95            CIBIL 780 -> +38.2%
Income: 12L           OneHotEncoder            LightGBM : 0.94            Income 12L -> +19.8%
CIBIL: 780            Features -> Vector       CatBoost : 0.93            FOIR 42.5% -> -12.1%
                                               Meta-MLP : 94.2%           (Generates Waterfall Chart)
                                               STATUS   : APPROVED
```

1. **Preprocessing (`preprocessor.pkl`)**: Converts raw applicant data into a normalized feature vector $X$.
2. **Stacking Ensemble Inference (`loan_model.pkl`)**: Base algorithms evaluate features and MLP Meta-Learner computes final approval probability ($94.2\%$).
3. **Threshold Decision (`threshold.pkl`)**: Since $94.2\% \ge 50\%$, Status = **APPROVED**.
4. **SHAP Explainability (`shap.TreeExplainer`)**: Calculates exact Shapley attributions explaining **WHY** the loan was approved:
   * **CIBIL Score (780)**: **+38.2%** (Major approval driver).
   * **Annual Income (12L)**: **+19.8%** (Positive approval driver).
   * **FOIR Ratio (42.5%)**: **-12.1%** (Small risk penalty).

---

## 🎓 Simple Defense Script for Review 2

> *"Respected Examiners, our ML pipeline uses a 2-Level Stacking Ensemble. First, we preprocess raw financial data using `StandardScaler` and `OneHotEncoder`. To prevent default approval bias caused by 95:5 class imbalance, we apply `SMOTE` oversampling to balance the dataset 50:50.*
>
> *We train four base classifiers—XGBoost, LightGBM, CatBoost, and Random Forest—and combine their outputs using an ANN Meta-Learner, achieving 96.68% accuracy. When an applicant submits data, the Stacking Model predicts approval probability, and SHAP calculates Shapley feature attributions to show positive approval drivers in green and risk penalties in red."*
