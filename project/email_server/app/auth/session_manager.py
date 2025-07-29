import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired
from .models import UserSession


class SessionManager:
    """Manages user sessions with secure signed cookies"""
    
    def __init__(self):
        self.secret_key = os.getenv("SESSION_SECRET", "dev-secret-key-change-in-production")
        self.signer = TimestampSigner(self.secret_key)
        self.session_duration = timedelta(hours=24)  # 24 hour sessions
        
    def create_session(self, user_email: str, access_token: str, refresh_token: Optional[str] = None, expires_in: int = 3600) -> str:
        """
        Create a new user session and return signed session cookie value
        
        Args:
            user_email: User's email address
            access_token: OAuth access token
            refresh_token: OAuth refresh token (optional)
            expires_in: Token expiration time in seconds
            
        Returns:
            Signed session cookie value
        """
        session_data = UserSession(
            user_email=user_email,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        
        # Convert to dict and then to JSON
        session_json = session_data.model_dump_json()
        
        # Sign the session data
        signed_session = self.signer.sign(session_json)
        return signed_session.decode('utf-8')
    
    def verify_session(self, signed_session: str) -> Optional[UserSession]:
        """
        Verify and decode a signed session cookie
        
        Args:
            signed_session: Signed session cookie value
            
        Returns:
            UserSession object if valid, None if invalid or expired
        """
        try:
            # Verify signature and check if not older than session_duration
            unsigned_session = self.signer.unsign(
                signed_session, 
                max_age=self.session_duration.total_seconds()
            )
            
            # Parse JSON and create UserSession object
            session_data = json.loads(unsigned_session)
            user_session = UserSession(**session_data)
            
            # Check if token is still valid
            if user_session.token_expires_at > datetime.utcnow():
                return user_session
            else:
                return None
                
        except (BadSignature, SignatureExpired, json.JSONDecodeError, ValueError):
            return None
    
    def destroy_session(self) -> bool:
        """
        Destroy a session (client-side cookie deletion)
        
        Returns:
            True to indicate successful session destruction
        """
        return True
    
    def refresh_session(self, user_session: UserSession, new_access_token: str, expires_in: int = 3600) -> str:
        """
        Refresh an existing session with new tokens
        
        Args:
            user_session: Current user session
            new_access_token: New access token
            expires_in: New token expiration time in seconds
            
        Returns:
            New signed session cookie value
        """
        return self.create_session(
            user_email=user_session.user_email,
            access_token=new_access_token,
            refresh_token=user_session.refresh_token,
            expires_in=expires_in
        ) 