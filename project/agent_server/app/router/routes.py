import asyncio
import time
import sys
import os
from typing import Optional

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from fastapi import APIRouter, Depends, HTTPException
from models.query_models import QueryRequest, QueryResponse, ModelsListResponse, CalendarFillRequest, CalendarFillResponse
from app.services.ollama_service import OllamaService

router = APIRouter()

# Initialize Ollama service
ollama_service = OllamaService()

@router.get("/test-connection")
async def test_connection(
                        verbose: Optional[bool] = False
                        ):
    """
    Route to /test-connection GET endpoint

    Args:
        # verbose (Optional[bool]): If True, prints the query execution time. Defaults to False.

    Returns:
        dict:

    Raises:
        HTTPException:
    """

    try:
        return {
            "success" : True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_llm(
    request: QueryRequest,
    verbose: Optional[bool] = False
):
    """
    Send a query to the Ollama LLM and get a text response
    
    Args:
        request: QueryRequest containing the query text and optional parameters
        verbose: If True, logs additional debug information

    Returns:
        QueryResponse: The generated response from the LLM with metadata

    Raises:
        HTTPException: If there is an error with the query or Ollama service
    """
    try:
        if verbose:
            print(f"Processing query with model: {request.model}")
        
        # Check if Ollama is running
        if not await ollama_service.check_connection():
            raise HTTPException(
                status_code=503, 
                detail="Ollama service is not running. Please start Ollama and try again."
            )
        
        # Generate response using Ollama
        response = await ollama_service.generate_response(
            query=request.query,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt
        )
        
        if verbose and response.execution_time_ms:
            print(f"Query processing took {response.execution_time_ms} ms")
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/models", response_model=ModelsListResponse)
async def list_available_models(verbose: Optional[bool] = False):
    """
    List all available Ollama models
    
    Args:
        verbose: If True, logs additional debug information

    Returns:
        ModelsListResponse: List of available models

    Raises:
        HTTPException: If there is an error connecting to Ollama
    """
    try:
        if verbose:
            print("Fetching available models from Ollama...")
        
        # Check if Ollama is running
        if not await ollama_service.check_connection():
            raise HTTPException(
                status_code=503, 
                detail="Ollama service is not running. Please start Ollama and try again."
            )
        
        response = await ollama_service.list_models()
        
        if verbose:
            print(f"Found {len(response.models)} available models")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/health")
async def health_check(verbose: Optional[bool] = False):
    """
    Comprehensive health check for the Ollama service
    
    Args:
        verbose: If True, logs additional debug information

    Returns:
        dict: Health check results including Ollama status and available models

    Raises:
        HTTPException: If there is an error during health check
    """
    try:
        if verbose:
            print("Performing Ollama health check...")
        
        health_data = await ollama_service.health_check()
        
        if verbose:
            print(f"Health check completed. Ollama running: {health_data['ollama_server_running']}")
        
        return health_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/leash-daily-calendar-fill", response_model=CalendarFillResponse)
async def leash_daily_calendar_fill(
    request: CalendarFillRequest,
    verbose: Optional[bool] = False
):
    """
    Generate calendar suggestions for pet care activities based on current calendar,
    pet details, and owner preferences.
    
    This endpoint uses a custom system prompt that incorporates pet information,
    owner preferences, and current calendar events to generate intelligent
    suggestions for pet care activities like walks, feeding, medication, and play time.
    
    Args:
        request: CalendarFillRequest containing current calendar, pet details, and owner preferences
        verbose: If True, logs additional debug information

    Returns:
        CalendarFillResponse: Generated calendar suggestions with metadata

    Raises:
        HTTPException: If there is an error with the request or Ollama service
    """
    try:
        if verbose:
            print(f"Processing calendar fill request with {len(request.pet_details)} pets and {len(request.current_calendar)} existing events")
        
        # Check if Ollama is running
        if not await ollama_service.check_connection():
            raise HTTPException(
                status_code=503, 
                detail="Ollama service is not running. Please start Ollama and try again."
            )
        
        # Validate that we have at least one pet
        if not request.pet_details:
            raise HTTPException(
                status_code=422,
                detail="At least one pet must be provided in pet_details"
            )
        
        # Generate calendar suggestions using Ollama
        response = await ollama_service.generate_calendar_suggestions(request)
        
        if verbose and response.execution_time_ms:
            print(f"Calendar generation took {response.execution_time_ms} ms")
            if response.success:
                print(f"Generated {len(response.suggestions)} calendar suggestions")
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/sample-post")
async def create_sample_embeddings_endpoint(
                                            request,
                                            verbose: Optional[bool] = False
                                            ):
    """
    Route to testing the /sample-post POST endpoint
    
    Args:
        request.

    Returns:
        dict: A dictionary containing the success status, a message

    Raises:
        HTTPException: If there is an error connecting to the database.
    """
    try:
        t0 = time.time()
        # Implement the logic here
        t1 = time.time()
        if verbose: print(f"create-sample-embeddings routine took {round((t1-t0)*1000, 2)} seconds")
        return {
            "success" : True,
            "internal_execution_time" : t1-t0,
            "message" : "Sample embeddings created successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
