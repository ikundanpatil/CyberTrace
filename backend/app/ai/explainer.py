from anthropic import Anthropic
from app.core.config import settings
from app.ai.guardrails import AIGuardrails
import logging

logger = logging.getLogger(__name__)


class AIExplainer:
    """
    AI-powered explanation generator (NARRATOR role)
    
    Position in architecture: DOWNSTREAM of Risk Engine
    Purpose: Convert technical findings to officer-friendly language
    Authority: ZERO - only explains, never decides
    """
    
    def __init__(self):
        self.client = None
        if settings.ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.guardrails = AIGuardrails()
    
    def generate_explanation(self, risk_assessment: dict) -> str:
        """
        Generate human-friendly explanation
        
        Args:
            risk_assessment: Output from Risk Engine (already computed)
        
        Returns:
            Safe, explainable text for PDF report
        """
        # If no API key, return rule-based explanation
        if not self.client:
            logger.info("AI explainer disabled - using rule-based explanation")
            return risk_assessment.get('explanation', '')
        
        try:
            # Generate safe prompt
            prompt = self.guardrails.get_safe_prompt(risk_assessment)
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            explanation = message.content[0].text
            
            # Validate output
            is_valid, result = self.guardrails.validate_output(explanation)
            
            if not is_valid:
                logger.warning(f"AI output failed validation: {result}")
                # Fallback to rule-based
                return risk_assessment.get('explanation', '')
            
            # Add disclaimer
            risk_level = risk_assessment.get('risk_level', 'MEDIUM')
            disclaimer = self.guardrails.DISCLAIMERS.get(risk_level, '')
            
            final_explanation = f"{result} {disclaimer}"
            
            logger.info("AI explanation generated successfully")
            return final_explanation
            
        except Exception as e:
            logger.error(f"AI explanation failed: {str(e)}")
            # Always fallback to rule-based
            return risk_assessment.get('explanation', '')