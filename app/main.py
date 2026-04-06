from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import routes
from app.routers import auth_endpoints, projects, tasks, workspaces

app = FastAPI(
    title="Task Management API",
    description="A minimal but clean task management API built with FastAPI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_endpoints.router)
app.include_router(workspaces.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    """Health check endpoint"""
    return {"message": "Task Management API is running", "version": "1.0.0"}


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}


