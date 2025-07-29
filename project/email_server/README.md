# Email Server

A FastAPI-based server designed to handle email and calendar integration services. This server will provide the primary interface for Google Calendar operations via OAuth authentication.

## 🚀 Features

- **FastAPI Framework**: High-performance async web framework
- **CORS Support**: Cross-origin resource sharing enabled
- **Environment Configuration**: Flexible configuration via environment variables
- **Swagger Documentation**: Auto-generated API documentation at root endpoint
- **Health Check Endpoints**: Connection testing and monitoring

## 📋 Prerequisites

- Python 3.11
- Conda (Anaconda or Miniconda) OR Docker & Docker Compose
- Google Cloud Project with Calendar API enabled

## 🛠️ Installation & Setup

### 1. Clone and Navigate
```bash
cd project/email_server
```

### 2. Create Conda Environment
```bash
conda create -n email_server python=3.11
conda activate email_server
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
PORT=5000
# OAuth Configuration (for Google Calendar integration)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback
SESSION_SECRET=your_random_session_secret
# Frontend URL for post-auth redirects
FRONTEND_URL=http://localhost:5000
```

**Generate a secure session secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Google Calendar API Setup
> **Note**: Calendar integration is now fully implemented!
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project (if you don't have one)
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials for a web application
5. Set authorized redirect URIs to: `http://localhost:5000/auth/callback`
6. Download the `credentials.json` file
7. Store credentials in `app/auth/credentials.json`
8. Set up environment variables for OAuth (see Environment Configuration)

## 🚀 Running the Server

### Development Mode
```bash
conda activate email_server
python server.py
```
The server will start on `http://localhost:5000` (or the port specified in your `.env` file).

### Production Mode
```bash
conda activate email_server
uvicorn server:app --host 0.0.0.0 --port 5000
```

### Docker

#### Using Docker Compose (Recommended)
```bash
# Copy and configure environment variables
cp env.example .env
# Edit .env with your actual values

# Build and start the service
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop the service
docker-compose down
```

#### Using Docker directly
```bash
# Build the image
docker build -t email-server:latest .

# Run the container with environment file
docker run -p 5000:5000 --env-file .env email-server:latest

# Or run with individual environment variables
docker run -p 5000:5000 \
  -e GOOGLE_CLIENT_ID=your_client_id \
  -e GOOGLE_CLIENT_SECRET=your_client_secret \
  -e SESSION_SECRET=your_session_secret \
  email-server:latest
```

#### Production Deployment
For production, modify the docker-compose.yml:
1. Remove the development volume mount
2. Use environment variables or secrets management
3. Enable HTTPS and set secure cookies
4. Consider using a reverse proxy like nginx

## 📖 API Documentation

### Base URL
```
http://localhost:5000
```

### Available Endpoints

#### Health Check
```http
GET /test-connection?verbose=false
```

**Description**: Tests server connectivity and health status.

**Query Parameters**:
- `verbose` (optional, boolean): Enable verbose logging. Default: `false`

**Response**:
```json
{
  "success": true
}
```

#### Sample POST Endpoint
```http
POST /sample-post?verbose=false
```

**Description**: Sample POST endpoint for testing request handling.

**Query Parameters**:
- `verbose` (optional, boolean): Enable verbose logging and timing. Default: `false`

**Response**:
```json
{
  "success": true,
  "internal_execution_time": 0.001,
  "message": "Sample embeddings created successfully"
}
```

### Authentication Endpoints

#### Initiate Google OAuth Login
```http
GET /auth/login
```

**Description**: Redirects user to Google OAuth consent screen.

**Response**: HTTP 302 redirect to Google OAuth URL

#### OAuth Callback
```http
GET /auth/callback?code=AUTH_CODE&state=STATE
```

**Description**: Handles Google OAuth callback and creates user session.

**Query Parameters**:
- `code` (required): Authorization code from Google
- `state` (optional): CSRF protection state parameter

**Response**: HTTP 302 redirect to frontend with session cookie set

#### Check Authentication Status
```http
GET /auth/status
```

**Description**: Checks if user is currently authenticated.

**Headers**:
- `Cookie`: Session cookie from login

**Response**:
```json
{
  "authenticated": true,
  "user_email": "user@example.com",
  "expires_at": "2024-06-01T15:00:00Z"
}
```

#### Logout
```http
POST /auth/logout
```

**Description**: Destroys user session and clears authentication.

**Headers**:
- `Cookie`: Session cookie

**Response**:
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

#### API Documentation
```http
GET /
```

**Description**: Serves the Swagger UI for interactive API documentation.

```http
GET /swagger.yaml
```

**Description**: Returns the OpenAPI specification in YAML format.

### Calendar Endpoints

#### Read Calendar
```http
GET /calendar/events?date=YYYY-MM-DD
```

**Description**: Retrieve calendar events for a specified date. Requires authentication.

**Headers**:
- `Cookie`: Session cookie from login

**Query Parameters**:
- `date` (required): Date in YYYY-MM-DD format

**Response**:
```json
{
  "success": true,
  "events": [
    {
      "id": "event123",
      "title": "Dog Walk",
      "start_time": "2024-06-01T14:00:00Z",
      "end_time": "2024-06-01T15:00:00Z",
      "description": "Take Gus for his afternoon walk"
    }
  ]
}
```

#### Update Calendar
```http
POST /calendar/events
```

**Description**: Add new events to the calendar. Requires authentication.

**Headers**:
- `Cookie`: Session cookie from login

**Request Body**:
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

**Response**:
```json
{
  "success": true,
  "results": [
    {
      "event_id": "abc123",
      "status": "created",
      "title": "Dog Walk"
    }
  ]
}
```

**Error Responses**:
- `401`: User not authenticated (redirect to login)
- `400`: Invalid request data (end time before start time, etc.)
- `500`: Google API error or server error

## 🔧 Development

### Environment Management
Always activate the conda environment before development:
```bash
conda activate email_server
```

To deactivate when done:
```bash
conda deactivate
```

### Project Structure
```
email_server/
├── app/
│   ├── auth/                    # Authentication modules
│   │   ├── __init__.py
│   │   ├── models.py           # Pydantic models for auth/calendar
│   │   ├── session_manager.py  # Session management with signed cookies
│   │   ├── oauth.py            # Google OAuth handler
│   │   └── dependencies.py     # FastAPI dependencies for auth
│   ├── router/
│   │   ├── __init__.py
│   │   ├── routes.py           # Main router with health check
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   └── calendar_routes.py  # Calendar management endpoints
│   └── services/
│       ├── __init__.py
│       └── calendar_service.py # Google Calendar API service
├── server.py                   # Main application entry point
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
└── README.md                  # This file
```

### Dependencies
- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and serialization
- **python-dotenv**: Environment variable management
- **greenlet**: Async support library
- **google-auth**: Google authentication library
- **google-auth-oauthlib**: OAuth flow handling
- **google-api-python-client**: Google Calendar API client
- **python-multipart**: Form data handling
- **itsdangerous**: Session management and CSRF protection
- **pyyaml**: YAML processing for OpenAPI documentation
- **requests**: HTTP client library for health checks

### Adding New Endpoints
1. Add route functions to `app/router/routes.py`
2. Use appropriate FastAPI decorators (`@router.get`, `@router.post`, etc.)
3. Include proper documentation strings
4. Handle exceptions with `HTTPException`

## 🐛 Error Handling

The server includes comprehensive error handling:
- All endpoints return appropriate HTTP status codes
- Detailed error messages in development mode
- Structured JSON error responses

## 🔒 Authentication Flow

The server implements **backend authentication** for security and centralized token management:

### Flow Overview
1. **Frontend** → User clicks "Login with Google"
2. **Frontend** → Redirects to `/auth/login`
3. **Backend** → Redirects to Google OAuth consent screen
4. **Google** → User grants permissions
5. **Google** → Redirects to `/auth/callback` with authorization code
6. **Backend** → Exchanges code for access/refresh tokens
7. **Backend** → Stores tokens securely, creates session
8. **Backend** → Redirects to frontend with session cookie
9. **Frontend** → Makes API calls using session cookie
