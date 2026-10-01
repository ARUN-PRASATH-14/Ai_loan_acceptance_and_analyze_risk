import os
import sys
import warnings

# Suppress scikit-learn version mismatch & non-critical warnings
warnings.filterwarnings("ignore")

# Configure UTF-8 output encoding for Windows compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import re
import pickle
import numpy as np
import pandas as pd
import shap
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from dotenv import load_dotenv
load_dotenv()

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
static_dir = "dist" if os.path.exists("dist") else "."
app = Flask(__name__, static_folder="dist", static_url_path="")
app.json.ensure_ascii = False
CORS(app)

# Initialize Groq API Client from Environment Variables
client = None
groq_api_key = os.getenv("GROQ_API_KEY", "")
groq_model = os.getenv("GROQ_MODEL", "llama3-70b-8192")

if groq_api_key:
    try:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_api_key,
            timeout=8.0
        )
        print(f"🚀 Groq API Client initialized using model: {groq_model}")
    except Exception as e:
        print(f"Could not initialize Groq client: {e}")

# Load ML & RAG Models
print("Loading Stacking ML Classifier and SHAP explainer...")
MODELS_DIR = "models" if os.path.exists("models") else "."
RAG_DIR = "rag_index" if os.path.exists("rag_index") else "."

model_path = os.path.join(MODELS_DIR, "loan_model.pkl")
prep_path = os.path.join(MODELS_DIR, "preprocessor.pkl")
thresh_path = os.path.join(MODELS_DIR, "threshold.pkl")
feat_path = os.path.join(MODELS_DIR, "feature_names.pkl")
enc_path = os.path.join(MODELS_DIR, "encoded_feature_names.pkl")

model = pickle.load(open(model_path, "rb"))
preprocessor = pickle.load(open(prep_path, "rb"))
THRESHOLD = pickle.load(open(thresh_path, "rb"))
feature_names = pickle.load(open(feat_path, "rb"))
encoded_features = pickle.load(open(enc_path, "rb"))
explainer = shap.TreeExplainer(model)

print("Loading FAISS & BM25 Hybrid RAG components...")
try:
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu', 'local_files_only': True},
        encode_kwargs={'normalize_embeddings': True}
    )
except Exception:
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

faiss_path = os.path.join(RAG_DIR, "faiss_index") if os.path.exists(os.path.join(RAG_DIR, "faiss_index")) else "faiss_index"
vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)

bm25_data = None
bm25_path = os.path.join(RAG_DIR, "bm25_index.pkl") if os.path.exists(os.path.join(RAG_DIR, "bm25_index.pkl")) else "bm25_index.pkl"
if os.path.exists(bm25_path):
    with open(bm25_path, "rb") as f:
        bm25_data = pickle.load(f)

def expand_user_query(query: str) -> str:
    """Enriches simple user queries with domain synonyms and bank tags."""
    q_lower = query.lower()
    expansions = []
    
    if "sbi" in q_lower: expansions.append("State Bank of India SBI")
    if "hdfc" in q_lower: expansions.append("HDFC Bank")
    if "icici" in q_lower: expansions.append("ICICI Bank")
    if "iob" in q_lower: expansions.append("Indian Overseas Bank IOB")
    if "canara" in q_lower: expansions.append("Canara Bank")
    
    if "home" in q_lower or "house" in q_lower: expansions.append("Home Loan Housing Mortgage LTV FOIR Property")
    if "personal" in q_lower or "salary" in q_lower: expansions.append("Personal Loan Net Income Monthly Salary FOIR")
    if "kcc" in q_lower or "farm" in q_lower or "agri" in q_lower: expansions.append("Kisan Credit Card KCC Agriculture Scale of Finance Collateral Free Subvention Prompt Repayment")
    if "edu" in q_lower or "student" in q_lower or "college" in q_lower: expansions.append("Education Loan Student Moratorium Premier Institute Vidya Scholar")
    if "kyc" in q_lower or "doc" in q_lower or "ovd" in q_lower: expansions.append("KYC Officially Valid Documents Aadhaar PAN V-CIP Periodic Updation 2025 2026")
    if "cibil" in q_lower or "score" in q_lower: expansions.append("CIBIL score threshold credit score bureau")
    if "ntc" in q_lower or "no credit" in q_lower or "new to credit" in q_lower: expansions.append("New To Credit NTC first time borrower zero history")
    if "age" in q_lower: expansions.append("minimum entry age maximum exit age threshold years mature")
    
    return f"{query} {' '.join(expansions)}" if expansions else query

def hybrid_rrf_search(query: str, top_k=5):
    """Executes Hybrid Search (FAISS Dense + BM25 Sparse) and Reciprocal Rank Fusion (RRF) Re-Ranking with Bank-Aware Boosting."""
    if not vectorstore:
        return []
        
    enriched_query = expand_user_query(query)
    q_lower = query.lower()
    
    target_banks = []
    if "sbi" in q_lower: target_banks.append("SBI")
    if "hdfc" in q_lower: target_banks.append("HDFC BANK")
    if "icici" in q_lower: target_banks.append("ICICI BANK")
    if "iob" in q_lower: target_banks.append("IOB")
    if "canara" in q_lower: target_banks.append("CANARA BANK")
    if "rbi" in q_lower: target_banks.append("RBI MASTER DIRECTION")

    # 1. Dense Vector Search (FAISS)
    dense_docs = vectorstore.similarity_search(enriched_query, k=10)
    
    # 2. Sparse BM25 Search
    sparse_docs = []
    if bm25_data and "bm25" in bm25_data:
        bm25 = bm25_data["bm25"]
        chunks = bm25_data["chunks"]
        tokens = re.findall(r'\w+', enriched_query.lower())
        if tokens:
            scores = bm25.get_scores(tokens)
            top_indices = np.argsort(scores)[::-1][:10]
            sparse_docs = [chunks[idx] for idx in top_indices if scores[idx] > 0]

    # 3. Reciprocal Rank Fusion (RRF) Re-Ranking with Bank-Aware Boosting
    rrf_scores = {}
    doc_map = {}
    
    for rank, doc in enumerate(dense_docs):
        doc_key = doc.page_content[:150]
        doc_map[doc_key] = doc
        bank_tag = doc.metadata.get('bank', '')
        boost = 1.5 if any(tb in bank_tag.upper() for tb in target_banks) else 1.0
        rrf_scores[doc_key] = rrf_scores.get(doc_key, 0.0) + (1.0 / (60 + rank + 1)) * boost
        
    for rank, doc in enumerate(sparse_docs):
        doc_key = doc.page_content[:150]
        doc_map[doc_key] = doc
        bank_tag = doc.metadata.get('bank', '')
        boost = 1.5 if any(tb in bank_tag.upper() for tb in target_banks) else 1.0
        rrf_scores[doc_key] = rrf_scores.get(doc_key, 0.0) + (1.0 / (60 + rank + 1)) * boost
        
    sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
    
    results = []
    for k in sorted_keys[:top_k]:
        results.append((doc_map[k], rrf_scores[k]))
        
    return results

