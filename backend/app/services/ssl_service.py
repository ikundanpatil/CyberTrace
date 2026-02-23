import ssl
import socket
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SSLService:
    """SSL/HTTPS certificate checker"""
    
    def check_ssl(self, domain: str) -> Dict[str, Any]:
        """
        Check if domain has valid HTTPS/SSL
        
        Returns:
        - https_enabled: bool
        - ssl_valid: bool
        - ssl_issuer: str
        - ssl_expiry: str
        """
        result = {
            'https_enabled': False,
            'ssl_valid': False,
            'ssl_issuer': None,
            'ssl_expiry': None,
        }
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to domain on port 443
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    result['https_enabled'] = True
                    
                    # Get certificate
                    cert = ssock.getpeercert()
                    
                    if cert:
                        result['ssl_valid'] = True
                        
                        # Extract issuer
                        issuer = dict(x[0] for x in cert.get('issuer', []))
                        result['ssl_issuer'] = issuer.get('organizationName') or issuer.get('commonName')
                        
                        # Extract expiry
                        not_after = cert.get('notAfter')
                        if not_after:
                            expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                            result['ssl_expiry'] = expiry_date.strftime('%Y-%m-%d')
                            
                            # Check if expired
                            if expiry_date < datetime.now():
                                result['ssl_valid'] = False
                    
        except ssl.SSLError as e:
            logger.debug(f"SSL error for {domain}: {str(e)}")
            result['https_enabled'] = True  # SSL exists but invalid
            result['ssl_valid'] = False
        except socket.timeout:
            logger.debug(f"SSL check timeout for {domain}")
        except Exception as e:
            logger.debug(f"SSL check failed for {domain}: {str(e)}")
        
        return result