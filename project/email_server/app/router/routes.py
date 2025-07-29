import os
import time
from typing import Optional

from fastapi import HTTPException, APIRouter, Request
from app.auth.dependencies import get_current_user, UserSession
from fastapi import Depends
import json

router = APIRouter()

# Include auth and calendar routes
from .auth_routes import router as auth_router
from .calendar_routes import router as calendar_router

router.include_router(auth_router, prefix="/auth", tags=["authentication"])
router.include_router(calendar_router, prefix="/calendar", tags=["calendar"])

@router.get("/test-connection")
async def test_connection(
                        verbose: Optional[bool] = False
                        ):
    """
    Test the connection to the server.
    """
    
    if verbose:
        print("Executing test-connection endpoint")
    
    try:
        if verbose:
            print("test-connection executed successfully")
        
        return {"success": True}
    except Exception as e:
        if verbose:
            print(f"Error in test-connection: {str(e)}")
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sample-post")
async def create_sample_embeddings_endpoint(
                                            request,
                                            verbose: Optional[bool] = False
                                            ):
    """
    Sample endpoint to test POST requests.
    """
    start_time = time.time()
    
    if verbose:
        print("Creating sample embeddings")
    
    try:
        # Simulate some processing
        if verbose:
            print("Sample embeddings created successfully")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return {
            "success": True,
            "internal_execution_time": execution_time,
            "message": "Sample embeddings created successfully"
        }
    except Exception as e:
        if verbose:
            print(f"Error creating sample embeddings: {str(e)}")
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profiles/users")
async def get_user_profiles(
    user_session: UserSession = Depends(get_current_user)
):
    """
    Get user profile data. Returns current user's profile or all users for admin.
    """
    try:
        profiles_path = os.path.join(os.path.dirname(__file__), "..", "..", "profiles", "users.json")
        
        with open(profiles_path, 'r') as f:
            data = json.load(f)
        
        # Filter to current user's data based on email
        user_details = data.get("userDetails", [])
        current_user_profile = next(
            (user for user in user_details if user.get("email") == user_session.user_email), 
            None
        )
        
        if current_user_profile:
            return {
                "success": True,
                "user": current_user_profile
            }
        else:
            # Return all users if current user not found (for development)
            return {
                "success": True,
                "users": user_details,
                "current_email": user_session.user_email
            }
            
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User profiles not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading user profiles: {str(e)}")

@router.get("/profiles/pets")
async def get_pet_profiles(
    user_session: UserSession = Depends(get_current_user)
):
    """
    Get pet profile data for the authenticated user.
    """
    try:
        profiles_path = os.path.join(os.path.dirname(__file__), "..", "..", "profiles", "pets.json")
        
        with open(profiles_path, 'r') as f:
            data = json.load(f)
        
        pets = data.get("pets", [])
        
        return {
            "success": True,
            "pets": pets
        }
            
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Pet profiles not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading pet profiles: {str(e)}")
