from app.error.error import APIException, ErrorCode
from fastapi import APIRouter, Request
import logging
import os
from dotenv import load_dotenv

from ..security.jwt_handler import create_access_token
from app.models.auth import TokenResponse, LoginRequest

router = APIRouter()
logger = logging.getLogger("main.api.users")

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

@router.post("/v1/users/login")
async def login(request: Request, login_request: LoginRequest):
    
    logger.info(f"Login request for {login_request.username}",
        extra={
        "request_id": request.state.request_id,
        "username": login_request.username
    })
    
    service = request.app.state.user_service
    user = service.authenticate_user(login_request.username, login_request.password)

    if not user:
        logger.warning(f"Logging failed for {login_request.username}", 
        extra={
            "request_id": request.state.request_id,
            "username": login_request.username
        })
        raise APIException(
            code=ErrorCode.UNAUTHORIZED,
            status_code=401,
            message="Invalid username or password",
            details={"username": login_request.username}
        )

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
