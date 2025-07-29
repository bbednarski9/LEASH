# Agent Server

AI agent server using Ollama for local LLM inference with quantized open source models. This server provides a REST API to interact with locally hosted language models without requiring external API calls.

## Requirements

1. **Ollama Installation**: Install Ollama from [https://ollama.ai](https://ollama.ai)
2. **Python Dependencies**: Install via `pip install -r requirements.txt`
3. **LLM Model**: Pull at least one model, e.g., `ollama pull llama3.2`

## Quick Start

1. **Start Ollama in a separate terminal**:
   ```bash
   ollama serve
   ```

2. **Pull a model** (if not already done):
   ```bash
   ollama pull llama3.2
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**:
   ```bash
   python server.py
   ```

5. **View API documentation**: Visit `http://localhost:5002` for Swagger UI

## API Endpoints

### POST `/query`

Send a query to the LLM and receive a text response.

**Request Body:**

```json
{
  "query": "What is the capital of France?",
  "model": "llama3.2",
  "temperature": 0.7,
  "max_tokens": 1000,
  "system_prompt": "You are a helpful assistant."
}
```

**Response:**

```json
{
  "success": true,
  "response": "The capital of France is Paris.",
  "model_used": "llama3.2",
  "execution_time_ms": 1234.56,
  "metadata": {
    "total_duration": 1500000000,
    "eval_count": 15
  }
}
```

### GET `/models`

List all available Ollama models.

**Response:**

```json
{
  "success": true,
  "models": [
    {
      "name": "llama3.2:latest",
      "size": "2.0GB",
      "modified_at": "2024-01-15T10:30:00Z",
      "digest": "sha256:abc123..."
    }
  ]
}
```

### GET `/health`

Comprehensive health check for Ollama service.

**Response:**

```json
{
  "ollama_server_running": true,
  "models_available": 2,
  "available_models": ["llama3.2:latest", "mistral:latest"],
  "recommended_models": [],
  "timestamp": 1640995200.123
}
```

### POST `/leash-daily-calendar-fill`

**🆕 NEW ENDPOINT** - Generate intelligent pet care calendar suggestions based on current calendar, pet details, and owner preferences.

**Request Body:**

```json
{
  "current_calendar": [
    {
      "date": "2024-01-15",
      "event_start_time_utc": "2024-01-15T09:00:00Z",
      "event_end_time_utc": "2024-01-15T17:00:00Z",
      "event_title": "Work",
      "event_description": "Office work day"
    }
  ],
  "pet_details": [
    {
      "name": "Buddy",
      "age": "3 years",
      "breed": "Golden Retriever",
      "weight": "65 lbs",
      "walk_time_per_day": "60 minutes",
      "activity_level": "high",
      "special_needs": "Needs mental stimulation",
      "current_medications": []
    }
  ],
  "owner_details": {
    "owner_name": "John",
    "yard_access": true,
    "preferred_walk_times": ["morning", "evening"],
    "work_schedule": "9 AM - 5 PM weekdays",
    "availability_notes": "Free weekends",
    "preferred_activity_duration": "45 minutes"
  },
  "target_date": "2024-01-15",
  "model": "llama3.2",
  "temperature": 0.7
}
```

**Response:**

```json
{
  "success": true,
  "suggestions": [
    {
      "date": "2024-01-15",
      "event_start_time_utc": "2024-01-15T07:00:00Z",
      "event_end_time_utc": "2024-01-15T07:45:00Z",
      "event_title": "Morning Walk & Training - Buddy",
      "event_description": "High-energy morning walk with basic training exercises",
      "priority": "high",
      "activity_type": "walk",
      "pet_names": ["Buddy"]
    }
  ],
  "execution_time_ms": 2456.78,
  "model_used": "llama3.2"
}
```

**Features:**
- Analyzes current calendar to avoid conflicts
- Considers pet-specific needs and activity levels
- Respects owner preferences and schedule
- Generates variety of activities (walks, feeding, medication, play)
- Intelligent prioritization (essential vs. optional activities)
- Custom system prompt with detailed context

### POST `/generate-recommendations` (Legacy)

Generates calendar events for pet care activities.

**Request Body:**

```json
{
  "currentCalendar": {
    "events": [
      {
        "date": "2024-06-01",
        "event-start-time-UTC": "2024-06-01T14:00:00Z",
        "event-end-time-UTC": "2024-06-01T15:00:00Z",
        "event-title": "Dog Walk",
        "event-description": "Take Gus for his afternoon walk"
      }
    ]
  },
  "petDetails": {
    "pets": [
      {
        "name": "Gus",
        "age": "3 years",
        "breed": "Golden Retriever",
        "weight": "65 lbs",
        "walk-time-per-day": "60 minutes",
        "current_medications": [
          {
            "start_date": "2024-06-01",
            "end_date": "2024-06-14",
            "count-per-day": 2,
            "mg-per-serving": 25,
            "give-with-food": true
          }
        ]
      }
    ]
  },
  "userPreferences": {
    "owner-name": "John",
    "yard-access": true,
    "preferred-walk-times": ["morning", "evening"]
  }
}
```

**Response:**

```json
{
  "events": [
    {
      "date": "2024-06-01",
      "event-start-time-UTC": "2024-06-01T14:00:00Z",
      "event-end-time-UTC": "2024-06-01T15:00:00Z",
      "event-title": "Dog Walk",
      "event-description": "Take Gus for his afternoon walk"
    }
  ]
}
```

## Features

- **FastAPI Framework**: High-performance async web framework
- **Ollama Integration**: Direct integration with local Ollama models
- **Automatic Model Management**: Automatically pulls models if not available
- **Comprehensive Health Checks**: Monitor Ollama service and model availability
- **CORS Support**: Cross-origin resource sharing enabled
- **Swagger Documentation**: Interactive API documentation at root endpoint
- **Async Processing**: Non-blocking request handling for better performance

## Recommended Models

- `llama3.2` - Good general purpose model (2GB)
- `llama3.2:1b` - Smaller, faster model (1GB)
- `llama3.1:8b` - Larger, more capable model (4.7GB)
- `mistral` - Alternative high-quality model (4GB)
- `codellama` - Specialized for code generation (4GB)

## Configuration

The server can be configured via environment variables:

- `PORT` - Server port (default: 5002)
- `OLLAMA_BASE_URL` - Ollama server URL (default: http://localhost:11434)

## Error Handling

The API includes comprehensive error handling:

- **503 Service Unavailable**: Ollama server is not running
- **500 Internal Server Error**: Model errors or unexpected failures
- **422 Validation Error**: Invalid request parameters

## Testing

Test the connection:
```bash
curl http://localhost:5001/test-connection
```

Send a basic query:
```bash
curl -X POST http://localhost:5001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?", "model": "llama3.2"}'
```

Test the calendar endpoint with the provided script:
```bash
python test_calendar_endpoint.py
```

Or test manually with curl:
```bash
curl -X POST http://localhost:5001/leash-daily-calendar-fill \
  -H "Content-Type: application/json" \
  -d '{
    "current_calendar": [
      {
        "date": "2024-01-15",
        "event_start_time_utc": "2024-01-15T09:00:00Z",
        "event_end_time_utc": "2024-01-15T17:00:00Z",
        "event_title": "Work",
        "event_description": "Office day"
      }
    ],
    "pet_details": [
      {
        "name": "Buddy",
        "age": "3 years",
        "breed": "Golden Retriever",
        "weight": "65 lbs",
        "walk_time_per_day": "60 minutes",
        "activity_level": "high"
      }
    ],
    "owner_details": {
      "owner_name": "John",
      "yard_access": true,
      "preferred_walk_times": ["morning", "evening"],
      "work_schedule": "9 AM - 5 PM weekdays"
    },
    "model": "llama3.2"
  }'
```



conda create -n agent_server python=3.11
conda activate agent_server
pip install -r requirements.txt
