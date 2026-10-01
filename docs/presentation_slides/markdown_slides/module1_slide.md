# MODULE 1: DATA PREPARATION AND FEATURE ENGINEERING

![Module 1 Presentation Slide](file:///C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/module1_data_prep_slide_1789581738342.png)

---

## Slide Text (100% English - Copy-Paste Ready)

```text
               DATA PREPARATION AND FEATURE ENGINEERING

❖ Load financial dataset with CIBIL score, annual income, loan amount, and asset details to build the loan risk model.

❖ Remove incomplete or corrupted financial records, like missing income or invalid credit scores, to ensure data reliability.

❖ Keep essential financial attributes such as FOIR, Loan-to-Value (LTV), Debt-to-Income (DTI), and collateral value for pattern detection.

❖ Standardize numerical features using StandardScaler and encode categorical variables using OneHotEncoder.

❖ Apply SMOTE (Synthetic Minority Over-sampling Technique) to handle class imbalance and prevent default prediction bias.
```

---

### Detailed Step-by-Step Defense Explanation

| Step | Technical Operation | Project Implementation (Loan-IQ) | Purpose & Value |
| :--- | :--- | :--- | :--- |
| **1. Data Ingestion** | Synthetic Data & Field Mapping | Loads applicant dataset with CIBIL (300-900), Income, Loan Amount, Tenure, and Assets. | Establishes the feature matrix for loan risk evaluation. |
| **2. Data Cleaning** | Imputation & Outlier Handling | Drops null values, cleans negative income entries, and caps extreme outliers. | Ensures financial data integrity before model training. |
| **3. Feature Engineering** | Financial Ratio Computation | Computes $\text{FOIR} = \frac{\text{Total Monthly Obligations}}{\text{Gross Monthly Income}}$ and $\text{LTV} = \frac{\text{Loan Amount}}{\text{Collateral Value}}$. | Captures true repayment capability beyond raw salary. |
| **4. Feature Scaling** | StandardScaler & OneHotEncoder | Scales numerical features to zero mean and unit variance; encodes employment & loan intent. | Normalizes feature scales across gradient boosting models. |
| **5. Class Balancing** | SMOTE Oversampling | Synthesizes synthetic minority (defaulted) samples to balance 95:5 class ratio. | Eliminates model bias towards over-approving risky loans. |
