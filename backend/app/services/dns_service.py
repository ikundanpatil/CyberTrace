"""
DNS Resolution Service with Caching

Provides DNS lookups with LRU caching to avoid repeated network requests.
Uses explicit public DNS servers (Cloudflare, Google) for reliability.
"""
import dns.resolver
import socket
from typing import List, Optional, Tuple
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# Public DNS Configuration
# =============================================================================
# Ordered by reliability and speed. Cloudflare is generally fastest.
PUBLIC_DNS_SERVERS: List[str] = [
    "1.1.1.1",        # Cloudflare Primary
    "1.0.0.1",        # Cloudflare Secondary
    "8.8.8.8",        # Google Primary
    "8.8.4.4",        # Google Secondary
    "9.9.9.9",        # Quad9 (Privacy-focused)
]

# Timeout settings (in seconds)
DNS_TIMEOUT = 10.0   # Timeout per DNS server
DNS_LIFETIME = 30.0  # Total time allowed for all retries


def _create_resolver() -> dns.resolver.Resolver:
    """
    Create a DNS resolver configured with public DNS servers.
    
    This avoids relying on the system resolver, which may be slow,
    misconfigured, or blocked by firewalls/VPNs.
    """
    resolver = dns.resolver.Resolver(configure=False)  # Don't use system config
    resolver.nameservers = PUBLIC_DNS_SERVERS
    resolver.timeout = DNS_TIMEOUT
    resolver.lifetime = DNS_LIFETIME
    return resolver


class DNSService:
    """DNS resolution service with caching and public DNS fallback."""
    
    def __init__(self):
        self.resolver = _create_resolver()
        logger.info(f"DNSService initialized with nameservers: {self.resolver.nameservers}")
    
    def resolve_domain(self, domain: str) -> Optional[str]:
        """
        Resolve domain to IP address (cached).
        
        Returns:
            Primary IP address or None if resolution fails.
        """
        return _cached_resolve_domain(domain)
    
    def get_all_ips(self, domain: str) -> List[str]:
        """Get all IP addresses for domain (cached)."""
        return list(_cached_get_all_ips(domain))
    
    def get_nameservers(self, domain: str) -> List[str]:
        """Get nameservers for domain."""
        nameservers = []
        try:
            resolver = _create_resolver()
            answers = resolver.resolve(domain, 'NS')
            nameservers = [str(answer).rstrip('.') for answer in answers]
            logger.debug(f"Found {len(nameservers)} nameservers for {domain}")
        except dns.resolver.NXDOMAIN:
            logger.warning(f"Domain {domain} does not exist (NXDOMAIN)")
        except dns.resolver.NoAnswer:
            logger.warning(f"No NS records found for {domain}")
        except dns.resolver.Timeout:
            logger.warning(f"DNS timeout getting nameservers for {domain}")
        except Exception as e:
            logger.debug(f"Could not get nameservers for {domain}: {type(e).__name__}: {str(e)}")
        
        return nameservers
    
    def reverse_dns(self, ip: str) -> Optional[str]:
        """Reverse DNS lookup (PTR record)."""
        try:
            hostname = socket.gethostbyaddr(ip)
            return hostname[0]
        except socket.herror as e:
            logger.debug(f"Reverse DNS failed for {ip}: Host not found")
            return None
        except socket.gaierror as e:
            logger.debug(f"Reverse DNS failed for {ip}: Address-related error")
            return None
        except Exception as e:
            logger.debug(f"Reverse DNS failed for {ip}: {type(e).__name__}: {str(e)}")
            return None
    
    def get_mx_records(self, domain: str) -> List[Tuple[int, str]]:
        """Get MX records for domain, sorted by priority."""
        mx_records = []
        try:
            resolver = _create_resolver()
            answers = resolver.resolve(domain, 'MX')
            mx_records = [(answer.preference, str(answer.exchange).rstrip('.')) for answer in answers]
            mx_records.sort(key=lambda x: x[0])  # Sort by priority
            logger.debug(f"Found {len(mx_records)} MX records for {domain}")
        except dns.resolver.NXDOMAIN:
            logger.warning(f"Domain {domain} does not exist (NXDOMAIN)")
        except dns.resolver.NoAnswer:
            logger.debug(f"No MX records found for {domain}")
        except dns.resolver.Timeout:
            logger.warning(f"DNS timeout getting MX records for {domain}")
        except Exception as e:
            logger.debug(f"Could not get MX records for {domain}: {type(e).__name__}: {str(e)}")
        
        return mx_records
    
    def get_txt_records(self, domain: str) -> List[str]:
        """Get TXT records for domain (useful for SPF, DKIM, etc.)."""
        txt_records = []
        try:
            resolver = _create_resolver()
            answers = resolver.resolve(domain, 'TXT')
            txt_records = [str(answer).strip('"') for answer in answers]
            logger.debug(f"Found {len(txt_records)} TXT records for {domain}")
        except dns.resolver.NXDOMAIN:
            logger.warning(f"Domain {domain} does not exist (NXDOMAIN)")
        except dns.resolver.NoAnswer:
            logger.debug(f"No TXT records found for {domain}")
        except dns.resolver.Timeout:
            logger.warning(f"DNS timeout getting TXT records for {domain}")
        except Exception as e:
            logger.debug(f"Could not get TXT records for {domain}: {type(e).__name__}: {str(e)}")
        
        return txt_records


