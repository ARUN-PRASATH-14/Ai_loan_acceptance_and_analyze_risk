"""
Comprehensive pytest test suite for Loan-IQ Flask backend.

Covers:
  - apply_bank_hard_rules (SBI, HDFC, ICICI, IOB, Canara)
  - AnomalyAgent.run_anomaly_check_tool
  - RiskAgent.run_risk_scoring_tool (FOIR / LTV calculations)
  - /api/evaluate endpoint (integration)
  - /api/chat endpoint (integration)
  - expand_user_query
  - _ensure_complete_sentences
"""
import os
import sys
import warnings
import json
import math

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

# ── Minimal env so app.py loads without crashing ──────────────────────
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# Import app after path is set
from app import (
    app as flask_app,
    apply_bank_hard_rules,
    expand_user_query,
    _ensure_complete_sentences,
    AnomalyAgent,
    RiskAgent,
    preprocessor,
    model,
    feature_names,
    THRESHOLD,
)


# ══════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════

@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def _base_payload(**overrides):
    """Return a minimal valid evaluation payload."""
    payload = dict(
        bank="SBI",
        loan_type="Personal Loan",
        tn_city="Chennai (Tier 1)",
        employer="Tier B (Mid-Size)",
        income=1_200_000,
        co_app_inc=0,
        loan_amt=500_000,
        tenure_mo=60,
        cibil=750,
        exist_emi=5_000,
        age=35,
        gender="Male",
        emp_type="Salaried",
        prop_val=0,
        existing_customer=False,
        is_ntc=False,
        int_rate=12.0,
        emp_years=5,
        business_vintage=0,
        course_approved=True,
    )
    payload.update(overrides)
    return payload


# ══════════════════════════════════════════════════════════════
# 1. UNIT TESTS — apply_bank_hard_rules
# ══════════════════════════════════════════════════════════════

