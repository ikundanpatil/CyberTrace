from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Converts messy external API responses into clean, standardized data
    
    Why this matters:
    - Different APIs return data in different formats
    - Missing fields need safe defaults
    - Dates need standardization
    - Country codes need consistency
    
    This layer ensures Risk Engine always receives predictable input
    """
    
    @staticmethod
    def normalize_whois_data(raw_whois: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize WHOIS/RDAP data"""
        normalized = {}
        
        try:
            # Registrar
            normalized['registrar'] = raw_whois.get('registrar', 'Unknown')
            
            # Dates
            creation_date = raw_whois.get('creation_date')
            if creation_date:
                normalized['creation_date'] = DataNormalizer._format_date(creation_date)
                normalized['domain_age_days'] = DataNormalizer._calculate_age(creation_date)
            
            expiry_date = raw_whois.get('expiration_date')
            if expiry_date:
                normalized['expiry_date'] = DataNormalizer._format_date(expiry_date)
            
            # Nameservers
            nameservers = raw_whois.get('name_servers', [])
            if isinstance(nameservers, list):
                normalized['nameservers'] = [ns.lower() for ns in nameservers]
            else:
                normalized['nameservers'] = []
            
            # Status
            status = raw_whois.get('status', [])
            normalized['status'] = status if isinstance(status, list) else [status] if status else []
            
        except Exception as e:
            logger.error(f"WHOIS normalization error: {str(e)}")
        
        return normalized
    
    @staticmethod
    def normalize_ip_data(raw_ip: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize IP geolocation data"""
        normalized = {}
        
        try:
            normalized['ip_address'] = raw_ip.get('ip')
            normalized['country'] = raw_ip.get('country')
            normalized['country_code'] = raw_ip.get('country_code', '').upper()
            normalized['city'] = raw_ip.get('city')
            normalized['region'] = raw_ip.get('region')
            normalized['isp'] = raw_ip.get('isp') or raw_ip.get('org')
            
            # ASN
            asn = raw_ip.get('asn')
            if asn:
                normalized['asn'] = f"AS{asn}" if not str(asn).startswith('AS') else asn
            
            normalized['organization'] = raw_ip.get('organization') or raw_ip.get('org')
            
            # Determine hosting type (heuristic)
            isp_lower = (normalized.get('isp') or '').lower()
            if any(cloud in isp_lower for cloud in ['aws', 'azure', 'google cloud', 'digitalocean']):
                normalized['hosting_type'] = 'cloud'
            elif 'dedicated' in isp_lower:
                normalized['hosting_type'] = 'dedicated'
            else:
                normalized['hosting_type'] = 'shared'
                
        except Exception as e:
            logger.error(f"IP normalization error: {str(e)}")
        
        return normalized
    
    @staticmethod
    def normalize_ssl_data(raw_ssl: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize SSL/HTTPS data"""
        normalized = {}
        
        try:
            normalized['https_enabled'] = raw_ssl.get('https_enabled', False)
            normalized['ssl_valid'] = raw_ssl.get('ssl_valid', False)
            normalized['ssl_issuer'] = raw_ssl.get('ssl_issuer')
            normalized['ssl_expiry'] = raw_ssl.get('ssl_expiry')
            
        except Exception as e:
            logger.error(f"SSL normalization error: {str(e)}")
        
        return normalized
    
    @staticmethod
    def normalize_blacklist_data(raw_blacklist: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize blacklist check data"""
        normalized = {}
        
        try:
            normalized['blacklisted'] = raw_blacklist.get('blacklisted', False)
            normalized['blacklist_sources'] = raw_blacklist.get('sources', [])
            
        except Exception as e:
            logger.error(f"Blacklist normalization error: {str(e)}")
        
        return normalized
    
    @staticmethod
    def merge_normalized_data(domain: str, *data_dicts: Dict[str, Any]) -> Dict[str, Any]:
        """Merge all normalized data sources into single dict"""
        merged = {'domain': domain}
        
        for data_dict in data_dicts:
            merged.update(data_dict)
        
        return merged
    
    @staticmethod
    def _format_date(date_value: Any) -> Optional[str]:
        """Standardize date to ISO format string"""
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
        elif isinstance(date_value, str):
            try:
                dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d')
            except:
                return date_value
        elif isinstance(date_value, list) and len(date_value) > 0:
            return DataNormalizer._format_date(date_value[0])
        return None
    
    @staticmethod
    def _calculate_age(creation_date: Any) -> Optional[int]:
        """Calculate domain age in days"""
        try:
            if isinstance(creation_date, datetime):
                dt = creation_date
            elif isinstance(creation_date, str):
                dt = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
            elif isinstance(creation_date, list) and len(creation_date) > 0:
                return DataNormalizer._calculate_age(creation_date[0])
            else:
                return None
            
            age_days = (datetime.now() - dt).days
            return max(0, age_days)  # Prevent negative ages
            
        except Exception as e:
            logger.error(f"Age calculation error: {str(e)}")
            return None