"""
Authentication API Endpoints

Provides /login and /signup endpoints for user authentication.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import User
from app.core.security import verify_password, get_password_hash, create_access_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# =====================================================
# Request/Response Models
# =====================================================

class LoginRequest(BaseModel):
    """Login request payload"""
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    """Signup request payload"""
    email: EmailStr
    password: str
    fullName: str
    organization: str


class AuthResponse(BaseModel):
    """Authentication success response"""
    token: str
    message: str
    user_name: str
    organization: str


# =====================================================
# Endpoints
# =====================================================

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    
    Returns:
        AuthResponse with JWT token on success
        
    Raises:
        401: Invalid email or password
    """
    logger.info(f"Login attempt for: {request.email}")
    
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        logger.warning(f"Login failed - user not found: {request.email}")
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        logger.warning(f"Login failed - invalid password: {request.email}")
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login failed - inactive account: {request.email}")
        raise HTTPException(
            status_code=401,
            detail="Account is deactivated"
        )
    
    # Create JWT token
    token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "full_name": user.full_name
        }
    )
    
    logger.info(f"Login successful: {request.email}")
    return AuthResponse(
        token=token,
        message="Login successful",
        user_name=user.full_name or "Agent",
        organization=user.organization or "Cyber Cell"
    )


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    
    Returns:
        AuthResponse with JWT token on success
        
    Raises:
        400: Email already registered
    """
    logger.info(f"Signup attempt for: {request.email}")
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    
    if existing_user:
        logger.warning(f"Signup failed - email exists: {request.email}")
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.fullName,
        organization=request.organization,
        is_active=True
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User created successfully: {request.email} (ID: {new_user.id})")
        
        # Create JWT token for immediate login
        token = create_access_token(
            data={
                "sub": new_user.email,
                "user_id": new_user.id,
                "full_name": new_user.full_name
            }
        )
        
        return AuthResponse(
            token=token,
            message="Account created successfully",
            user_name=new_user.full_name or "Agent",
            organization=new_user.organization or "Cyber Cell"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Signup failed - database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create account"
        )


@router.get("/me")
async def get_current_user_info():
    """
    Placeholder endpoint - returns info about current user.
    Full implementation requires token verification middleware.
    """
    return {
        "message": "Token verification not yet implemented",
        "note": "Frontend should decode JWT client-side for user info"
    }
