This project integrates multiple services to provide AI-powered pet care calendar suggestions using local LLM models.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Email Server   │    │  Agent Server   │
│   (React/Vite)  │    │   (FastAPI)     │    │   (FastAPI)     │
│   Port: 5173    │    │   Port: 5001    │    │   Port: 5002    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Profiles   │    │ Google Calendar │    │  Ollama LLM     │
│   (Static JSON) │    │      API        │    │  (Local Host)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
1. **Ollama** - Install from [https://ollama.ai](https://ollama.ai)
2. **Node.js** - For the frontend
3. **Python 3.11+** - For backend services
4. **Google Calendar API** - Setup required for email server

### 1. Start Ollama
```bash
# Install a model
# ollama pull llama3.2
ollama pull mistral

# Start Ollama service
ollama serve
```

### 2. Start Agent Server
```bash
cd project/agent_server
conda create -n agent_server python=3.11
conda activate agent_server
pip install -r requirements.txt
python server.py
# Runs on http://localhost:5002
```

### 3. Start Email Server
```bash
cd project/email_server
conda create -n email_server python=3.11
conda activate email_server
pip install -r requirements.txt
python server.py
# Runs on http://localhost:5001
```

### 4. Start Frontend
```bash
cd project/frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

## 🎯 How to Use

### Schedule Dog Care Feature

1. **Open the app** at `http://localhost:5173`
2. **Login** to authenticate with Google Calendar
3. **Navigate to any day** in the calendar view
4. **Click "Schedule Dog Care"** button
5. **Review AI suggestions** in the modal popup
6. **Accept or reject** individual suggestions
7. **Accepted events** are automatically added to your Google Calendar

### The AI Process

1. **Data Collection**: The frontend loads pet and owner profiles from `public/profiles/`
2. **Context Building**: Current calendar events and profile data are combined
3. **AI Generation**: Agent server uses Ollama LLM to generate personalized suggestions
4. **Event Creation**: Accepted suggestions are added to Google Calendar via email server

## 📁 Project Structure

```
project/
├── agent_server/          # AI service for calendar suggestions
│   ├── api/              # Swagger documentation
│   ├── app/              # FastAPI application
│   │   ├── router/       # API endpoints
│   │   └── services/     # Ollama integration
│   ├── models/           # Pydantic models
│   └── server.py         # Main server
├── email_server/         # Google Calendar integration
│   ├── app/              # FastAPI application
│   │   ├── auth/         # OAuth & session management
│   │   ├── router/       # API endpoints
│   │   └── services/     # Google Calendar API
│   └── server.py         # Main server
└── frontend/             # React application
    ├── public/profiles/  # User and pet profiles
    ├── src/components/   # React components
    └── src/services/     # API integration
```

## 🔧 Key Features

### Agent Server
- **Local LLM Integration**: Uses Ollama for privacy-first AI
- **Custom System Prompts**: Tailored prompts for pet care scheduling
- **Multiple Model Support**: Works with llama3.2, mistral, etc.
- **Intelligent Suggestions**: Considers pet needs, owner schedule, existing events

### Frontend Integration
- **Profile Management**: JSON-based pet and owner profiles
- **Interactive UI**: Modal-based suggestion review
- **Real-time Updates**: Calendar refreshes after accepting suggestions
- **Error Handling**: Graceful fallbacks for service issues

### Calendar Integration
- **Google Calendar API**: Full read/write access to calendar
- **OAuth Authentication**: Secure Google login
- **Event Validation**: Prevents scheduling conflicts
- **Bulk Operations**: Efficient event creation

## 🐕 Profile Configuration

### Pet Profiles (`public/profiles/pets.json`)
```json
{
  "pets": [
    {
      "name": "Luna",
      "age": "4 years",
      "breed": "Border Collie",
      "weight": "45 lbs",
      "walk-time-per-day": "90 minutes",
      "energy-level": "high",
      "current_medications": [...],
      "behavioral-notes": "Highly intelligent, needs mental stimulation"
    }
  ]
}
```

### User Profiles (`public/profiles/users.json`)
```json
{
  "userDetails": [
    {
      "name": "Your Name",
      "email": "your.email@gmail.com",
      "yard-access": true,
      "preferred-walk-times": ["early morning", "late evening"],
      "exercise-level": "high"
    }
  ]
}
```

## 🤖 AI System Prompt

The agent server creates dynamic system prompts that include:
- **Pet Details**: Breed, age, energy level, medications, special needs
- **Owner Context**: Schedule, preferences, yard access, work hours
- **Calendar Analysis**: Current events to avoid conflicts
- **Activity Types**: Walks, feeding, medication, play, grooming, training

## 📊 API Endpoints

### Agent Server (Port 5002)
- `POST /leash-daily-calendar-fill` - Generate calendar suggestions
- `GET /health` - Service health check
- `GET /models` - List available Ollama models
- `POST /query` - General LLM queries

### Email Server (Port 5001)
- `POST /calendar/events` - Create calendar events
- `GET /calendar/events` - Get events for date
- `GET /auth/status` - Check authentication status
- `GET /auth/login` - Google OAuth login

## 🔍 Troubleshooting

### Common Issues

**Agent Server Not Responding**
- Ensure Ollama is running: `ollama serve`
- Check if model is available: `ollama list`
- Verify port 5002 is free

**Calendar Events Not Creating**
- Check Google Calendar authentication
- Verify email server is running on port 5001
- Check browser console for API errors

**Profile Data Not Loading**
- Ensure profiles are in `frontend/public/profiles/`
- Check JSON file formatting
- Verify frontend dev server is serving static files

### Debug Information
- Frontend: Check browser console for detailed logs
- Agent Server: Visit `http://localhost:5002` for Swagger UI
- Email Server: Check server logs for authentication issues

## 🛠️ Development

### Testing Agent Server
```bash
# Test basic connectivity
curl http://localhost:5002/health

# Test LLM query
curl -X POST http://localhost:5002/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello!", "model": "llama3.2"}'
```

### Adding New Features
1. **New Activity Types**: Update system prompt in `ollama_service.py`
2. **Profile Fields**: Modify JSON structure and conversion logic
3. **UI Enhancements**: Add components to `frontend/src/components/`

## 📄 License

This project is for the Microsoft Senior Applied Scientist application demonstration.

---

## 💡 Next Steps

- [ ] Calendar template system
- [ ] Accident prediction network ;)