def apply_bank_hard_rules(bank, loan_type, age, income, co_applicant_income, cibil, foir, ltv, emp_years, business_vintage, course_approved, emp_type, employer, tn_city, existing_customer):
    violations = []
    cibil_leniency = 50 if existing_customer else 0
    foir_leniency = 0.05 if existing_customer else 0.0
    if employer == "Tier A (Top MNC)": foir_leniency += 0.05
    
    income_multiplier = 1.0
    if "Tier 1" in tn_city: income_multiplier = 1.2
    if "Tier 3" in tn_city: income_multiplier = 0.8
    
    if bank == "SBI":
        if age < 18 or age > 70: violations.append("Age outside SBI criteria (18-70 years)")
        if cibil != 0 and cibil < (650 - cibil_leniency): violations.append(f"SBI requires CIBIL ≥ {650-cibil_leniency}")
        if cibil == 0 and loan_type == "Personal Loan" and income/12 < (30000 * income_multiplier): violations.append(f"NTC Personal Loan requires ₹{int(30000*income_multiplier):,}/mo income in {tn_city}")
        if foir > (0.65 + foir_leniency): violations.append(f"FOIR ({foir:.1%}) exceeds SBI's limit ({0.65+foir_leniency:.1%})")
        if loan_type == "Home Loan" and ltv > 0.90: violations.append("LTV exceeds SBI limit (90%)")
        if emp_type == "Self-employed" and business_vintage < 3: violations.append("SBI requires 3+ years business vintage")
        if emp_type == "Salaried" and emp_years < 1: violations.append("SBI requires 1+ year employment")
        if loan_type == "Personal Loan" and income/12 < (20000 * income_multiplier): violations.append(f"SBI Personal Loan requires net income ≥ ₹{int(20000*income_multiplier):,}/mo in {tn_city}")
            
    elif bank == "HDFC":
        if age < 21 or age > 65: violations.append("Age outside HDFC criteria (21-65 years)")
        if cibil != 0 and foir > (0.60 + foir_leniency): violations.append(f"FOIR ({foir:.1%}) exceeds HDFC's limit ({0.60+foir_leniency:.1%})")
        if cibil == 0 and foir > 0.50: violations.append(f"NTC FOIR ({foir:.1%}) exceeds HDFC's strict 50% limit")
        if cibil != 0 and cibil < (650 - cibil_leniency): violations.append(f"HDFC requires CIBIL ≥ {650-cibil_leniency}")
        if emp_type == "Self-employed" and business_vintage < 2: violations.append("HDFC requires 2+ years business vintage")
        if emp_type == "Salaried" and (income/12 < (25000 * income_multiplier) and loan_type == "Personal Loan"): violations.append(f"HDFC Personal Loan requires net income ≥ ₹{int(25000*income_multiplier):,}/mo in {tn_city}")
        if loan_type == "Home Loan" and ltv > 0.90: violations.append("LTV exceeds HDFC limit (90%)")
        if loan_type == "Education Loan" and not course_approved: violations.append("Institution/Course not approved by HDFC")
            
    elif bank == "ICICI":
        if age < 20 or age > 65: violations.append("Age outside ICICI criteria (20-65 years)")
        if emp_type == "Salaried" and income/12 < (25000 * income_multiplier): violations.append(f"ICICI requires salaried income ≥ ₹{int(25000*income_multiplier):,}/mo in {tn_city}")
        if cibil != 0 and cibil < (650 - cibil_leniency): violations.append(f"ICICI requires CIBIL ≥ {650-cibil_leniency}")
        if cibil == 0 and loan_type == "Home Loan": violations.append("ICICI does not allow NTC Home Loans")
        if foir > (0.60 + foir_leniency): violations.append(f"FOIR ({foir:.1%}) exceeds ICICI's limit ({0.60+foir_leniency:.1%})")
        if loan_type == "Home Loan" and ltv > 0.85: violations.append("LTV exceeds ICICI limit (85%)")

    elif bank == "IOB":
        if age < 21 or age > 70: violations.append("Age outside IOB criteria (21-70 years)")
        if loan_type == "Home Loan" and income < (600000 * income_multiplier): violations.append(f"IOB Home Loan requires annual income ≥ ₹{int(600000*income_multiplier):,} in {tn_city}")
        if cibil != 0 and cibil < (650 - cibil_leniency): violations.append(f"IOB requires CIBIL ≥ {650-cibil_leniency}")
        if foir > (0.60 + foir_leniency): violations.append(f"FOIR ({foir:.1%}) exceeds IOB's limit ({0.60+foir_leniency:.1%})")
        if loan_type == "Home Loan" and ltv > 0.90: violations.append("LTV exceeds IOB limit (90%)")
        if emp_type == "Salaried" and emp_years < 2: violations.append("IOB requires 2+ years employment")
            
    elif bank == "Canara":
        if age < 21 or age > 75: violations.append("Age outside Canara criteria (21-75 years)")
        if emp_type == "Salaried" and income/12 < (15000 * income_multiplier): violations.append(f"Canara requires salaried income ≥ ₹{int(15000*income_multiplier):,}/mo in {tn_city}")
        if emp_years < 2 and emp_type == "Salaried": violations.append("Canara requires 2+ years employment")
        if cibil != 0 and cibil < (600 - cibil_leniency): violations.append(f"Canara requires CIBIL ≥ {600-cibil_leniency}")
        if foir > (0.60 + foir_leniency): violations.append(f"FOIR ({foir:.1%}) exceeds Canara's limit ({0.60+foir_leniency:.1%})")
        if loan_type == "Home Loan" and ltv > 0.90: violations.append("LTV exceeds Canara limit (90%)")

    return violations

