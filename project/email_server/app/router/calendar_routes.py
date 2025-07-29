from fastapi import APIRouter, HTTPException, Depends, status, Query
from googleapiclient.errors import HttpError
from typing import List
from ..auth import (
    get_current_user,
    get_oauth_handler,
    UserSession,
    GoogleOAuthHandler,
    CalendarEventRequest,
    CalendarEventResponse
)
from ..services.calendar_service import CalendarService

router = APIRouter(tags=["calendar"])


def get_calendar_service(
    oauth_handler: GoogleOAuthHandler = Depends(get_oauth_handler)
) -> CalendarService:
    """Dependency to get calendar service instance"""
    return CalendarService(oauth_handler)


@router.get("/events", response_model=CalendarEventResponse)
async def get_calendar_events(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    user_session: UserSession = Depends(get_current_user),
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    """
    Retrieve calendar events for a specified date
    
    Requires authentication via session cookie
    
    Args:
        date: Date in YYYY-MM-DD format
        user_session: Current authenticated user session
        calendar_service: Calendar service instance
        
    Returns:
        CalendarEventResponse with list of events
    """
    try:
        # Validate date format
        from datetime import datetime
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD."
            )
        
        # Get events from Google Calendar
        events = calendar_service.get_events(
            access_token=user_session.access_token,
            date=date
        )
        
        return CalendarEventResponse(
            success=True,
            events=events
        )
        
    except HttpError as error:
        if error.resp.status == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google Calendar access denied. Please re-authenticate."
            )
        elif error.resp.status == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access Google Calendar."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Google Calendar API error: {error}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve calendar events"
        )


@router.post("/events", response_model=CalendarEventResponse)
async def create_calendar_events(
    event_request: CalendarEventRequest,
    user_session: UserSession = Depends(get_current_user),
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    """
    Add new events to the calendar
    
    Requires authentication via session cookie
    
    Args:
        event_request: Request containing list of events to create
        user_session: Current authenticated user session
        calendar_service: Calendar service instance
        
    Returns:
        CalendarEventResponse with creation results
    """
    try:
        if not event_request.events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No events provided"
            )
        
        # Validate events
        for event in event_request.events:
            if event.end_time <= event.start_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Event '{event.title}': end time must be after start time"
                )
        
        # Create events in Google Calendar
        results = calendar_service.create_events(
            access_token=user_session.access_token,
            events=event_request.events
        )
        
        # Convert results to dict format for response
        results_dict = [result.model_dump() for result in results]
        
        return CalendarEventResponse(
            success=True,
            results=results_dict
        )
        
    except HTTPException:
        raise
    except HttpError as error:
        if error.resp.status == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google Calendar access denied. Please re-authenticate."
            )
        elif error.resp.status == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access Google Calendar."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Google Calendar API error: {error}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create calendar events"
        ) 


@router.get("/events/bulk", response_model=CalendarEventResponse)
async def get_calendar_events_bulk(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    user_session: UserSession = Depends(get_current_user),
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    """
    Retrieve calendar events for a date range
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        user_session: Current authenticated user session
        calendar_service: Calendar service instance
        
    Returns:
        CalendarEventResponse with list of events
    """
    try:
        # Validate date format
        from datetime import datetime
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD."
            )
        
        # Get events from Google Calendar
        events = calendar_service.get_events_bulk(
            access_token=user_session.access_token,
            start_date=start_date,
            end_date=end_date
        )
        
        return CalendarEventResponse(
            success=True,
            events=events
        )
        
    except HttpError as error:
        if error.resp.status == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google Calendar access denied. Please re-authenticate."
            )
        elif error.resp.status == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access Google Calendar."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Google Calendar API error: {error}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve calendar events: {str(e)}"
        ) 