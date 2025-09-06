import logging
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import User, Conversation, Message
from app.db import engine
from app.models.user import UserStatus
from app.security.password_security import hash_password

logger = logging.getLogger(__name__)

def create_tables():
    """Create database tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

def init_db(db: Session):
    """Initialize the database with initial setup if needed"""
    # Log the database initialization
    logger.info("Checking database setup")
    
    # Here we can add any required database initialization
    # without automatically creating test users
    
    logger.info("Database initialization complete")