# --- API ROUTES ---

# =====================================================================
# MCP MULTI-AGENT ORCHESTRATION LAYER (4 DEDICATED MCP AGENTS)
# =====================================================================

# =====================================================================
# MCP MULTI-AGENT ORCHESTRATION LAYER (4 DEDICATED MCP AGENTS)
# =====================================================================

class AnomalyAgent:
    """Agent 1: Anomaly & Security MCP Agent (mcp_anomaly_check_tool)"""
    @staticmethod
    def run_anomaly_check_tool(data: dict) -> tuple[list, list]:
        """Validates payload sanity & executes bank policy hard rule engine."""
        anomalies = []
        age = int(data.get("age", 30))
        income = float(data.get("income", 1200000))
        loan_amt = float(data.get("loan_amt", 5000000))
        cibil = int(data.get("cibil", 780))
        
        if age < 18 or age > 100: anomalies.append("Invalid applicant age")
        if income <= 0: anomalies.append("Zero or negative annual income")
        if loan_amt <= 0: anomalies.append("Invalid loan amount requested")
        if cibil < 0 or (cibil > 0 and cibil < 300) or cibil > 900: anomalies.append("Out-of-bounds CIBIL score")

        bank = data.get("bank", "SBI")
        loan_type = data.get("loan_type", "Home Loan")
        co_app_inc = float(data.get("co_app_inc", 0))
        exist_emi = float(data.get("exist_emi", 0))
        prop_val = float(data.get("prop_val", 0))
        emp_years = int(data.get("emp_years", 3))
        business_vintage = int(data.get("business_vintage", 0))
        course_approved = bool(data.get("course_approved", True))
        emp_type = data.get("emp_type", "Salaried")
        employer = data.get("employer", "Tier B (Mid-Size)")
        tn_city = data.get("tn_city", "Chennai (Tier 1)")
        existing_customer = bool(data.get("existing_customer", False))
        int_rate = float(data.get("int_rate", 8.5))
        tenure_mo = int(data.get("tenure_mo", 240))
        
        monthly_rate = int_rate / 100 / 12
        proposed_emi = (loan_amt * monthly_rate * (1 + monthly_rate)**tenure_mo) / ((1 + monthly_rate)**tenure_mo - 1) if monthly_rate > 0 else loan_amt / tenure_mo
        total_monthly_income = (income + co_app_inc) / 12
        foir = (exist_emi + proposed_emi) / total_monthly_income if total_monthly_income > 0 else 1.0
        if prop_val > 0:
            prop_val_calc = prop_val * 100000.0 if prop_val < 1000 else prop_val
            ltv = min(1.0, loan_amt / prop_val_calc) if prop_val_calc > 0 else 0.0
        else:
            ltv = 0.0

        violations = apply_bank_hard_rules(
            bank, loan_type, age, income, co_app_inc, cibil, foir, ltv, 
            emp_years, business_vintage, course_approved, emp_type, employer, tn_city, existing_customer
        )
        return anomalies, violations

class RiskAgent:
    """Agent 2: Risk Scoring & ML MCP Agent (mcp_risk_scoring_tool & SHAP)"""
    @staticmethod
    def run_risk_scoring_tool(data: dict, preprocessor, model, feature_names, threshold: float):
        """Preprocesses input data and runs Stacking ML Ensemble prediction."""
        bank = data.get("bank", "SBI")
        loan_type = data.get("loan_type", "Home Loan")
        age = int(data.get("age", 30))
        income = float(data.get("income", 1200000))
        co_app_inc = float(data.get("co_app_inc", 300000))
        loan_amt = float(data.get("loan_amt", 5000000))
        tenure_mo = int(data.get("tenure_mo", 240))
        int_rate = float(data.get("int_rate", 8.5))
        is_ntc = bool(data.get("is_ntc", False))
        cibil = 0 if is_ntc else int(data.get("cibil", 780))
        exist_emi = float(data.get("exist_emi", 15000))
        prop_val = float(data.get("prop_val", 6500000))
        emp_years = int(data.get("emp_years", 5))
        business_vintage = int(data.get("business_vintage", 0))
        course_approved = bool(data.get("course_approved", True))
        emp_type = data.get("emp_type", "Salaried")
        employer = data.get("employer", "Tier B (Mid-Size)")
        tn_city = data.get("tn_city", "Chennai (Tier 1)")
        gender = data.get("gender", "Male")
        existing_customer = bool(data.get("existing_customer", False))

        monthly_rate = int_rate / 100 / 12
        proposed_emi = (loan_amt * monthly_rate * (1 + monthly_rate)**tenure_mo) / ((1 + monthly_rate)**tenure_mo - 1) if monthly_rate > 0 else loan_amt / tenure_mo
        total_monthly_income = (income + co_app_inc) / 12
        foir = (exist_emi + proposed_emi) / total_monthly_income if total_monthly_income > 0 else 1.0
        if prop_val > 0:
            prop_val_calc = prop_val * 100000.0 if prop_val < 1000 else prop_val
            ltv = min(1.0, loan_amt / prop_val_calc) if prop_val_calc > 0 else 0.0
        else:
            ltv = 0.0

        input_data = {
            "Bank": bank, "Loan_Type": loan_type, "TN_City": tn_city,
            "Employer_Category": employer, "Gender": gender, "Employment_Type": emp_type,
            "Existing_Customer": 1 if existing_customer else 0, "Age": age,
            "Annual_Income": income, "Co_Applicant_Income": co_app_inc,
            "Loan_Amount": loan_amt, "Tenure_Months": tenure_mo, "Interest_Rate": int_rate,
            "CIBIL_Score": cibil, "Existing_EMI": exist_emi, "FOIR": foir, "LTV": ltv,
            "Employment_Years": emp_years, "Business_Vintage": business_vintage, "Course_Approved": 1 if course_approved else 0
        }

        df_in = pd.DataFrame([input_data])[feature_names]
        df_processed = preprocessor.transform(df_in)
        prob = float(model.predict_proba(df_processed)[0][1])

        return {
            "probability": prob, "foir": foir, "ltv": ltv,
            "proposed_emi": proposed_emi, "df_processed": df_processed
        }

    @staticmethod
    def run_shap_explainer_tool(explainer, df_processed, encoded_features):
        """Computes local SHAP waterfall feature impact attributions."""
        shap_values = explainer(df_processed)
        vals = shap_values.values[0]
        sorted_indices = np.argsort(np.abs(vals))[::-1][:6]
        top_labels = [str(encoded_features[idx]) for idx in sorted_indices]
        top_values = [round(float(vals[idx]) * 100, 2) for idx in sorted_indices]
        return {"labels": top_labels, "values": top_values}

