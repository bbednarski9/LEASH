import os
import secrets
from typing import Optional, Tuple
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json


class GoogleOAuthHandler:
    """Handles Google OAuth authentication flow"""
    
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/auth/callback")
        self.scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/calendar'
        ]
        print(f"GoogleOAuthHandler initialized with:")
        print(f"  client_id: {self.client_id}")
        print(f"  client_secret: {'<hidden>' if self.client_secret else None}")
        print(f"  redirect_uri: {self.redirect_uri}")
        print(f"  scopes: {self.scopes}")
        
        # Create client config for OAuth flow
        self.client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
    def get_authorization_url(self) -> Tuple[str, str]:
        """
        Generate authorization URL and state for OAuth flow
        
        Returns:
            Tuple of (authorization_url, state)
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
        
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        # Generate secure random state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent screen to get refresh token
        )
        
        return authorization_url, state
    
    def exchange_code_for_tokens(self, code: str, state: Optional[str] = None) -> dict:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from Google
            state: State parameter for CSRF protection
            
        Returns:
            Dictionary containing tokens and user info
        """
        print(f"DEBUG: Starting token exchange with code: {code[:20]}...")
        print(f"DEBUG: State: {state}")
        print(f"DEBUG: Redirect URI: {self.redirect_uri}")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")
        
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri,
                state=state
            )
            print("DEBUG: Flow created successfully")
            
            # Exchange code for tokens
            flow.fetch_token(code=code)
            print("DEBUG: Token fetched successfully")
            
            credentials = flow.credentials
            print(f"DEBUG: Got credentials, token: {credentials.token[:20] if credentials.token else 'None'}...")
            
            # Try to get user info using the people API, fallback to token info
            user_email = None
            try:
                # Method 1: Use People API (requires People API to be enabled)
                people_service = build('people', 'v1', credentials=credentials)
                print("DEBUG: People service built successfully")
                
                profile = people_service.people().get(
                    resourceName='people/me',
                    personFields='names,emailAddresses'
                ).execute()
                print(f"DEBUG: Profile fetched successfully: {profile}")
                
                # Extract user email
                if 'emailAddresses' in profile:
                    user_email = profile['emailAddresses'][0]['value']
                    print(f"DEBUG: Extracted email from People API: {user_email}")
                    
            except Exception as people_error:
                print(f"DEBUG: People API failed: {people_error}")
                print("DEBUG: Falling back to OAuth2 userinfo endpoint")
                
                # Method 2: Use OAuth2 userinfo endpoint (simpler, doesn't need People API)
                try:
                    oauth2_service = build('oauth2', 'v2', credentials=credentials)
                    userinfo = oauth2_service.userinfo().get().execute()
                    print(f"DEBUG: Got userinfo: {userinfo}")
                    
                    user_email = userinfo.get('email')
                    print(f"DEBUG: Extracted email from userinfo: {user_email}")
                    
                except Exception as oauth2_error:
                    print(f"DEBUG: OAuth2 userinfo also failed: {oauth2_error}")
                    raise Exception("Could not retrieve user email from Google")
            
            if not user_email:
                print("DEBUG: No email found in any method")
                raise Exception("Could not retrieve user email from Google")
                
        except Exception as e:
            print(f"DEBUG: Exception in token exchange: {type(e).__name__}: {str(e)}")
            raise
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'expires_in': 3600,  # Default to 1 hour
            'scope': ' '.join(self.scopes),
            'user_email': user_email,
            'credentials': credentials
        }
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dictionary containing new access token and expiration
        """
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_uri="https://oauth2.googleapis.com/token"
        )
        
        # Refresh the token
        credentials.refresh(Request())
        
        return {
            'access_token': credentials.token,
            'expires_in': 3600,
            'refresh_token': refresh_token  # Keep the same refresh token
        }
    
    def get_calendar_service(self, access_token: str):
        """
        Create Google Calendar service object
        
        Args:
            access_token: Valid access token
            
        Returns:
            Google Calendar service object
        """
        credentials = Credentials(
            token=access_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_uri="https://oauth2.googleapis.com/token"
        )
        
        return build('calendar', 'v3', credentials=credentials)
    
    def verify_credentials(self, access_token: str) -> bool:
        """
        Verify if access token is still valid
        
        Args:
            access_token: Access token to verify
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            credentials = Credentials(
                token=access_token,
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_uri="https://oauth2.googleapis.com/token"
            )
            
            # Try to use the token to make a simple API call
            people_service = build('people', 'v1', credentials=credentials)
            people_service.people().get(
                resourceName='people/me',
                personFields='names'
            ).execute()
            
            return True
        except Exception:
            return False 