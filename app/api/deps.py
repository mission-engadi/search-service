"""API Dependencies

Provides common dependencies for API endpoints.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import get_db from session
from app.db.session import get_db

# Re-export get_db for convenience
__all__ = ["get_db", "get_current_user", "get_current_user_optional"]

# Security scheme for JWT
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user.
    
    This is a placeholder implementation. In production, you should:
    1. Verify the JWT token
    2. Check token expiration
    3. Validate user permissions
    4. Return user information from the token
    
    For now, we extract the user info from the token without verification
    (assuming Auth Service has already validated it at the gateway level).
    """
    try:
        # In a real implementation, decode and verify JWT
        # For now, assume the token is valid and return a mock user
        # The token format is typically: Bearer <token>
        token = credentials.credentials
        
        # Mock user data - in production, decode JWT and get real user data
        return {
            "sub": "00000000-0000-0000-0000-000000000000",  # User ID
            "email": "user@example.com",
            "roles": ["user"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[dict]:
    """Get current user if authenticated, None otherwise.
    
    This dependency doesn't raise an error if the user is not authenticated.
    Useful for endpoints that work differently based on authentication status.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
