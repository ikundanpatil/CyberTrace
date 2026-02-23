import requests
from typing import Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class IPService:
    """IP geolocation and ASN lookup service"""
    
    def __init__(self):
        self.ipwhois_api = "https://ipwho.is"
        self.ipinfo_api = "https://ipinfo.io"
    
    def get_ip_info(self, ip: str) -> Dict[str, Any]:
        """
        Get geolocation and network info for IP
        
        Returns dict with:
        - country, country_code
        - city, region
        - isp, org
        - asn
        """
        try:
            # Method 1: Try ipwho.is (free, unlimited)
            data = self._fetch_with_ipwhois(ip)
            if data:
                return data
            
            # Method 2: Try ipinfo.io (free tier)
            data = self._fetch_with_ipinfo(ip)
            if data:
                return data
            
            logger.warning(f"All IP lookup methods failed for {ip}")
            return {}
            
        except Exception as e:
            logger.error(f"IP lookup failed for {ip}: {str(e)}")
            return {}
    
    def _fetch_with_ipwhois(self, ip: str) -> Optional[Dict[str, Any]]:
        """Fetch using ipwho.is API"""
        try:
            url = f"{self.ipwhois_api}/{ip}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data.get('success', True):
                return None
            
            return {
                'ip': ip,
                'country': data.get('country'),
                'country_code': data.get('country_code'),
                'city': data.get('city'),
                'region': data.get('region'),
                'isp': data.get('connection', {}).get('isp'),
                'org': data.get('connection', {}).get('org'),
                'asn': data.get('connection', {}).get('asn'),
                'organization': data.get('connection', {}).get('org'),
            }
            
        except Exception as e:
            logger.debug(f"ipwho.is method failed: {str(e)}")
            return None
    
    def _fetch_with_ipinfo(self, ip: str) -> Optional[Dict[str, Any]]:
        """Fetch using ipinfo.io API"""
        try:
            url = f"{self.ipinfo_api}/{ip}/json"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            return {
                'ip': ip,
                'country': data.get('country'),
                'country_code': data.get('country'),
                'city': data.get('city'),
                'region': data.get('region'),
                'org': data.get('org'),
                'organization': data.get('org'),
            }
            
        except Exception as e:
            logger.debug(f"ipinfo.io method failed: {str(e)}")
            return None