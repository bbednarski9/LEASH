from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from .models import UserSession
from .session_manager import SessionManager
from .oauth import GoogleOAuthHandler

# Global instances
session_manager = SessionManager()
oauth_handler = GoogleOAuthHandler()
security = HTTPBearer(auto_error=False)


async def get_session_from_cookie(request: Request) -> Optional[UserSession]:
    """
    Extract and verify user session from cookie
    
    Args:
        request: FastAPI request object
        
    Returns:
        UserSession if valid session exists, None otherwise
    """
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return None
    
    return session_manager.verify_session(session_cookie)


async def get_current_user(request: Request) -> UserSession:
    """
    Dependency to get current authenticated user (required)
    
    Args:
        request: FastAPI request object
        
    Returns:
        UserSession object
        
    Raises:
        HTTPException: If user is not authenticated
    """
    user_session = await get_session_from_cookie(request)
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please login.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify token is still valid with Google
    if not oauth_handler.verify_credentials(user_session.access_token):
        # Try to refresh token if we have a refresh token
        if user_session.refresh_token:
            try:
                new_tokens = oauth_handler.refresh_access_token(user_session.refresh_token)
                # Note: In a real implementation, you'd want to update the session cookie here
                # For now, we'll just return the original session
                pass
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired and refresh failed. Please login again.",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired. Please login again.",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    return user_session


async def get_current_user_optional(request: Request) -> Optional[UserSession]:
    """
    Dependency to get current authenticated user (optional)
    
    Args:
        request: FastAPI request object
        
    Returns:
        UserSession object if authenticated, None if not authenticated
    """
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


def get_session_manager() -> SessionManager:
    """Dependency to get session manager instance"""
    return session_manager


def get_oauth_handler() -> GoogleOAuthHandler:
    """Dependency to get OAuth handler instance"""
    return oauth_handler 