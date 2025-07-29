from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for sending queries to the LLM"""
    query: str = Field(..., description="The text query to send to the model", min_length=1)
    model: Optional[str] = Field(default="llama3.2", description="The Ollama model to use for inference")
    temperature: Optional[float] = Field(default=0.7, description="Temperature for response generation", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=1000, description="Maximum number of tokens to generate", gt=0)
    system_prompt: Optional[str] = Field(default=None, description="Optional system prompt to set context")


class QueryResponse(BaseModel):
    """Response model for LLM query results"""
    success: bool = Field(..., description="Whether the query was successful")
    response: Optional[str] = Field(default=None, description="The generated text response from the model")
    model_used: Optional[str] = Field(default=None, description="The model that was used for inference")
    execution_time_ms: Optional[float] = Field(default=None, description="Time taken to generate response in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if the query failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the response")


class ModelInfo(BaseModel):
    """Model information for available models"""
    name: str = Field(..., description="Model name")
    size: Optional[str] = Field(default=None, description="Model size")
    modified_at: Optional[str] = Field(default=None, description="Last modified date")
    digest: Optional[str] = Field(default=None, description="Model digest/hash")
    
    @classmethod
    def model_validate(cls, data):
        # Handle size field being int or string
        if isinstance(data, dict) and 'size' in data:
            if isinstance(data['size'], int):
                data['size'] = str(data['size'])
        return super().model_validate(data)


class ModelsListResponse(BaseModel):
    """Response model for listing available models"""
    success: bool = Field(..., description="Whether the request was successful")
    models: List[ModelInfo] = Field(default=[], description="List of available models")
    error: Optional[str] = Field(default=None, description="Error message if the request failed")


# Calendar-related models for the leash daily calendar fill endpoint

class CalendarEvent(BaseModel):
    """Model for a calendar event"""
    date: str = Field(..., description="Event date in YYYY-MM-DD format")
    event_start_time_local: str = Field(..., description="Event start time in local timezone ISO format")
    event_end_time_local: str = Field(..., description="Event end time in local timezone ISO format")
    event_title: str = Field(..., description="Event title")
    event_description: Optional[str] = Field(default="", description="Event description")


class PetDetails(BaseModel):
    """Model for pet information"""
    name: str = Field(..., description="Pet name")
    age: str = Field(..., description="Pet age")
    breed: str = Field(..., description="Pet breed")
    weight: str = Field(..., description="Pet weight")
    walk_time_per_day: str = Field(..., description="Required walk time per day")
    current_medications: Optional[List[Dict[str, Any]]] = Field(default=[], description="Current medications")
    special_needs: Optional[str] = Field(default="", description="Any special needs or health considerations")
    activity_level: Optional[str] = Field(default="moderate", description="Pet's activity level (low, moderate, high)")


class OwnerDetails(BaseModel):
    """Model for owner/user preferences"""
    owner_name: str = Field(..., description="Owner's name")
    yard_access: bool = Field(default=False, description="Whether owner has yard access")
    preferred_walk_times: List[str] = Field(default=[], description="Preferred times for walks")
    work_schedule: Optional[str] = Field(default="", description="Owner's work schedule")
    availability_notes: Optional[str] = Field(default="", description="Notes about availability")
    preferred_activity_duration: Optional[str] = Field(default="30-60 minutes", description="Preferred activity duration")


class CalendarFillRequest(BaseModel):
    """Request model for leash daily calendar fill endpoint"""
    current_calendar: List[CalendarEvent] = Field(..., description="Current calendar events")
    pet_details: List[PetDetails] = Field(..., description="List of pets and their details")
    owner_details: OwnerDetails = Field(..., description="Owner preferences and details")
    target_date: Optional[str] = Field(default=None, description="Target date for suggestions (YYYY-MM-DD)")
    user_timezone: Optional[str] = Field(default=None, description="User's timezone (e.g. 'America/Los_Angeles')")
    model: Optional[str] = Field(default="llama3.2", description="LLM model to use")
    temperature: Optional[float] = Field(default=0.7, description="Temperature for generation")


class CalendarSuggestion(BaseModel):
    """Model for a calendar suggestion"""
    date: str = Field(..., description="Suggested event date in YYYY-MM-DD format")
    event_start_time_local: str = Field(..., description="Suggested start time in user's local timezone ISO format")
    event_end_time_local: str = Field(..., description="Suggested end time in user's local timezone ISO format")
    event_title: str = Field(..., description="Suggested event title")
    event_description: str = Field(..., description="Detailed description of the suggested activity")
    priority: Optional[str] = Field(default="medium", description="Priority level (low, medium, high)")
    activity_type: Optional[str] = Field(default="general", description="Type of activity (walk, feeding, medication, play, etc.)")
    pet_names: Optional[List[str]] = Field(default=[], description="Names of pets this activity is for")


class CalendarFillResponse(BaseModel):
    """Response model for leash daily calendar fill endpoint"""
    success: bool = Field(..., description="Whether the request was successful")
    suggestions: List[CalendarSuggestion] = Field(default=[], description="Generated calendar suggestions")
    execution_time_ms: Optional[float] = Field(default=None, description="Time taken to generate suggestions")
    model_used: Optional[str] = Field(default=None, description="Model used for generation")
    error: Optional[str] = Field(default=None, description="Error message if the request failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata") 