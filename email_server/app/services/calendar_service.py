from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from googleapiclient.errors import HttpError
from ..auth.oauth import GoogleOAuthHandler
from ..auth.models import CalendarEvent, CalendarEventResult


class CalendarService:
    """Service for Google Calendar operations"""
    
    def __init__(self, oauth_handler: GoogleOAuthHandler):
        self.oauth_handler = oauth_handler
    
    def get_events(self, access_token: str, date: str) -> List[Dict[str, Any]]:
        """
        Get calendar events for a specific date
        
        Args:
            access_token: User's access token
            date: Date in YYYY-MM-DD format
            
        Returns:
            List of calendar events
            
        Raises:
            HttpError: If Google API request fails
        """
        try:
            service = self.oauth_handler.get_calendar_service(access_token)
            
            # Convert date to RFC3339 format for Google Calendar API
            start_time = f"{date}T00:00:00Z"
            end_time = f"{date}T23:59:59Z"
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Transform events to match our API format
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_event = {
                    'id': event['id'],
                    'title': event.get('summary', 'No Title'),
                    'start_time': start,
                    'end_time': end,
                    'description': event.get('description', ''),
                    'color_id': event.get('colorId', '1'),  # Default to colorId 1 (blue)
                    'background_color': event.get('backgroundColor'),
                    'foreground_color': event.get('foregroundColor')
                }
                formatted_events.append(formatted_event)
            
            return formatted_events
            
        except HttpError as error:
            raise error
    
    def get_events_bulk(self, access_token: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get calendar events for a date range
        
        Args:
            access_token: User's access token
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of calendar events
            
        Raises:
            HttpError: If Google API request fails
        """
        try:
            service = self.oauth_handler.get_calendar_service(access_token)
            
            # Convert dates to RFC3339 format for Google Calendar API
            start_time = f"{start_date}T00:00:00Z"
            end_time = f"{end_date}T23:59:59Z"
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Transform events to match our API format
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_event = {
                    'id': event['id'],
                    'title': event.get('summary', 'No Title'),
                    'start_time': start,
                    'end_time': end,
                    'description': event.get('description', ''),
                    'color_id': event.get('colorId', '1'),  # Default to colorId 1 (blue)
                    'background_color': event.get('backgroundColor'),
                    'foreground_color': event.get('foregroundColor')
                }
                formatted_events.append(formatted_event)
            
            return formatted_events
            
        except HttpError as error:
            raise error
    
    def create_events(self, access_token: str, events: List[CalendarEvent]) -> List[CalendarEventResult]:
        """
        Create multiple calendar events
        
        Args:
            access_token: User's access token
            events: List of CalendarEvent objects to create
            
        Returns:
            List of CalendarEventResult objects with creation status
            
        Raises:
            HttpError: If Google API request fails
        """
        try:
            service = self.oauth_handler.get_calendar_service(access_token)
            results = []
            
            for event in events:
                try:
                    # Validate event times
                    if event.end_time <= event.start_time:
                        results.append(CalendarEventResult(
                            event_id="",
                            status="failed",
                            title=event.title
                        ))
                        continue
                    
                    # Create Google Calendar event object
                    calendar_event = {
                        'summary': event.title,
                        'description': event.description or '',
                        'start': {
                            'dateTime': event.start_time.isoformat(),
                            'timeZone': 'UTC',
                        },
                        'end': {
                            'dateTime': event.end_time.isoformat(),
                            'timeZone': 'UTC',
                        }
                    }
                    
                    # Create the event
                    created_event = service.events().insert(
                        calendarId='primary',
                        body=calendar_event
                    ).execute()
                    
                    results.append(CalendarEventResult(
                        event_id=created_event['id'],
                        status="created",
                        title=event.title
                    ))
                    
                except HttpError as error:
                    results.append(CalendarEventResult(
                        event_id="",
                        status="failed",
                        title=event.title
                    ))
                except Exception as error:
                    results.append(CalendarEventResult(
                        event_id="",
                        status="failed", 
                        title=event.title
                    ))
            
            return results
            
        except HttpError as error:
            raise error
    
    def update_event(self, access_token: str, event_id: str, event_data: Dict[str, Any]) -> bool:
        """
        Update an existing calendar event
        
        Args:
            access_token: User's access token
            event_id: Google Calendar event ID
            event_data: Event data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            service = self.oauth_handler.get_calendar_service(access_token)
            
            # Get the existing event
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Update with new data
            if 'title' in event_data:
                event['summary'] = event_data['title']
            if 'description' in event_data:
                event['description'] = event_data['description']
            if 'start_time' in event_data:
                event['start']['dateTime'] = event_data['start_time']
            if 'end_time' in event_data:
                event['end']['dateTime'] = event_data['end_time']
            
            # Update the event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return True
            
        except HttpError:
            return False
    
    def delete_event(self, access_token: str, event_id: str) -> bool:
        """
        Delete a calendar event
        
        Args:
            access_token: User's access token
            event_id: Google Calendar event ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            service = self.oauth_handler.get_calendar_service(access_token)
            
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
            
        except HttpError:
            return False 