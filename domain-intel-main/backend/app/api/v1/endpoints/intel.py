"""
Threat Intelligence API Endpoints

Provides endpoints for threat map visualization and statistics.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel
from app.db.base import get_db
from app.db.models import ThreatIntel

router = APIRouter()


# =====================================================
# Response Models
# =====================================================

class MapPoint(BaseModel):
    """Lightweight point for heatmap rendering."""
    lat: float
    lon: float
    type: str


class CountryCount(BaseModel):
    country: str
    count: int


class TypeCount(BaseModel):
    type: str
    count: int


class ThreatStats(BaseModel):
    """Aggregated threat statistics."""
    total_threats: int
    by_country: List[CountryCount]
    by_type: List[TypeCount]


# =====================================================
# Endpoints
# =====================================================

@router.get("/map", response_model=List[MapPoint])
async def get_threat_map(
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """
    Get threat coordinates for heatmap visualization.
    
    Returns lightweight lat/lon/type objects for map rendering.
    Filters out entries with missing coordinates.
    """
    threats = (
        db.query(
            ThreatIntel.latitude,
            ThreatIntel.longitude,
            ThreatIntel.threat_type
        )
        .filter(ThreatIntel.latitude.isnot(None))
        .filter(ThreatIntel.longitude.isnot(None))
        .limit(limit)
        .all()
    )
    
    return [
        MapPoint(lat=t.latitude, lon=t.longitude, type=t.threat_type)
        for t in threats
    ]


@router.get("/stats", response_model=ThreatStats)
async def get_threat_stats(db: Session = Depends(get_db)):
    """
    Get aggregated threat statistics for dashboard charts.
    
    Returns:
        - Total threat count
        - Top 5 countries by threat count
        - Breakdown by threat type
    """
    # Total count
    total = db.query(func.count(ThreatIntel.id)).scalar() or 0
    
    # Top 5 countries
    country_stats = (
        db.query(
            ThreatIntel.country,
            func.count(ThreatIntel.id).label("count")
        )
        .filter(ThreatIntel.country.isnot(None))
        .group_by(ThreatIntel.country)
        .order_by(func.count(ThreatIntel.id).desc())
        .limit(5)
        .all()
    )
    
    # By threat type
    type_stats = (
        db.query(
            ThreatIntel.threat_type,
            func.count(ThreatIntel.id).label("count")
        )
        .group_by(ThreatIntel.threat_type)
        .order_by(func.count(ThreatIntel.id).desc())
        .all()
    )
    
    return ThreatStats(
        total_threats=total,
        by_country=[
            CountryCount(country=c.country, count=c.count)
            for c in country_stats
        ],
        by_type=[
            TypeCount(type=t.threat_type, count=t.count)
            for t in type_stats
        ]
    )
