# REVIEW 2 DEFENSE GUIDE: SCRIPTS FOLDER BREAKDOWN

This guide provides a complete, line-by-line explanation of all four Python scripts inside the `scripts/` directory for your **Review 2 Defense**.

---

## 📂 Overview of the `scripts/` Directory

```text
e:\flutter\Ai_loan_acceptance_and_analyze_risk\Ai_loan_acceptance_and_analyze_risk\scripts\
├── 1. generate_synthetic_data.py   <-- Generates 75,000 synthetic banking records
├── 2. train_model.py               <-- Preprocesses, applies SMOTE & trains XGBoost Stacking Model
├── 3. build_rag.py                 <-- Builds FAISS Dense Vector DB + BM25 Sparse Index from PDFs
└── 4. test_rules.py                <-- Diagnostic script testing bank rule boundary scenarios
```

---

## 1️⃣ `scripts/generate_synthetic_data.py` (Synthetic Data Generator)

### 🎯 Purpose
Generates **75,000 synthetic applicant records** (15,000 per bank across SBI, HDFC, ICICI, IOB, Canara Bank) tailored to Indian retail credit distributions and DPDP Act 2023 compliance.

### 🔑 Key Functions & Highlights
* **Demographic & Credit Features**: Generates Age (18-75), Employment Type (Salaried, Self-Employed, Agriculturist), City Tiers (`Chennai Tier 1`, `Coimbatore Tier 2`, `Rural TN Tier 3`), and Employer Categories (`Tier A Top MNC` to `Unlisted`).
* **Realistic Financial Ratios**: Calculates monthly EMI, FOIR (Fixed Obligation to Income Ratio), and LTV (Loan-to-Value).
* **New-To-Credit (NTC) Handling**: Includes a 15% probability of NTC borrowers with CIBIL = 0.
* **Bank Rule Engine**: Applies authentic underwriting cutoffs:
  * **SBI**: CIBIL ≥ 700, FOIR ≤ 65%, LTV ≤ 90%, Age 18-70.
  * **HDFC**: CIBIL ≥ 650, FOIR ≤ 60%, Age 21-65.
  * **ICICI**: CIBIL ≥ 650, FOIR ≤ 60%, LTV ≤ 85%, NTC Home Loan restricted.
  * **IOB**: CIBIL ≥ 650, Annual Income ≥ 6 Lakhs for Home Loan.
  * **Canara**: CIBIL ≥ 600, Salaried Income ≥ 15k/mo, Age 21-75.
* **Output File**: Saves dataset to `data/synthetic_loan_data.csv`.

---

## 2️⃣ `scripts/train_model.py` (Machine Learning Training Pipeline)

### 🎯 Purpose
Preprocesses the credit dataset, handles severe class imbalance using SMOTE, trains the Machine Learning Classifier, and saves `.pkl` artifacts.

### 🔑 Key Functions & Highlights
* **Preprocessing Pipeline**: Uses `ColumnTransformer` with `StandardScaler` for numerical attributes and `OneHotEncoder` for categorical features.
* **Class Balancing via SMOTE**: Applies **Synthetic Minority Over-sampling Technique (SMOTE)** to balance minority defaulted loan samples, creating an equal 50:50 training ratio.
* **Model Training**: Fits `XGBClassifier` (400 estimators, max depth 7, logloss evaluation metric).
* **Performance Metrics**: Evaluates test set performance:
  * **Accuracy**: **96.68%**
  * **ROC-AUC**: **0.9942**
* **Serialized Output Artifacts (Saved to `models/`)**:
  * `loan_model.pkl`: Trained ML Classifier.
  * `preprocessor.pkl`: Fitted `ColumnTransformer`.
  * `threshold.pkl`: Optimal cutoff threshold (`0.50`).
  * `feature_names.pkl`: Pre-transformation input column names.
  * `encoded_feature_names.pkl`: Post-encoding feature labels for SHAP TreeExplainer.

---

## 3️⃣ `scripts/build_rag.py` (FAISS & BM25 Vector Index Builder)

### 🎯 Purpose
Scans all bank policy PDFs and text files in `knowledge_base/`, chunks the text, computes vector embeddings, and builds a **Hybrid RAG Index** (FAISS Dense + BM25 Sparse).

### 🔑 Key Functions & Highlights
* **Document Ingestion**: Loads PDF and TXT files using LangChain's `DirectoryLoader`, `TextLoader`, and `PyPDFLoader`.
* **Semantic Chunking**: Uses `RecursiveCharacterTextSplitter` (chunk size 750, overlap 100) separating on structural chapter/section breaks.
* **Header-Aware Prefixing**: Prepends metadata tags to every chunk (e.g. `[INSTITUTION: SBI] [FILE: sbi_policy.txt]`) to guarantee high-precision bank retrieval.
* **Dense Embedding (FAISS)**: Encodes text using HuggingFace's `all-MiniLM-L6-v2` model and saves the index to `rag_index/faiss_index/`.
* **Sparse Keyword Index (BM25)**: Tokenizes corpus using `BM25Okapi` and saves `rag_index/bm25_index.pkl` for exact term matching.

---

## 4️⃣ `scripts/test_rules.py` (Automated Rule Testing & Verification)

### 🎯 Purpose
Acts as an automated diagnostic test suite to verify that the trained ML model and bank hard rules work accurately on edge-case applicant profiles.

### 🔑 Boundary Test Scenarios
1. **Test 1: The High Debt Applicant (FOIR 63%)**
   * *Result*: SBI approves (allows up to 65%), while HDFC, ICICI, and Canara reject (cap at 60%).
2. **Test 2: The Low CIBIL Applicant (CIBIL 620)**
   * *Result*: Canara Bank approves (allows 600+), while SBI, HDFC, and IOB reject.
3. **Test 3: Senior Citizen Applicant (Age 72)**
   * *Result*: Canara Bank approves (allows up to 75), while HDFC, ICICI, and SBI reject.

---

## 🎓 Expected Review 2 Questions on `scripts/`

### Q1: "Where does your dataset come from?"
> **Answer**: `generate_synthetic_data.py` generates 75,000 synthetic financial records adhering to Indian credit distributions and RBI guidelines. Synthetic data is used to comply with India's DPDP Act 2023 and bank secrecy laws while maintaining statistical realism.

### Q2: "Why do you run `build_rag.py` before starting the server?"
> **Answer**: `build_rag.py` processes raw policy PDFs from `knowledge_base/` into FAISS vector embeddings (`rag_index/faiss_index`) and BM25 indices (`rag_index/bm25_index.pkl`). Pre-building the index allows `app.py` to perform instant sub-10ms policy search during user queries.

### Q3: "How do you test your model's policy enforcement?"
> **Answer**: We run `test_rules.py` to simulate edge cases—such as applicants with high FOIR (63%), low CIBIL (620), or advanced age (72)—verifying that bank-specific criteria are strictly enforced by the model.
