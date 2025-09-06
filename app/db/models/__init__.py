# Import ORM models for easy access
from app.db.models.user import User
from app.db.models.conversation import Conversation, conversation_members
from app.db.models.message import Message

# This allows imports like: from app.db.models import User, Conversation, Message
