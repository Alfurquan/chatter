from typing import Dict
import uuid
from ..models.user import User, UserRegistrationRequest
from ..exception.user_exceptions import UsernameTakenException
from ..security.password_security import hash_password

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
        
        