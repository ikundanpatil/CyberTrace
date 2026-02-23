"""
Safety Score System - Rule-Based Risk Assessment

Court-defensible scoring logic for domain intelligence.

Design Principles:
- NO AI predictions
- NO black-box decisions  
- ONLY transparent, explainable rules
- Each rule has a penalty value and clear reason

Scoring System:
- Scale: 1.0 to 10.0
- Higher score = SAFER domain
- 10/10 = Perfectly Safe
- 1/10 = Critical Danger
"""
from typing import Dict, List, Tuple


class RiskRules:
    """
    Rule-based Safety Score calculator.
    
    All domains start at 10.0 (perfect) and lose points for risk factors.
    """
    
    # Risk level classifications
    RISK_HIGH = "HIGH"      # Score 1.0 - 3.9 (Dangerous)
    RISK_MEDIUM = "MEDIUM"  # Score 4.0 - 6.9 (Suspicious)
    RISK_LOW = "LOW"        # Score 7.0 - 10.0 (Safe)
    
    # Score boundaries
    MAX_SCORE = 10.0
    MIN_SCORE = 1.0
    
    # Thresholds for risk level classification
    LOW_RISK_THRESHOLD = 7.0     # >= 7.0 is LOW risk (safe)
    MEDIUM_RISK_THRESHOLD = 4.0  # >= 4.0 but < 7.0 is MEDIUM risk
    # Below 4.0 is HIGH risk (dangerous)
    
    # ==========================================================================
    # PENALTY DEFINITIONS
    # ==========================================================================
    PENALTY_BLACKLISTED = 5.0           # Critical: known malicious
    PENALTY_NEW_DOMAIN = 3.0            # Age < 7 days
    PENALTY_RECENT_DOMAIN = 2.0         # Age < 30 days
    PENALTY_YOUNG_DOMAIN = 1.0          # Age < 90 days
    PENALTY_NO_HTTPS = 2.0              # SSL missing or invalid
    PENALTY_HIGH_RISK_GEO = 2.0         # Hosted in high-risk country
    PENALTY_SUSPICIOUS_TLD = 1.0        # Risky TLD
    PENALTY_FRAUD_KEYWORD = 0.5         # Phishing keywords in domain
    PENALTY_SHARED_HOSTING = 1.0        # Shared hosting infrastructure
    
    # High-risk countries (cyber threat origins)
    HIGH_RISK_COUNTRIES = [
        "CN",  # China
        "RU",  # Russia
        "VN",  # Vietnam
        "UA",  # Ukraine
        "KP",  # North Korea
        "IR",  # Iran
    ]
    
    # Suspicious TLDs (frequently abused)
    SUSPICIOUS_TLDS = [
        ".xyz", ".top", ".club", ".loan", ".zip", ".gq",
        ".win", ".review", ".cricket", ".work", ".science"
    ]
    
    # Fraud/phishing keywords in domain names
    FRAUD_KEYWORDS = [
        "login", "verify", "bank", "secure", "update", "wallet",
        "signin", "account", "password", "confirm", "suspend"
    ]
    
    # Abused registrars (optional tracking)
    ABUSED_REGISTRARS = ["namecheap", "freenom", "dynadot"]
    
    @staticmethod
    def calculate_risk_score(normalized_data: Dict) -> Tuple[float, List[str]]:
        """
        Calculate Safety Score based on domain characteristics.
        
        Args:
            normalized_data: Dictionary with domain analysis results
            
        Returns:
            Tuple of (safety_score, list_of_penalty_reasons)
            - safety_score: 1.0 to 10.0 (higher = safer)
            - reasons: List explaining each penalty applied
        """
        score = RiskRules.MAX_SCORE  # Start at perfect 10.0
        reasons = []
        
        # ======================================================================
        # RULE 1: Blacklist Status (CRITICAL)
        # ======================================================================
        if normalized_data.get('blacklisted', False):
            score -= RiskRules.PENALTY_BLACKLISTED
            sources = normalized_data.get('blacklist_sources', [])
            source_str = ', '.join(sources) if sources else 'security databases'
            reasons.append(f"Blacklisted in {source_str} (-5.0)")
        
        # ======================================================================
        # RULE 2: Domain Age (NON-STACKING - only apply one)
        # ======================================================================
        domain_age = normalized_data.get('domain_age_days')
        if domain_age is not None:
            if domain_age < 7:
                score -= RiskRules.PENALTY_NEW_DOMAIN
                reasons.append(f"Domain is only {domain_age} days old (-3.0)")
            elif domain_age < 30:
                score -= RiskRules.PENALTY_RECENT_DOMAIN
                reasons.append(f"Domain is only {domain_age} days old (-2.0)")
            elif domain_age < 90:
                score -= RiskRules.PENALTY_YOUNG_DOMAIN
                reasons.append(f"Domain is only {domain_age} days old (-1.0)")
        
        # ======================================================================
        # RULE 3: HTTPS/SSL Status
        # ======================================================================
        https_enabled = normalized_data.get('https_enabled', False)
        ssl_valid = normalized_data.get('ssl_valid', False)
        
        if not https_enabled or not ssl_valid:
            score -= RiskRules.PENALTY_NO_HTTPS
            if not https_enabled:
                reasons.append("No HTTPS encryption (-2.0)")
            else:
                reasons.append("SSL certificate invalid or expired (-2.0)")
        
        # ======================================================================
        # RULE 4: High-Risk Geographic Location
        # ======================================================================
        country_code = normalized_data.get('country_code', '').upper()
        if country_code in RiskRules.HIGH_RISK_COUNTRIES:
            score -= RiskRules.PENALTY_HIGH_RISK_GEO
            reasons.append(f"Hosted in high-risk region: {country_code} (-2.0)")
        
        # ======================================================================
        # RULE 5: Suspicious TLD
        # ======================================================================
        domain = normalized_data.get('domain', '')
        tld = f".{domain.split('.')[-1].lower()}" if '.' in domain else ""
        if tld in RiskRules.SUSPICIOUS_TLDS:
            score -= RiskRules.PENALTY_SUSPICIOUS_TLD
            reasons.append(f"Suspicious TLD: {tld} (-1.0)")
        
        # ======================================================================
        # RULE 6: Fraud Keywords in Domain Name
        # ======================================================================
        domain_lower = domain.lower()
        found_keywords = [kw for kw in RiskRules.FRAUD_KEYWORDS if kw in domain_lower]
        if found_keywords:
            score -= RiskRules.PENALTY_FRAUD_KEYWORD
            reasons.append(f"Contains fraud keyword: '{found_keywords[0]}' (-0.5)")
        
        # ======================================================================
        # RULE 7: Shared Hosting (if detectable)
        # ======================================================================
        hosting_type = normalized_data.get('hosting_type', '').lower()
        if hosting_type == 'shared':
            score -= RiskRules.PENALTY_SHARED_HOSTING
            reasons.append("Uses shared hosting infrastructure (-1.0)")
        
        # ======================================================================
        # FINALIZE: Clamp to valid range and round
        # ======================================================================
        score = max(RiskRules.MIN_SCORE, min(RiskRules.MAX_SCORE, score))
        score = round(score, 1)
        
        return score, reasons
    
    @staticmethod
    def get_risk_level(score: float) -> str:
        """
        Convert numeric safety score to risk level.
        
        - LOW risk (Safe): 7.0 - 10.0
        - MEDIUM risk (Suspicious): 4.0 - 6.9
        - HIGH risk (Dangerous): 1.0 - 3.9
        """
        if score >= RiskRules.LOW_RISK_THRESHOLD:
            return RiskRules.RISK_LOW
        elif score >= RiskRules.MEDIUM_RISK_THRESHOLD:
            return RiskRules.RISK_MEDIUM
        else:
            return RiskRules.RISK_HIGH
    
    @staticmethod
    def get_confidence_level(data_completeness: float) -> str:
        """
        Determine assessment confidence based on data completeness.
        
        Args:
            data_completeness: Percentage of available data (0.0 to 1.0)
        """
        if data_completeness >= 0.8:
            return "high"
        elif data_completeness >= 0.5:
            return "medium"
        else:
            return "low"