class RecommendationAgent:
    """Agent 3: Recommendation MCP Agent (mcp_recommendation_tool)"""
    @staticmethod
    def run_recommendation_tool(bank: str, loan_type: str, approved: bool, is_hard_rejected: bool, prob: float, foir: float, cibil: int, is_ntc: bool, violations: list):
        """Generates AI decision rationale & actionable improvement recommendations."""
        recommendations = []
        if approved:
            recommendations.append(f"🟢 **High Approval Score ({round(prob * 100, 1)}%)**: Strong credit profile matching {bank} underwriting standards.")
            if foir < 0.50:
                recommendations.append(f"🟢 **Optimal Debt Burden (FOIR {round(foir * 100, 1)}%)**: Monthly EMI obligations are well within acceptable income limits.")
            if cibil >= 750:
                recommendations.append(f"🟢 **Strong Credit Bureau Score ({cibil})**: Qualifies applicant for preferential interest rate discounts.")
            elif is_ntc:
                recommendations.append("ℹ️ **New To Credit (NTC)**: Approved based on robust monthly income and low obligation ratio.")
            recommendations.append("📋 **Recommended Action**: Proceed to instant sanction letter generation & KYC document collection.")
        else:
            if is_hard_rejected:
                recommendations.append(f"🔴 **Hard Policy Breach**: Application violated baseline policy rules for {bank} {loan_type}.")
                for v in violations:
                    if "CIBIL" in v:
                        recommendations.append("💡 **Actionable Fix**: Pay off credit card balances/overdues to raise CIBIL above requirement, or add a co-applicant with score ≥ 700.")
                    elif "FOIR" in v:
                        recommendations.append("💡 **Actionable Fix**: Increase loan tenure (months) or reduce requested loan amount to lower monthly EMI.")
                    elif "LTV" in v:
                        recommendations.append("💡 **Actionable Fix**: Increase down payment / property equity contribution to reduce loan-to-value ratio below threshold.")
                    elif "Income" in v or "income" in v or "NTC" in v:
                        recommendations.append("💡 **Actionable Fix**: Add a salaried co-applicant (spouse/parent) to increase combined household income.")
                    elif "vintage" in v or "employment" in v:
                        recommendations.append("💡 **Actionable Fix**: Apply with an eligible co-applicant or consider banks with lower vintage requirements (e.g. Canara Bank).")
            else:
                recommendations.append(f"🟡 **Borderline Credit Score ({round(prob * 100, 1)}%)**: Risk model score fell below approval threshold.")
                recommendations.append("💡 **Actionable Fix**: Clear active EMIs or reduce loan request by 10-15% to boost approval score.")
        return recommendations

class PolicyAgent:
    """Agent 4: Policy MCP Agent (mcp_policy_lookup_tool)"""
    @staticmethod
    def run_policy_lookup_tool(prompt: str, context: dict = None):
        """Performs hybrid RRF retrieval & bank policy Q&A orchestration."""
        return _local_policy_synthesize(prompt, [], [], context)

