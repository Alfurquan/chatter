from typing import Dict, List
import uuid
from ..models.user import User, UserRegistrationRequest, UserResponse
from ..exception.user_exceptions import UsernameTakenException
from ..security.password_security import hash_password, verify_password

class UserService:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.user_name_to_user: Dict[str, User] = {}
        
    def add_user(self, user_request: UserRegistrationRequest) -> User:
        username = user_request.username
        
        if username in self.user_name_to_user:
            raise UsernameTakenException()
        
        hashed_password = hash_password(user_request.password)
        
        user_id = str(uuid.uuid4())
        user = User(
            id = user_id,
            name = user_request.name,
            username = user_request.username,
            password = hashed_password
        )
        
        self.users[user_id] = user
        self.user_name_to_user[username] = user
        return user
    
    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.user_name_to_user.get(username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
    def get_user(self, username: str) -> User | None:
        user = self.user_name_to_user.get(username)
        if not user:
            return None
        return user
    
    def get_user_by_id(self, id: str) -> User | None:
        user = self.users.get(id)
        if not user:
            return None
        return user
    
    def get_user_response(self, id: str) -> UserResponse | None:
        user = self.get_user_by_id(id)
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            name=user.name,
            username=user.username,
            status=user.status
        )
        
    def get_all_users(self) -> List[User]:
        """Get all registered users"""
        return list(self.users.values())
