# Agent Server

AI agent using Ollama for generating pet care recommendations based on calendar and pet data.

## API Endpoints

### POST `/generate-recommendations`

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
- **LangChain Agent**: AI-powered recommendations using Ollama
- **CORS Support**: Cross-origin resource sharing enabled
- **Swagger Documentation**: Auto-generated API docs at root endpoint