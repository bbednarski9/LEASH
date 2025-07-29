import os
from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
from ..auth import (
    get_current_user,
    get_current_user_optional,
    get_session_manager,
    get_oauth_handler,
    AuthStatus,
    LogoutResponse,
    UserSession,
    SessionManager,
    GoogleOAuthHandler
)

router = APIRouter(tags=["authentication"])


@router.get("/login")
async def login(
    request: Request,
    oauth_handler: GoogleOAuthHandler = Depends(get_oauth_handler)
):
    """
    Initiate Google OAuth login flow
    
    Redirects user to Google OAuth consent screen
    """
    try:
        authorization_url, state = oauth_handler.get_authorization_url()
        
        # Store state in session for CSRF protection
        response = RedirectResponse(url=authorization_url)
        response.set_cookie(
            key="oauth_state",
            value=state,
            max_age=600,  # 10 minutes
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate OAuth flow"
        )


@router.get("/callback")
async def oauth_callback(
    request: Request,
    code: str,
    state: Optional[str] = None,
    oauth_handler: GoogleOAuthHandler = Depends(get_oauth_handler),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Handle Google OAuth callback
    
    Exchanges authorization code for tokens and creates user session
    """
    try:
        # Verify state parameter for CSRF protection
        stored_state = request.cookies.get("oauth_state")
        if not stored_state or stored_state != state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter. Possible CSRF attack."
            )
        
        # Exchange code for tokens
        token_data = oauth_handler.exchange_code_for_tokens(code, state)
        
        if not token_data.get('user_email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user email from Google"
            )
        
        # Create session
        session_cookie = session_manager.create_session(
            user_email=token_data['user_email'],
            access_token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            expires_in=token_data.get('expires_in', 3600)
        )
        
        # Redirect to frontend with session cookie
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5000")
        response = RedirectResponse(url=frontend_url)
        
        response.set_cookie(
            key="session",
            value=session_cookie,
            max_age=86400,  # 24 hours
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        # Clear the OAuth state cookie
        response.delete_cookie("oauth_state")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth callback failed"
        )


@router.get("/status", response_model=AuthStatus)
async def auth_status(
    user_session: Optional[UserSession] = Depends(get_current_user_optional)
):
    """
    Check authentication status
    
    Returns authentication status and user information if authenticated
    """
    if user_session:
        return AuthStatus(
            authenticated=True,
            user_email=user_session.user_email,
            expires_at=user_session.token_expires_at
        )
    else:
        return AuthStatus(authenticated=False)


@router.post("/logout", response_model=LogoutResponse)
async def logout(request: Request):
    """
    Logout user and destroy session
    
    Clears session cookie
    """
    response = JSONResponse(
        content=LogoutResponse(
            success=True,
            message="Logged out successfully"
        ).model_dump()
    )
    
    # Clear session cookie
    response.delete_cookie("session")
    
    return response 