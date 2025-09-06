from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db import get_db
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRegistrationRequest, UserResponse, UserStatus
from app.security.password_security import hash_password, verify_password

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.repo = UserRepository(db)
        
    def add_user(self, user_request: UserRegistrationRequest) -> User:
        """Add a new user"""
        hashed_password = hash_password(user_request.password)
        return self.repo.create(user_request, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = self.repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.repo.get_by_username(username)
    
    def get_user_by_id(self, id: str) -> Optional[User]:
        """Get a user by ID"""
        return self.repo.get_by_id(id)
    
    def get_user_response(self, id: str) -> Optional[UserResponse]:
        """Get a user response object"""
        user = self.get_user_by_id(id)
        if not user:
            return None
        
        return UserResponse(
            id=str(user.id),
            name=user.name,
            username=user.username,
            status=user.status
        )
        
    def get_all_users(self) -> List[User]:
        """Get all registered users"""
        return self.repo.get_all()
        
    def update_user_status(self, user_id: str, status: UserStatus) -> Optional[User]:
        """Update a user's status"""
        return self.repo.update_status(user_id, status)
