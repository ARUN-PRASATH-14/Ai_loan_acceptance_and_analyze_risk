# 🏦 Loan-IQ: Autonomous Credit Risk & Policy Engine

Loan-IQ is an enterprise-grade AI credit scoring, explainability, and multi-bank policy RAG system. It combines a 2-tier Stacking Ensemble Machine Learning model (XGBoost, LightGBM, CatBoost, Random Forest + ANN Meta-Learner), SHAP explainable AI, and an **Advanced Hybrid Policy RAG Engine (FAISS + BM25)** with **Reciprocal Rank Fusion (RRF) Re-Ranking**.

---

## 📁 Codebase Directory Structure

```
c:\Users\massa\Desktop\Ai_loan_acceptance_and_analyze_risk\
├── app.py                         # Flask Web Server & AI Policy RAG Assistant API
├── index.html                     # Loan-IQ Interactive Web Application UI
├── README.md                      # Project documentation & architecture overview
│
├── models/                        # ML Model Artifacts & Scalers
│   ├── loan_model.pkl             # Trained Stacking Classifier model
│   ├── preprocessor.pkl           # ColumnTransformer (OneHot / StandardScaler)
│   ├── threshold.pkl              # Optimal decision threshold
│   ├── feature_names.pkl          # Base feature schema
│   └── encoded_feature_names.pkl  # One-Hot encoded feature schema for SHAP
│
├── rag_index/                     # Hybrid RAG Vector & Keyword Indices
│   ├── faiss_index/               # FAISS Dense Vector Database
│   └── bm25_index.pkl             # BM25 Sparse Keyword Index
│
├── knowledge_base/                # Exhaustive 10-Chapter Bank Policy Manuals
│   ├── sbi_kyc_loan_policy_manual.txt
│   ├── hdfc_kyc_loan_policy_manual.txt
│   ├── icici_kyc_loan_policy_manual.txt
│   ├── iob_kyc_loan_policy_manual.txt
│   ├── canara_kyc_loan_policy_manual.txt
│   ├── rbi_master_direction_kyc_aml_2025_2026.txt
│   └── rbi_circular_2025.txt
│
├── data/                          # Dataset Storage
│   └── synthetic_loan_data.csv    # Synthetic training dataset (10,000 records)
│
├── scripts/                       # Model Training & RAG Indexing Scripts
│   ├── generate_synthetic_data.py # Synthetic data generator script
│   ├── train_model.py             # XGBoost Model training script
│   ├── build_rag.py               # Hybrid RAG index builder script
│   └── test_rules.py              # Bank rule verification test suite
│
└── docs/                          # Project Documentation Assets
    └── README.docx                # Executive Word documentation
```

---

## ⚡ How to Run the Applications

### 1. Launch Streamlit Web Application Server
```bash
python -m streamlit run app.py
```
- Open browser at **http://localhost:8501**
- Features:
  - **Tab 1: AI Risk Engine**: Institutional bank selection (SBI, HDFC, ICICI, IOB, Canara), Location tiering (Tamil Nadu cities), FOIR/LTV calculations, SHAP Waterfall Plot, and hard rule checks.
  - **Tab 2: AI Banking & KYC Policy Assistant**: Hybrid RAG Chatbot with RRF re-ranking and vector search explorer.

### 2. View Loan-IQ Web Application (`index.html`)
- Double click or open `index.html` in any web browser.
- Features:
  - System Overview & Bilingual Tamil/English Loan Glossary (`CIBIL`, `FOIR`, `LTV`, `EMI`, `DTI`, `NTC`, `NPA`, `Moratorium`, etc.).
  - Preset Applicant Buttons (Low Risk SBI Home Loan, High Risk HDFC Personal Loan, Canara NTC Loan).
  - Dynamic Form with instantaneous rule evaluation & SHAP Bar Chart breakdown.
  - Policy RAG Q&A Assistant.
  - A4 Landscape PDF Print export.

### 3. Re-build Hybrid RAG Vector & BM25 Index
```bash
python build_rag.py
```

### 4. Run Policy Rule Unit Tests
```bash
python test_rules.py
```
