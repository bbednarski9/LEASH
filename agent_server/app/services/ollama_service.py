import asyncio
import logging
import time
from typing import Optional, List, Dict, Any
import ollama
from ollama import Client
import httpx
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from models.query_models import QueryResponse, ModelInfo, ModelsListResponse, CalendarFillRequest, CalendarFillResponse, CalendarSuggestion
import json

logger = logging.getLogger(__name__)


class OllamaService:
    """Service class for interacting with Ollama models"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama service
        
        Args:
            base_url: The base URL for the Ollama server
        """
        self.base_url = base_url
        self.client = Client(host=base_url)
        
    async def check_connection(self) -> bool:
        """
        Check if Ollama server is running and accessible
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/version", timeout=5.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to Ollama server: {e}")
            return False
    
    async def list_models(self) -> ModelsListResponse:
        """
        List all available models in Ollama
        
        Returns:
            ModelsListResponse: List of available models
        """
        try:
            # Use asyncio to run the sync ollama client in a thread pool
            models_data = await asyncio.get_event_loop().run_in_executor(
                None, self.client.list
            )
            
            models = []
            for model in models_data.get('models', []):
                model_info = ModelInfo(
                    name=model.get('name', ''),
                    size=model.get('size', ''),
                    modified_at=model.get('modified_at', ''),
                    digest=model.get('digest', '')
                )
                models.append(model_info)
            
            return ModelsListResponse(success=True, models=models)
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return ModelsListResponse(
                success=False, 
                models=[], 
                error=f"Failed to list models: {str(e)}"
            )
    
    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama registry if not already available
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.pull, model_name
            )
            return True
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    async def generate_response(
        self, 
        query: str, 
        model: str = "llama3.2",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
    ) -> QueryResponse:
        """
        Generate a response using the specified model
        
        Args:
            query: The input query/prompt
            model: Model name to use for generation
            temperature: Temperature for response generation
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            
        Returns:
            QueryResponse: The generated response with metadata
        """
        start_time = time.time()
        
        try:
            # Check if model is available, if not try to pull it
            models_response = await self.list_models()
            available_models = [m.name for m in models_response.models] if models_response.success else []
            
            # Check if the requested model is available (handle version tags)
            model_available = any(model in available_model for available_model in available_models)
            
            if not model_available:
                logger.info(f"Model {model} not found, attempting to pull...")
                pull_success = await self.pull_model(model)
                if not pull_success:
                    return QueryResponse(
                        success=False,
                        error=f"Failed to pull model {model}. Please ensure the model name is correct."
                    )
            
            # Prepare the messages for the chat API
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": query})
            
            # Generate response using ollama
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.client.chat(
                    model=model,
                    messages=messages,
                    options={
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                )
            )
            
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return QueryResponse(
                success=True,
                response=response['message']['content'],
                model_used=model,
                execution_time_ms=round(execution_time, 2),
                metadata={
                    "total_duration": response.get('total_duration'),
                    "load_duration": response.get('load_duration'),
                    "prompt_eval_count": response.get('prompt_eval_count'),
                    "eval_count": response.get('eval_count')
                }
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Failed to generate response: {e}")
            return QueryResponse(
                success=False,
                error=f"Failed to generate response: {str(e)}",
                execution_time_ms=round(execution_time, 2)
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive health check of the Ollama service
        
        Returns:
            Dict containing health check results
        """
        health_data = {
            "ollama_server_running": False,
            "models_available": 0,
            "recommended_models": [],
            "timestamp": time.time()
        }
        
        # Check if server is running
        health_data["ollama_server_running"] = await self.check_connection()
        
        if health_data["ollama_server_running"]:
            # Get available models
            models_response = await self.list_models()
            if models_response.success:
                health_data["models_available"] = len(models_response.models)
                health_data["available_models"] = [m.name for m in models_response.models]
        
        # Recommend some popular models if none are available
        if health_data["models_available"] == 0:
            health_data["recommended_models"] = [
                "llama3.2",
                "llama3.2:1b", 
                "llama3.1:8b",
                "mistral",
                "codellama"
            ]
        
        return health_data
    
    def _create_calendar_system_prompt(self, request: CalendarFillRequest) -> str:
        """
        Create a system prompt for calendar generation based on user data
        
        Args:
            request: CalendarFillRequest containing pet and owner details
            
        Returns:
            str: Formatted system prompt
        """
        
        # Format pet details
        pets_info = []
        for pet in request.pet_details:
            pet_info = f"- {pet.name} ({pet.breed}, {pet.age}, {pet.weight})"
            pet_info += f"\n  • Daily walk time needed: {pet.walk_time_per_day}"
            pet_info += f"\n  • Activity level: {pet.activity_level}"
            if pet.special_needs:
                pet_info += f"\n  • Special needs: {pet.special_needs}"
            if pet.current_medications:
                pet_info += f"\n  • Medications: {len(pet.current_medications)} active medications"
            pets_info.append(pet_info)
        
        pets_section = "\n".join(pets_info)
        
        # Format owner details
        owner = request.owner_details
        owner_info = f"""
Owner: {owner.owner_name}
- Yard access: {'Yes' if owner.yard_access else 'No'}
- Preferred walk times: {', '.join(owner.preferred_walk_times) if owner.preferred_walk_times else 'No specific preference'}
- Work schedule: {owner.work_schedule if owner.work_schedule else 'Not specified'}
- Preferred activity duration: {owner.preferred_activity_duration}
- Availability notes: {owner.availability_notes if owner.availability_notes else 'None'}"""
        
        # Format current calendar  
        current_events = []
        for event in request.current_calendar:
            # Show full datetime format to match the output format the AI should generate
            # This helps the AI properly compare times and avoid conflicts
            event_info = f"- {event.event_title}"
            event_info += f"\n  Start: {event.event_start_time_local}"
            event_info += f"\n  End: {event.event_end_time_local}"
            if event.event_description:
                event_info += f"\n  Description: {event.event_description}"
            current_events.append(event_info)
        
        calendar_section = "\n".join(current_events) if current_events else "No current events"
        
        target_date_section = f"Target date for suggestions: {request.target_date}" if request.target_date else "Generate suggestions for the next few days"
        
        timezone_section = f"User timezone: {request.user_timezone}" if request.user_timezone else "User timezone: Not specified (assume local time)"
        
        system_prompt = f"""You are a professional pet care scheduler and dog training expert. Your job is to analyze the current calendar and pet/owner information to generate intelligent calendar suggestions for pet care activities.

CONTEXT INFORMATION:

Pet Details:
{pets_section}

{owner_info}

Current Calendar Events:
{calendar_section}

{target_date_section}

{timezone_section}

INSTRUCTIONS:
1. Analyze the current calendar to identify gaps where pet care activities can be scheduled
2. Consider each pet's specific needs, activity level, and any medications
3. Respect the owner's preferences, work schedule, and availability
4. Generate realistic, practical suggestions that fit the owner's lifestyle
5. Include a variety of activities: walks, feeding times, play sessions, medication reminders, grooming, etc.
6. Consider the time of day, weather appropriateness, and pet energy levels
7. Avoid conflicts with existing calendar events
8. Prioritize essential activities (medication, feeding) over optional ones (extra play time)

IMPORTANT TIMEZONE INFORMATION:
- All times in the current calendar are shown in the owner's LOCAL timezone
- When suggesting new activities, use times that make sense in the owner's daily routine
- Consider that 7:00 AM means 7:00 AM in the owner's timezone, NOT UTC

OUTPUT FORMAT:
Respond with a JSON array of calendar suggestions. Each suggestion should be a JSON object with these exact fields:
- "date": "YYYY-MM-DD"
- "event_start_time_local": "YYYY-MM-DDTHH:MM:SS" (MUST include full date and time, e.g., "2025-07-29T06:30:00")
- "event_end_time_local": "YYYY-MM-DDTHH:MM:SS" (MUST include full date and time, e.g., "2025-07-29T07:00:00")
- "event_title": "Brief descriptive title"
- "event_description": "Detailed description including specific instructions"
- "priority": "high" | "medium" | "low"
- "activity_type": "walk" | "feeding" | "medication" | "play" | "grooming" | "training" | "general"
- "pet_names": ["PetName1", "PetName2"] (array of pet names this activity is for)

IMPORTANT: 
- Respond ONLY with valid JSON array, no additional text
- Provide times in the user's LOCAL timezone (same format as the input calendar events)
- ALWAYS include the full date in time fields (e.g., "2025-07-29T06:30:00", NOT just "06:30:00")
- Include 3-5 realistic suggestions
- CRITICAL: Compare your suggested times against the existing calendar events shown above to avoid any time overlaps
- Check that your start/end times don't conflict with any existing event start/end times
- Consider realistic timing for the user's timezone (don't schedule walks at 3 AM local time)
- Use 24-hour format for times (e.g., "14:00:00" for 2 PM)

EXAMPLE OUTPUT:
[
  {{
    "date": "2025-07-29",
    "event_start_time_local": "2025-07-29T07:00:00",
    "event_end_time_local": "2025-07-29T07:30:00",
    "event_title": "Morning Dog Walk",
    "event_description": "Take the dogs for their morning exercise",
    "priority": "high",
    "activity_type": "walk",
    "pet_names": ["June", "Gus"]
  }}
]"""

        return system_prompt
    
    async def generate_calendar_suggestions(self, request: CalendarFillRequest) -> CalendarFillResponse:
        """
        Generate calendar suggestions based on pet and owner details
        
        Args:
            request: CalendarFillRequest with all necessary details
            
        Returns:
            CalendarFillResponse: Generated calendar suggestions
        """
        start_time = time.time()
        
        try:
            # Create the system prompt
            system_prompt = self._create_calendar_system_prompt(request)
            
            # Simple query asking for suggestions
            user_query = "Please generate calendar suggestions based on the provided context."
            
            # Generate response using the standard generate_response method
            llm_response = await self.generate_response(
                query=user_query,
                model=request.model,
                temperature=request.temperature,
                max_tokens=2000,  # More tokens for JSON response
                system_prompt=system_prompt
            )
            
            if not llm_response.success:
                return CalendarFillResponse(
                    success=False,
                    error=f"LLM generation failed: {llm_response.error}"
                )
            
            # Parse the JSON response
            try:
                # Clean the response - sometimes models add extra text
                response_text = llm_response.response.strip()
                
                # Find the JSON array in the response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                
                if start_idx == -1 or end_idx == 0:
                    raise ValueError("No JSON array found in response")
                
                json_text = response_text[start_idx:end_idx]
                suggestions_data = json.loads(json_text)
                
                # Convert to CalendarSuggestion objects
                suggestions = []
                for suggestion_dict in suggestions_data:
                    try:
                        suggestion = CalendarSuggestion(**suggestion_dict)
                        suggestions.append(suggestion)
                    except Exception as e:
                        logger.warning(f"Failed to parse suggestion: {e}")
                        continue
                
                execution_time = (time.time() - start_time) * 1000
                
                return CalendarFillResponse(
                    success=True,
                    suggestions=suggestions,
                    execution_time_ms=round(execution_time, 2),
                    model_used=request.model,
                    metadata={
                        "total_suggestions_generated": len(suggestions_data),
                        "valid_suggestions": len(suggestions),
                        "system_prompt_length": len(system_prompt)
                    }
                )
                
            except json.JSONDecodeError as e:
                return CalendarFillResponse(
                    success=False,
                    error=f"Failed to parse JSON response: {str(e)}. Raw response: {llm_response.response[:200]}..."
                )
            except Exception as e:
                return CalendarFillResponse(
                    success=False,
                    error=f"Failed to process suggestions: {str(e)}"
                )
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Failed to generate calendar suggestions: {e}")
            return CalendarFillResponse(
                success=False,
                error=f"Failed to generate calendar suggestions: {str(e)}",
                execution_time_ms=round(execution_time, 2)
            ) 