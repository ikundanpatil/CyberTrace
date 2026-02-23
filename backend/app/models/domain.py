from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import re


class DomainAnalysisRequest(BaseModel):
    """Request model for domain analysis"""
    domain: str = Field(..., description="Domain name to analyze")
    analyst_name: Optional[str] = Field(None, description="Police officer name")
    case_id: Optional[str] = Field(None, description="FIR/Case ID")
    
    @validator('domain')
    def validate_domain(cls, v):
        # Remove http://, https://, www.
        v = re.sub(r'^https?://', '', v)
        v = re.sub(r'^www\.', '', v)
        v = v.split('/')[0]  # Remove path
        
        # Basic domain validation
        domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, v):
            raise ValueError('Invalid domain format')
        return v.lower()


class DomainInfo(BaseModel):
    """Domain registration information"""
    registrar: Optional[str] = None
    creation_date: Optional[str] = None
    expiry_date: Optional[str] = None
    updated_date: Optional[str] = None
    domain_age_days: Optional[int] = None
    nameservers: List[str] = []
    status: List[str] = []


class HostingInfo(BaseModel):
    """Hosting and network information"""
    ip_address: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    isp: Optional[str] = None
    asn: Optional[str] = None
    organization: Optional[str] = None
    hosting_type: Optional[str] = "unknown"  # shared, dedicated, cloud


class SecurityInfo(BaseModel):
    """Security-related information"""
    https_enabled: bool = False
    ssl_valid: bool = False
    ssl_issuer: Optional[str] = None
    ssl_expiry: Optional[str] = None
    blacklisted: bool = False
    blacklist_sources: List[str] = []


class RiskAssessment(BaseModel):
    """
    Risk assessment results using the Safety Score system.
    
    Safety Score Scale:
    - 1.0 to 10.0 (higher = safer)
    - 10/10 = Perfectly Safe
    - 1/10 = Critical Danger
    
    Risk Levels:
    - HIGH: Score 1.0 - 3.9 (Dangerous)
    - MEDIUM: Score 4.0 - 6.9 (Suspicious)
    - LOW: Score 7.0 - 10.0 (Safe)
    """
    risk_score: float = Field(..., ge=1.0, le=10.0, description="Safety score (1-10, higher is safer)")
    risk_level: str = Field(..., pattern="^(LOW|MEDIUM|HIGH)$")
    confidence: str = Field(..., pattern="^(low|medium|high)$")
    reasons: List[str] = []
    explanation: Optional[str] = None


class DomainAnalysisResponse(BaseModel):
    """Complete domain analysis response"""
    status: str = "success"
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)