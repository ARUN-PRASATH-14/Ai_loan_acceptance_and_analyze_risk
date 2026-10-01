import pandas as pd
import numpy as np
import random
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

NUM_RECORDS = 75000  # 15,000 per bank

banks = ["SBI", "HDFC", "ICICI", "IOB", "Canara"]
loan_types = ["Home Loan", "PersonalLoan", "Education Loan", "Agriculture/KCC"]
tn_cities = [
    "Chennai (Tier 1)", 
    "Coimbatore (Tier 2)", "Madurai (Tier 2)", "Trichy (Tier 2)", "Salem (Tier 2)", 
    "Vellore (Tier 3)", "Rural TN (Tier 3)"
]
employer_categories = ["Tier A (Top MNC)", "Tier B (Mid-Size)", "Tier C (Small)", "Unlisted/Startup"]

data = []

def generate_record(bank, loan_type):
    # Base applicant data
    age = np.random.randint(18, 75)
    gender = random.choice(["Male", "Female"])
    emp_type = random.choices(["Salaried", "Self-employed", "Agriculturist"], weights=[0.5, 0.3, 0.2])[0]
    
    # Advanced features
    tn_city = random.choice(tn_cities)
    if emp_type == "Salaried":
        employer = random.choices(employer_categories, weights=[0.2, 0.3, 0.3, 0.2])[0]
    else:
        employer = "Not Applicable"
        
    existing_customer = random.choice([True, False])
    
    # Adjust employment type if KCC
    if loan_type == "Agriculture/KCC":
        emp_type = "Agriculturist"
        employer = "Not Applicable"
        tn_city = random.choice(["Rural TN (Tier 3)", "Vellore (Tier 3)", "Salem (Tier 2)"])
        
    # Income & Loan Amount based on Loan Type
    if loan_type == "Home Loan":
        income = np.random.randint(300000, 3000000)
        co_applicant_income = random.choice([0, np.random.randint(200000, 1500000)])
        loan_amount = np.random.randint(1500000, 20000000)
        tenure = np.random.randint(120, 360)
        interest_rate = round(random.uniform(8.0, 10.5), 2)
    elif loan_type == "Personal Loan":
        income = np.random.randint(250000, 1500000)
        co_applicant_income = 0 # Usually no co-applicant for PL
        loan_amount = np.random.randint(50000, 1500000)
        tenure = np.random.randint(12, 60)
        interest_rate = round(random.uniform(10.5, 18.0), 2)
    elif loan_type == "Education Loan":
        income = np.random.randint(0, 300000) # Student income is low
        co_applicant_income = np.random.randint(300000, 2000000) # Parent income
        loan_amount = np.random.randint(500000, 5000000)
        tenure = np.random.randint(60, 180)
        interest_rate = round(random.uniform(8.5, 12.0), 2)
    else: # KCC
        income = np.random.randint(100000, 800000)
        co_applicant_income = 0
        loan_amount = np.random.randint(50000, 300000)
        tenure = 60
        interest_rate = round(random.uniform(4.0, 9.0), 2)

    # 15% chance of being New to Credit (NTC) / No Credit History
    has_credit = random.random() > 0.15
    cibil = np.random.randint(500, 850) if has_credit else 0

    existing_emi = np.random.randint(0, int((income + co_applicant_income) / 12 * 0.4) + 1) if has_credit else 0
    
    # Calculate monthly payment for this loan
    monthly_rate = interest_rate / 100 / 12
    if monthly_rate > 0:
        emi = (loan_amount * monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)
    else:
        emi = loan_amount / tenure
        
    total_monthly_income = (income + co_applicant_income) / 12
    foir = (existing_emi + emi) / total_monthly_income if total_monthly_income > 0 else 1.0
    ltv = random.uniform(0.6, 0.95) if loan_type == "Home Loan" else 0.0
    
    emp_years = np.random.randint(0, 20)
    business_vintage = np.random.randint(0, 15) if emp_type == "Self-employed" else 0
    
    course_approved = random.choice([True, False]) if loan_type == "Education Loan" else True
    
    # Default assumption
    approved = True
    reject_reason = ""

    # -------------------------------------------------------------
    # ADVANCED BANK SPECIFIC RULES
    # -------------------------------------------------------------
    
    # Apply Leniency for Existing Customers
    cibil_leniency = 50 if existing_customer else 0
    foir_leniency = 0.05 if existing_customer else 0.0
    
    # Apply Leniency for Tier A Employers
    if employer == "Tier A (Top MNC)":
        foir_leniency += 0.05
    
    # Adjust Income limits by City Tier
    income_multiplier = 1.0
    if "Tier 1" in tn_city: income_multiplier = 1.2 # Higher income req in Chennai
    if "Tier 3" in tn_city: income_multiplier = 0.8 # Lower income req in rural TN
    
    # SBI Rules
    if bank == "SBI":
        if age < 18 or age > 70:
            approved, reject_reason = False, "Age outside SBI criteria"
        elif cibil != 0 and cibil < (700 - cibil_leniency):
            approved, reject_reason = False, "CIBIL < 700"
        elif cibil == 0 and loan_type == "Personal Loan" and income/12 < (30000 * income_multiplier):
            approved, reject_reason = False, "NTC Personal Loan requires 30k/mo income"
        elif foir > (0.65 + foir_leniency):
            approved, reject_reason = False, "FOIR > 65%"
        elif loan_type == "Home Loan" and ltv > 0.90:
            approved, reject_reason = False, "LTV > 90%"
        elif emp_type == "Self-employed" and business_vintage < 3:
            approved, reject_reason = False, "Business vintage < 3 yrs"
        elif emp_type == "Salaried" and emp_years < 1:
            approved, reject_reason = False, "Employment < 1 yr"
        elif loan_type == "Personal Loan" and income/12 < (20000 * income_multiplier):
            approved, reject_reason = False, "Income < 20k/mo"
            
    # HDFC Rules
    elif bank == "HDFC":
        if age < 21 or age > 65:
            approved, reject_reason = False, "Age outside HDFC criteria"
        elif cibil != 0 and foir > (0.60 + foir_leniency):
            approved, reject_reason = False, "FOIR > 60%"
        elif cibil == 0 and foir > 0.50:
            approved, reject_reason = False, "NTC FOIR > 50%"
        elif cibil != 0 and cibil < (650 - cibil_leniency):
            approved, reject_reason = False, "CIBIL < 650"
        elif emp_type == "Self-employed" and business_vintage < 2:
            approved, reject_reason = False, "Business vintage < 2 yrs"
        elif emp_type == "Salaried" and (income/12 < (25000 * income_multiplier) and loan_type == "Personal Loan"):
            approved, reject_reason = False, "Income < 25k/mo for PL"
        elif loan_type == "Education Loan" and not course_approved:
            approved, reject_reason = False, "Course not approved"
            
    # ICICI Rules
    elif bank == "ICICI":
        if age < 20 or age > 65:
            approved, reject_reason = False, "Age outside ICICI criteria"
        elif emp_type == "Salaried" and income/12 < (25000 * income_multiplier):
            approved, reject_reason = False, "Salaried Income < 25k/mo"
        elif cibil != 0 and cibil < (650 - cibil_leniency):
            approved, reject_reason = False, "CIBIL < 650"
        elif cibil == 0 and loan_type == "Home Loan":
            approved, reject_reason = False, "ICICI does not allow NTC Home Loans"
        elif foir > (0.60 + foir_leniency):
            approved, reject_reason = False, "FOIR > 60%"
        elif loan_type == "Home Loan" and ltv > 0.85:
            approved, reject_reason = False, "LTV > 85%"

    # IOB Rules
    elif bank == "IOB":
        if age < 21 or age > 70:
            approved, reject_reason = False, "Age outside IOB criteria"
        elif loan_type == "Home Loan" and income < (600000 * income_multiplier):
            approved, reject_reason = False, "Annual income < 6L for Home Loan"
        elif (total_monthly_income - emi - existing_emi) < total_monthly_income*0.5 and loan_type == "Personal Loan":
            approved, reject_reason = False, "Take home pay < 50%"
        elif cibil != 0 and cibil < (650 - cibil_leniency):
            approved, reject_reason = False, "CIBIL < 650"
            
    # Canara Rules
    elif bank == "Canara":
        if age < 21 or age > 75:
            approved, reject_reason = False, "Age outside Canara criteria"
        elif emp_type == "Salaried" and income/12 < (15000 * income_multiplier):
            approved, reject_reason = False, "Income < 15k/mo"
        elif emp_years < 2 and emp_type == "Salaried":
            approved, reject_reason = False, "Employment < 2 yrs"
        elif cibil != 0 and cibil < (600 - cibil_leniency):
            approved, reject_reason = False, "CIBIL < 600"
        elif foir > (0.60 + foir_leniency):
            approved, reject_reason = False, "FOIR > 60%"
            
    # Add some stochastic noise (even if approved by hard rules, soft reject based on risk factors)
    if approved:
        # Increase risk score if Tier A or Existing Customer
        bonus = 0.1 if employer == "Tier A (Top MNC)" else 0
        bonus += 0.1 if existing_customer else 0
        
        risk_score = (cibil / 900) * 0.5 + (1 - foir) * 0.5 + bonus
        if risk_score < 0.45: # Random soft reject threshold
            if random.random() < 0.8:
                approved = False
                reject_reason = "High risk profile"
    
    return {
        "Bank": bank,
        "Loan_Type": loan_type,
        "TN_City": tn_city,
        "Employer_Category": employer,
        "Existing_Customer": 1 if existing_customer else 0,
        "Age": age,
        "Gender": gender,
        "Employment_Type": emp_type,
        "Annual_Income": income,
        "Co_Applicant_Income": co_applicant_income,
        "Loan_Amount": loan_amount,
        "Tenure_Months": tenure,
        "Interest_Rate": interest_rate,
        "CIBIL_Score": cibil,
        "Existing_EMI": existing_emi,
        "FOIR": round(foir, 3),
        "LTV": round(ltv, 3),
        "Employment_Years": emp_years,
        "Business_Vintage": business_vintage,
        "Course_Approved": 1 if course_approved else 0,
        "Approved": 1 if approved else 0
    }

print("Generating synthetic data with advanced TN specific features...")
for bank in banks:
    for loan_type in loan_types:
        for _ in range(NUM_RECORDS // (len(banks) * len(loan_types))):
            data.append(generate_record(bank, loan_type))

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

df = pd.DataFrame(data)
csv_out = os.path.join(DATA_DIR, 'synthetic_loan_data.csv')
df.to_csv(csv_out, index=False)
print(f"\nSaved {len(df)} records to '{csv_out}'.")

