from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..models.user import UserRegistrationResponse, UserRegistrationRequest
from ..exception.user_exceptions import UsernameTakenException

router = APIRouter()

@router.post("/v1/users/register", response_model=UserRegistrationResponse)
async def register_user(request: Request, user_request: UserRegistrationRequest):    
    try:
        service = request.app.state.user_service
        user = service.add_user(user_request)
        return JSONResponse(
            status_code=201,
            content=UserRegistrationResponse(
                id=user.id,
                name=user.name,
                username=user.username,
                status=user.status
            ).dict()
        )
    except UsernameTakenException:
        return JSONResponse(
            status_code = 409,
            content = {
                "Error": "username is already taken"
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content={"error": str(e)}
        )