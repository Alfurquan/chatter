from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.models.user import UserRegistrationRequest, UserStatus

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_request: UserRegistrationRequest, hashed_password: str) -> User:
        """Create a new user in the database"""
        db_user = User(
            name=user_request.name,
            username=user_request.username,
            password=hashed_password,
            status=UserStatus.ONLINE
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_all(self) -> List[User]:
        """Get all users"""
        return self.db.query(User).all()
    
    def update_status(self, user_id: str, status: UserStatus) -> Optional[User]:
        """Update a user's status"""
        user = self.get_by_id(user_id)
        if user:
            user.status = status
            self.db.commit()
            self.db.refresh(user)
        return user