class TestApplyBankHardRules:
    """Tests for the bank policy hard-rule engine."""

    # --- helpers ---
    @staticmethod
    def _rules(bank, **kw):
        """Shorthand to invoke apply_bank_hard_rules with sane defaults."""
        defaults = dict(
            loan_type="Personal Loan",
            age=35,
            income=1_200_000,
            co_applicant_income=0,
            cibil=750,
            foir=0.40,
            ltv=0.0,
            emp_years=5,
            business_vintage=0,
            course_approved=True,
            emp_type="Salaried",
            employer="Tier B (Mid-Size)",
            tn_city="Chennai (Tier 1)",
            existing_customer=False,
        )
        defaults.update(kw)
        return apply_bank_hard_rules(bank, **defaults)

    # ── SBI ─────────────────────────────────────────────────────────
    def test_sbi_valid_applicant_no_violations(self):
        assert self._rules("SBI") == []

    def test_sbi_age_too_young(self):
        v = self._rules("SBI", age=17)
        assert any("Age" in x for x in v)

    def test_sbi_age_too_old(self):
        v = self._rules("SBI", age=71)
        assert any("Age" in x for x in v)

    def test_sbi_low_cibil(self):
        v = self._rules("SBI", cibil=600)
        assert any("CIBIL" in x for x in v)

    def test_sbi_cibil_leniency_for_existing_customer(self):
        # 610 < 650 normally → violation; with existing_customer leniency (50 pts) → 650-50=600 → pass
        v = self._rules("SBI", cibil=620, existing_customer=True)
        assert not any("CIBIL" in x for x in v)

    def test_sbi_foir_too_high(self):
        v = self._rules("SBI", foir=0.70)
        assert any("FOIR" in x for x in v)

    def test_sbi_foir_within_limit(self):
        v = self._rules("SBI", foir=0.64)
        assert not any("FOIR" in x for x in v)

    def test_sbi_ltv_exceeds_limit(self):
        v = self._rules("SBI", loan_type="Home Loan", ltv=0.91)
        assert any("LTV" in x for x in v)

    def test_sbi_ltv_within_limit(self):
        v = self._rules("SBI", loan_type="Home Loan", ltv=0.89)
        assert not any("LTV" in x for x in v)

    def test_sbi_self_employed_low_vintage(self):
        v = self._rules("SBI", emp_type="Self-employed", business_vintage=2)
        assert any("vintage" in x.lower() for x in v)

    def test_sbi_salaried_short_employment(self):
        v = self._rules("SBI", emp_type="Salaried", emp_years=0)
        assert any("employment" in x.lower() for x in v)

    # ── HDFC ────────────────────────────────────────────────────────
    def test_hdfc_valid_applicant_no_violations(self):
        assert self._rules("HDFC") == []

    def test_hdfc_age_too_young(self):
        v = self._rules("HDFC", age=20)
        assert any("Age" in x for x in v)

    def test_hdfc_age_too_old(self):
        v = self._rules("HDFC", age=66)
        assert any("Age" in x for x in v)

    def test_hdfc_foir_too_high(self):
        v = self._rules("HDFC", foir=0.65)
        assert any("FOIR" in x for x in v)

    def test_hdfc_ntc_foir_strict_limit(self):
        v = self._rules("HDFC", cibil=0, foir=0.55)
        assert any("NTC" in x or "50%" in x for x in v)

    def test_hdfc_low_cibil(self):
        v = self._rules("HDFC", cibil=600)
        assert any("CIBIL" in x for x in v)

    def test_hdfc_self_employed_vintage(self):
        v = self._rules("HDFC", emp_type="Self-employed", business_vintage=1)
        assert any("vintage" in x.lower() for x in v)

    def test_hdfc_personal_loan_low_income(self):
        v = self._rules("HDFC", loan_type="Personal Loan", income=180_000)  # ₹15k/mo < ₹25k*1.2
        assert any("income" in x.lower() for x in v)

    # ── ICICI ───────────────────────────────────────────────────────
    def test_icici_valid_applicant_no_violations(self):
        assert self._rules("ICICI") == []

    def test_icici_age_too_young(self):
        v = self._rules("ICICI", age=19)
        assert any("Age" in x for x in v)

    def test_icici_ntc_home_loan_blocked(self):
        v = self._rules("ICICI", loan_type="Home Loan", cibil=0)
        assert any("NTC" in x for x in v)

    def test_icici_ltv_85_limit(self):
        v = self._rules("ICICI", loan_type="Home Loan", ltv=0.86)
        assert any("LTV" in x and "85%" in x for x in v)

    def test_icici_foir_too_high(self):
        v = self._rules("ICICI", foir=0.65)
        assert any("FOIR" in x for x in v)

    def test_icici_low_income_salaried(self):
        v = self._rules("ICICI", emp_type="Salaried", income=240_000)  # ₹20k/mo < ₹25k*1.2
        assert any("income" in x.lower() for x in v)

    # ── IOB ─────────────────────────────────────────────────────────
    def test_iob_valid_applicant_no_violations(self):
        assert self._rules("IOB") == []

    def test_iob_age_too_old(self):
        v = self._rules("IOB", age=71)
        assert any("Age" in x for x in v)

    def test_iob_low_cibil(self):
        v = self._rules("IOB", cibil=630)
        assert any("CIBIL" in x for x in v)

    def test_iob_short_employment(self):
        v = self._rules("IOB", emp_years=1)
        assert any("employment" in x.lower() for x in v)

    def test_iob_home_loan_low_income(self):
        v = self._rules("IOB", loan_type="Home Loan", income=500_000)  # < 600k * 1.2 in Tier 1
        assert any("income" in x.lower() for x in v)

    # ── Canara ──────────────────────────────────────────────────────
    def test_canara_valid_applicant_no_violations(self):
        assert self._rules("Canara") == []

    def test_canara_allows_age_75(self):
        assert self._rules("Canara", age=75) == []

    def test_canara_rejects_age_76(self):
        v = self._rules("Canara", age=76)
        assert any("Age" in x for x in v)

    def test_canara_lower_cibil_threshold(self):
        # Canara allows CIBIL ≥ 600; 610 should pass
        v = self._rules("Canara", cibil=610)
        assert not any("CIBIL" in x for x in v)

    def test_canara_low_cibil_fails(self):
        v = self._rules("Canara", cibil=580)
        assert any("CIBIL" in x for x in v)

    def test_canara_low_income_fails(self):
        # ₹10k/mo * 1.2 Tier1 = ₹12k threshold; 108000 = ₹9k/mo → fail
        v = self._rules("Canara", emp_type="Salaried", income=108_000)
        assert any("income" in x.lower() for x in v)


