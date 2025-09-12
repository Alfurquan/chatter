from app.db.models import User

class UserSerializer:
    """
    Serializer for User model
    Converts User instances to and from dictionary representations
    """
    @staticmethod
    def to_dict(user: User) -> dict:
        """
        Convert a User instance to a dictionary
        """
        return {
            "id": str(user.id),
            "name": user.name,
            "username": user.username,
            "status": user.status
        }
        
    @staticmethod
    def from_dict(data: dict) -> User:
        """
        Create a User instance from a dictionary
        """
        user = User(
            id=data.get("id"),
            name=data.get("name"),
            username=data.get("username"),
            status=data.get("status")
        )
        return user