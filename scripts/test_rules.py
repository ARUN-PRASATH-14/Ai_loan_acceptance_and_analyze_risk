import pickle
import pandas as pd
import sys
import warnings
warnings.filterwarnings('ignore')

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models") if os.path.exists(os.path.join(BASE_DIR, "models")) else "."

model = pickle.load(open(os.path.join(MODELS_DIR, 'loan_model.pkl'), 'rb'))
preprocessor = pickle.load(open(os.path.join(MODELS_DIR, 'preprocessor.pkl'), 'rb'))
features = pickle.load(open(os.path.join(MODELS_DIR, 'feature_names.pkl'), 'rb'))

def test_applicant(bank, age, cibil, income, existing_emi, loan_type="Personal Loan"):
    loan_amt = 500000
    tenure_mo = 60
    int_rate = 12.0
    
    monthly_rate = int_rate / 100 / 12
    proposed_emi = (loan_amt * monthly_rate * (1 + monthly_rate)**tenure_mo) / ((1 + monthly_rate)**tenure_mo - 1)
    
    foir = (existing_emi + proposed_emi) / (income / 12)
    
    data = {
        "Bank": bank,
        "Loan_Type": loan_type,
        "TN_City": "Chennai (Tier 1)",
        "Employer_Category": "Tier A (Top MNC)",
        "Gender": "Male",
        "Employment_Type": "Salaried",
        "Existing_Customer": 0,
        "Age": age,
        "Annual_Income": income,
        "Co_Applicant_Income": 0,
        "Loan_Amount": loan_amt,
        "Tenure_Months": tenure_mo,
        "Interest_Rate": int_rate,
        "CIBIL_Score": cibil,
        "Existing_EMI": existing_emi,
        "FOIR": foir,
        "LTV": 0.0,
        "Employment_Years": 5,
        "Business_Vintage": 0,
        "Course_Approved": 1
    }
    
    df_in = pd.DataFrame([data])[features]
    df_processed = preprocessor.transform(df_in)
    prob = model.predict_proba(df_processed)[0][1]
    
    result = "✅ APPROVED" if prob >= 0.50 else "❌ REJECTED"
    print(f"Bank: {bank:6} | Age: {age} | CIBIL: {cibil} | Income: {income} | FOIR: {foir:.1%} => {result} (Score: {prob:.2f})")

print("--- TEST 1: The High Debt Applicant ---")
print("Applicant has 63% Debt-to-Income (FOIR). SBI allows up to 65%, but others cap at 60%.")
for b in ["SBI", "HDFC", "ICICI", "Canara"]:
    test_applicant(b, age=35, cibil=750, income=1200000, existing_emi=52000)

print("\n--- TEST 2: The Low CIBIL Applicant ---")
print("Applicant has 620 CIBIL. IOB & HDFC need 650, SBI needs 700, but Canara allows 600.")
for b in ["Canara", "SBI", "HDFC", "IOB"]:
    test_applicant(b, age=35, cibil=620, income=1200000, existing_emi=10000)

print("\n--- TEST 3: The 72-Year-Old Applicant ---")
print("Applicant is 72 years old. Canara allows up to 75, others cut off at 65 or 70.")
for b in ["Canara", "HDFC", "ICICI", "SBI"]:
    test_applicant(b, age=72, cibil=750, income=1200000, existing_emi=10000)
