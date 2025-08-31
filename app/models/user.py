from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum

class UserStatus(str, Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"

@dataclass
class User:
    id: str
    name: str
    username: str
    password: str
    status: UserStatus = UserStatus.ONLINE

class UserRegistrationRequest(BaseModel):
    name: str = Field(..., min_length=1, description="User's full name")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, description="User password")
    
class UserRegistrationResponse(BaseModel):
    id: str
    name: str
    username: str
    status: UserStatus
    

class LoginRequest(BaseModel):
    username: str
    password: str
    
class UserResponse(BaseModel):
    id: str
    name: str
    username: str
    status: UserStatus