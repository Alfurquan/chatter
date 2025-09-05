from fastapi import APIRouter, Request, Depends, Header
from fastapi.responses import JSONResponse
import logging
from ..models.user import UserRegistrationResponse, UserRegistrationRequest, UserResponse
from app.middleware.auth import get_current_user
from app.error.error import APIException, ErrorCode

router = APIRouter()
logger = logging.getLogger("main.api.users")

@router.post("/v1/users/register", response_model=UserRegistrationResponse)
async def register_user(request: Request, user_request: UserRegistrationRequest):    
    try:
        logger.info(f"User registration request for username: {user_request.username}",
                    extra={
                        "request_id": request.state.request_id,
                        "username": user_request.username
                        })
        
        service = request.app.state.user_service
        if service.get_user(user_request.username):
            raise APIException(
                code=ErrorCode.INVALID_REQUEST,
                message="Username already taken",
                details={"username": user_request.username}
            )
        
        user = service.add_user(user_request)

        logger.info(f"User registered: {user.username} (ID: {user.id})",
                    extra={
                        "request_id": request.state.request_id,
                        "username": user.username
                    })

        return JSONResponse(
            status_code=201,
            content=UserRegistrationResponse(
                id=user.id,
                name=user.name,
                username=user.username,
                status=user.status
            ).dict()
        )
    except Exception as e:
        logger.error(f"Error occurred while registering user: {str(e)}",
                     extra={
                         "request_id": request.state.request_id,
                         "username": user_request.username
                     })
        raise APIException(
            code=ErrorCode.INTERNAL_ERROR,
            message="Failed to register user",
            details={"error": str(e)}
        )
        
@router.get("/v1/users/me")
async def me(request: Request, user=Depends(get_current_user)):
    logger.info(f"User info requested for user: {user.username}",
                extra={
                    "request_id": request.state.request_id,
                    "username": user.username
                })
    
    return UserResponse(
        id=user.id,
        name=user.name,
        username=user.username,
        status=user.status
    )
    
@router.get("/v1/users")
async def get_all_users(request: Request, current_user = Depends(get_current_user)):
    """Get all users except the current user"""
    try:
        logger.info(f"Fetching all users excluding current user {current_user.username}",
                    extra={
                        "request_id": request.state.request_id,
                        "username": current_user.username
                    })
        
        service = request.app.state.user_service
        users = service.get_all_users()
        
        other_users = [user for user in users if user.id != current_user.id]
        logger.info(f"Retrieved {len(other_users)} users excluding current user {current_user.username}")
        return JSONResponse(
            status_code=200,
            content=[service.get_user_response(user.id).dict() for user in other_users]
        )
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}",
                     extra={
                            "request_id": request.state.request_id,
                            "username": current_user.username
                        })
        raise APIException(
            code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve users",
            details={"error": str(e)}
        )