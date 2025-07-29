import os

import uvicorn
# from app.database import Base, engine
from app.routes import router
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

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
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))