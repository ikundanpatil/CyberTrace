class AIGuardrails:
    """
    Safety rules for AI-generated explanations
    
    CRITICAL: AI must NEVER make accusations or predictions
    AI can ONLY explain what the rules already determined
    """
    
    # Forbidden phrases - AI must never say these
    FORBIDDEN_PHRASES = [
        "this is fraud",
        "this is malicious",
        "this is phishing",
        "ai predicts",
        "ai detected",
        "guilty",
        "criminal",
        "will cause",
        "definitely",
    ]
    
    # Required disclaimers
    DISCLAIMERS = {
        "HIGH": "Based on the factors analyzed, this domain requires immediate verification and investigation.",
        "MEDIUM": "Based on the factors analyzed, further investigation may be warranted.",
        "LOW": "Based on the factors analyzed, standard monitoring procedures apply."
    }
    
    @staticmethod
    def validate_output(text: str) -> tuple[bool, str]:
        """
        Validate AI output against safety rules
        
        Returns:
            (is_valid, error_message or cleaned_text)
        """
        text_lower = text.lower()
        
        # Check for forbidden phrases
        for phrase in AIGuardrails.FORBIDDEN_PHRASES:
            if phrase in text_lower:
                return False, f"Output contains forbidden phrase: '{phrase}'"
        
        # Ensure no accusatory language
        accusatory_words = ['guilty', 'criminal', 'fraud', 'scam', 'fake']
        for word in accusatory_words:
            if word in text_lower and 'indicator' not in text_lower:
                return False, f"Output contains accusatory language: '{word}'"
        
        return True, text
    
    @staticmethod
    def get_safe_prompt(risk_data: dict) -> str:
        """
        Generate safe prompt for AI that enforces guardrails
        """
        prompt = f"""You are a forensic analyst assistant. Your role is to EXPLAIN findings, not make judgments.

STRICT RULES:
- NEVER say "this is fraud" or "this is malicious"
- ONLY explain what the data shows
- Use phrases like "indicates", "suggests", "associated with"
- Base explanation ONLY on the provided factors

Risk Assessment Data:
- Risk Level: {risk_data.get('risk_level')}
- Risk Score: {risk_data.get('risk_score')}
- Factors: {', '.join(risk_data.get('reasons', []))}

Write a 2-3 sentence explanation for a police officer that:
1. Summarizes the technical findings in plain language
2. Connects the factors to the risk level
3. Ends with appropriate next steps

Remember: You are explaining what was found, not predicting what will happen."""
        
        return prompt