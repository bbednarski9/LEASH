from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserSession(BaseModel):
    """User session model for storing authentication state"""
    user_email: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    
class AuthStatus(BaseModel):
    """Authentication status response model"""
    authenticated: bool
    user_email: Optional[str] = None
    expires_at: Optional[datetime] = None


class LogoutResponse(BaseModel):
    """Logout response model"""
    success: bool
    message: str


class CalendarEvent(BaseModel):
    """Single calendar event model"""
    id: Optional[str] = None
    title: str = Field(..., alias="event-title")
    start_time: datetime = Field(..., alias="event-start-time-UTC")
    end_time: datetime = Field(..., alias="event-end-time-UTC")
    description: Optional[str] = Field(None, alias="event-description")
    date: str  # YYYY-MM-DD format
    
    class Config:
        populate_by_name = True


class CalendarEventRequest(BaseModel):
    """Request model for creating calendar events"""
    events: List[CalendarEvent]


class CalendarEventResponse(BaseModel):
    """Response model for calendar event operations"""
    success: bool
    events: Optional[List[dict]] = None
    results: Optional[List[dict]] = None


class CalendarEventResult(BaseModel):
    """Individual calendar event operation result"""
    event_id: str
    status: str
    title: str


class OAuthTokens(BaseModel):
    """OAuth token storage model"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int
    scope: str
    token_type: str = "Bearer" 