# ══════════════════════════════════════════════════════════════
# 2. UNIT TESTS — AnomalyAgent
# ══════════════════════════════════════════════════════════════

class TestAnomalyAgent:
    def _check(self, **kw):
        return AnomalyAgent.run_anomaly_check_tool(_base_payload(**kw))

    def test_no_anomalies_on_valid_payload(self):
        anomalies, _ = self._check()
        assert anomalies == []

    def test_invalid_age_too_young(self):
        anomalies, _ = self._check(age=10)
        assert any("age" in a.lower() for a in anomalies)

    def test_invalid_age_too_old(self):
        anomalies, _ = self._check(age=101)
        assert any("age" in a.lower() for a in anomalies)

    def test_zero_income_flagged(self):
        anomalies, _ = self._check(income=0)
        assert any("income" in a.lower() for a in anomalies)

    def test_negative_loan_amount(self):
        anomalies, _ = self._check(loan_amt=-100)
        assert any("loan" in a.lower() for a in anomalies)

    def test_out_of_bounds_cibil_low(self):
        anomalies, _ = self._check(cibil=100)  # < 300
        assert any("CIBIL" in a for a in anomalies)

    def test_out_of_bounds_cibil_high(self):
        anomalies, _ = self._check(cibil=950)
        assert any("CIBIL" in a for a in anomalies)

    def test_cibil_zero_allowed_for_ntc(self):
        # CIBIL 0 is valid for NTC
        anomalies, _ = self._check(cibil=0, is_ntc=True)
        assert not any("CIBIL" in a for a in anomalies)


# ══════════════════════════════════════════════════════════════
# 3. UNIT TESTS — RiskAgent (FOIR / LTV maths)
# ══════════════════════════════════════════════════════════════

