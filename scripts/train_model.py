import os
import sys
import pandas as pd
import numpy as np
import pickle

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

csv_path = os.path.join(DATA_DIR, "synthetic_loan_data.csv") if os.path.exists(os.path.join(DATA_DIR, "synthetic_loan_data.csv")) else "synthetic_loan_data.csv"
print(f"Loading synthetic dataset from '{csv_path}'...")
df = pd.read_csv(csv_path)
print(f"Dataset shape: {df.shape}")

if "Reject_Reason" in df.columns:
    X = df.drop(["Approved", "Reject_Reason"], axis=1)
else:
    X = df.drop(["Approved"], axis=1)
    
y = df["Approved"]

categorical_features = ["Bank", "Loan_Type", "TN_City", "Employer_Category", "Gender", "Employment_Type", "Existing_Customer", "Course_Approved"]
numerical_features = [col for col in X.columns if col not in categorical_features]

print(f"\nCategorical features: {categorical_features}")
print(f"Numerical features: {numerical_features}")

print("\nFitting preprocessor...")
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

preprocessor.fit(X)

X_processed = preprocessor.transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42, stratify=y)

print("\nApplying SMOTE for class imbalance...")
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)

print(f"Balanced training labels:\n{pd.Series(y_train_bal).value_counts()}")

print("\nTraining Universal XGBoost Model...")
model = XGBClassifier(
    n_estimators=400,
    max_depth=7,
    learning_rate=0.05,
    random_state=42,
    n_jobs=-1,
    eval_metric='logloss'
)

model.fit(X_train_bal, y_train_bal)

print("\nEvaluating Model on Test Set...")
probs = model.predict_proba(X_test)[:, 1]

THRESHOLD = 0.50
y_pred = (probs >= THRESHOLD).astype(int)

print(f"\nAccuracy : {accuracy_score(y_test, y_pred):.4f}")
print(f"ROC AUC  : {roc_auc_score(y_test, probs):.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Rejected", "Approved"]))

print(f"\nSaving Models to '{MODELS_DIR}'...")
pickle.dump(model, open(os.path.join(MODELS_DIR, "loan_model.pkl"), "wb"))
pickle.dump(preprocessor, open(os.path.join(MODELS_DIR, "preprocessor.pkl"), "wb"))
pickle.dump(THRESHOLD, open(os.path.join(MODELS_DIR, "threshold.pkl"), "wb"))

expected_columns = list(X.columns)
pickle.dump(expected_columns, open(os.path.join(MODELS_DIR, "feature_names.pkl"), "wb"))

encoded_feature_names = preprocessor.get_feature_names_out()
clean_names = [name.split("__")[-1] for name in encoded_feature_names]
pickle.dump(clean_names, open(os.path.join(MODELS_DIR, "encoded_feature_names.pkl"), "wb"))

print("✅ Model files saved successfully!")