"""
DomainIntel FastAPI Application

Main application entry point with:
- CORS configuration
- Rate limiting (slowapi)
- Database initialization
- Router registration
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.v1.endpoints import domain, report, auth, intel
from app.db.base import init_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# =====================================================
# Rate Limiter Setup
# =====================================================
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Domain Intelligence & Risk Assessment for Cybercrime Investigation",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add rate limiter to app state
app.state.limiter = limiter

# Add rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    domain.router,
    prefix="/api/v1/domain",
    tags=["domain"]
)
app.include_router(
    report.router, 
    prefix="/api/v1/report", 
    tags=["report"]
)
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["auth"]
)
app.include_router(
    intel.router,
    prefix="/api/v1/intel",
    tags=["intel"]
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database tables
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"{settings.APP_NAME} shutting down...")


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "DomainIntel API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "features": {
            "rate_limiting": "5 requests/minute per IP",
            "caching": "LRU cache (128 entries)",
            "database": "SQLite persistence"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway/container orchestration"""
    return {"status": "healthy", "version": settings.APP_VERSION}