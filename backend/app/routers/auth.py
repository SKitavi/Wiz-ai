from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional, Dict, Any

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
    PasswordChange
)
from app.utils.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
    validate_password_strength
)
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    - **preferences**: Optional user preferences
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        preferences=user_data.preferences or {},
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"✅ New user registered: {new_user.email}")
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(new_user)
    }


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    
    Returns JWT access token on successful authentication
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.post("/login/json", response_model=Token)
async def login_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Alternative login endpoint accepting JSON
    
    Use this if you're not using OAuth2PasswordRequestForm
    """
    user = authenticate_user(db, user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    
    Requires authentication token in header:
    Authorization: Bearer <token>
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    full_name: Optional[str] = None,
    preferences: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information
    """
    if full_name is not None:
        current_user.full_name = full_name
    
    if preferences is not None:
        current_user.preferences = preferences
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"✅ User {current_user.email} updated their profile")
    
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    from app.utils.auth import verify_password, get_password_hash
    
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Validate new password strength
    is_valid, error_msg = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    logger.info(f"✅ User {current_user.email} changed their password")
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout endpoint (for completeness)
    
    Note: With JWT, actual logout happens client-side by deleting the token
    In a production app, you'd implement token blacklisting here
    """
    logger.info(f"User {current_user.email} logged out")
    return {"message": "Logged out successfully"}