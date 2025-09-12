from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db import get_db
from app.utils.cache import Cache
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRegistrationRequest, UserResponse, UserStatus
from app.security.password_security import hash_password, verify_password

class UserService:
    USER_ID_PREFIX = "user:id"
    USER_USERNAME_PREFIX = "user:username"
    USER_RESPONSE_PREFIX = "user:response"
    USERS_ALL_KEY = "users:all"
    TTL = 60 * 60 * 24
    
    def __init__(self, db: Session = Depends(get_db), cache: Cache = Depends(Cache)):
        self.repo = UserRepository(db)
        self.cache = cache

    def add_user(self, user_request: UserRegistrationRequest) -> User:
        """
        Add a new user
        """
        hashed_password = hash_password(user_request.password)
        user = self.repo.create(user_request, hashed_password)
        if self.cache:
            self.cache.invalidate(self.USERS_ALL_KEY)
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user
        """
        user = self.repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Get a user by username
        """
        if self.cache:
            cached_user = self.cache.get_cached(f"{self.USER_USERNAME_PREFIX}:{username}")
            if cached_user:
                return cached_user
        
        user = self.repo.get_by_username(username)
        if self.cache and user:
            self.cache.set_cache(f"{self.USER_USERNAME_PREFIX}:{username}", user, self.TTL)
        return user

    def get_user_by_id(self, id: str) -> Optional[User]:
        """
        Get a user by ID
        """
        if self.cache:
            cached_user = self.cache.get_cached(f"{self.USER_ID_PREFIX}:{id}")
            if cached_user:
                return cached_user
        user = self.repo.get_by_id(id)
        if self.cache and user:
            self.cache.set_cache(f"{self.USER_ID_PREFIX}:{id}", user, self.TTL)
        return user
    
    def get_user_response(self, id: str) -> Optional[UserResponse]:
        """
        Get a user response object
        """
        user = self.get_user_by_id(id)
        if not user:
            return None
        
        if self.cache:
            cached_response = self.cache.get_cached(f"{self.USER_RESPONSE_PREFIX}:{id}")
            if cached_response:
                return cached_response
        
        response = UserResponse(
            id=str(user.id),
            name=user.name,
            username=user.username,
            status=user.status
        )
        
        if self.cache:
            self.cache.set_cache(f"{self.USER_RESPONSE_PREFIX}:{id}", response, self.TTL)
        
        return response
        
    def get_all_users(self) -> List[User]:
        """
        Get all registered users
        """
        if self.cache:
            cached_users = self.cache.get_cached(self.USERS_ALL_KEY)
            if cached_users:
                return cached_users
            users = self.repo.get_all()
            self.cache.set_cache(self.USERS_ALL_KEY, users, self.TTL)
            return users
                
    def update_user_status(self, user_id: str, status: UserStatus) -> Optional[User]:
        """
        Update a user's status
        """
        user = self.repo.update_status(user_id, status)
        if self.cache and user:
            self.cache.invalidate(f"{self.USER_ID_PREFIX}:{user_id}")
            self.cache.invalidate(f"{self.USER_USERNAME_PREFIX}:{user.username}")
            self.cache.invalidate(f"{self.USER_RESPONSE_PREFIX}:{user_id}")
        return user
