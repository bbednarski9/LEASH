import asyncio
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

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
