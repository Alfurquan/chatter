from fastapi import APIRouter, HTTPException, Request
import logging
from ..security.jwt_handler import create_access_token
from app.models.user import LoginRequest

router = APIRouter()
logger = logging.getLogger("main.api.users")

@router.post("/v1/users/login")
async def login(request: Request, login_request: LoginRequest):
    service = request.app.state.user_service
    user = service.authenticate_user(login_request.username, login_request.password)

    if not user:
        logger.warning(f"Logging failed for {login_request.username}", extra={
            "username": login_request.username
        })
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
