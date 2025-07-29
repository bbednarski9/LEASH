import os
from dotenv import load_dotenv

# Load environment variables FIRST, before any other imports
load_dotenv()

import uvicorn
# from app.database import Base, engine
from app.router.routes import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(
    title="Email Server API",
    description="FastAPI server for email and calendar integration services with Google OAuth authentication",
    version="1.0.0",
    docs_url=None,  # Disable default docs to customize
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", include_in_schema=False)
async def docs():
    """Serve custom Swagger UI documentation"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Email Server API Documentation"
    )


@app.get("/swagger.yaml", include_in_schema=False)
async def get_swagger_yaml():
    """Return OpenAPI specification in YAML format"""
    from fastapi.openapi.utils import get_openapi
    import yaml
    
    openapi_schema = get_openapi(
        title="Email Server API",
        version="1.0.0", 
        description="FastAPI server for email and calendar integration services",
        routes=app.routes
    )
    
    return JSONResponse(
        content=yaml.dump(openapi_schema, default_flow_style=False),
        media_type="application/x-yaml"
    )


@app.on_event("startup")
async def startup():
    print("Starting up the server on port: ", os.environ.get("PORT", 5001))
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

current_dir = os.path.dirname(os.path.abspath(__file__))
swagger_path = os.path.join(current_dir, './api/swagger.yaml')
html_path = os.path.join(current_dir, './api/index.html')

# localhost:PORT/swagger.yaml
@app.get('/swagger.yaml', response_class=FileResponse)
async def serve_swagger_yaml():
    try:
        return FileResponse(path= swagger_path, filename=swagger_path, media_type='application/yaml')
    except Exception as e:
        return JSONResponse ({"error": str(e)}, 500)

# localhost:PORT/
@app.get('/', response_class=FileResponse)
async def serve_swagger_ui():
    return FileResponse(html_path)

if __name__ == "__main__":
    env_vars = [
        "PORT",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REDIRECT_URI",
        "SESSION_SECRET",
        "FRONTEND_URL"
    ]
    print("Loaded environment variables:")
    for var in env_vars:
        print(f"{var} = {os.environ.get(var)}")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))