@app.route("/api/evaluate", methods=["POST"])
def evaluate_loan():
    try:
        data = request.get_json(silent=True) or {}
        bank = data.get("bank", "SBI")
        loan_type = data.get("loan_type", "Home Loan")
        existing_customer = bool(data.get("existing_customer", False))
        employer = data.get("employer", "Tier B (Mid-Size)")
        cibil = int(data.get("cibil", 780)) if not data.get("is_ntc") else 0
        is_ntc = bool(data.get("is_ntc", False))
        
        # 1. MCP AGENT 1: Anomaly Agent
        anomalies, violations = AnomalyAgent.run_anomaly_check_tool(data)
        
        # 2. MCP AGENT 2: Risk Agent (Risk Scoring & SHAP)
        risk_res = RiskAgent.run_risk_scoring_tool(data, preprocessor, model, feature_names, THRESHOLD)
        prob = risk_res["probability"]
        foir = risk_res["foir"]
        ltv = risk_res["ltv"]
        proposed_emi = risk_res["proposed_emi"]
        df_processed = risk_res["df_processed"]

        is_hard_rejected = len(violations) > 0
        approved = (prob >= THRESHOLD) and not is_hard_rejected

        shap_res = RiskAgent.run_shap_explainer_tool(explainer, df_processed, encoded_features)
        top_labels = shap_res["labels"]
        top_values = shap_res["values"]

        # 3. MCP AGENT 3: Recommendation Agent
        recommendations = RecommendationAgent.run_recommendation_tool(
            bank, loan_type, approved, is_hard_rejected, prob, foir, cibil, is_ntc, violations
        )

        audit_notes = []
        if approved:
            audit_notes.append(f"[PASS] Applicant met all {bank} {loan_type} baseline criteria.")
            if existing_customer: audit_notes.append("[INFO] Granted leniency for Salary Account relationship.")
            if employer == "Tier A (Top MNC)": audit_notes.append("[INFO] Granted FOIR leniency for Tier A Employer.")
        else:
            for v in violations:
                audit_notes.append(f"[FAIL] {v}")

        return jsonify({
            "approved": approved,
            "is_hard_rejected": is_hard_rejected,
            "probability": round(0.0 if is_hard_rejected else prob * 100, 1),
            "foir": round(foir * 100, 1),
            "ltv": round(ltv * 100, 1) if loan_type == "Home Loan" else "N/A",
            "proposed_emi": round(proposed_emi),
            "violations": violations,
            "audit_notes": audit_notes,
            "recommendations": recommendations,
            "shap": {
                "labels": top_labels,
                "values": top_values
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat_rag():
    prompt = ""
    try:
        data = request.get_json(silent=True) or {}
        prompt = data.get("prompt", "").strip()
        eval_ctx = data.get("context", {})
        
        eval_info = ""
        if eval_ctx and isinstance(eval_ctx, dict) and eval_ctx.get("bank"):
            res_status = "APPROVED" if eval_ctx.get("approved") else "REJECTED"
            viols = eval_ctx.get("violations", [])
            viols_text = "; ".join(viols) if viols else "None (Applicant met baseline criteria)."
            eval_info = f"\nLATEST APPLICANT EVALUATION CONTEXT:\n- Target Bank: {eval_ctx.get('bank')}\n- Loan Scheme: {eval_ctx.get('loan_type')}\n- Final Decision: {res_status}\n- AI Score: {eval_ctx.get('probability')}%\n- Calculated FOIR: {eval_ctx.get('foir')}%\n- Calculated LTV: {eval_ctx.get('ltv')}\n- Applicant CIBIL: {eval_ctx.get('cibil')}\n- Hard Policy Violations: {viols_text}\n"

        # 0. Detect Greetings, Personal Name Introductions & General Small Talk
        prompt_clean = prompt.lower().strip()
        
        name_match = re.search(r"^(?:my\s+name\s+is|i\s+am|myself|this\s+is)\s+([a-zA-Z\s]+)[\.\!\?]*$", prompt_clean)
        if name_match:
            raw_name = name_match.group(1).strip().title()
            return jsonify({
                "answer": f"Hello **{raw_name}**! 👋 Welcome to your **Loan-IQ Banking & Policy AI Assistant**.\n\nI can help you check loan eligibility criteria, interest rates, CIBIL score rules, and document requirements for **SBI, HDFC Bank, ICICI Bank, IOB, and Canara Bank**.\n\n**Try asking me questions like:**\n• \"What is the minimum income for an SBI Personal Loan?\"\n• \"What are ICICI Bank's CIBIL score requirements for Home Loans?\"\n• \"Canara Bank Education Loan interest rates and collateral limits\"\n• \"What is the FOIR limit for HDFC Bank?\"\n\nHow can I assist you with loan policies today, {raw_name}?",
                "sources": [],
                "query_expansion": prompt
            })

        GREETINGS = {"hi", "hello", "hey", "hola", "namaste", "hi there", "hello there", "good morning", "good afternoon", "good evening", "help"}
        SMALLTALK_PATTERNS = [
            r"^(hi|hello|hey|hola|namaste)(\s+there|\s+bot)?[\.\!\?]*$",
            r"^who\s+are\s+you[\.\!\?]*$",
            r"^what\s+can\s+you\s+do[\.\!\?]*$",
            r"^help(\s+me)?[\.\!\?]*$",
            r"^(thanks|thank\s+you|thx)[\.\!\?]*$",
            r"^good\s+(morning|afternoon|evening|day)[\.\!\?]*$",
            r"^how\s+are\s+you[\.\!\?]*$"
        ]

        if prompt_clean in GREETINGS or any(re.match(p, prompt_clean) for p in SMALLTALK_PATTERNS):
            return jsonify({
                "answer": "Hello! 👋 I am your **Loan-IQ Banking & Policy AI Assistant**.\n\nI can help you check loan eligibility criteria, interest rates, CIBIL score rules, and document requirements for **SBI, HDFC Bank, ICICI Bank, IOB, and Canara Bank**.\n\n**Try asking me questions like:**\n• \"What is the minimum income for an SBI Personal Loan?\"\n• \"What are ICICI Bank's CIBIL score requirements for Home Loans?\"\n• \"Canara Bank Education Loan interest rates and collateral limits\"\n• \"What is the FOIR limit for HDFC Bank?\"\n\nHow can I help you today?",
                "sources": [],
                "query_expansion": prompt
            })

        # 0B. STRICT DOMAIN GUARDRAIL (Python Code Firewall)
        BANKING_KEYWORDS = {
            "loan", "loans", "bank", "banks", "cibil", "credit", "foir", "ltv", "interest", "rate", "rates", 
            "income", "salary", "emi", "emis", "sbi", "hdfc", "icici", "iob", "canara", "rbi", "kyc", "ovd", "ovds",
            "v-cip", "tenure", "age", "eligibility", "document", "documents", "applicant", "mortgage", 
            "kcc", "agriculture", "education", "moratorium", "pension", "ntc", "borrower", "borrowers",
            "collateral", "underwriting", "policy", "policies", "reject", "rejection", "approve", "approval", 
            "score", "statement", "home", "personal", "scheme", "housing", "ratio", "margin", "vintage",
            "employment", "business", "co-applicant", "rule", "rules", "guideline", "guidelines", "limit", "limits",
            "why", "result", "rejected", "approved", "decision", "evaluation", "reason", "reasons",
            "student", "students", "study", "studies", "college", "university", "course", "courses", "fees", "fee",
            "subsidy", "vidyalaxmi", "scholarship", "salaried", "self-employed", "farmer", "farmers", "agriculturist",
            "pensioner", "co-borrower", "guarantor"
        }

        prompt_words = set(re.findall(r'\w+', prompt_clean))
        is_banking_related = bool(prompt_words & BANKING_KEYWORDS) or bool(eval_info)

        if not is_banking_related:
            return jsonify({
                "answer": "⛔ **Off-Topic Query Prohibited**\n\nI am exclusively trained as a **Retail Banking & Loan Policy AI Assistant** for this project. I am strictly prohibited from answering general knowledge, personal, political, sports, celebrity, or non-banking questions (such as inquiries about political leaders, weather, or sports figures).\n\n**Please ask questions related to Indian Retail Banking, such as:**\n• \"What is the minimum CIBIL score required for SBI Home Loan?\"\n• \"What are HDFC Bank's personal loan eligibility rules?\"\n• \"What are the RBI Master Direction guidelines for KYC OVDs?\"",
                "sources": [],
                "query_expansion": prompt
            })

        # 1. Hybrid Search + RRF Re-Ranking
        hybrid_results = hybrid_rrf_search(prompt, top_k=4)
        
        rag_context = ""
        retrieved_sources = []
        clean_text_snippets = []
        
        for i, (doc, rrf_score) in enumerate(hybrid_results):
            raw_source = doc.metadata.get("source", "Unknown Policy Document")
            clean_source = os.path.basename(raw_source).replace(".txt", "").replace("_", " ").upper()
            bank_tag = doc.metadata.get("bank", "REGULATORY")
            retrieved_sources.append({
                "document": clean_source,
                "bank": bank_tag,
                "score": round(rrf_score, 4),
                "snippet": doc.page_content[:350]
            })
            clean_text_snippets.append(doc.page_content)
            rag_context += f"[{clean_source}]\n{doc.page_content}\n\n"

        # 1B. INSTANT SYNTHESIS FALLBACK (Only when LLM client is unavailable or explicit result query)
        is_result_query = any(w in prompt_clean for w in ["accepted", "approved", "rejected", "declined", "why was my", "why my"])
        if not client and (bool(eval_info) or is_result_query):
            answer = _local_policy_synthesize(prompt, clean_text_snippets, retrieved_sources, eval_ctx)
            return jsonify({
                "answer": answer,
                "sources": retrieved_sources,
                "query_expansion": expand_user_query(prompt)
            })

        answer = None
        
        # 2. Execute Groq LLM Completion with Bank Policy PDF Chunks & Applicant Assessment Context
        if client:
            candidate_models = [
                groq_model,
                "llama3-70b-8192",
                "llama3-8b-8192",
                "gemma2-9b-it",
                "mixtral-8x7b-32768"
            ]
            
            SYSTEM_PROMPT = f"""YOU ARE AN EXPERT RETAIL BANKING & LOAN POLICY AI ASSISTANT POWERED BY GROQ & LLAMA-3.3-70B FOR THIS LOAN-IQ PLATFORM.

CRITICAL DIRECTIVES:
1. UNDERSTAND & ANSWER ONLY THE USER'S SPECIFIC INTENDED QUESTION:
   - Answer ONLY what the user asked in their prompt.
   - If the user asks a general policy question (e.g., "how to get education loan in IOB bank"), answer ONLY about that specific bank and loan type. DO NOT mention unrelated banks (like Canara, HDFC, ICICI, SBI) unless explicitly asked.
   - ONLY include an "Assessment Summary" if the user explicitly asks about their application result (e.g., "why was my loan rejected/accepted").
2. VERIFY EVERYTHING AGAINST THE RETRIEVED BANK POLICY PDF CHUNKS BELOW:
   - Base your eligibility rules, interest rates, margin money, CIBIL cutoffs, FOIR caps, and document requirements directly on the authentic PDF chunks provided below.
3. TRANSLATE TO SIMPLE, CLEAR, EVERYDAY USER-FRIENDLY LANGUAGE:
   - Speak clearly and authoritatively as a Senior Bank Officer.
   - NEVER output raw file tags (like [FILE: ...]), technical document codes, or chapter numbers.
4. STRUCTURE YOUR RESPONSE WITH CLEAN BOLD TITLES & BULLETS:
   - Provide a clear, well-structured response answering the user's query directly with bullet points.

RETRIEVED BANK POLICY PDF DOCUMENT CHUNKS:
{rag_context}

APPLICANT ASSESSMENT METRICS (Use ONLY if user explicitly asks about their application result):
{eval_info if eval_info else "No active evaluation result in session."}"""
            
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            for model_name in candidate_models:
                try:
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.1,
                        max_tokens=1500,
                        timeout=6.0
                    )
                    if completion and completion.choices and completion.choices[0].message.content:
                        raw_text = completion.choices[0].message.content.strip()
                        
                        # Strip any leading thinking process text if generated
                        raw_text = re.sub(r"(?i)^Here's a thinking process:.*?(?=\n\n|\n[1-9]\.|\n\*\*|\n[A-Z]|\n#)", "", raw_text, flags=re.DOTALL).strip()
                        raw_text = re.sub(r"(?i)<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
                        
                        if len(raw_text) > 30:
                            answer = _ensure_complete_sentences(raw_text)
                            print(f"✅ Groq LLM synthesis successfully generated via model: {model_name}")
                            break
                except Exception as api_err:
                    print(f"Groq LLM synthesis info ({model_name}): {api_err}")
                    continue

        # 3. Intelligent Local Policy Synthesizer (comprehensive full fallback)
        if not answer:
            answer = _local_policy_synthesize(prompt, clean_text_snippets, retrieved_sources, eval_ctx)

        return jsonify({
            "answer": answer,
            "sources": retrieved_sources,
            "query_expansion": expand_user_query(prompt)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "answer": "Sorry, I encountered an error processing your request. Please try again or rephrase your question.",
            "sources": [],
            "query_expansion": prompt
        }), 200


def _ensure_complete_sentences(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    if text[-1] in {'.', '!', '?', '%', ')', '"', '*', ']'}:
        return text
    lines = text.split('\n')
    while lines and lines[-1].strip() and lines[-1].strip()[-1] not in {'.', '!', '?', '%', ')', '"', '*', ']', ':'}:
        lines.pop()
    if lines and lines[-1].strip().endswith(':'):
        lines.pop()
    return '\n'.join(lines).strip() if lines else text

def _local_policy_synthesize(prompt: str, snippets: list, sources: list, eval_ctx: dict = None) -> str:
    """Intelligent local synthesizer: extracts crisp, highly relevant policy data
    from retrieved snippets and formats as clean structured natural language."""
    q_lower = prompt.lower().strip()
    is_result_query = any(w in q_lower for w in ["accepted", "approved", "rejected", "declined", "my loan", "my application", "why was my", "why my"])

    if is_result_query:
        if eval_ctx and isinstance(eval_ctx, dict) and eval_ctx.get("bank"):
            b_name = eval_ctx.get("bank")
            l_type = eval_ctx.get("loan_type")
            approved = eval_ctx.get("approved", False)
            res_st = "APPROVED" if approved else "REJECTED"
            viols = eval_ctx.get("violations", [])
            foir_val = eval_ctx.get("foir", "N/A")
            ltv_val = eval_ctx.get("ltv", "N/A")
            cibil_val = eval_ctx.get("cibil", "N/A")
            prob_val = eval_ctx.get("probability", 0.0)
            
            status_icon = "🟢 APPROVED" if approved else "🔴 REJECTED"
            
            lines = []
            lines.append(f"📊 **Assessment Summary ({b_name} {l_type})**")
            lines.append(f"• **Final Decision**: **{status_icon}** (Score: **{prob_val}%**)")
            lines.append(f"• **Calculated FOIR**: **{foir_val}%**")
            
            # Omit LTV if not applicable (e.g. Personal Loans or N/A)
            if ltv_val and str(ltv_val).upper() not in {"N/A", "0%", "0.0%", "0"}:
                lines.append(f"• **Calculated LTV**: **{ltv_val}**")
                
            if cibil_val and str(cibil_val) != "0":
                lines.append(f"• **CIBIL Score**: **{cibil_val}**")
            lines.append("")
            
            if approved:
                lines.append("🟢 **Key Approval Drivers**")
                lines.append(f"• ✅ **Underwriting Compliance**: Applicant satisfied all mandatory policy criteria for {b_name} {l_type}.")
                lines.append(f"• ✅ **Controlled FOIR Ratio**: Debt-to-income ratio ({foir_val}%) is within permissible limits.")
                if cibil_val and cibil_val >= 750:
                    lines.append(f"• ✅ **Strong Credit Rating**: CIBIL of {cibil_val} qualifies for preferential rate benefits.")
                lines.append("")
                lines.append("📋 **Recommended Next Steps**")
                lines.append("1. **Submit KYC Documentation**: Collect OVDs (Aadhaar/PAN/Voter ID) & bank statements.")
                lines.append("2. **Sanction Letter Issuance**: Proceed to instant sanction letter generation.")
            else:
                lines.append("❌ **Primary Policy Breach Reasons**")
                if viols:
                    for v in viols:
                        lines.append(f"• ❌ **{v}**")
                else:
                    lines.append(f"• ❌ **High Obligation Ratio**: Calculated FOIR ({foir_val}%) exceeds permissible limits.")
                    lines.append(f"• ❌ **Risk Score Threshold Breach**: ML Stacking model score did not meet approval criteria.")
                lines.append("")
                lines.append("💡 **Actionable Steps to Get Approved**")
                if viols:
                    for v in viols:
                        if "FOIR" in v:
                            lines.append("• 💡 **Lower Monthly Obligations**: Increase loan tenure or reduce requested loan amount to bring FOIR below limit.")
                        elif "CIBIL" in v:
                            lines.append("• 💡 **Improve Credit Rating**: Clear overdue credit card balances or add a co-applicant with CIBIL ≥ 700.")
                        elif "income" in v.lower() or "annual income" in v.lower():
                            lines.append("• 💡 **Enhance Income Eligibility**: Add a salaried co-applicant (spouse/parent) to meet the income threshold.")
                        elif "LTV" in v:
                            lines.append("• 💡 **Increase Down Payment**: Contribute higher property margin to bring LTV ratio below maximum cap.")
                else:
                    lines.append("• 💡 **Lower Loan Amount**: Reduce requested loan sum by 15-20% to decrease EMI obligation.")
                    lines.append("• 💡 **Add Salaried Co-Applicant**: Combine income with spouse/parent to reduce household FOIR.")
                    lines.append("• 💡 **Extend Loan Tenure**: Select a longer tenure (months) to lower monthly EMI.")
            
            return "\n".join(lines)
        else:
            return "ℹ️ **Application Evaluation Required!**\n\nTo get a personalized breakdown of why your loan was accepted or rejected, please go to **Tab 2 (Loan Application Form)** and click the **'⚡ Evaluate Application'** button to run your assessment through the Risk Orchestrator Engine. Once evaluated, ask me again!"

    if not snippets:
        return "I couldn't find specific policy details for that query. Please specify the bank name (SBI, HDFC, ICICI, IOB, Canara Bank) or loan type."

    # Format general policy snippets cleanly into structured markdown for human readability
    q_lower = prompt.lower()
    target_bank_filter = None
    if "sbi" in q_lower: target_bank_filter = "SBI"
    elif "hdfc" in q_lower: target_bank_filter = "HDFC BANK"
    elif "icici" in q_lower: target_bank_filter = "ICICI BANK"
    elif "iob" in q_lower: target_bank_filter = "IOB"
    elif "canara" in q_lower: target_bank_filter = "CANARA BANK"

    filtered_sources = [s for s in sources if s.get("bank") == target_bank_filter or s.get("bank") == "REGULATORY"] if target_bank_filter else sources
    bank_names = list(set(s.get("bank", "") for s in filtered_sources if s.get("bank")))
    bank_label = " & ".join(bank_names) if bank_names else (target_bank_filter if target_bank_filter else "Bank Policy Guidelines")
    
    clean_lines = []
    seen = set()
    for snip in snippets[:5]:
        for line in snip.split("\n"):
            line = line.strip()
            if not line or len(line) < 15: continue
            
            # Skip technical metadata tags and raw file paths
            if any(p in line for p in ["[FILE:", "[INSTITUTION:", "CHAPTER ", "SECTION ", "DOCUMENT REFERENCE", "SUBJECT:"]):
                continue
                
            # Filter line by target bank if user specified bank name
            if target_bank_filter and target_bank_filter != "REGULATORY":
                if any(other_bank in line.upper() for other_bank in ["SBI", "HDFC", "ICICI", "CANARA"]) and target_bank_filter not in line.upper():
                    continue
                
            # Clean raw numbering and tags
            clean = re.sub(r"\[INSTITUTION:[^\]]+\]", "", line)
            clean = re.sub(r"\[FILE:[^\]]+\]", "", clean)
            clean = re.sub(r"^(\d+(\.\d+)*[-\s\.]*|CHAPTER \d+:?\s*|SECTION \d+:?\s*|[-\u2022*]\s*)", "", clean).strip()
            
            if len(clean) > 15 and clean not in seen:
                if clean[-1] in {'.', '!', '?', '%', ')', '"', '*', ']'}:
                    seen.add(clean)
                    clean_lines.append(f"• {clean}")
            if len(clean_lines) >= 6: break

    result = f"📜 **Policy Guidelines ({bank_label})**\n\n" + "\n".join(clean_lines)
    return _ensure_complete_sentences(result)

    q = prompt.lower()
    keywords = [w for w in re.findall(r"\w+", q) if len(w) > 3 and w not in {"what", "where", "which", "how", "needed", "get", "from", "loan", "bank", "explain", "simply", "cannot", "understand"}]

    STRUCTURAL_SKIP = [
        r"^\[INSTITUTION:", r"^\[FILE:", r"^={4,}", r"^-{4,}",
        r"^CHAPTER \d+", r"^SECTION \d+", r"^DOCUMENT REFERENCE:",
        r"^SUBJECT:", r"^={10,}",
    ]

    all_lines = []
    for snip in snippets[:5]:
        for line in snip.split("\n"):
            line = line.strip()
            if not line or len(line) < 15:
                continue
            if any(re.match(p, line) for p in STRUCTURAL_SKIP):
                continue
            all_lines.append(line)

    # Filter lines matching user query keywords if keywords exist
    matching_lines = []
    if keywords:
        for line in all_lines:
            if any(kw in line.lower() for kw in keywords):
                matching_lines.append(line)

    selected_lines = matching_lines if len(matching_lines) >= 3 else all_lines

    # Identify bank names from sources
    bank_names = list(set(s.get("bank", "") for s in sources if s.get("bank")))
    bank_label = " & ".join(bank_names) if bank_names else "Bank Policy"

    # Intent title
    if any(w in q for w in ["income", "salary", "earn", "nmi", "minimum"]):
        title = f"Income Requirements ({bank_label})"
    elif any(w in q for w in ["cibil", "credit score"]):
        title = f"CIBIL Score Rules ({bank_label})"
    elif any(w in q for w in ["foir", "obligation"]):
        title = f"FOIR & Obligation Limits ({bank_label})"
    elif any(w in q for w in ["age", "years old"]):
        title = f"Age Limits ({bank_label})"
    elif any(w in q for w in ["document", "kyc", "proof"]):
        title = f"Required Documents & KYC Rules ({bank_label})"
    elif any(w in q for w in ["rate", "interest"]):
        title = f"Interest Rates ({bank_label})"
    else:
        title = f"Policy Summary ({bank_label})"

    bullet_lines = []
    seen = set()
    for line in selected_lines:
        if line.endswith(":") and len(line.split()) <= 7:
            continue
        # Clean up line
        clean = re.sub(r"^(\d+(\.\d+)*[-\s\.]*|CHAPTER \d+:?\s*|SECTION \d+:?\s*|[-\u2022*]\s*)", "", line).strip()
        if len(clean) > 15 and clean not in seen:
            # Drop incomplete fragments
            if clean[-1] in {'.', '!', '?', '%', ')', '"', '*', ']'}:
                seen.add(clean)
                bullet_lines.append(f"• {clean}")
        if len(bullet_lines) >= 10:
            break

    if not bullet_lines:
        return "I couldn't find exact policy rules for your query. Please specify the bank (e.g. SBI, HDFC, ICICI, IOB, Canara) or loan type."

    result = f"**{title}**\n\n" + "\n".join(bullet_lines)
    return _ensure_complete_sentences(result)

@app.route("/api/search", methods=["POST"])
def search_policy():
    try:
        data = request.get_json(silent=True) or {}
        query = data.get("query", "").strip()
        if not query:
            return jsonify({"results": []})

        hybrid_results = hybrid_rrf_search(query, top_k=6)
        results = []
        for idx, (doc, score) in enumerate(hybrid_results):
            src_file = os.path.basename(doc.metadata.get('source', 'Policy File'))
            bank_name = doc.metadata.get('bank', 'BANK')
            results.append({
                "rank": idx + 1,
                "file": src_file,
                "bank": bank_name,
                "score": round(score, 4),
                "content": doc.page_content
            })

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    dist_html = os.path.join(BASE_DIR, "dist", "index.html")
    root_html = os.path.join(BASE_DIR, "index.html")
    
    if os.path.exists(dist_html):
        with open(dist_html, "r", encoding="utf-8") as f:
            return f.read()
    if os.path.exists(root_html):
        with open(root_html, "r", encoding="utf-8") as f:
            return f.read()
    return "Index file not found."

@app.route("/<path:path>")
def serve_static_file(path):
    dist_dir = os.path.join(BASE_DIR, "dist")
    if os.path.exists(os.path.join(dist_dir, path)):
        return send_from_directory(dist_dir, path)
    if os.path.exists(os.path.join(BASE_DIR, path)):
        return send_from_directory(BASE_DIR, path)
    dist_html = os.path.join(dist_dir, "index.html")
    if os.path.exists(dist_html):
        with open(dist_html, "r", encoding="utf-8") as f:
            return f.read()
    return "File not found."

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    print(f"🚀 Starting Loan-IQ Server at http://{host}:{port} ...")
    app.run(host=host, port=port, debug=debug)