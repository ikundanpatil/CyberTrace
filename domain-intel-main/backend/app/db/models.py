"""
Database Models for DomainIntel

SQLAlchemy ORM models for persisting scan history and other data.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from datetime import datetime
from app.db.base import Base


class User(Base):
    """
    User model for authentication.
    
    Stores operator/analyst credentials and profile info.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class ScanHistory(Base):
    """
    Stores history of all domain scans performed.
    
    This enables:
    - Historical tracking of investigations
    - Analytics on scanned domains
    - Audit trail for law enforcement
    """
    __tablename__ = "scan_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    domain = Column(String(255), nullable=False, index=True)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(10), nullable=False)  # LOW, MEDIUM, HIGH
    confidence = Column(String(10), nullable=True)   # low, medium, high
    scan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    pdf_path = Column(String(500), nullable=True)
    
    # Additional useful fields
    analyst_name = Column(String(255), nullable=True)
    case_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)  # Supports IPv6
    country_code = Column(String(5), nullable=True)
    
    def __repr__(self):
        return f"<ScanHistory(id={self.id}, domain='{self.domain}', risk_level='{self.risk_level}')>"


class ThreatIntel(Base):
    """
    Threat Intelligence data for geospatial analysis.
    
    Stores indicators (IPs/domains) with threat classification
    and geographic coordinates for mapping.
    """
    __tablename__ = "threat_intel"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    indicator = Column(String(255), index=True, nullable=False)  # IP or Domain
    threat_type = Column(String(100), nullable=False)  # e.g. "Phishing", "Malware"
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    source = Column(String(100), nullable=True)  # e.g. "PhishTank", "AbuseIPDB"
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ThreatIntel(id={self.id}, indicator='{self.indicator}', type='{self.threat_type}')>"

