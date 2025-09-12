from fastapi import FastAPI, Depends
from app.db import SessionLocal
from app.db.init_db import create_tables, init_db
from fastapi.middleware.cors import CORSMiddleware
from app.logging import LoggerFactory
import logging

LoggerFactory.create_logger("main", "json")

from app.api import health
from app.api import users
from app.api import auth
from app.api import conversation
from app.services.user_service import UserService
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService 
from app.websocket import router as websocket_router
from app.websocket.connection_manager import ConnectionManager
from app.error.error import api_exception_handler, APIException
from app.middleware.sanity import RequestIDMiddleware
from app.db import SessionLocal
from app.db.redis_client import RedisClient
from app.utils.cache import Cache
from app.db.init_db import create_tables, init_db

logger = logging.getLogger("main")


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

# Include error handler
app.add_exception_handler(APIException, api_exception_handler)

# Include middleware
app.add_middleware(RequestIDMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(conversation.router)
app.include_router(websocket_router)

# Initialize database
create_tables()

# Initialize database for first run
db = SessionLocal()
try:
    init_db(db)
finally:
    db.close()

# Initialize services and store in app.state
# This ensures they're available throughout the application
db_for_services = SessionLocal()
redis_client = RedisClient()
cache = Cache(redis_client)
user_service = UserService(db_for_services, cache)
app.state.user_service = user_service
app.state.conversation_service = ConversationService(user_service, db_for_services)
app.state.message_service = MessageService(db_for_services)
app.state.connection_manager = ConnectionManager()
app.state.redis_client = redis_client
app.state.cache = cache


# Create a shutdown event to close the database connection
@app.on_event("shutdown")
def shutdown_db_client():
    db_for_services.close()
    redis_client.close()

@app.get("/")
async def root():
    return {"message": "Welcome to Chatter API"}
