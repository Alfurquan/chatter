from fastapi import HTTPException, Header, Request
from dotenv import load_dotenv
from typing import Optional
import logging

from app.models.user import User
from ..security.jwt_handler import decode_access_token

load_dotenv()
logger = logging.getLogger("main.middleware.auth")

async def get_current_user(request: Request, authorization: Optional[str] = Header(None)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        logger.warning("Missing or invalid Authorization header format")
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    
    token = authorization.split()[1]
    logger.debug(f"Attempting to validate token")
    payload = decode_access_token(token)
    
    if not payload:
        logger.warning("Token validation failed")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    username = payload.get("sub")
    if not username:
        logger.warning("Token payload missing 'sub' claim")
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    logger.debug(f"Looking up user: {username}")
    service = request.app.state.user_service
    user = service.get_user_by_id(username)
    
    if not user:
        logger.warning(f"User not found: {username}")
        raise HTTPException(status_code=401, detail="User not found")
    
    logger.debug(f"User authenticated: {username}")
    return user