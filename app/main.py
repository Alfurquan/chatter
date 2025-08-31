from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.logging import LoggerFactory

LoggerFactory.create_logger("main", "json")

from app.api import health
from app.api import users
from app.api import auth
from app.services.user_service import UserService

# Create FastAPI app
app = FastAPI(
    title="Chatter API",
    description="Real-time chat application API",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)

app.state.user_service = UserService()

@app.get("/")
async def root():
    return {"message": "Welcome to Chatter API"}