# =============================================================================
# Cached Functions (module-level for lru_cache to work)
# =============================================================================

@lru_cache(maxsize=256)
def _cached_resolve_domain(domain: str) -> Optional[str]:
    """
    Cached DNS resolution using public DNS servers.
    
    LRU cache avoids repeated network requests for the same domain.
    Cache up to 256 domains.
    """
    try:
        resolver = _create_resolver()
        answers = resolver.resolve(domain, 'A')
        if answers:
            ip = str(answers[0])
            logger.info(f"DNS resolved: {domain} -> {ip}")
            return ip
    except dns.resolver.NXDOMAIN:
        logger.warning(f"Domain {domain} does not exist (NXDOMAIN)")
    except dns.resolver.NoAnswer:
        logger.warning(f"No A records found for {domain}")
    except dns.resolver.Timeout:
        logger.error(f"DNS timeout for {domain} (tried servers: {PUBLIC_DNS_SERVERS})")
    except dns.resolver.NoNameservers:
        logger.error(f"No nameservers available to resolve {domain}")
    except Exception as e:
        logger.error(f"DNS resolution failed for {domain}: {type(e).__name__}: {str(e)}")
    
    return None


@lru_cache(maxsize=256)
def _cached_get_all_ips(domain: str) -> tuple:
    """
    Get all IP addresses for domain (cached).
    
    Returns tuple for hashability with lru_cache.
    """
    ips = []
    try:
        resolver = _create_resolver()
        answers = resolver.resolve(domain, 'A')
        ips = [str(answer) for answer in answers]
        logger.debug(f"Found {len(ips)} IP addresses for {domain}")
    except dns.resolver.NXDOMAIN:
        logger.warning(f"Domain {domain} does not exist (NXDOMAIN)")
    except dns.resolver.NoAnswer:
        logger.debug(f"No A records found for {domain}")
    except dns.resolver.Timeout:
        logger.error(f"DNS timeout getting all IPs for {domain}")
    except Exception as e:
        logger.debug(f"Could not get all IPs for {domain}: {type(e).__name__}: {str(e)}")
    
    return tuple(ips)


def clear_dns_cache():
    """Clear DNS cache (useful for testing or forced refresh)."""
    _cached_resolve_domain.cache_clear()
    _cached_get_all_ips.cache_clear()
    logger.info("DNS cache cleared")


def test_dns_connectivity() -> bool:
    """
    Test if DNS resolution is working.
    
    Useful for diagnostics. Tries to resolve a known-good domain.
    Returns True if DNS is functional, False otherwise.
    """
    test_domains = ["google.com", "cloudflare.com", "microsoft.com"]
    
    for domain in test_domains:
        try:
            resolver = _create_resolver()
            resolver.resolve(domain, 'A')
            logger.info(f"DNS connectivity test passed: {domain} resolved successfully")
            return True
        except Exception as e:
            logger.warning(f"DNS test failed for {domain}: {type(e).__name__}")
            continue
    
    logger.error("DNS connectivity test FAILED - all test domains unreachable")
    return False