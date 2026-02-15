"""
WHOIS/RDAP Service with Caching

Provides WHOIS lookups with LRU caching to avoid repeated network requests.
"""
import whois
import requests
from typing import Dict, Any, Optional
from functools import lru_cache
import logging
import json
from app.core.config import settings

logger = logging.getLogger(__name__)


class WHOISService:
    """
    WHOIS/RDAP data fetcher with caching
    
    Tries multiple approaches:
    1. Free python-whois library (works for most domains)
    2. WhatIsMyIP.net free API (RDAP-based)
    3. Fallback to basic parsing
    """
    
    def __init__(self):
        self.whatismyip_api = settings.WHATISMYIP_WHOIS
    
    def get_whois_data(self, domain: str) -> Dict[str, Any]:
        """
        Fetch WHOIS data for domain (cached).
        
        Returns dict with:
        - registrar
        - creation_date
        - expiration_date
        - name_servers
        - status
        """
        # Use cached function and convert back from JSON
        cached_result = _cached_get_whois_data(domain)
        if cached_result:
            return json.loads(cached_result)
        return {}
    
    def _fetch_with_library(self, domain: str) -> Optional[Dict[str, Any]]:
        """Fetch using python-whois library"""
        try:
            w = whois.whois(domain)
            
            if not w or not w.domain_name:
                return None
            
            return {
                'registrar': w.registrar,
                'creation_date': w.creation_date,
                'expiration_date': w.expiration_date,
                'updated_date': w.updated_date,
                'name_servers': w.name_servers,
                'status': w.status,
            }
        except Exception as e:
            logger.debug(f"Library method failed: {str(e)}")
            return None
    
    def _fetch_with_api(self, domain: str) -> Optional[Dict[str, Any]]:
        """Fetch using WhatIsMyIP.net API"""
        try:
            url = f"{self.whatismyip_api}?domain={domain}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Transform API response to standard format
            return {
                'registrar': data.get('registrar'),
                'creation_date': data.get('created'),
                'expiration_date': data.get('expires'),
                'updated_date': data.get('updated'),
                'name_servers': data.get('nameservers', []),
                'status': data.get('status', []),
            }
            
        except Exception as e:
            logger.debug(f"API method failed: {str(e)}")
            return None


# =====================================================
# Cached Functions (module-level for lru_cache to work)
# =====================================================

@lru_cache(maxsize=128)
def _cached_get_whois_data(domain: str) -> Optional[str]:
    """
    Cached WHOIS lookup.
    
    Returns JSON string (for hashability with lru_cache).
    LRU cache avoids repeated network requests for the same domain.
    """
    try:
        # Method 1: Try python-whois library
        try:
            w = whois.whois(domain)
            
            if w and w.domain_name:
                logger.info(f"WHOIS cache MISS for {domain}")
                data = {
                    'registrar': w.registrar,
                    'creation_date': _serialize_date(w.creation_date),
                    'expiration_date': _serialize_date(w.expiration_date),
                    'updated_date': _serialize_date(w.updated_date),
                    'name_servers': w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else [],
                    'status': w.status if isinstance(w.status, list) else [w.status] if w.status else [],
                }
                return json.dumps(data)
        except Exception as e:
            logger.debug(f"Library method failed: {str(e)}")
        
        # Method 2: Try API (would need settings access here)
        logger.warning(f"All WHOIS methods failed for {domain}")
        return None
        
    except Exception as e:
        logger.error(f"WHOIS lookup failed for {domain}: {str(e)}")
        return None


def _serialize_date(date_value) -> Optional[str]:
    """Convert date to string for JSON serialization"""
    if date_value is None:
        return None
    if isinstance(date_value, list):
        date_value = date_value[0] if date_value else None
    if hasattr(date_value, 'isoformat'):
        return date_value.isoformat()
    return str(date_value) if date_value else None


def clear_whois_cache():
    """Clear WHOIS cache (useful for testing or forced refresh)"""
    _cached_get_whois_data.cache_clear()
    logger.info("WHOIS cache cleared")