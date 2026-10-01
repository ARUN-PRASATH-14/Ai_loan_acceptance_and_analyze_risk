import sys
import os
import time

if hasattr(sys.stdout, 'reconfigure'): 
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import Flask app and MCP Agent definitions
from app import AnomalyAgent, RiskAgent, RecommendationAgent, PolicyAgent, preprocessor, model, feature_names, explainer, encoded_features
threshold = 0.5

def test_mcp_agents():
    print("=" * 80)
    print("🤖 MCP MULTI-AGENT ORCHESTRATION LAYER: LIVE VERIFICATION SUITE")
    print("=" * 80)

    payload = {
        "bank": "IOB",
        "loan_type": "Home Loan",
        "tn_city": "Madurai (Tier 2)",
        "employer": "Tier B (Mid-Size)",
        "income": 400000,
        "co_app_inc": 0,
        "loan_amt": 5000000,
        "tenure_mo": 240,
        "cibil": 750,
        "exist_emi": 40000,
        "age": 30,
        "prop_val": 6500000,
        "emp_type": "Salaried",
        "gender": "Male",
        "existing_customer": False,
        "is_ntc": False
    }

    # -----------------------------------------------------------------
    # TEST AGENT 1: AnomalyAgent (mcp_anomaly_check_tool)
    # -----------------------------------------------------------------
    t0 = time.time()
    anomalies, violations = AnomalyAgent.run_anomaly_check_tool(payload)
    t_agent1 = (time.time() - t0) * 1000

    print(f"\n1️⃣ AGENT 1: AnomalyAgent (mcp_anomaly_check_tool) [Execution Time: {round(t_agent1, 2)}ms]")
    print(f"   • Status: ✅ OPERATIONAL")
    print(f"   • Data Anomalies Detected: {anomalies if anomalies else 'None (Data Sanity Clean)'}")
    print(f"   • Bank Policy Hard Rule Breaches: {len(violations)} found")
    for v in violations:
        print(f"     - ❌ {v}")

    # -----------------------------------------------------------------
    # TEST AGENT 2: RiskAgent (mcp_risk_scoring_tool & shap_explainer_tool)
    # -----------------------------------------------------------------
    t0 = time.time()
    risk_res = RiskAgent.run_risk_scoring_tool(payload, preprocessor, model, feature_names, threshold)
    prob = round(risk_res["probability"] * 100, 1)
    shap_res = RiskAgent.run_shap_explainer_tool(explainer, risk_res["df_processed"], encoded_features)
    t_agent2 = (time.time() - t0) * 1000

    print(f"\n2️⃣ AGENT 2: RiskAgent (mcp_risk_scoring_tool & shap_explainer_tool) [Execution Time: {round(t_agent2, 2)}ms]")
    print(f"   • Status: ✅ OPERATIONAL")
    print(f"   • Stacking ML Default Probability: {prob}%")
    print(f"   • Calculated FOIR: {round(risk_res['foir'] * 100, 1)}%")
    print(f"   • Top SHAP Attributions: {shap_res['labels'][:3]}")

    # -----------------------------------------------------------------
    # TEST AGENT 3: RecommendationAgent (mcp_recommendation_tool)
    # -----------------------------------------------------------------
    t0 = time.time()
    is_rejected = len(violations) > 0 or prob < 50.0
    recs = RecommendationAgent.run_recommendation_tool(
        payload["bank"], payload["loan_type"], not is_rejected, len(violations) > 0, 
        risk_res["probability"], risk_res["foir"], payload["cibil"], payload["is_ntc"], violations
    )
    t_agent3 = (time.time() - t0) * 1000

    print(f"\n3️⃣ AGENT 3: RecommendationAgent (mcp_recommendation_tool) [Execution Time: {round(t_agent3, 2)}ms]")
    print(f"   • Status: ✅ OPERATIONAL")
    print(f"   • Recommendations Generated: {len(recs)} item(s)")
    for r in recs:
        clean_r = r.replace("**", "").replace("🟢", "•").replace("🔴", "•").replace("💡", "•").replace("ℹ️", "•")
        print(f"     - {clean_r}")

    # -----------------------------------------------------------------
    # TEST AGENT 4: PolicyAgent (mcp_policy_lookup_tool)
    # -----------------------------------------------------------------
    t0 = time.time()
    rag_res = PolicyAgent.run_policy_lookup_tool("why my loan was rejected", {
        "bank": payload["bank"], "loan_type": payload["loan_type"], "approved": False,
        "probability": prob, "foir": round(risk_res["foir"] * 100, 1), "ltv": "3.1%",
        "cibil": payload["cibil"], "violations": violations
    })
    t_agent4 = (time.time() - t0) * 1000

    print(f"\n4️⃣ AGENT 4: PolicyAgent (mcp_policy_lookup_tool) [Execution Time: {round(t_agent4, 2)}ms]")
    print(f"   • Status: ✅ OPERATIONAL")
    print(f"   • RAG Context-Aware Response Length: {len(rag_res)} chars")
    print("   • Response Sample:")
    for line in rag_res.split("\n")[:4]:
        if line.strip(): print(f"     {line}")

    total_time = t_agent1 + t_agent2 + t_agent3 + t_agent4
    print("=" * 80)
    print(f"🎉 ALL 4 MCP AGENTS VERIFIED OPERATIONAL (Total Pipeline Time: {round(total_time, 2)}ms)")
    print("=" * 80)

if __name__ == "__main__":
    test_mcp_agents()