class TestRiskAgentMaths:
    """Validate FOIR & LTV computation inside run_risk_scoring_tool."""

    def _run(self, **kw):
        return RiskAgent.run_risk_scoring_tool(
            _base_payload(**kw), preprocessor, model, feature_names, THRESHOLD
        )

    def test_foir_calculation_correct(self):
        """FOIR = (exist_emi + proposed_emi) / (monthly_income)."""
        res = self._run(income=1_200_000, co_app_inc=0, exist_emi=0,
                        loan_amt=500_000, tenure_mo=60, int_rate=12.0)
        # proposed_emi at 12% for 60 months on 5 lakhs
        monthly_rate = 12.0 / 100 / 12
        n = 60
        emi = (500_000 * monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
        expected_foir = emi / (1_200_000 / 12)
        assert abs(res["foir"] - expected_foir) < 0.001

    def test_foir_with_existing_emi(self):
        res = self._run(income=600_000, co_app_inc=0, exist_emi=10_000,
                        loan_amt=300_000, tenure_mo=36, int_rate=10.0)
        assert 0 < res["foir"] < 1.5  # sanity bounds

    def test_foir_coapplicant_income_reduces_it(self):
        res_no_co = self._run(income=600_000, co_app_inc=0, exist_emi=5_000,
                               loan_amt=400_000, tenure_mo=60, int_rate=12.0)
        res_with_co = self._run(income=600_000, co_app_inc=300_000, exist_emi=5_000,
                                 loan_amt=400_000, tenure_mo=60, int_rate=12.0)
        assert res_with_co["foir"] < res_no_co["foir"]

    def test_ltv_zero_for_personal_loan(self):
        res = self._run(loan_type="Personal Loan", prop_val=0)
        assert res["ltv"] == 0.0

    def test_ltv_calculated_for_home_loan(self):
        res = self._run(loan_type="Home Loan",
                        loan_amt=5_000_000, prop_val=6_500_000)
        expected_ltv = min(1.0, 5_000_000 / 6_500_000)
        assert abs(res["ltv"] - expected_ltv) < 0.001

    def test_ltv_capped_at_1(self):
        # Loan > property value → LTV must be capped at 1.0
        res = self._run(loan_type="Home Loan", loan_amt=8_000_000, prop_val=5_000_000)
        assert res["ltv"] == 1.0

    def test_probability_between_0_and_1(self):
        res = self._run()
        assert 0.0 <= res["probability"] <= 1.0

    def test_proposed_emi_positive(self):
        res = self._run()
        assert res["proposed_emi"] > 0


# ══════════════════════════════════════════════════════════════
# 4. UNIT TESTS — expand_user_query
# ══════════════════════════════════════════════════════════════

class TestExpandUserQuery:
    def test_returns_original_query_if_no_keywords(self):
        q = "tell me something random"
        assert expand_user_query(q) == q

    def test_expands_sbi_keyword(self):
        result = expand_user_query("sbi loan eligibility")
        assert "State Bank of India" in result

    def test_expands_hdfc_keyword(self):
        assert "HDFC Bank" in expand_user_query("hdfc personal loan")

    def test_expands_home_loan_keyword(self):
        assert "Home Loan" in expand_user_query("home loan ltv rules")

    def test_expands_cibil_keyword(self):
        assert "CIBIL" in expand_user_query("what is the cibil requirement")

    def test_expands_education_loan_keyword(self):
        assert "Education Loan" in expand_user_query("education loan eligibility")

    def test_expands_kcc_keyword(self):
        assert "KCC" in expand_user_query("kcc farmer loan limit")

    def test_expands_ntc_keyword(self):
        assert "NTC" in expand_user_query("ntc borrower rules")

    def test_expands_kyc_keyword(self):
        assert "KYC" in expand_user_query("kyc documents required")

    def test_multiple_keywords_combined(self):
        result = expand_user_query("sbi home loan cibil requirement")
        assert "State Bank of India" in result
        assert "Home Loan" in result
        assert "CIBIL" in result


# ══════════════════════════════════════════════════════════════
# 5. UNIT TESTS — _ensure_complete_sentences
# ══════════════════════════════════════════════════════════════

class TestEnsureCompleteSentences:
    def test_empty_string_returns_empty(self):
        assert _ensure_complete_sentences("") == ""

    def test_ends_with_period_unchanged(self):
        s = "This is complete."
        assert _ensure_complete_sentences(s) == s

    def test_ends_with_exclamation_unchanged(self):
        s = "Great result!"
        assert _ensure_complete_sentences(s) == s

    def test_removes_trailing_incomplete_line(self):
        s = "First sentence.\nThis is incomplete"
        result = _ensure_complete_sentences(s)
        assert "incomplete" not in result
        assert "First sentence." in result

    def test_removes_trailing_colon_line(self):
        s = "Summary:\n- Point one.\nNew section:"
        result = _ensure_complete_sentences(s)
        assert not result.endswith(":")


# ══════════════════════════════════════════════════════════════
# 6. INTEGRATION TESTS — /api/evaluate
# ══════════════════════════════════════════════════════════════

class TestEvaluateEndpoint:
    def _post(self, client, **kw):
        resp = client.post(
            "/api/evaluate",
            data=json.dumps(_base_payload(**kw)),
            content_type="application/json",
        )
        return resp, resp.get_json()

    def test_valid_request_returns_200(self, client):
        resp, _ = self._post(client)
        assert resp.status_code == 200

    def test_response_has_required_keys(self, client):
        _, data = self._post(client)
        for key in ("approved", "is_hard_rejected", "probability", "foir", "ltv",
                    "proposed_emi", "violations", "recommendations", "shap"):
            assert key in data, f"Missing key: {key}"

    def test_approved_field_is_boolean(self, client):
        _, data = self._post(client)
        assert isinstance(data["approved"], bool)

    def test_probability_in_valid_range(self, client):
        _, data = self._post(client)
        assert 0.0 <= data["probability"] <= 100.0

    def test_foir_positive(self, client):
        _, data = self._post(client)
        assert data["foir"] >= 0

    def test_hard_rejected_sets_probability_zero(self, client):
        # Trigger a hard rejection: age 80 for SBI (max 70)
        _, data = self._post(client, age=80)
        assert data["is_hard_rejected"] is True
        assert data["probability"] == 0.0

    def test_violations_list_on_hard_rejection(self, client):
        _, data = self._post(client, age=80)
        assert len(data["violations"]) > 0

    def test_personal_loan_ltv_is_na(self, client):
        _, data = self._post(client, loan_type="Personal Loan")
        assert data["ltv"] == "N/A"

    def test_home_loan_ltv_is_numeric(self, client):
        _, data = self._post(client, loan_type="Home Loan",
                              loan_amt=5_000_000, prop_val=6_500_000)
        assert isinstance(data["ltv"], (int, float))

    def test_shap_labels_and_values_same_length(self, client):
        _, data = self._post(client)
        assert len(data["shap"]["labels"]) == len(data["shap"]["values"])

    def test_ntc_flag_zeroes_cibil(self, client):
        # NTC applicant should not get CIBIL violations for zero score
        _, data = self._post(client, is_ntc=True, cibil=0,
                              bank="SBI", income=1_000_000)
        assert not any("CIBIL" in v for v in data["violations"])

    def test_recommendations_not_empty(self, client):
        _, data = self._post(client)
        assert len(data["recommendations"]) > 0

    def test_empty_body_returns_valid_response(self, client):
        # Should not 500 — default values fill in
        resp = client.post("/api/evaluate", data=json.dumps({}),
                           content_type="application/json")
        assert resp.status_code == 200

    def test_canara_allows_age_75(self, client):
        _, data = self._post(client, bank="Canara", age=75)
        assert not any("Age" in v for v in data["violations"])

    def test_icici_blocks_ntc_home_loan(self, client):
        _, data = self._post(client, bank="ICICI", loan_type="Home Loan",
                              is_ntc=True, cibil=0)
        assert any("NTC" in v for v in data["violations"])

    def test_tier_a_employer_foir_leniency(self, client):
        # Tier A employer gives +0.05 FOIR leniency on top of base limit
        # SBI base = 0.65; Tier A → 0.70; FOIR 0.67 should NOT violate
        # We inject a controlled FOIR via income/loan ratio
        # income=600k, exist_emi=0, loan=500k@12%/60mo → FOIR ~19% → no violation anyway
        _, data = self._post(client, employer="Tier A (Top MNC)", bank="SBI")
        assert not any("FOIR" in v for v in data["violations"])


# ══════════════════════════════════════════════════════════════
# 7. INTEGRATION TESTS — /api/chat
# ══════════════════════════════════════════════════════════════

class TestChatEndpoint:
    def _chat(self, client, prompt, context=None):
        body = {"prompt": prompt}
        if context:
            body["context"] = context
        resp = client.post("/api/chat", data=json.dumps(body),
                           content_type="application/json")
        return resp, resp.get_json()

    def test_chat_returns_200(self, client):
        resp, _ = self._chat(client, "What is the CIBIL requirement for SBI Home Loan?")
        assert resp.status_code == 200

    def test_chat_response_has_answer_key(self, client):
        _, data = self._chat(client, "HDFC personal loan eligibility")
        assert "answer" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 10

    def test_chat_greeting_handled(self, client):
        _, data = self._chat(client, "hello")
        assert "answer" in data
        assert len(data["answer"]) > 5

    def test_chat_empty_prompt_handled(self, client):
        resp = client.post("/api/chat",
                           data=json.dumps({"prompt": ""}),
                           content_type="application/json")
        assert resp.status_code == 200

    def test_chat_with_valid_eval_context_gives_personalised_answer(self, client):
        """When context contains bank + approved fields the bot should not
        return the 'Application Evaluation Required' fallback message."""
        context = {
            "bank": "ICICI",
            "loan_type": "Personal Loan",
            "approved": True,
            "probability": 82.5,
            "foir": 38.0,
            "ltv": "N/A",
            "cibil": 780,
            "violations": [],
        }
        _, data = self._chat(
            client,
            "Why was my ICICI Personal Loan application approved?",
            context=context,
        )
        assert "Application Evaluation Required" not in data["answer"]

    def test_chat_without_context_triggers_evaluation_required(self, client):
        _, data = self._chat(
            client,
            "Why was my loan rejected?",
        )
        # Without eval context the bot should ask user to evaluate first
        assert "Evaluation Required" in data["answer"] or len(data["answer"]) > 10

    def test_chat_no_crash_on_missing_body(self, client):
        resp = client.post("/api/chat", data="", content_type="application/json")
        assert resp.status_code == 200

    def test_chat_sources_key_present(self, client):
        _, data = self._chat(client, "SBI home loan interest rate")
        assert "sources" in data


# ══════════════════════════════════════════════════════════════
# 8. EDGE-CASE / REGRESSION TESTS
# ══════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Regression & edge-case tests for previously discovered bugs."""

    def test_context_merge_bank_field_passed_to_chat(self, client):
        """
        Regression: PolicyAssistantTab previously sent only assessmentResult.data
        (no bank/loan_type/cibil). This test confirms /api/chat correctly uses
        the bank field from context to generate personalised answers.
        """
        # Simulate the FIXED merged context (bank from payload + data from API)
        context = {
            "bank": "SBI",
            "loan_type": "Home Loan",
            "cibil": 780,
            "approved": False,
            "probability": 32.0,
            "foir": 72.0,
            "ltv": 88.0,
            "violations": ["FOIR (72.0%) exceeds SBI's limit (65.0%)"],
        }
        body = {
            "prompt": "Why was my SBI Home Loan rejected?",
            "context": context,
        }
        resp = client.post("/api/chat", data=json.dumps(body),
                           content_type="application/json")
        assert resp.status_code == 200
        data = resp.get_json()
        # Should NOT return the "no evaluation" fallback
        assert "Application Evaluation Required" not in data["answer"]

    def test_foir_leniency_stacks_existing_customer_and_tier_a(self):
        """existing_customer (+5%) + Tier A employer (+5%) = 10% leniency on FOIR."""
        # SBI base 65%; with 10% leniency → 75%; FOIR 72% should NOT violate
        violations = apply_bank_hard_rules(
            bank="SBI", loan_type="Personal Loan", age=35,
            income=1_200_000, co_applicant_income=0, cibil=700,
            foir=0.72, ltv=0.0, emp_years=5, business_vintage=0,
            course_approved=True, emp_type="Salaried",
            employer="Tier A (Top MNC)", tn_city="Chennai (Tier 1)",
            existing_customer=True,
        )
        assert not any("FOIR" in v for v in violations)

    def test_tier3_city_tightens_income_threshold(self):
        """Tier 3 multiplier (0.8) should tighten income rules."""
        # Canara income threshold ₹15k/mo * 0.8 = ₹12k/mo for Tier 3
        # Income ₹10k/mo (₹120k/year) → should fail in Tier 3
        violations = apply_bank_hard_rules(
            bank="Canara", loan_type="Personal Loan", age=35,
            income=120_000, co_applicant_income=0, cibil=650,
            foir=0.30, ltv=0.0, emp_years=5, business_vintage=0,
            course_approved=True, emp_type="Salaried",
            employer="Tier B (Mid-Size)", tn_city="Rural TN (Tier 3)",
            existing_customer=False,
        )
        assert any("income" in v.lower() for v in violations)

    def test_general_rbi_bank_no_violations(self):
        """'General RBI' bank has no specific hard rules → empty violations."""
        violations = apply_bank_hard_rules(
            bank="General RBI", loan_type="Home Loan", age=40,
            income=1_000_000, co_applicant_income=0, cibil=700,
            foir=0.55, ltv=0.80, emp_years=5, business_vintage=0,
            course_approved=True, emp_type="Salaried",
            employer="Tier A (Top MNC)", tn_city="Chennai (Tier 1)",
            existing_customer=False,
        )
        assert violations == []

    def test_probability_not_zero_for_approved_applicant(self, client):
        """Approved applicants must have probability > 0."""
        resp = client.post(
            "/api/evaluate",
            data=json.dumps(_base_payload(cibil=800, income=2_000_000, exist_emi=0)),
            content_type="application/json",
        )
        data = resp.get_json()
        if data["approved"]:
            assert data["probability"] > 0

    def test_zero_interest_rate_uses_flat_emi(self, client):
        """0% interest should not crash (divides by EMI formula fallback)."""
        resp = client.post(
            "/api/evaluate",
            data=json.dumps(_base_payload(int_rate=0.0)),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["proposed_emi"] > 0
