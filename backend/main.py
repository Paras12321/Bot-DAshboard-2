import os
import sys
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import engine, Base
from backend.routes import bots, tasks, logs, automations

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Platform Bot Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(bots.router)
app.include_router(tasks.router)
app.include_router(logs.router)
app.include_router(automations.auto_reply_router)
app.include_router(automations.welcome_router)

# Paths for frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.get("/dashboard")
def get_dashboard():
    dashboard_path = os.path.join(FRONTEND_DIR, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"error": "dashboard.html not found"}

# Mount static files (HTML, CSS, JS) at the root
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    print(f"Warning: Frontend directory not found at {FRONTEND_DIR}")

if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import uvicorn
    # pyrefly: ignore [missing-import]  
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
