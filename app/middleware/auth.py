from fastapi import HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from typing import Optional
import os
import jwt

from app.services.user_service import UserService
from app.models.user import User

# Load environment variables from .env file
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split()[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    username = payload.get("sub")
    user = await UserService().get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user