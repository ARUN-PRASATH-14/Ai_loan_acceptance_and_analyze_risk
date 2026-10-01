# EXACT GEMINI PROMPT FOR 5-LAYER SYSTEM ARCHITECTURAL DIAGRAM

This document provides the precise **Gemini Image Generation Prompt** to extend your existing 4-layer diagram by adding **Layer 5** on the right side while preserving Layers 1 through 4 exactly as they are, with **100% English text and NO Tamil references**.

---

## 🌟 Exact Gemini Image Generation Prompt (Copy & Paste)

```text
A crisp, high-resolution 16:9 system architecture flowchart diagram on a solid royal blue background (#0000FF) with white card shapes and sharp black text. 5 vertical column layers arranged left to right:

Layer 1: Customer Input Layer
- Top Parallelogram: "Customer Loan Application"
- Middle Box: "Collect Customer Details"
- Bottom Parallelogram: "OUTPUT: Raw Financial Data"

Layer 2: Preprocessing & Security Layer
- Top Box: "Handle Missing Values"
- Box 2: "OneHotEncoder"
- Box 3: "SMOTE"
- Decision Diamond 1: "Anomaly Detected?" -> [Yes: "Flag Suspicious"]
- Decision Diamond 2: "Violates RBI Rules?" -> [Yes: "Reject Application"]
- Bottom Parallelogram: "OUTPUT: Clean Feature Vector & Security Flag"

Layer 3: Machine Learning Risk Analysis & Explainability
- Top Parallelogram: "Clean Feature Vector"
- Box 1: "RiskAgent"
- Box 2: "Meta-Learner Stacking Ensemble Loan Prediction Model ANN Meta-Learner"
- Box 3: "Predict Loan Risk SHAP Explainer Tool"
- Box 4: "Identify Important Features"
- Bottom Parallelogram: "OUTPUT: Loan Risk Score, SHAP Importance, Explainable AI Report"

Layer 4: Policy RAG & Chatbot Engine
- Top Parallelogram: "Output of Layer 3 & Pre-Loaded Bank Policy PDFs (knowledge_base/)"
- Box 1: "PolicyAgent"
- Box 2: "Text Chunking & Embeddings (all-MiniLM-L6-v2)"
- Box 3: "FAISS Vector Database (faiss_index/)"
- Box 4: "Interactive RAG Policy Chatbot"
- Bottom Parallelogram: "OUTPUT: RAG Policy Context & Cited Rule Verification"

Layer 5: Decision Orchestration & Dashboard UI Layer
- Top Parallelogram: "Output of Layer 4 & Underwriting Rationale"
- Box 1: "RecommendationAgent"
- Box 2: "Generate Actionable Credit Score Fixes"
- Box 3: "Bank Audit Checklist & Compliance Logging"
- Box 4: "Interactive Underwriting Web UI"
- Bottom Parallelogram: "OUTPUT: Final Customer Dashboard (Approved/Rejected Status, SHAP Reason Charts, Cited Policy Rules & Interactive Chatbot, Instant Sanction Letter PDF)"

Visual style: High contrast white boxes, black text, clean black arrows pointing from left layer outputs to next layer inputs, sharp engineering flowchart style on bright royal blue background. 100% English text only.
```

---

## 📋 Text Flow Representation of Layer 5 Addition

```text
                                LAYER 5 FLOW ONLY
+-----------------------------------------------------------------------------------+
|               Layer 5: Decision Orchestration & Dashboard UI Layer                |
+-----------------------------------------------------------------------------------+
|  / Input Parallelogram:                                                          /|
| /  Output of Layer 4 & Underwriting Rationale                                   / |
|+-------------------------------------------------------------------------------+--+
|                                       │                                           |
|                                       ▼                                           |
|  [ Process Box 1: RecommendationAgent ]                                           |
|                                       │                                           |
|                                       ▼                                           |
|  [ Process Box 2: Generate Actionable Credit Score Fixes ]                        |
|                                       │                                           |
|                                       ▼                                           |
|  [ Process Box 3: Bank Audit Checklist & Compliance Logging ]                     |
|                                       │                                           |
|                                       ▼                                           |
|  [ Process Box 4: Interactive Underwriting Web UI ]                               |
|                                       │                                           |
|                                       ▼                                           |
|  / Output Parallelogram:                                                         /|
| /  OUTPUT: Final Customer Dashboard (Approved/Rejected Status, SHAP Reason      / |
|/   Charts, Cited Policy Rules & Interactive Chatbot, Instant Sanction PDF)     /  |
+-----------------------------------------------------------------------------------+
```
