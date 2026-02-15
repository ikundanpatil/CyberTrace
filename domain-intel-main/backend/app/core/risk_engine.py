"""
Risk Engine - The Authority for Domain Risk Assessment

This engine makes all risk decisions using deterministic, rule-based logic.
AI is used ONLY for explanation enhancement, never for scoring.

Safe for law enforcement and court usage.
"""
from typing import Dict
from app.core.rules import RiskRules
from app.models.domain import RiskAssessment
from app.ai.explainer import AIExplainer
import logging

logger = logging.getLogger(__name__)


class RiskEngine:
    """
    The AUTHORITY — makes all risk decisions.

    Safety Score System:
    - Scale: 1.0 to 10.0
    - Higher score = SAFER domain
    - 10/10 = Perfectly Safe
    - 1/10 = Critical Danger
    
    Risk Thresholds:
    - LOW risk (Safe): 7.0 - 10.0
    - MEDIUM risk (Suspicious): 4.0 - 6.9
    - HIGH risk (Dangerous): 1.0 - 3.9
    """

    def __init__(self):
        self.rules = RiskRules()
        self.ai_explainer = AIExplainer()

    def assess_risk(self, normalized_data: Dict) -> RiskAssessment:
        """
        Perform complete risk assessment using Safety Score system.

        AI is NEVER involved in:
        - Scoring
        - Classification
        - Rule execution
        """
        try:
            # 1️⃣ Calculate safety score (source of truth)
            score, reasons = self.rules.calculate_risk_score(normalized_data)
            risk_level = self.rules.get_risk_level(score)

            # 2️⃣ Calculate confidence based on data completeness
            completeness = self._calculate_completeness(normalized_data)
            confidence = self.rules.get_confidence_level(completeness)

            # 3️⃣ Generate deterministic explanation
            explanation = self._generate_explanation(
                score, risk_level, reasons, normalized_data
            )

            # 4️⃣ Optional: AI enhancement (non-authoritative)
            ai_payload = {
                "domain": normalized_data.get("domain"),
                "risk_level": risk_level,
                "safety_score": score,
                "reasons": reasons,
                "confidence": confidence,
            }

            ai_explanation = self.ai_explainer.generate_explanation(ai_payload)
            if ai_explanation:
                explanation = ai_explanation

            logger.info(
                f"Safety assessment: {normalized_data.get('domain')} "
                f"scored {score}/10 ({risk_level} risk)"
            )

            return RiskAssessment(
                risk_score=score,
                risk_level=risk_level,
                confidence=confidence,
                reasons=reasons,
                explanation=explanation
            )

        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            raise

    def _calculate_completeness(self, data: Dict) -> float:
        """Calculate percentage of expected data fields present."""
        expected_fields = [
            "domain_age_days",
            "registrar",
            "country_code",
            "https_enabled",
            "ip_address",
        ]
        available = sum(1 for f in expected_fields if data.get(f) is not None)
        return available / len(expected_fields)

    def _generate_explanation(
        self,
        score: float,
        risk_level: str,
        reasons: list,
        data: Dict
    ) -> str:
        """
        Generate deterministic, human-readable explanation.
        
        Uses new "Safety Score" terminology throughout.
        """
        domain = data.get("domain", "this domain")

        # Build the opening statement based on risk level
        if risk_level == "HIGH":
            opening = (
                f"⚠️ DANGER: Safety score is critically low ({score}/10). "
                f"The domain '{domain}' shows multiple high-risk indicators."
            )
        elif risk_level == "MEDIUM":
            opening = (
                f"⚡ CAUTION: Safety score is moderate ({score}/10). "
                f"The domain '{domain}' has some suspicious characteristics."
            )
        else:
            opening = (
                f"✅ SAFE: Safety score is good ({score}/10). "
                f"The domain '{domain}' appears trustworthy."
            )

        # Build the reason breakdown
        if reasons:
            penalty_details = " | ".join(reasons)
            factor_text = f" Factors: {penalty_details}."
        else:
            factor_text = " No risk factors detected."

        # Build recommendation
        recommendations = {
            "HIGH": " Immediate investigation strongly recommended.",
            "MEDIUM": " Further verification may be warranted.",
            "LOW": " Standard monitoring procedures apply.",
        }
        recommendation = recommendations.get(risk_level, "")

        return opening + factor_text + recommendation
