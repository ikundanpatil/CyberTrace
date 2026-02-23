import requests
import socket
import logging
from sqlalchemy.orm import Session
from datetime import datetime
from urllib.parse import urlparse
from app.db.models import ThreatIntel
from app.db.base import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- DEMO DATA (Failsafe) ---
MOCK_THREATS = [
    {"ip": "103.27.184.22", "url": "http://suspicious-bank-login.com", "lat": 35.6895, "lon": 139.6917, "city": "Tokyo", "country": "Japan", "type": "Phishing"},
    {"ip": "45.155.205.233", "url": "http://free-crypto-giveaway.net", "lat": 55.7558, "lon": 37.6173, "city": "Moscow", "country": "Russia", "type": "Malware"},
    {"ip": "185.220.101.44", "url": "http://secure-update-apple.com", "lat": 52.5200, "lon": 13.4050, "city": "Berlin", "country": "Germany", "type": "C2"},
    {"ip": "192.241.220.1", "url": "http://paypal-verification-v2.com", "lat": 40.7128, "lon": -74.0060, "city": "New York", "country": "USA", "type": "Phishing"},
    {"ip": "116.203.245.2", "url": "http://royal-mail-delivery-fee.com", "lat": 51.5074, "lon": -0.1278, "city": "London", "country": "UK", "type": "Scam"},
]

def get_geolocation(ip):
    """
    Get Lat/Lon for an IP using free ip-api.com
    """
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "fail":
                return None
            return {
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "country": data.get("country"),
                "city": data.get("city")
            }
    except Exception as e:
        logger.warning(f"Geo-lookup failed for {ip}: {e}")
    return None

def fetch_openphish_data(limit=10):
    """
    Fetch active phishing URLs from OpenPhish (Text feed = reliable)
    """
    url = "https://openphish.com/feed.txt"
    try:
        logger.info("Fetching OpenPhish data...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # feed.txt is just one URL per line
            entries = response.text.strip().split('\n')[:limit]
            logger.info(f"Fetched {len(entries)} entries from OpenPhish")
            return [{"url": u.strip(), "source": "OpenPhish"} for u in entries]
    except Exception as e:
        logger.error(f"Failed to fetch OpenPhish: {e}")
    return []

def populate_threat_db(db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # 1. Try to get Real Data
        threats = fetch_openphish_data(limit=10)
        
        # 2. If Real Data fails (or is empty), use Mock Data
        if not threats:
            logger.warning("Using MOCK DATA because live feed failed (Perfect for Demos!)")
            threats = [{"url": m["url"], "ip": m["ip"], "source": "MockData"} for m in MOCK_THREATS]

        stats = {"added": 0, "skipped": 0, "errors": 0}

        for entry in threats:
            try:
                # Check duplicate
                existing = db.query(ThreatIntel).filter(ThreatIntel.indicator == entry['url']).first()
                if existing:
                    stats['skipped'] += 1
                    continue

                # Get IP if missing
                ip = entry.get('ip')
                if not ip:
                    try:
                        domain = urlparse(entry['url']).netloc
                        # Handle potential empty domain (e.g. if url is just http://)
                        if domain: 
                             ip = socket.gethostbyname(domain)
                    except:
                        pass # Could not resolve, skip geo
                
                # Get Location
                lat, lon, country, city = None, None, None, None
                
                # Use Mock location if available (for demo), else query API
                if entry.get("source") == "MockData":
                    # Match mock data
                    mock_match = next((m for m in MOCK_THREATS if m["url"] == entry["url"]), None)
                    if mock_match:
                        lat, lon = mock_match["lat"], mock_match["lon"]
                        country, city = mock_match["country"], mock_match["city"]
                elif ip:
                    geo = get_geolocation(ip)
                    if geo:
                        lat, lon = geo['lat'], geo['lon']
                        country, city = geo['country'], geo['city']

                # Create Record
                threat_node = ThreatIntel(
                    indicator=entry['url'],
                    threat_type="Phishing",
                    latitude=lat,
                    longitude=lon,
                    country=country,
                    city=city,
                    source=entry.get('source', 'Unknown')
                )
                db.add(threat_node)
                stats['added'] += 1
                
            except Exception as e:
                logger.error(f"Error processing entry {entry.get('url')}: {e}")
                stats['errors'] += 1

        db.commit()
        logger.info(f"Threat DB Populated: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Critical Ingestor Failure: {e}")
        db.rollback()
    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    populate_threat_db()