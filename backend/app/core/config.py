from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """
    Central configuration for DomainIntel

    - Strictly validated
    - Court / investigation safe
    - AI is optional and gated
    """

    # -----------------------------
    # Application
    # -----------------------------
    APP_NAME: str = "DomainIntel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # -----------------------------
    # CORS
    # -----------------------------
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
    ]

    # -----------------------------
    # External API Keys (Optional)
    # -----------------------------
    WHOIS_API_KEY: Optional[str] = None
    VIRUSTOTAL_API_KEY: Optional[str] = None

    # -----------------------------
    # AI Configuration (Optional)
    # -----------------------------
    AI_ENABLED: bool = False
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # -----------------------------
    # Database
    # -----------------------------
    DATABASE_URL: str = "sqlite:///./domainintel.db"

    # -----------------------------
    # Report Settings
    # -----------------------------
    REPORT_OUTPUT_DIR: str = "./reports"
    MAX_REPORT_AGE_DAYS: int = 30

    # -----------------------------
    # Risk Thresholds
    # -----------------------------
    DOMAIN_AGE_HIGH_RISK_DAYS: int = 7
    DOMAIN_AGE_MEDIUM_RISK_DAYS: int = 30

    # -----------------------------
    # External Endpoints
    # -----------------------------
    IPWHOIS_API: str = "https://api.ipwhois.org/ip"
    WHATISMYIP_WHOIS: str = "https://www.whatismyip.net/whois/"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
